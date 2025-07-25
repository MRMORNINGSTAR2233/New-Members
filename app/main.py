import logging
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, BackgroundTasks, Depends, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, calendar, email, jira, slack, chroma, status
from app.core.config import settings
from app.services.agents.gmail_agent import GmailAgent
from app.services.agents.calendar_agent import CalendarAgent
from app.services.agents.slack_agent import SlackAgent
from app.services.agents.jira_agent import JiraAgent
from app.services.vector.chroma_service import chroma_service
from app.utils.audit_logger import audit_logger


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Include API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(email.router, prefix=f"{settings.API_V1_PREFIX}/email", tags=["Email"])
app.include_router(calendar.router, prefix=f"{settings.API_V1_PREFIX}/calendar", tags=["Calendar"])
app.include_router(slack.router, prefix=f"{settings.API_V1_PREFIX}/slack", tags=["Slack"])
app.include_router(jira.router, prefix=f"{settings.API_V1_PREFIX}/jira", tags=["Jira"])
app.include_router(chroma.router, prefix=f"{settings.API_V1_PREFIX}/chroma", tags=["ChromaDB"])
app.include_router(status.router, prefix=f"{settings.API_V1_PREFIX}/status", tags=["Status"])

# Add the direct API endpoints for compatibility with frontend
app.include_router(status.router, prefix="/api", tags=["API-Status"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    # Initialize ChromaDB service
    await chroma_service.initialize()
    
    audit_logger.log(
        action="application_startup",
        resource_type="application",
        status="success"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    audit_logger.log(
        action="application_shutdown",
        resource_type="application",
        status="success"
    )


@app.get("/", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}
