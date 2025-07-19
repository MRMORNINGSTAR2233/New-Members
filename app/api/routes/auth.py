from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.auth.google_auth import (
    create_oauth_flow, 
    exchange_code, 
    get_authorization_url, 
    save_credentials
)
from app.utils.audit_logger import audit_logger


router = APIRouter()


class AuthRequest(BaseModel):
    """Model for auth request with scopes"""
    user_id: str
    scopes: List[str]


class AuthCodeRequest(BaseModel):
    """Model for auth code request"""
    user_id: str
    code: str
    scopes: List[str]


@router.post("/google/url", status_code=status.HTTP_200_OK)
async def get_google_auth_url(
    request: AuthRequest
):
    """
    Get Google OAuth2 authorization URL.
    """
    try:
        # Generate auth URL
        auth_url = get_authorization_url(request.scopes)
        
        audit_logger.log(
            action="google_auth_url_generated",
            resource_type="oauth",
            status="success",
            user_id=request.user_id,
            details={"scopes": request.scopes}
        )
        
        return {
            "auth_url": auth_url
        }
        
    except Exception as e:
        audit_logger.log(
            action="google_auth_url_generated",
            resource_type="oauth",
            status="failure",
            user_id=request.user_id,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {e}"
        )


@router.post("/google/token", status_code=status.HTTP_200_OK)
async def exchange_google_code(
    request: AuthCodeRequest
):
    """
    Exchange Google OAuth2 authorization code for tokens.
    """
    try:
        # Exchange auth code for tokens
        token_info = exchange_code(request.code, request.scopes)
        
        # Save credentials for the user
        save_credentials(request.user_id, token_info)
        
        audit_logger.log(
            action="google_auth_completed",
            resource_type="oauth",
            status="success",
            user_id=request.user_id,
            details={"scopes": request.scopes}
        )
        
        return {
            "status": "success",
            "message": "Authentication successful",
            "scopes": token_info.scopes
        }
        
    except Exception as e:
        audit_logger.log(
            action="google_auth_completed",
            resource_type="oauth",
            status="failure",
            user_id=request.user_id,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange auth code: {e}"
        )


@router.get("/google/callback")
async def google_oauth_callback(
    code: str,
    state: Optional[str] = None
):
    """
    Handle Google OAuth2 callback.
    
    This endpoint is the redirect URI for Google OAuth2 flow.
    In a real application, it would typically set cookies or redirect
    to a frontend application with the authorization code.
    """
    # In a real app, this would handle the redirect from Google
    # and transfer control back to the frontend
    return {
        "message": "Authentication successful. You can close this window."
    }
