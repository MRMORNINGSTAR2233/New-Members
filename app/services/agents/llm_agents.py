from typing import Dict, List, Optional, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.models.email import EmailMessage, EmailSummary, ReplyDraft
from app.services.llm.gemini_provider import gemini_model
from app.utils.audit_logger import audit_logger


class ClassifierAgent:
    """
    Sub-agent for classifying email content into categories like
    'auto-reply', 'draft-for-review', or 'manual'.
    """
    
    @staticmethod
    async def classify(email: EmailMessage) -> str:
        """
        Classify an email based on its content.
        
        Args:
            email: The email to classify
            
        Returns:
            Classification category
        """
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
        
        audit_logger.log(
            action="email_classified",
            resource_type="email",
            resource_id=email.message_id,
            status="success",
            details={"classification": classification}
        )
        
        return classification


class SummarizerAgent:
    """
    Sub-agent for condensing an email thread into concise bullet points.
    """
    
    @staticmethod
    async def summarize(email: EmailMessage) -> EmailSummary:
        """
        Summarize an email into key components.
        
        Args:
            email: The email to summarize
            
        Returns:
            EmailSummary object
        """
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
                details={"error": str(e)}
            )
            return summary
        
        audit_logger.log(
            action="email_summarized",
            resource_type="email",
            resource_id=email.message_id,
            status="success"
        )
        
        return summary


class ReplyAgent:
    """
    Sub-agent for drafting context-aware replies based on email content and summary.
    """
    
    @staticmethod
    async def draft_reply(email: EmailMessage, summary: EmailSummary, classification: str) -> ReplyDraft:
        """
        Draft a reply to an email based on its content and summary.
        
        Args:
            email: The original email
            summary: Summary of the email
            classification: Classification of the email
            
        Returns:
            ReplyDraft object
        """
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
        
        audit_logger.log(
            action="email_reply_drafted",
            resource_type="email",
            resource_id=email.message_id,
            status="success",
            details={"needs_review": reply_draft.needs_review}
        )
        
        return reply_draft
