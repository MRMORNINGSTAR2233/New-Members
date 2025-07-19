from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    """Model representing an email message from Gmail API"""
    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    date: str
    body: str
    labels: List[str]


class EmailSummary(BaseModel):
    """Model representing a summarized email"""
    main_purpose: str
    key_details: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    deadlines: List[str] = Field(default_factory=list)


class ReplyDraft(BaseModel):
    """Model representing a draft reply to an email"""
    to: str
    subject: str
    body: str
    needs_review: bool = True
