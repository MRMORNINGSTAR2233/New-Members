from typing import Dict, List, Optional, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.models.jira import JiraIssue, JiraComment
from app.services.agents.jira_agent import JiraAgent
from app.utils.audit_logger import audit_logger


router = APIRouter()
jira_agent = JiraAgent()


class EmailToJiraRequest(BaseModel):
    """Model for creating Jira issue from email"""
    email_subject: str
    email_body: str
    project_key: str


class CalendarToJiraRequest(BaseModel):
    """Model for creating Jira issue from calendar event"""
    event_title: str
    event_description: str
    event_start: str
    event_end: str
    project_key: str


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: JiraIssue
):
    """
    Create a new Jira issue directly.
    """
    try:
        issue_key = await jira_agent.create_issue(issue)
        
        audit_logger.log(
            action="jira_issue_created",
            resource_type="jira_issue",
            resource_id=issue_key,
            status="success",
            details={"summary": issue.summary}
        )
        
        return {
            "status": "created",
            "issue_key": issue_key,
            "summary": issue.summary
        }
        
    except Exception as e:
        audit_logger.log(
            action="jira_issue_created",
            resource_type="jira_issue",
            status="failure",
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Jira issue: {e}"
        )


@router.post("/comment/{issue_key}", status_code=status.HTTP_201_CREATED)
async def add_comment(
    issue_key: str,
    comment: JiraComment
):
    """
    Add a comment to a Jira issue.
    """
    try:
        comment_id = await jira_agent.add_comment(issue_key, comment)
        
        audit_logger.log(
            action="jira_comment_added",
            resource_type="jira_comment",
            resource_id=comment_id,
            status="success",
            details={"issue_key": issue_key}
        )
        
        return {
            "status": "created",
            "comment_id": comment_id,
            "issue_key": issue_key
        }
        
    except Exception as e:
        audit_logger.log(
            action="jira_comment_added",
            resource_type="jira_comment",
            status="failure",
            details={"error": str(e), "issue_key": issue_key}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment to Jira issue: {e}"
        )


@router.post("/from-email", status_code=status.HTTP_201_CREATED)
async def create_issue_from_email(
    request: EmailToJiraRequest
):
    """
    Create a Jira issue from email content.
    """
    try:
        # Generate issue from email
        issue = await jira_agent.generate_issue_from_email(
            email_subject=request.email_subject,
            email_body=request.email_body,
            project_key=request.project_key
        )
        
        # Create the issue
        issue_key = await jira_agent.create_issue(issue)
        
        audit_logger.log(
            action="jira_issue_created_from_email",
            resource_type="jira_issue",
            resource_id=issue_key,
            status="success",
            details={"summary": issue.summary}
        )
        
        return {
            "status": "created",
            "issue_key": issue_key,
            "summary": issue.summary
        }
        
    except Exception as e:
        audit_logger.log(
            action="jira_issue_created_from_email",
            resource_type="jira_issue",
            status="failure",
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Jira issue from email: {e}"
        )


@router.post("/from-calendar", status_code=status.HTTP_201_CREATED)
async def create_issue_from_calendar(
    request: CalendarToJiraRequest
):
    """
    Create a Jira issue from calendar event.
    """
    try:
        # Generate issue from calendar event
        issue = await jira_agent.generate_issue_from_calendar(
            event_title=request.event_title,
            event_description=request.event_description,
            event_start=request.event_start,
            event_end=request.event_end,
            project_key=request.project_key
        )
        
        # Create the issue
        issue_key = await jira_agent.create_issue(issue)
        
        audit_logger.log(
            action="jira_issue_created_from_calendar",
            resource_type="jira_issue",
            resource_id=issue_key,
            status="success",
            details={"summary": issue.summary}
        )
        
        return {
            "status": "created",
            "issue_key": issue_key,
            "summary": issue.summary
        }
        
    except Exception as e:
        audit_logger.log(
            action="jira_issue_created_from_calendar",
            resource_type="jira_issue",
            status="failure",
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Jira issue from calendar event: {e}"
        )
