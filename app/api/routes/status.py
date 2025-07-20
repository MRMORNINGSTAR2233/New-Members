from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Models
class ServiceStatusResponse(BaseModel):
    connected: bool
    lastSync: datetime = None
    error: str = None

# Mock data storage - in production, this would be stored in a database
service_statuses = {
    "google": {"connected": False, "lastSync": None, "error": None},
    "jira": {"connected": False, "lastSync": None, "error": None},
    "slack": {"connected": False, "lastSync": None, "error": None}
}

@router.get("/google/status", response_model=ServiceStatusResponse)
async def get_google_status():
    """Get Google service connection status"""
    status_data = service_statuses.get("google", {"connected": False})
    return ServiceStatusResponse(**status_data)

@router.get("/jira/status", response_model=ServiceStatusResponse)
async def get_jira_status():
    """Get Jira service connection status"""
    status_data = service_statuses.get("jira", {"connected": False})
    return ServiceStatusResponse(**status_data)

@router.get("/slack/status", response_model=ServiceStatusResponse)
async def get_slack_status():
    """Get Slack service connection status"""
    status_data = service_statuses.get("slack", {"connected": False})
    return ServiceStatusResponse(**status_data)

@router.put("/google/status", response_model=ServiceStatusResponse)
async def update_google_status(status_update: ServiceStatusResponse):
    """Update Google service connection status"""
    service_statuses["google"] = status_update.dict()
    return service_statuses["google"]

@router.put("/jira/status", response_model=ServiceStatusResponse)
async def update_jira_status(status_update: ServiceStatusResponse):
    """Update Jira service connection status"""
    service_statuses["jira"] = status_update.dict()
    return service_statuses["jira"]

@router.put("/slack/status", response_model=ServiceStatusResponse)
async def update_slack_status(status_update: ServiceStatusResponse):
    """Update Slack service connection status"""
    service_statuses["slack"] = status_update.dict()
    return service_statuses["slack"]
