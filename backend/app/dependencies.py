from fastapi import Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Optional

from .models.token_usage import TokenUsage
from .models.user import User
from .services.auth import get_current_active_user, validate_api_key

# API Key header
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Helper function to get user from API key
async def get_user_from_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[User]:
    """Get user from API key"""
    if api_key:
        return await validate_api_key(api_key)
    return None

# Authentication dependency that accepts either JWT or API key
async def get_current_user_or_api_key(
    current_user: Optional[User] = Depends(get_current_active_user),
    api_key_user: Optional[User] = Depends(get_user_from_api_key)
) -> User:
    """Get current user from either JWT or API key"""
    if current_user:
        return current_user
    if api_key_user:
        return api_key_user
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
    return TokenUsage(user_id=str(user.id)) 