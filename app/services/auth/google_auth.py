import os
from typing import Dict, List, Optional

import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pydantic import BaseModel

from app.core.config import settings
from app.utils.audit_logger import audit_logger


class TokenInfo(BaseModel):
    """Model for OAuth token information"""
    token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    expiry: str
    scopes: List[str]


def create_oauth_flow(scopes: List[str], redirect_uri: Optional[str] = None):
    """
    Create an OAuth2 flow for Google API authentication.
    
    Args:
        scopes: List of OAuth scopes to request
        redirect_uri: Optional redirect URI override
        
    Returns:
        OAuth2 flow object
    """
    if not redirect_uri:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        
    # Create a flow instance using client secrets
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=scopes
    )
    
    flow.redirect_uri = redirect_uri
    
    return flow


def get_authorization_url(scopes: List[str]) -> str:
    """
    Get the authorization URL for Google OAuth2.
    
    Args:
        scopes: List of OAuth scopes to request
        
    Returns:
        Authorization URL
    """
    flow = create_oauth_flow(scopes)
    authorization_url, _ = flow.authorization_url(
        access_type='offline',  # Enable refresh tokens
        prompt='consent',       # Force to show the consent screen
        include_granted_scopes='true'  # Enable incremental auth
    )
    return authorization_url


def exchange_code(code: str, scopes: List[str]) -> TokenInfo:
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        code: Authorization code from OAuth callback
        scopes: List of OAuth scopes requested
        
    Returns:
        TokenInfo object
    """
    flow = create_oauth_flow(scopes)
    
    # Exchange the authorization code for credentials
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Create token info
    token_info = TokenInfo(
        token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        expiry=credentials.expiry.isoformat() if credentials.expiry else "",
        scopes=credentials.scopes
    )
    
    return token_info


def save_credentials(user_id: str, token_info: TokenInfo) -> None:
    """
    Save user credentials to secure storage.
    
    In a production environment, this should use a secure credential store.
    This example uses a simple file-based approach for demonstration.
    
    Args:
        user_id: ID of the user
        token_info: TokenInfo object with credential information
    """
    # In a real application, save this to a secure database or service
    # Here, we'll just log the action
    audit_logger.log(
        action="credentials_saved",
        resource_type="oauth_credentials",
        status="success",
        user_id=user_id,
        details={"scopes": token_info.scopes}
    )
    
    # In a real implementation, you would save credentials to secure storage
    # Example pseudocode:
    # secure_storage.save_user_credentials(user_id, token_info.dict())


def get_google_credentials(user_id: str, scopes: List[str]) -> Credentials:
    """
    Retrieve Google OAuth2 credentials for a user.
    
    Args:
        user_id: ID of the user
        scopes: List of OAuth scopes required
        
    Returns:
        Google OAuth2 credentials
        
    Raises:
        ValueError: If credentials are not found or cannot be refreshed
    """
    # In a real application, fetch this from secure database or service
    # Here, we'll just provide a placeholder method
    
    # This is placeholder code. In production, you would retrieve
    # real credentials from your secure storage.
    
    # Placeholder credentials for demonstration purposes
    credentials = Credentials(
        token="placeholder_token",
        refresh_token="placeholder_refresh_token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=scopes
    )
    
    # Refreshing would typically happen here
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            
            # Save the refreshed credentials
            token_info = TokenInfo(
                token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                expiry=credentials.expiry.isoformat() if credentials.expiry else "",
                scopes=credentials.scopes
            )
            save_credentials(user_id, token_info)
            
        except Exception as e:
            audit_logger.log(
                action="credentials_refresh",
                resource_type="oauth_credentials",
                status="failure",
                user_id=user_id,
                details={"error": str(e)}
            )
            raise ValueError(f"Failed to refresh credentials: {e}")
    
    audit_logger.log(
        action="credentials_retrieved",
        resource_type="oauth_credentials",
        status="success",
        user_id=user_id
    )
    
    return credentials
