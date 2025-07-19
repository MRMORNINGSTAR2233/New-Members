import json
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.models.slack import SlackEventPayload
from app.services.agents.slack_agent import SlackAgent
from app.utils.audit_logger import audit_logger


router = APIRouter()
slack_agent = SlackAgent()


@router.post("/events", status_code=status.HTTP_200_OK)
async def slack_events(
    request: Request,
    response: Response
):
    """
    Handle incoming Slack events.
    
    This endpoint handles events from the Slack Events API, including:
    - URL verification challenges
    - Message events
    - App mention events
    - And other configured event types
    """
    try:
        # Get request body as text for signature verification
        body = await request.body()
        body_text = body.decode("utf-8")
        
        # Get Slack signature headers
        signature = request.headers.get("X-Slack-Signature", "")
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        
        # Verify request signature
        if not slack_agent.verify_signature(signature, timestamp, body_text):
            audit_logger.log(
                action="slack_event_received",
                resource_type="slack",
                status="failure",
                details={"reason": "invalid_signature"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid request signature"
            )
        
        # Parse the request body
        payload = json.loads(body_text)
        
        # Handle URL verification challenge
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}
        
        # Handle events
        if payload.get("type") == "event_callback":
            # Create event payload model
            event_payload = SlackEventPayload(
                token=payload.get("token", ""),
                team_id=payload.get("team_id", ""),
                api_app_id=payload.get("api_app_id", ""),
                event=payload.get("event", {}),
                type=payload.get("type", ""),
                event_id=payload.get("event_id", ""),
                event_time=payload.get("event_time", 0)
            )
            
            # Process event in background to respond quickly to Slack
            background_tasks = BackgroundTasks()
            background_tasks.add_task(process_slack_event, event_payload)
            
            audit_logger.log(
                action="slack_event_received",
                resource_type="slack",
                status="success",
                details={"event_type": event_payload.event.type}
            )
            
            # Return 200 OK immediately to acknowledge receipt
            response.background = background_tasks
            return {"status": "processing"}
        
        # Unknown event type
        return {"status": "ignored"}
        
    except json.JSONDecodeError:
        audit_logger.log(
            action="slack_event_received",
            resource_type="slack",
            status="failure",
            details={"reason": "invalid_json"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
        
    except Exception as e:
        audit_logger.log(
            action="slack_event_received",
            resource_type="slack",
            status="failure",
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Slack event: {e}"
        )


@router.post("/commands", status_code=status.HTTP_200_OK)
async def slack_commands(
    request: Request,
    response: Response
):
    """
    Handle incoming Slack slash commands.
    """
    try:
        # Get form data from request
        form_data = await request.form()
        command_data = dict(form_data)
        
        # Get Slack signature headers
        signature = request.headers.get("X-Slack-Signature", "")
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        
        # Verify request signature (requires raw body, which is not available after form parsing)
        # In a real app, you'd need to implement a middleware to capture and verify the raw body
        
        # Process command in background to respond quickly to Slack
        background_tasks = BackgroundTasks()
        background_tasks.add_task(process_slack_command, command_data)
        
        audit_logger.log(
            action="slack_command_received",
            resource_type="slack",
            status="success",
            details={"command": command_data.get("command", "")}
        )
        
        # Return immediate acknowledgment response
        response.background = background_tasks
        return {
            "response_type": "ephemeral",
            "text": "Processing your command..."
        }
        
    except Exception as e:
        audit_logger.log(
            action="slack_command_received",
            resource_type="slack",
            status="failure",
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Slack command: {e}"
        )


async def process_slack_event(event_payload: SlackEventPayload):
    """
    Process a Slack event in the background.
    
    Args:
        event_payload: The Slack event payload
    """
    try:
        await slack_agent.handle_event(event_payload)
    except Exception as e:
        audit_logger.log(
            action="slack_event_processed",
            resource_type="slack",
            status="failure",
            details={"error": str(e), "event_type": event_payload.event.type}
        )


async def process_slack_command(command_data: Dict[str, Any]):
    """
    Process a Slack command in the background.
    
    Args:
        command_data: The Slack command data
    """
    try:
        await slack_agent.handle_command(command_data)
    except Exception as e:
        audit_logger.log(
            action="slack_command_processed",
            resource_type="slack",
            status="failure",
            details={"error": str(e), "command": command_data.get("command", "")}
        )
