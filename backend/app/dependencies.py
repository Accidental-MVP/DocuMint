from fastapi import Depends, Security, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Optional
import logging
import traceback
import os

from .models.token_usage import TokenUsage
from .models.user import User
from .services.auth import get_current_active_user, validate_api_key

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Debug mode
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Helper function to get user from API key
async def get_user_from_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[User]:
    """Get user from API key"""
    if api_key:
        logger.info(f"Attempting to authenticate with API key: {api_key[:5]}...")
        try:
            user = await validate_api_key(api_key)
            if user:
                logger.info(f"API key authentication successful for user: {user.email}")
                return user
            else:
                logger.warning(f"API key authentication failed: Invalid API key {api_key[:5]}...")
        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            logger.error(traceback.format_exc())
    return None

# Helper function to get user from debug header (only in development)
async def get_user_from_debug_header(
    request: Request,
    x_debug_user_id: Optional[str] = Header(None)
) -> Optional[User]:
    """Get user from debug header (only in development)"""
    if not DEBUG_MODE:
        return None
        
    if x_debug_user_id:
        from .services.auth import get_user_by_id
        logger.warning(f"DEVELOPMENT MODE: Attempting to authenticate with debug header: {x_debug_user_id}")
        try:
            user = await get_user_by_id(x_debug_user_id)
            if user:
                logger.warning(f"DEVELOPMENT MODE: Debug header authentication successful for user: {user.email}")
                return user
            else:
                logger.warning(f"DEVELOPMENT MODE: Debug header authentication failed: User not found {x_debug_user_id}")
        except Exception as e:
            logger.error(f"Error validating debug header: {str(e)}")
    return None

# Authentication dependency that accepts either JWT or API key
async def get_current_user_or_api_key(
    current_user: Optional[User] = Depends(get_current_active_user),
    api_key_user: Optional[User] = Depends(get_user_from_api_key),
    debug_user: Optional[User] = Depends(get_user_from_debug_header)
) -> User:
    """Get current user from either JWT or API key"""
    if current_user:
        logger.info(f"User authenticated via JWT: {current_user.email}")
        return current_user
    if api_key_user:
        logger.info(f"User authenticated via API key: {api_key_user.email}")
        return api_key_user
    if debug_user and DEBUG_MODE:
        logger.warning(f"DEVELOPMENT MODE: User authenticated via debug header: {debug_user.email}")
        return debug_user
    
    logger.warning("Authentication failed: No valid JWT or API key provided")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_token_usage(user: User = Depends(get_current_user_or_api_key)) -> TokenUsage:
    """
    Dependency to track token usage throughout a request
    
    Args:
        user: The current user
        
    Returns:
        TokenUsage: A token usage tracker
    """
    logger.info(f"Creating token usage tracker for user: {user.email}")
    return TokenUsage(user_id=str(user.id)) 