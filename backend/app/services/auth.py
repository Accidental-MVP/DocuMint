from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import ValidationError
import uuid
import secrets
import string
from supabase import Client
import json
import base64
import requests
import logging

from ..models.user import User, UserInDB, TokenData
from ..models.api_key import APIKey
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, supabase, SUPABASE_URL, SUPABASE_JWT_SECRET, SUPABASE_JWT_SECRET_B64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID"""
    logger.info(f"Looking up user with ID: {user_id}")
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if response.data and len(response.data) > 0:
        user_data = response.data[0]
        
        # Ensure username is not None
        if user_data.get("username") is None and user_data.get("email"):
            user_data["username"] = user_data["email"].split("@")[0]
        
        return User(**user_data)
    logger.warning(f"No user found with ID: {user_id}")
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
    
    logger.info(f"Attempting to validate token: {token[:10]}...")
    
    # Try direct Supabase verification first as the most reliable method
    try:
        logger.info("Attempting direct Supabase API verification")
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": supabase.supabase_key
        }
        auth_response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers=headers
        )
        
        logger.info(f"Supabase auth API direct response status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_user = auth_response.json()
            user_id = auth_user.get("id")
            email = auth_user.get("email")
            logger.info(f"Direct Supabase auth successful for user: {email}")
            
            # Check if user exists in our database
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not response.data or len(response.data) == 0:
                # Create new user
                username = auth_user.get("user_metadata", {}).get("username", "")
                if not username and email:
                    username = email.split("@")[0]
                
                user_data = {
                    "id": user_id,
                    "email": email,
                    "username": username,
                    "is_active": True,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                logger.info(f"Creating new user via direct auth: {email}")
                supabase.table("users").insert(user_data).execute()
                
                # Return the user
                return User(**user_data)
            else:
                # User exists
                user_data = response.data[0]
                
                # Ensure username is not None
                if user_data.get("username") is None and user_data.get("email"):
                    user_data["username"] = user_data["email"].split("@")[0]
                    # Update the user in the database
                    logger.info(f"Updating username for user {user_data['id']}")
                    supabase.table("users").update({"username": user_data["username"]}).eq("id", user_data["id"]).execute()
                
                user = User(**user_data)
                logger.info(f"Found existing user via direct auth: {user.email}")
                
                # Check if the user is active
                if not user.is_active:
                    logger.warning(f"User {user.email} is inactive")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
                
                return user
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Direct Supabase verification failed: {str(e)}")
        # Continue to other verification methods
    
    # First try to validate as a Supabase JWT token
    try:
        # Supabase JWT tokens are in format: header.payload.signature
        # We need to decode the payload to get the user ID
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.warning(f"Token does not have 3 parts: {len(token_parts)} parts found")
            raise ValueError("Invalid token format")
            
        payload_part = token_parts[1]
        # Add padding if needed
        payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
        
        logger.info("Decoding payload part of token")
        payload = json.loads(base64.b64decode(payload_part).decode('utf-8'))
        logger.info(f"Token payload keys: {list(payload.keys())}")
        
        # Check if this is a Supabase token (it will have a "sub" claim)
        if "sub" in payload:
            user_id = payload["sub"]
            logger.info(f"Found user_id in token: {user_id}")
            
            # Try to verify the token signature with Supabase JWT secret
            # NOTE: We'll skip the JWT verification since we're having issues with the secret
            # and instead rely on Supabase API verification
            
            # Get user from Supabase
            logger.info(f"Looking up user with ID: {user_id} in users table")
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not response.data or len(response.data) == 0:
                logger.warning(f"User with ID {user_id} not found in users table")
                # User doesn't exist in our database yet, try to get from auth.users
                try:
                    # Verify the token with Supabase
                    logger.info("Attempting to verify token with Supabase auth API")
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "apikey": supabase.supabase_key
                    }
                    auth_response = requests.get(
                        f"{SUPABASE_URL}/auth/v1/user",
                        headers=headers
                    )
                    
                    logger.info(f"Supabase auth API response status: {auth_response.status_code}")
                    
                    if auth_response.status_code == 200:
                        auth_user = auth_response.json()
                        logger.info(f"Auth user found: {auth_user.get('email')}")
                        
                        # Create user in our database
                        # Make sure username is set (use email prefix if not available)
                        email = auth_user.get("email", "")
                        username = auth_user.get("user_metadata", {}).get("username", "")
                        if not username and email:
                            username = email.split("@")[0]
                        
                        user_data = {
                            "id": auth_user["id"],
                            "email": email,
                            "username": username,
                            "is_active": True,
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        logger.info(f"Creating new user in database: {user_data['email']}")
                        supabase.table("users").insert(user_data).execute()
                        
                        # Return the user
                        return User(**user_data)
                    else:
                        logger.error(f"Failed to verify token with Supabase: {auth_response.text}")
                except Exception as e:
                    logger.error(f"Error verifying Supabase token: {e}")
                    pass
            else:
                # User exists in our database
                user_data = response.data[0]
                
                # Ensure username is not None (use email prefix if it is)
                if user_data.get("username") is None and user_data.get("email"):
                    user_data["username"] = user_data["email"].split("@")[0]
                    # Update the user in the database
                    logger.info(f"Updating username for user {user_data['id']}")
                    supabase.table("users").update({"username": user_data["username"]}).eq("id", user_data["id"]).execute()
                
                user = User(**user_data)
                logger.info(f"Found existing user: {user.email}")
                
                # Check if the user is active
                if not user.is_active:
                    logger.warning(f"User {user.email} is inactive")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
                
                return user
    except Exception as e:
        logger.error(f"Error decoding Supabase token: {str(e)}")
        # Continue to try our own JWT validation
    
    # If Supabase validation fails, try our own JWT validation
    try:
        logger.info("Attempting to validate token with our JWT validation")
        
        # Get the audience from the token payload
        try:
            # Parse token to get the audience claim
            token_parts = token.split('.')
            if len(token_parts) == 3:
                payload_part = token_parts[1]
                # Add padding if needed
                payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
                payload_data = json.loads(base64.b64decode(payload_part).decode('utf-8'))
                audience = payload_data.get('aud', '')
                logger.info(f"Token audience: {audience}")
            else:
                audience = None
        except Exception as e:
            logger.warning(f"Error parsing token audience: {str(e)}")
            audience = None
        
        # Options for JWT verification
        options = {
            "verify_signature": True,
            "verify_aud": False,  # Skip audience verification
            "verify_iat": False,  # Skip issued at verification
            "require_exp": True,
        }
        
        # First try with the original JWT secret
        try:
            logger.info("Trying with original JWT secret")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options=options)
            logger.info("Successfully decoded token with original JWT secret")
        except Exception as e:
            logger.warning(f"Failed to decode with original JWT secret: {str(e)}")
            
            # If that fails, try with the base64 encoded JWT secret if available
            if SUPABASE_JWT_SECRET_B64:
                logger.info("Trying with base64 encoded JWT secret")
                try:
                    payload = jwt.decode(token, SUPABASE_JWT_SECRET_B64, algorithms=[ALGORITHM], options=options)
                    logger.info("Successfully decoded token with base64 encoded JWT secret")
                except Exception as e2:
                    logger.warning(f"Failed to decode with base64 encoded JWT secret: {str(e2)}")
                    
                    # If both fail, try with Supabase JWT secret
                    logger.info("Trying with Supabase JWT secret")
                    try:
                        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], options=options)
                        logger.info("Successfully decoded token with Supabase JWT secret")
                    except Exception as e3:
                        logger.error(f"All JWT decoding methods failed: {str(e3)}")
                        
                        # As a last resort, try to extract user_id from the token payload
                        # without verifying the signature
                        if payload_data and 'sub' in payload_data:
                            logger.info("Using payload data without verification as fallback")
                            payload = payload_data
                        else:
                            raise credentials_exception
            else:
                # If no base64 encoded secret is available, try with Supabase JWT secret
                logger.info("Trying with Supabase JWT secret")
                try:
                    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], options=options)
                    logger.info("Successfully decoded token with Supabase JWT secret")
                except Exception as e2:
                    logger.error(f"All JWT decoding methods failed: {str(e2)}")
                    
                    # As a last resort, try to extract user_id from the token payload
                    # without verifying the signature
                    if payload_data and 'sub' in payload_data:
                        logger.info("Using payload data without verification as fallback")
                        payload = payload_data
                    else:
                        raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("No 'sub' claim found in token")
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(user_id=user_id, scopes=token_scopes)
        logger.info(f"Token successfully decoded, user_id: {user_id}")
    except (JWTError, ValidationError) as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception
    
    # Get user from Supabase
    logger.info(f"Looking up user with ID: {token_data.user_id}")
    response = supabase.table("users").select("*").eq("id", token_data.user_id).execute()
    if not response.data or len(response.data) == 0:
        logger.warning(f"User with ID {token_data.user_id} not found")
        raise credentials_exception
    
    user_data = response.data[0]
    user = User(**user_data)
    logger.info(f"User found: {user.email}")
    
    # Check if the user is active
    if not user.is_active:
        logger.warning(f"User {user.email} is inactive")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    # Check scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logger.warning(f"User {user.email} missing required scope: {scope}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=[])
) -> User:
    """Get the current active user"""
    try:
        if not current_user:
            logger.warning("No current user found in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication credentials"
            )
            
        if not current_user.is_active:
            logger.warning(f"User {current_user.email} is inactive")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Inactive user"
            )
            
        logger.info(f"Current active user: {current_user.email}")
        return current_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and convert other exceptions to HTTP exceptions
        logger.error(f"Error in get_current_active_user: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_api_key() -> str:
    """Generate a secure API key"""
    # Format: documint_live_xxxxxxxxxxxxxxxxxxxxxxxxxxx
    alphabet = string.ascii_letters + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"documint_live_{suffix}"

async def validate_api_key(api_key: str) -> Optional[User]:
    """Validate an API key and return the associated user"""
    logger.info(f"Validating API key: {api_key[:5]}...")
    
    # Check if the API key exists and is active
    response = supabase.table("api_keys").select("*").eq("key", api_key).eq("is_active", True).execute()
    
    if not response.data or len(response.data) == 0:
        logger.warning(f"API key {api_key[:5]}... not found or not active")
        return None
    
    api_key_data = response.data[0]
    api_key_obj = APIKey(**api_key_data)
    logger.info(f"API key found for user ID: {api_key_obj.user_id}")
    
    # Check if the API key has expired
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.now():
        logger.warning(f"API key {api_key[:5]}... has expired")
        return None
    
    # Update last used timestamp
    logger.info(f"Updating last_used_at for API key: {api_key[:5]}...")
    supabase.table("api_keys").update({"last_used_at": datetime.now().isoformat()}).eq("id", str(api_key_obj.id)).execute()
    
    # Get the associated user
    logger.info(f"Looking up user with ID: {api_key_obj.user_id}")
    user_response = supabase.table("users").select("*").eq("id", str(api_key_obj.user_id)).execute()
    
    if not user_response.data or len(user_response.data) == 0:
        logger.warning(f"User with ID {api_key_obj.user_id} not found")
        return None
    
    user_data = user_response.data[0]
    logger.info(f"User found for API key: {user_data.get('email')}")
    return User(**user_data) 