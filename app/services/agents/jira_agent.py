from typing import Dict, List, Optional, Any

import jira
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.models.jira import JiraIssue, JiraComment
from app.services.llm.gemini_provider import gemini_model
from app.utils.audit_logger import audit_logger


class JiraAgent:
    """
    Agent for interacting with Jira API, creating issues and comments.
    """

    def __init__(self):
        """Initialize the Jira agent with API connection"""
        self.client = jira.JIRA(
            server=settings.JIRA_SERVER_URL,
            basic_auth=(settings.JIRA_USER_EMAIL, settings.JIRA_API_TOKEN)
        )
        
        audit_logger.log(
            action="jira_agent_initialized",
            resource_type="jira",
            status="success"
        )
    
    async def create_issue(self, issue_data: JiraIssue) -> str:
        """
        Create a new Jira issue.
        
        Args:
            issue_data: JiraIssue object with issue details
            
        Returns:
            Key of the created issue
        """
        # Convert our model to Jira's expected format
        fields = {
            'project': {'key': issue_data.project_key},
            'summary': issue_data.summary,
            'description': issue_data.description,
            'issuetype': {'name': issue_data.issue_type},
        }
        
        # Add optional fields if present
        if issue_data.assignee:
            fields['assignee'] = {'name': issue_data.assignee}
            
        if issue_data.priority:
            fields['priority'] = {'name': issue_data.priority}
            
        if issue_data.labels:
            fields['labels'] = issue_data.labels
            
        if issue_data.components:
            fields['components'] = [{'name': c} for c in issue_data.components]
            
        # Add any custom fields
        if issue_data.custom_fields:
            for field_id, value in issue_data.custom_fields.items():
                fields[field_id] = value
        
        try:
            # Create the issue
            new_issue = self.client.create_issue(fields=fields)
            
            # Add any attachments
            if issue_data.attachments:
                for attachment in issue_data.attachments:
                    self.client.add_attachment(
                        issue=new_issue.key,
                        attachment=attachment.file_data,
                        filename=attachment.filename
                    )
            
            audit_logger.log(
                action="jira_issue_created",
                resource_type="jira_issue",
                resource_id=new_issue.key,
                status="success",
                details={
                    "project": issue_data.project_key,
                    "summary": issue_data.summary,
                    "issue_type": issue_data.issue_type
                }
            )
            
            return new_issue.key
            
        except Exception as e:
            audit_logger.log(
                action="jira_issue_created",
                resource_type="jira_issue",
                status="failure",
                details={"error": str(e), "issue_data": issue_data.model_dump()}
            )
            raise
    
    async def add_comment(self, issue_key: str, comment_data: JiraComment) -> str:
        """
        Add a comment to a Jira issue.
        
        Args:
            issue_key: Key of the issue to comment on
            comment_data: JiraComment object with comment details
            
        Returns:
            ID of the created comment
        """
        try:
            comment = self.client.add_comment(
                issue_key, 
                comment_data.body,
                visibility={'type': comment_data.visibility_type, 
                           'value': comment_data.visibility_value} if comment_data.visibility_type else None
            )
            
            audit_logger.log(
                action="jira_comment_added",
                resource_type="jira_comment",
                resource_id=str(comment.id),
                status="success",
                details={"issue_key": issue_key}
            )
            
            return str(comment.id)
            
        except Exception as e:
            audit_logger.log(
                action="jira_comment_added",
                resource_type="jira_comment",
                status="failure",
                details={"error": str(e), "issue_key": issue_key}
            )
            raise
    
    async def generate_issue_from_email(self, email_subject: str, email_body: str, project_key: str) -> JiraIssue:
        """
        Generate a Jira issue from an email using LLM processing.
        
        Args:
            email_subject: Subject of the email
            email_body: Body of the email
            project_key: Key of the Jira project
            
        Returns:
            JiraIssue object ready to be created
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are an AI assistant that converts emails into structured Jira issues.
            Based on the email content, extract:
            
            1. A concise but descriptive summary (title)
            2. A well-formatted description with key details
            3. The appropriate issue type (Task, Bug, Story, etc.)
            4. Priority level (if mentioned)
            5. Any labels that would be appropriate
            
            Format your response as a JSON object with these keys:
            summary, description, issue_type, priority, labels
            """),
            HumanMessage(content=f"""
            Email Subject: {email_subject}
            
            Email Body:
            {email_body}
            """)
        ])
        
        # Get issue details from LLM
        response = gemini_model.invoke(prompt)
        
        try:
            # Parse the response into a dictionary
            issue_dict = eval(response.content.strip())
            
            # Create JiraIssue object
            issue = JiraIssue(
                project_key=project_key,
                summary=issue_dict.get("summary", email_subject),
                description=issue_dict.get("description", email_body),
                issue_type=issue_dict.get("issue_type", "Task"),
                priority=issue_dict.get("priority"),
                labels=issue_dict.get("labels", [])
            )
            
            audit_logger.log(
                action="jira_issue_generated_from_email",
                resource_type="jira_issue",
                status="success",
                details={"email_subject": email_subject}
            )
            
            return issue
            
        except Exception as e:
            # Fallback if parsing fails
            issue = JiraIssue(
                project_key=project_key,
                summary=email_subject,
                description=email_body,
                issue_type="Task"
            )
            
            audit_logger.log(
                action="jira_issue_generated_from_email",
                resource_type="jira_issue",
                status="failure",
                details={"error": str(e), "email_subject": email_subject}
            )
            
            return issue
    
    async def generate_issue_from_calendar(self, 
                                        event_title: str, 
                                        event_description: str,
                                        event_start: str,
                                        event_end: str,
                                        project_key: str) -> JiraIssue:
        """
        Generate a Jira issue from a calendar event using LLM processing.
        
        Args:
            event_title: Title of the calendar event
            event_description: Description of the calendar event
            event_start: Start time of the event
            event_end: End time of the event
            project_key: Key of the Jira project
            
        Returns:
            JiraIssue object ready to be created
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are an AI assistant that converts calendar events into structured Jira issues.
            Based on the event details, extract:
            
            1. A concise but descriptive summary (title)
            2. A well-formatted description with key details and action items
            3. The appropriate issue type (usually Task)
            4. Priority level (default to Medium if not clear)
            5. Any labels that would be appropriate
            6. Due date (based on the event timing)
            
            Format your response as a JSON object with these keys:
            summary, description, issue_type, priority, labels, due_date
            """),
            HumanMessage(content=f"""
            Event Title: {event_title}
            Event Description: {event_description}
            Event Start: {event_start}
            Event End: {event_end}
            """)
        ])
        
        # Get issue details from LLM
        response = gemini_model.invoke(prompt)
        
        try:
            # Parse the response into a dictionary
            issue_dict = eval(response.content.strip())
            
            # Create JiraIssue object
            issue = JiraIssue(
                project_key=project_key,
                summary=issue_dict.get("summary", event_title),
                description=issue_dict.get("description", 
                                         f"{event_description}\n\nEvent Time: {event_start} to {event_end}"),
                issue_type=issue_dict.get("issue_type", "Task"),
                priority=issue_dict.get("priority", "Medium"),
                labels=issue_dict.get("labels", []),
                due_date=issue_dict.get("due_date")
            )
            
            audit_logger.log(
                action="jira_issue_generated_from_calendar",
                resource_type="jira_issue",
                status="success",
                details={"event_title": event_title}
            )
            
            return issue
            
        except Exception as e:
            # Fallback if parsing fails
            issue = JiraIssue(
                project_key=project_key,
                summary=event_title,
                description=f"{event_description}\n\nEvent Time: {event_start} to {event_end}",
                issue_type="Task"
            )
            
            audit_logger.log(
                action="jira_issue_generated_from_calendar",
                resource_type="jira_issue",
                status="failure",
                details={"error": str(e), "event_title": event_title}
            )
            
            return issue
