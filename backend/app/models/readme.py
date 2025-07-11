from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, HttpUrl

class ReadmeTone(str, Enum):
    """Enum for README tone options"""
    PROFESSIONAL = "professional"
    STARTUP = "startup"
    MEME = "meme"

class GenerationMode(str, Enum):
    """Enum for README generation modes"""
    STANDARD = "standard"
    DETAILED = "detailed"
    CONCISE = "concise"
    CREATIVE = "creative"

class GenerateRequest(BaseModel):
    """Request model for README generation"""
    repo_url: HttpUrl
    tone: ReadmeTone = ReadmeTone.PROFESSIONAL
    model: str = "gpt-4"
    mode: GenerationMode = GenerationMode.STANDARD
    max_files: Optional[int] = None

class GenerateResponse(BaseModel):
    """Response model for README generation"""
    success: bool
    readme: str
    metadata: Optional[Dict] = None
    error: Optional[str] = None

class ModelInfo(BaseModel):
    """Model information"""
    id: str
    name: str
    description: str
    max_tokens: int

class ModeInfo(BaseModel):
    """Generation mode information"""
    id: str
    name: str
    description: str
    temperature: float

class ModelsResponse(BaseModel):
    """Response model for available models"""
    models: List[ModelInfo]

class ModesResponse(BaseModel):
    """Response model for available generation modes"""
    modes: List[ModeInfo] 