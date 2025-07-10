from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
import logging

from ..services.generate import generate_readme_for_repo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Define request models
class GenerateRequest(BaseModel):
    repo_url: HttpUrl
    tone: Optional[str] = "professional"  # professional, startup, meme

class GenerateResponse(BaseModel):
    success: bool
    readme: str
    metadata: Optional[Dict] = None
    error: Optional[str] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_readme(request: GenerateRequest):
    """
    Generate a README for a GitHub repository
    """
    try:
        logger.info(f"Received request to generate README for: {request.repo_url}")
        
        # Call the service to generate the README
        result = await generate_readme_for_repo(
            repo_url=str(request.repo_url),
            tone=request.tone
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
