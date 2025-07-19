from typing import Dict, List, Optional, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.models.calendar import CalendarEvent, TimeSlot
from app.services.agents.calendar_agent import CalendarAgent
from app.services.auth.google_auth import get_google_credentials
from app.utils.audit_logger import audit_logger


router = APIRouter()


class TimeSlotRequest(BaseModel):
    """Model for time slot proposal request"""
    user_id: str
    duration_minutes: int
    start_date: str  # ISO format YYYY-MM-DD
    end_date: str  # ISO format YYYY-MM-DD
    timezone: Optional[str] = "UTC"


@router.post("/book", status_code=status.HTTP_201_CREATED)
async def create_event(
    event: CalendarEvent,
    request: Request
):
    """
    Create a calendar event for a user.
    
    Requires user authentication via token or session.
    """
    try:
        # In a real app, get user_id from token or session
        user_id = request.headers.get("X-User-ID")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication required"
            )
        
        # Get credentials for the user
        credentials = get_google_credentials(user_id, None)  # Use default scopes
        
        # Initialize the Calendar agent
        calendar_agent = CalendarAgent(user_id, credentials)
        
        # Create event using the payload
        event_dict = event.to_google_calendar_dict()
        event_id = await calendar_agent.create_event(event_dict)
        
        audit_logger.log(
            action="calendar_event_created",
            resource_type="calendar_event",
            resource_id=event_id,
            status="success",
            user_id=user_id,
            details={"summary": event.summary}
        )
        
        return {
            "status": "created",
            "event_id": event_id,
            "summary": event.summary
        }
        
    except Exception as e:
        audit_logger.log(
            action="calendar_event_created",
            resource_type="calendar_event",
            status="failure",
            user_id=user_id if 'user_id' in locals() else None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create calendar event: {e}"
        )


@router.post("/propose-slots", status_code=status.HTTP_200_OK)
async def propose_time_slots(
    request: TimeSlotRequest
):
    """
    Propose available time slots for a meeting based on calendar availability.
    """
    try:
        # Get credentials for the user
        credentials = get_google_credentials(request.user_id, None)  # Use default scopes
        
        # Initialize the Calendar agent
        calendar_agent = CalendarAgent(request.user_id, credentials)
        
        # Get proposed time slots
        time_slots = await calendar_agent.propose_time_slots(
            duration_minutes=request.duration_minutes,
            start_date=request.start_date,
            end_date=request.end_date,
            timezone=request.timezone
        )
        
        audit_logger.log(
            action="time_slots_proposed",
            resource_type="calendar",
            status="success",
            user_id=request.user_id,
            details={
                "duration_minutes": request.duration_minutes,
                "slots_count": len(time_slots)
            }
        )
        
        return {
            "status": "success",
            "slots": [slot.model_dump() for slot in time_slots]
        }
        
    except Exception as e:
        audit_logger.log(
            action="time_slots_proposed",
            resource_type="calendar",
            status="failure",
            user_id=request.user_id,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to propose time slots: {e}"
        )
