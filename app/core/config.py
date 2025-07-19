import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with validation.
    """
    # Application settings
    PROJECT_NAME: str = "AI Assistant API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(..., env="ENVIRONMENT")  # development, staging, production
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # Google OAuth2 settings
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field(..., env="GOOGLE_REDIRECT_URI")
    
    # Gemini API settings
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    
    # Pinecone settings
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(..., env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(..., env="PINECONE_INDEX_NAME")
    
    # Slack settings
    SLACK_BOT_TOKEN: str = Field(..., env="SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: str = Field(..., env="SLACK_SIGNING_SECRET")
    
    # Jira settings
    JIRA_SERVER_URL: str = Field(..., env="JIRA_SERVER_URL")
    JIRA_API_TOKEN: str = Field(..., env="JIRA_API_TOKEN")
    JIRA_USER_EMAIL: str = Field(..., env="JIRA_USER_EMAIL")
    
    # Logging settings
    AUDIT_LOG_PATH: str = Field(..., env="AUDIT_LOG_PATH")
    
    # Scopes for Google APIs
    GOOGLE_GMAIL_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.compose"
    ]
    
    GOOGLE_CALENDAR_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ]
    
    @validator("AUDIT_LOG_PATH")
    def validate_audit_log_path(cls, v: str) -> str:
        """Validate the audit log path exists or can be created"""
        log_dir = Path(v).parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Failed to create log directory: {e}")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
