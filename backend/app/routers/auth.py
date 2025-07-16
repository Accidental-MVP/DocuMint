from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from ..models.user import User, UserCreate, UserResponse, Token
from ..models.api_key import APIKeyCreate, APIKeyResponse, APIKeyInfo
from ..services.auth import authenticate_user, create_access_token, get_password_hash, generate_api_key
from ..dependencies import get_current_user_or_api_key
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, supabase

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_create: UserCreate):
    """Register a new user"""
    # Check if user already exists
    response = supabase.table("users").select("*").eq("email", user_create.email).execute()
    if response.data and len(response.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user in Supabase
    hashed_password = get_password_hash(user_create.password)
    user_id = str(UUID())
    
    user_data = {
        "id": user_id,
        "email": user_create.email,
        "username": user_create.username,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    response = supabase.table("users").insert(user_data).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    created_user = response.data[0]
    return UserResponse(**created_user)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include requested scopes in token
    scopes = form_data.scopes if form_data.scopes else ["user"]
    # Add admin scope if user is superuser
    if user.is_superuser and "admin" not in scopes:
        scopes.append("admin")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "scopes": scopes},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user_or_api_key)):
    """Get current user info"""
    return current_user

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_create: APIKeyCreate,
    current_user: User = Depends(get_current_user_or_api_key)
):
    """Create a new API key"""
    # Generate API key
    key = generate_api_key()
    
    # Calculate expiration date if provided
    expires_at = None
    if api_key_create.expires_in_days:
        expires_at = datetime.now() + timedelta(days=api_key_create.expires_in_days)
    
    # Create API key in Supabase
    api_key_data = {
        "id": str(UUID()),
        "user_id": str(current_user.id),
        "name": api_key_create.name,
        "key": key,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None
    }
    
    response = supabase.table("api_keys").insert(api_key_data).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )
    
    created_api_key = response.data[0]
    return APIKeyResponse(**created_api_key)

@router.get("/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys(current_user: User = Depends(get_current_user_or_api_key)):
    """List all API keys for the current user"""
    response = supabase.table("api_keys").select("*").eq("user_id", str(current_user.id)).execute()
    
    if not response.data:
        return []
    
    return [APIKeyInfo(**api_key) for api_key in response.data]

@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: UUID,
    current_user: User = Depends(get_current_user_or_api_key)
):
    """Delete an API key"""
    # Check if API key exists and belongs to the current user
    response = supabase.table("api_keys").select("*").eq("id", str(api_key_id)).eq("user_id", str(current_user.id)).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Delete API key
    supabase.table("api_keys").delete().eq("id", str(api_key_id)).execute()
    
    return None 