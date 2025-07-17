from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class User(BaseModel):
    """User model"""
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        # Allow extra fields for flexibility with external systems
        extra = "ignore"
        
    def model_post_init(self, __context):
        # Set username from email if not provided
        if not self.username and self.email:
            self.username = self.email.split("@")[0]

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    username: Optional[str] = None
    password: str
    
    class Config:
        # Allow extra fields for flexibility with external systems
        extra = "ignore"
        
    def model_post_init(self, __context):
        # Set username from email if not provided
        if not self.username and self.email:
            self.username = self.email.split("@")[0]

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """User response model"""
    id: UUID
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserInDB(User):
    """User model with hashed password"""
    hashed_password: Optional[str] = None

class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model"""
    user_id: Optional[str] = None
    scopes: List[str] = [] 