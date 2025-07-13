from enum import Enum
from typing import Optional, Dict, List, Any
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

class FilePreview(BaseModel):
    """Preview of a file used in README generation"""
    path: str
    preview: str

class ProcessingMetadata(BaseModel):
    """Metadata about the processing of files"""
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    chunk_errors: int
    error_details: Optional[List[Dict[str, Any]]] = None

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
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    file_preview: Optional[List[FilePreview]] = None
    processing_metadata: Optional[ProcessingMetadata] = None

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