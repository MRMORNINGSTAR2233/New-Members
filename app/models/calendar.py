from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    """Model representing an available time slot"""
    start: str  # ISO format datetime
    end: str  # ISO format datetime
    timezone: str = "UTC"


class CalendarEvent(BaseModel):
    """Model representing a calendar event"""
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: str  # ISO format datetime
    end_time: str  # ISO format datetime
    timezone: str = "UTC"
    attendees: List[Dict[str, str]] = Field(default_factory=list)
    conference_data: Optional[Dict[str, Any]] = None
    
    def to_google_calendar_dict(self) -> Dict[str, Any]:
        """Convert to Google Calendar API event format"""
        event = {
            'summary': self.summary,
            'start': {
                'dateTime': self.start_time,
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': self.end_time,
                'timeZone': self.timezone,
            }
        }
        
        if self.description:
            event['description'] = self.description
            
        if self.location:
            event['location'] = self.location
            
        if self.attendees:
            event['attendees'] = self.attendees
            
        if self.conference_data:
            event['conferenceData'] = self.conference_data
            
        return event
