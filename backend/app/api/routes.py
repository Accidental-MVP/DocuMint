from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, List
import logging

from ..services.generate import generate_readme_for_repo
from ..config import AVAILABLE_MODELS, GENERATION_MODES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Define request models
class GenerateRequest(BaseModel):
    repo_url: HttpUrl
    tone: Optional[str] = "professional"  # professional, startup, meme
    model: Optional[str] = "gpt-4"
    mode: Optional[str] = "standard"

class GenerateResponse(BaseModel):
    success: bool
    readme: str
    metadata: Optional[Dict] = None
    error: Optional[str] = None

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    max_tokens: int

class ModeInfo(BaseModel):
    id: str
    name: str
    description: str
    temperature: float

class ModelsResponse(BaseModel):
    models: List[ModelInfo]

class ModesResponse(BaseModel):
    modes: List[ModeInfo]

@router.post("/generate", response_model=GenerateResponse)
def generate_readme(request: GenerateRequest):
    """
    Generate a README for a GitHub repository
    """
    try:
        logger.info(f"Received request to generate README for: {request.repo_url}")
        
        # Validate model
        if request.model not in AVAILABLE_MODELS:
            logger.warning(f"Invalid model: {request.model}, using default")
            request.model = "gpt-4"
            
        # Validate mode
        if request.mode not in GENERATION_MODES:
            logger.warning(f"Invalid mode: {request.mode}, using default")
            request.mode = "standard"
        
        # Call the service to generate the README
        result = generate_readme_for_repo(
            repo_url=str(request.repo_url),
            tone=request.tone,
            model=request.model,
            mode=request.mode
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=ModelsResponse)
def get_available_models():
    """
    Get available models for README generation
    """
    models = []
    for model_id, model_data in AVAILABLE_MODELS.items():
        models.append(
            ModelInfo(
                id=model_id,
                name=model_data["name"],
                description=model_data["description"],
                max_tokens=model_data["max_tokens"]
            )
        )
    return {"models": models}

@router.get("/modes", response_model=ModesResponse)
def get_generation_modes():
    """
    Get available generation modes
    """
    modes = []
    for mode_id, mode_data in GENERATION_MODES.items():
        modes.append(
            ModeInfo(
                id=mode_id,
                name=mode_data["name"],
                description=mode_data["description"],
                temperature=mode_data["temperature"]
            )
        )
    return {"modes": modes}

@router.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
