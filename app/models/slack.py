from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class SlackMessage(BaseModel):
    """Model representing a Slack message"""
    text: str
    user: str
    channel: str
    ts: str
    thread_ts: Optional[str] = None


class SlackCommand(BaseModel):
    """Model representing a Slack slash command"""
    command: str
    text: str
    user_id: str
    channel_id: str
    response_url: str
    trigger_id: str


class SlackEventType(BaseModel):
    """Model representing a Slack event"""
    type: str
    user: Optional[str] = None
    channel: Optional[str] = None
    text: Optional[str] = None
    ts: Optional[str] = None
    thread_ts: Optional[str] = None
    bot_id: Optional[str] = None


class SlackEventPayload(BaseModel):
    """Model representing a Slack event payload"""
    token: str
    team_id: str
    api_app_id: str
    event: SlackEventType
    type: str
    event_id: str
    event_time: int
