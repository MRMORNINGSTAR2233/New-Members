import datetime
from typing import Dict, List, Optional, Any, Tuple

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.models.calendar import CalendarEvent, TimeSlot
from app.services.auth.google_auth import get_google_credentials
from app.services.llm.gemini_provider import gemini_model
from app.utils.audit_logger import audit_logger


class CalendarAgent:
    """
    Agent for interacting with Google Calendar, using LangGraph for orchestrating
    calendar-related workflows.
    """

    def __init__(self, user_id: str, credentials: Optional[Credentials] = None):
        """
        Initialize the Calendar agent with user credentials.
        
        Args:
            user_id: The ID of the user whose Calendar is being accessed
            credentials: Optional Google OAuth2 credentials. If not provided,
                        they will be loaded using the user_id.
        """
        self.user_id = user_id
        
        # Initialize credentials if not provided
        if credentials is None:
            credentials = get_google_credentials(user_id, settings.GOOGLE_CALENDAR_SCOPES)
        
        # Refresh credentials if expired
        if credentials.expired:
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
        
        # Create Calendar API client
        self.calendar_service = build('calendar', 'v3', credentials=credentials)
        
        audit_logger.log(
            action="calendar_agent_initialized",
            resource_type="calendar",
            status="success",
            user_id=user_id
        )
    
    async def create_event(self, event_data: Dict[str, Any]) -> str:
        """
        Create a new calendar event.
        
        Args:
            event_data: Dictionary containing event details
            
        Returns:
            ID of the created event
        """
        # Create the event
        try:
            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            
            event_id = event['id']
            
            audit_logger.log(
                action="calendar_event_created",
                resource_type="calendar_event",
                resource_id=event_id,
                status="success",
                user_id=self.user_id,
                details={
                    "summary": event_data.get("summary", ""),
                    "start": str(event_data.get("start", {})),
                    "end": str(event_data.get("end", {}))
                }
            )
            
            return event_id
            
        except Exception as e:
            audit_logger.log(
                action="calendar_event_created",
                resource_type="calendar_event",
                status="failure",
                user_id=self.user_id,
                details={"error": str(e), "event_data": str(event_data)}
            )
            raise
    
    async def propose_time_slots(self, 
                               duration_minutes: int,
                               start_date: str,
                               end_date: str,
                               timezone: str = "UTC",
                               working_hours: Optional[Dict[str, Tuple[int, int]]] = None) -> List[TimeSlot]:
        """
        Propose available time slots based on free/busy information.
        
        Args:
            duration_minutes: Duration of the proposed event in minutes
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            timezone: Timezone for the proposed slots
            working_hours: Dictionary mapping weekday names to (start_hour, end_hour) tuples
                          e.g. {"monday": (9, 17)} for 9 AM to 5 PM
            
        Returns:
            List of available time slots
        """
        # Default working hours if not provided (9 AM to 5 PM, Monday to Friday)
        if working_hours is None:
            working_hours = {
                "monday": (9, 17),
                "tuesday": (9, 17),
                "wednesday": (9, 17),
                "thursday": (9, 17),
                "friday": (9, 17)
            }
        
        # Parse dates
        start_datetime = datetime.datetime.fromisoformat(f"{start_date}T00:00:00")
        end_datetime = datetime.datetime.fromisoformat(f"{end_date}T23:59:59")
        
        # Get busy periods
        body = {
            "timeMin": start_datetime.isoformat() + 'Z',
            "timeMax": end_datetime.isoformat() + 'Z',
            "timeZone": timezone,
            "items": [{"id": "primary"}]
        }
        
        freebusy_response = self.calendar_service.freebusy().query(body=body).execute()
        busy_periods = freebusy_response['calendars']['primary']['busy']
        
        # Generate all possible slots within working hours
        available_slots = []
        current_date = start_datetime.date()
        end_date_obj = end_datetime.date()
        
        while current_date <= end_date_obj:
            weekday = current_date.strftime('%A').lower()
            
            # Skip if not a working day
            if weekday not in working_hours:
                current_date += datetime.timedelta(days=1)
                continue
            
            start_hour, end_hour = working_hours[weekday]
            
            # Create slots for this day
            slot_start = datetime.datetime.combine(
                current_date,
                datetime.time(hour=start_hour, minute=0)
            )
            
            day_end = datetime.datetime.combine(
                current_date,
                datetime.time(hour=end_hour, minute=0)
            )
            
            while slot_start < day_end:
                slot_end = slot_start + datetime.timedelta(minutes=duration_minutes)
                
                if slot_end > day_end:
                    break
                
                # Check if slot overlaps with any busy period
                is_available = True
                for busy in busy_periods:
                    busy_start = datetime.datetime.fromisoformat(
                        busy['start'].replace('Z', '+00:00')
                    )
                    busy_end = datetime.datetime.fromisoformat(
                        busy['end'].replace('Z', '+00:00')
                    )
                    
                    if (slot_start < busy_end and slot_end > busy_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(
                        TimeSlot(
                            start=slot_start.isoformat(),
                            end=slot_end.isoformat(),
                            timezone=timezone
                        )
                    )
                
                # Move to next slot (30-min increments)
                slot_start += datetime.timedelta(minutes=30)
            
            current_date += datetime.timedelta(days=1)
        
        audit_logger.log(
            action="time_slots_proposed",
            resource_type="calendar",
            status="success",
            user_id=self.user_id,
            details={
                "duration_minutes": duration_minutes,
                "start_date": start_date,
                "end_date": end_date,
                "available_slots_count": len(available_slots)
            }
        )
        
        return available_slots[:10]  # Return top 10 slots to avoid overloading
