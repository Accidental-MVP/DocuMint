from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import ValidationError
import uuid
import secrets
import string
from supabase import Client

from ..models.user import User, UserInDB, TokenData
from ..models.api_key import APIKey
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, supabase

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/token",
    scopes={
        "user": "Read user information",
        "generate": "Generate README files",
        "admin": "Admin access",
    },
)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email"""
    response = supabase.table("users").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        user_data = response.data[0]
        return UserInDB(**user_data)
    return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return User(**user.model_dump(exclude={"hashed_password"}))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get the current user from a token"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(user_id=user_id, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Get user from Supabase
    response = supabase.table("users").select("*").eq("id", token_data.user_id).execute()
    if not response.data or len(response.data) == 0:
        raise credentials_exception
    
    user_data = response.data[0]
    user = User(**user_data)
    
    # Check if the user is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    # Check scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

def generate_api_key() -> str:
    """Generate a secure API key"""
    # Format: documint_live_xxxxxxxxxxxxxxxxxxxxxxxxxxx
    alphabet = string.ascii_letters + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"documint_live_{suffix}"

async def validate_api_key(api_key: str) -> Optional[User]:
    """Validate an API key and return the associated user"""
    # Check if the API key exists and is active
    response = supabase.table("api_keys").select("*").eq("key", api_key).eq("is_active", True).execute()
    
    if not response.data or len(response.data) == 0:
        return None
    
    api_key_data = response.data[0]
    api_key_obj = APIKey(**api_key_data)
    
    # Check if the API key has expired
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.now():
        return None
    
    # Update last used timestamp
    supabase.table("api_keys").update({"last_used_at": datetime.now().isoformat()}).eq("id", str(api_key_obj.id)).execute()
    
    # Get the associated user
    user_response = supabase.table("users").select("*").eq("id", str(api_key_obj.user_id)).execute()
    
    if not user_response.data or len(user_response.data) == 0:
        return None
    
    user_data = user_response.data[0]
    return User(**user_data) 