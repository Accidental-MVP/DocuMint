from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class APIKey(BaseModel):
    """API key model"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    key: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class APIKeyCreate(BaseModel):
    """API key creation model"""
    name: str
    expires_in_days: Optional[int] = None  # None means no expiration

class APIKeyResponse(BaseModel):
    """API key response model"""
    id: UUID
    name: str
    key: str  # Only shown once when created
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

class APIKeyInfo(BaseModel):
    """API key info model (without the actual key)"""
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None 