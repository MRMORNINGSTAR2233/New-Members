import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from pydantic import BaseModel

from app.core.config import settings


class AuditEntry(BaseModel):
    """Model for structured audit log entries"""
    timestamp: str
    action: str
    user_id: Optional[str] = None
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    status: str
    ip_address: Optional[str] = None


class AuditLogger:
    def __init__(self):
        """Initialize the audit logger with rotation and retention policies"""
        # Remove default logger
        logger.remove()
        
        # Configure console logging for development
        if settings.ENVIRONMENT.lower() != "production":
            logger.add(
                sys.stderr,
                format="{time} | {level} | {message}",
                level="INFO"
            )
        
        # Configure file logging with rotation and retention
        logger.add(
            settings.AUDIT_LOG_PATH,
            rotation="100 MB",  # Rotate when the file reaches 100MB
            retention="90 days",  # Keep logs for 90 days
            compression="zip",  # Compress rotated logs
            serialize=True,  # JSON serialization for structured logging
            backtrace=True,
            diagnose=True,
            enqueue=True,  # Thread-safe logging
            level="INFO"
        )
    
    def log(
        self,
        action: str,
        resource_type: str,
        status: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None
    ):
        """
        Create an immutable audit log entry
        
        Args:
            action: The action being performed (e.g., "email_processed", "event_created")
            resource_type: Type of resource being accessed (e.g., "email", "calendar_event")
            status: Outcome of the action (e.g., "success", "failure", "pending")
            user_id: ID of the user performing the action
            resource_id: ID of the resource being accessed
            details: Additional context about the action
            ip_address: IP address of the client making the request
        """
        if details is None:
            details = {}
        
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            ip_address=ip_address
        )
        
        # Log the structured entry
        logger.info(entry.model_dump_json())
        
        # For critical actions, also log to stderr in development
        if status == "failure" and settings.ENVIRONMENT.lower() != "production":
            logger.error(f"AUDIT: {entry.model_dump_json()}")

# Create a singleton instance
audit_logger = AuditLogger()
