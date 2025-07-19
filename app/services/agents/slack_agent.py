import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

from app.core.config import settings
from app.models.slack import SlackMessage, SlackCommand, SlackEventPayload
from app.services.llm.gemini_provider import gemini_model
from app.utils.audit_logger import audit_logger


class SlackAgent:
    """
    Agent for interacting with Slack API, handling incoming events and sending messages.
    """

    def __init__(self):
        """Initialize the Slack agent with API token and signature verifier"""
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)
        self.signature_verifier = SignatureVerifier(settings.SLACK_SIGNING_SECRET)
        
        # Initialize event handlers
        self.event_handlers = {
            "message": self._handle_message,
            "app_mention": self._handle_mention,
        }
        
        # Initialize command handlers
        self.command_handlers = {}
        
        audit_logger.log(
            action="slack_agent_initialized",
            resource_type="slack",
            status="success"
        )
    
    def verify_signature(self, 
                        signature: str, 
                        timestamp: str, 
                        body: str) -> bool:
        """
        Verify the request signature from Slack.
        
        Args:
            signature: X-Slack-Signature header value
            timestamp: X-Slack-Request-Timestamp header value
            body: Request body
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Check if timestamp is too old (>5 min)
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
            
        # Verify signature
        return self.signature_verifier.is_valid(
            body=body,
            timestamp=timestamp,
            signature=signature
        )
    
    def register_command_handler(self, 
                               command: str, 
                               handler: Callable[[SlackCommand], Dict[str, Any]]):
        """
        Register a handler function for a slash command.
        
        Args:
            command: The slash command (e.g., "/approve")
            handler: Function to handle the command
        """
        self.command_handlers[command] = handler
        
        audit_logger.log(
            action="slack_command_handler_registered",
            resource_type="slack",
            status="success",
            details={"command": command}
        )
    
    def register_workflow_trigger(self, 
                                trigger_keyword: str, 
                                workflow_function: Callable):
        """
        Register a workflow trigger for specific messages.
        
        Args:
            trigger_keyword: Keyword to trigger the workflow
            workflow_function: Function to trigger the workflow
        """
        # This would integrate with a more complex workflow system
        pass
    
    async def handle_event(self, payload: SlackEventPayload) -> Dict[str, Any]:
        """
        Process an incoming Slack event.
        
        Args:
            payload: Slack event payload
            
        Returns:
            Dictionary with processing results
        """
        # Extract event data
        event_type = payload.event.type
        
        # Check if we have a handler for this event type
        if event_type in self.event_handlers:
            result = await self.event_handlers[event_type](payload.event)
            
            audit_logger.log(
                action=f"slack_event_handled_{event_type}",
                resource_type="slack_event",
                status="success",
                details={"event_type": event_type}
            )
            
            return result
        else:
            audit_logger.log(
                action="slack_event_unhandled",
                resource_type="slack_event",
                status="warning",
                details={"event_type": event_type}
            )
            
            return {"status": "unhandled", "event_type": event_type}
    
    async def handle_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming Slack slash command.
        
        Args:
            command_data: Slack command data
            
        Returns:
            Dictionary with processing results
        """
        command = command_data.get("command", "")
        
        # Create command model
        slack_command = SlackCommand(
            command=command,
            text=command_data.get("text", ""),
            user_id=command_data.get("user_id", ""),
            channel_id=command_data.get("channel_id", ""),
            response_url=command_data.get("response_url", ""),
            trigger_id=command_data.get("trigger_id", "")
        )
        
        # Check if we have a handler for this command
        if command in self.command_handlers:
            result = await self.command_handlers[command](slack_command)
            
            audit_logger.log(
                action="slack_command_handled",
                resource_type="slack_command",
                status="success",
                details={"command": command}
            )
            
            return result
        else:
            audit_logger.log(
                action="slack_command_unhandled",
                resource_type="slack_command",
                status="warning",
                details={"command": command}
            )
            
            return {
                "response_type": "ephemeral",
                "text": f"Sorry, I don't know how to handle the {command} command."
            }
    
    async def _handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message events.
        
        Args:
            event: Slack message event
            
        Returns:
            Processing result
        """
        # Ignore messages from bots (including our own)
        if event.get("bot_id"):
            return {"status": "ignored", "reason": "bot_message"}
        
        message = SlackMessage(
            text=event.get("text", ""),
            user=event.get("user", ""),
            channel=event.get("channel", ""),
            ts=event.get("ts", ""),
            thread_ts=event.get("thread_ts", None)
        )
        
        # Basic message processing logic
        # In a real app, this would be more sophisticated
        
        # Analyze message content with LLM if needed
        if any(keyword in message.text.lower() for keyword in ["help", "assist", "how to"]):
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""
                You are a helpful assistant that provides brief, concise answers to user questions.
                Keep your responses under 300 characters and focus on being practical.
                """),
                HumanMessage(content=message.text)
            ])
            
            response = gemini_model.invoke(prompt)
            
            # Post response to thread
            try:
                self.client.chat_postMessage(
                    channel=message.channel,
                    thread_ts=message.ts,
                    text=response.content
                )
                return {"status": "response_sent", "type": "help"}
            except SlackApiError as e:
                audit_logger.log(
                    action="slack_post_message",
                    resource_type="slack",
                    status="failure",
                    details={"error": str(e)}
                )
                return {"status": "error", "error": str(e)}
        
        return {"status": "processed", "action": "none_needed"}
    
    async def _handle_mention(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle app mention events.
        
        Args:
            event: Slack app_mention event
            
        Returns:
            Processing result
        """
        message = SlackMessage(
            text=event.get("text", ""),
            user=event.get("user", ""),
            channel=event.get("channel", ""),
            ts=event.get("ts", ""),
            thread_ts=event.get("thread_ts", None)
        )
        
        # Process the mention with LLM
        # Remove the bot mention from the text
        clean_text = message.text.split(">", 1)[1].strip() if ">" in message.text else message.text
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are an AI assistant in a Slack channel. You've been directly mentioned by a user.
            Provide a helpful, concise response under 200 characters. Be professional but friendly.
            """),
            HumanMessage(content=clean_text)
        ])
        
        response = gemini_model.invoke(prompt)
        
        # Post response
        try:
            self.client.chat_postMessage(
                channel=message.channel,
                thread_ts=message.ts if message.thread_ts is None else message.thread_ts,
                text=response.content
            )
            return {"status": "response_sent", "type": "mention"}
        except SlackApiError as e:
            audit_logger.log(
                action="slack_post_message",
                resource_type="slack",
                status="failure",
                details={"error": str(e)}
            )
            return {"status": "error", "error": str(e)}
    
    async def post_notification(self, 
                              channel: str, 
                              text: str, 
                              blocks: Optional[List[Dict[str, Any]]] = None,
                              thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a notification to a Slack channel.
        
        Args:
            channel: Channel ID to post to
            text: Message text
            blocks: Optional message blocks for rich formatting
            thread_ts: Optional thread timestamp to reply in thread
            
        Returns:
            API response from Slack
        """
        try:
            result = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts
            )
            
            audit_logger.log(
                action="slack_notification_sent",
                resource_type="slack",
                status="success",
                details={"channel": channel}
            )
            
            return result
        except SlackApiError as e:
            audit_logger.log(
                action="slack_post_message",
                resource_type="slack",
                status="failure",
                details={"error": str(e), "channel": channel}
            )
            raise
    
    async def open_approval_dialog(self, 
                                 trigger_id: str, 
                                 title: str, 
                                 content: str,
                                 callback_id: str) -> Dict[str, Any]:
        """
        Open a dialog for approval workflow.
        
        Args:
            trigger_id: The trigger ID from Slack interaction
            title: Dialog title
            content: Content to be approved
            callback_id: ID for the callback when form is submitted
            
        Returns:
            API response from Slack
        """
        try:
            result = self.client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": callback_id,
                    "title": {"type": "plain_text", "text": title},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Please review the following content:"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": content
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Approve"
                                    },
                                    "style": "primary",
                                    "value": "approve"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Reject"
                                    },
                                    "style": "danger",
                                    "value": "reject"
                                }
                            ]
                        }
                    ]
                }
            )
            
            audit_logger.log(
                action="slack_approval_dialog_opened",
                resource_type="slack",
                status="success",
                details={"callback_id": callback_id}
            )
            
            return result
        except SlackApiError as e:
            audit_logger.log(
                action="slack_open_dialog",
                resource_type="slack",
                status="failure",
                details={"error": str(e)}
            )
            raise
