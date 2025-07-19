from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class JiraAttachment(BaseModel):
    """Model representing a Jira attachment"""
    filename: str
    file_data: bytes
    content_type: Optional[str] = None


class JiraIssue(BaseModel):
    """Model representing a Jira issue"""
    project_key: str
    summary: str
    description: str
    issue_type: str = "Task"  # Default to Task
    assignee: Optional[str] = None
    priority: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    due_date: Optional[str] = None  # ISO format date
    attachments: List[JiraAttachment] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class JiraComment(BaseModel):
    """Model representing a Jira comment"""
    body: str
    visibility_type: Optional[str] = None  # e.g., "group", "role"
    visibility_value: Optional[str] = None  # e.g., "developers", "Administrators"
