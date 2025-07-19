from typing import Dict, List, Optional, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.services.agents.gmail_agent import GmailAgent
from app.services.auth.google_auth import get_google_credentials
from app.utils.audit_logger import audit_logger


router = APIRouter()


class EmailProcessRequest(BaseModel):
    """Model for email processing request"""
    user_id: str
    max_emails: Optional[int] = 10


@router.post("/webhook/process", status_code=status.HTTP_202_ACCEPTED)
async def process_emails(
    request: EmailProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Process unread emails for a user.
    
    This endpoint is triggered by webhooks or scheduled tasks to
    process unread emails in the background.
    """
    try:
        # Add the task to background processing
        background_tasks.add_task(process_emails_task, request.user_id, request.max_emails)
        
        audit_logger.log(
            action="email_processing_queued",
            resource_type="email",
            status="success",
            user_id=request.user_id
        )
        
        return {"status": "processing", "message": "Email processing started"}
        
    except Exception as e:
        audit_logger.log(
            action="email_processing_queued",
            resource_type="email",
            status="failure",
            user_id=request.user_id,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue email processing: {e}"
        )


async def process_emails_task(user_id: str, max_emails: int = 10):
    """
    Background task to process unread emails.
    
    Args:
        user_id: ID of the user
        max_emails: Maximum number of emails to process
    """
    try:
        # Get credentials for the user
        credentials = get_google_credentials(user_id, None)  # Use default scopes
        
        # Initialize the Gmail agent
        gmail_agent = GmailAgent(user_id, credentials)
        
        # Process unread emails
        results = await gmail_agent.process_unread(max_emails)
        
        audit_logger.log(
            action="email_processing_completed",
            resource_type="email",
            status="success",
            user_id=user_id,
            details={"processed_count": len(results)}
        )
        
    except Exception as e:
        audit_logger.log(
            action="email_processing_completed",
            resource_type="email",
            status="failure",
            user_id=user_id,
            details={"error": str(e)}
        )
