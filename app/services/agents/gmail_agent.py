import base64
import os
from typing import Dict, List, Optional, Any, Tuple

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain.schema import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.models.email import EmailMessage, EmailSummary, ReplyDraft
from app.services.auth.google_auth import get_google_credentials
from app.services.llm.gemini_provider import gemini_model
from app.utils.audit_logger import audit_logger


class GmailAgent:
    """
    Agent for interacting with Gmail, using LangGraph for orchestrating
    the email processing workflow.
    """

    def __init__(self, user_id: str, credentials: Optional[Credentials] = None):
        """
        Initialize the Gmail agent with user credentials.
        
        Args:
            user_id: The ID of the user whose Gmail is being accessed
            credentials: Optional Google OAuth2 credentials. If not provided,
                        they will be loaded using the user_id.
        """
        self.user_id = user_id
        
        # Initialize credentials if not provided
        if credentials is None:
            credentials = get_google_credentials(user_id, settings.GOOGLE_GMAIL_SCOPES)
        
        # Refresh credentials if expired
        if credentials.expired:
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
        
        # Create Gmail API client
        self.gmail_service = build('gmail', 'v1', credentials=credentials)
        
        # Initialize the LangGraph workflow for email processing
        self._create_email_workflow()
        
        audit_logger.log(
            action="gmail_agent_initialized",
            resource_type="gmail",
            status="success",
            user_id=user_id
        )
    
    def _create_email_workflow(self):
        """Create the LangGraph workflow for email processing"""
        # Define the state schema
        state_schema = {
            "email": EmailMessage,
            "classification": str,
            "summary": Optional[EmailSummary],
            "reply_draft": Optional[ReplyDraft],
            "user_id": str
        }
        
        # Create a new graph
        workflow = StateGraph(state_schema)
        
        # Add nodes for each step of the workflow
        workflow.add_node("classifier", self._classify_email)
        workflow.add_node("summarizer", self._summarize_email)
        workflow.add_node("reply_drafter", self._draft_reply)
        
        # Define the workflow edges
        workflow.add_edge("classifier", "summarizer")
        
        # Conditional edge: only draft replies for auto-reply or draft-for-review
        workflow.add_conditional_edges(
            "summarizer",
            lambda state: state["classification"] if state["classification"] in ["auto-reply", "draft-for-review"] else END,
            {
                "auto-reply": "reply_drafter", 
                "draft-for-review": "reply_drafter"
            }
        )
        
        # Set entry point
        workflow.set_entry_point("classifier")
        
        # Compile the graph
        self.email_workflow = workflow.compile()
    
    def _classify_email(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify an email as auto-reply, draft-for-review, or manual handling.
        
        Args:
            state: The current state containing the email
            
        Returns:
            Updated state with classification
        """
        email = state["email"]
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are an email classifier. Analyze the email content and categorize it into one of these categories:
            - auto-reply: Simple emails that can be automatically replied to without human review
            - draft-for-review: Emails that need a human to review a draft reply before sending
            - manual: Complex emails that require complete human attention
            
            Respond with ONLY the category name, nothing else.
            """),
            HumanMessage(content=f"""
            Subject: {email.subject}
            
            From: {email.sender}
            
            Body:
            {email.body}
            """)
        ])
        
        # Get classification from LLM
        response = gemini_model.invoke(prompt)
        classification = response.content.strip().lower()
        
        # Validate classification
        valid_classifications = ["auto-reply", "draft-for-review", "manual"]
        if classification not in valid_classifications:
            classification = "manual"  # Default to manual if invalid
        
        # Update state
        state["classification"] = classification
        
        audit_logger.log(
            action="email_classified",
            resource_type="email",
            resource_id=email.message_id,
            status="success",
            user_id=state["user_id"],
            details={"classification": classification}
        )
        
        return state
    
    def _summarize_email(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize an email thread into concise bullet points.
        
        Args:
            state: The current state containing the email
            
        Returns:
            Updated state with summary
        """
        email = state["email"]
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            Summarize the following email into concise bullet points. Extract:
            1. Main request or purpose of the email
            2. Key details or information provided
            3. Any explicit questions that need to be answered
            4. Any deadlines or time constraints mentioned
            
            Format your response as a JSON object with these keys: 
            main_purpose, key_details (array), questions (array), deadlines (array)
            """),
            HumanMessage(content=f"""
            Subject: {email.subject}
            
            From: {email.sender}
            
            Body:
            {email.body}
            """)
        ])
        
        # Get summary from LLM
        response = gemini_model.invoke(prompt)
        
        # Parse the summary into our data model
        try:
            summary_dict = eval(response.content.strip())
            summary = EmailSummary(
                main_purpose=summary_dict.get("main_purpose", ""),
                key_details=summary_dict.get("key_details", []),
                questions=summary_dict.get("questions", []),
                deadlines=summary_dict.get("deadlines", [])
            )
        except Exception as e:
            # Fallback if parsing fails
            summary = EmailSummary(
                main_purpose="Failed to extract summary",
                key_details=[],
                questions=[],
                deadlines=[]
            )
            audit_logger.log(
                action="email_summarized",
                resource_type="email",
                resource_id=email.message_id,
                status="failure",
                user_id=state["user_id"],
                details={"error": str(e)}
            )
        
        # Update state
        state["summary"] = summary
        
        audit_logger.log(
            action="email_summarized",
            resource_type="email",
            resource_id=email.message_id,
            status="success",
            user_id=state["user_id"]
        )
        
        return state
    
    def _draft_reply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Draft a context-aware reply based on the email and its summary.
        
        Args:
            state: The current state containing the email and summary
            
        Returns:
            Updated state with reply draft
        """
        email = state["email"]
        summary = state["summary"]
        classification = state["classification"]
        
        # Different system prompts based on classification
        system_content = """
        You are an email assistant drafting a reply. The email has been classified as 
        """
        
        if classification == "auto-reply":
            system_content += """
            'auto-reply', which means you can draft a complete response that can be sent
            automatically without human review. Be professional, clear, and concise.
            """
        else:  # draft-for-review
            system_content += """
            'draft-for-review', which means your draft will be reviewed by a human before
            sending. Address all questions and requests, but mark any areas of uncertainty
            with [CHECK: your question] for human review.
            """
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_content),
            HumanMessage(content=f"""
            Email Subject: {email.subject}
            
            From: {email.sender}
            
            Email Body:
            {email.body}
            
            Summary:
            Main Purpose: {summary.main_purpose}
            Key Details: {', '.join(summary.key_details)}
            Questions: {', '.join(summary.questions)}
            Deadlines: {', '.join(summary.deadlines)}
            
            Draft a professional and helpful reply to this email.
            """)
        ])
        
        # Get draft reply from LLM
        response = gemini_model.invoke(prompt)
        
        # Create reply draft
        reply_draft = ReplyDraft(
            to=email.sender,
            subject=f"Re: {email.subject}",
            body=response.content.strip(),
            needs_review=(classification == "draft-for-review")
        )
        
        # Update state
        state["reply_draft"] = reply_draft
        
        audit_logger.log(
            action="email_reply_drafted",
            resource_type="email",
            resource_id=email.message_id,
            status="success",
            user_id=state["user_id"],
            details={"needs_review": reply_draft.needs_review}
        )
        
        return state
    
    async def process_unread(self, max_emails: int = 10) -> List[Dict[str, Any]]:
        """
        Process unread emails from the user's inbox.
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            List of processed email results
        """
        # Fetch unread messages
        query = "is:unread"
        results = self.gmail_service.users().messages().list(
            userId="me", 
            q=query, 
            maxResults=max_emails
        ).execute()
        
        messages = results.get("messages", [])
        processed_results = []
        
        for message in messages:
            msg_id = message["id"]
            
            # Get the email content
            msg = self.gmail_service.users().messages().get(
                userId="me", 
                id=msg_id, 
                format="full"
            ).execute()
            
            email = self._parse_gmail_message(msg)
            
            # Mark as read
            self.gmail_service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            
            # Process through workflow
            result = self.email_workflow.invoke({
                "email": email,
                "classification": None,
                "summary": None,
                "reply_draft": None,
                "user_id": self.user_id
            })
            
            processed_results.append(result)
            
            audit_logger.log(
                action="email_processed",
                resource_type="email",
                resource_id=msg_id,
                status="success",
                user_id=self.user_id,
                details={"classification": result["classification"]}
            )
        
        return processed_results
    
    def _parse_gmail_message(self, msg: Dict) -> EmailMessage:
        """
        Parse a Gmail API message into our EmailMessage model.
        
        Args:
            msg: Gmail API message object
            
        Returns:
            Parsed EmailMessage
        """
        headers = msg["payload"]["headers"]
        
        # Extract headers
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "")
        to = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
        date = next((h["value"] for h in headers if h["name"].lower() == "date"), "")
        
        # Extract body
        body = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(
                        part["body"].get("data", "").encode("ASCII")
                    ).decode("utf-8")
                    break
        elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
            body = base64.urlsafe_b64decode(
                msg["payload"]["body"]["data"].encode("ASCII")
            ).decode("utf-8")
        
        return EmailMessage(
            message_id=msg["id"],
            thread_id=msg["threadId"],
            subject=subject,
            sender=sender,
            recipient=to,
            date=date,
            body=body,
            labels=msg["labelIds"]
        )
    
    def send_reply(self, reply: ReplyDraft) -> str:
        """
        Send a reply to an email.
        
        Args:
            reply: The reply to send
            
        Returns:
            The message ID of the sent email
        """
        # Create the email message
        message = {
            "raw": base64.urlsafe_b64encode(
                f"""To: {reply.to}
Subject: {reply.subject}
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8

{reply.body}
""".encode("utf-8")
            ).decode("utf-8")
        }
        
        # Send the message
        sent_message = self.gmail_service.users().messages().send(
            userId="me", 
            body=message
        ).execute()
        
        message_id = sent_message["id"]
        
        audit_logger.log(
            action="email_reply_sent",
            resource_type="email",
            resource_id=message_id,
            status="success",
            user_id=self.user_id
        )
        
        return message_id
