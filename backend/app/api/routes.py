from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
import logging
from typing import Dict, List, Optional, Any
import asyncio

from ..config import AVAILABLE_MODELS, GENERATION_MODES, DEFAULT_REPO_URL
from ..services.generate import generate_readme_for_repo
from ..services.advanced_generate import AdvancedReadmeGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/models")
async def get_models() -> Dict[str, Any]:
    """Get available models"""
    return {
        "models": [
            {
                "id": model_id,
                "name": model_info["name"],
                "description": model_info["description"]
            }
            for model_id, model_info in AVAILABLE_MODELS.items()
        ]
    }

@router.get("/modes")
async def get_modes() -> Dict[str, Any]:
    """Get available generation modes"""
    return {
        "modes": [
            {
                "id": mode_id,
                "name": mode_info["name"],
                "description": mode_info["description"]
            }
            for mode_id, mode_info in GENERATION_MODES.items()
        ]
    }

@router.post("/generate")
async def generate_readme(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a README for a GitHub repository"""
    repo_url = request.get("repo_url", DEFAULT_REPO_URL)
    tone = request.get("tone", "professional")
    model = request.get("model", "gpt-4")
    mode = request.get("mode", "standard")
    max_files = request.get("max_files")
    
    logger.info(f"Received request to generate README for: {repo_url}")
    
    try:
        result = generate_readme_for_repo(
            repo_url=repo_url,
            tone=tone,
            model=model,
            mode=mode,
            max_files=max_files
        )
        return result
    except Exception as e:
        logger.error(f"Error generating README: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advanced-generate")
async def advanced_generate_readme(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a README using advanced strategies"""
    repo_url = request.get("repo_url", DEFAULT_REPO_URL)
    tone = request.get("tone", "professional")
    model = request.get("model", "gpt-4-1106-preview")
    max_files = request.get("max_files")
    
    logger.info(f"Received request for advanced README generation for: {repo_url}")
    
    try:
        # First get repository understanding and file summaries using the standard method
        result = generate_readme_for_repo(
            repo_url=repo_url,
            tone=tone,
            model="gpt-3.5-turbo",  # Use faster model for initial analysis
            mode="standard",
            max_files=max_files
        )
        
        if not result["success"]:
            return result
            
        # Extract repository understanding and file summaries
        repo_understanding = result["metadata"].get("repo_understanding", "")
        file_summaries = {file_path: summary for file_path, summary in 
                         zip(result["metadata"].get("included_files", []), 
                             result["metadata"].get("file_summaries", []))}
        
        # Use advanced generator
        generator = AdvancedReadmeGenerator(model=model)
        readme_content = await generator.generate_readme(
            repo_url=repo_url,
            repo_understanding=repo_understanding,
            file_summaries=file_summaries,
            tone=tone
        )
        
        # Return the result
        return {
            "success": True,
            "readme": readme_content,
            "metadata": {
                **result["metadata"],
                "generation_method": "advanced",
                "model": model
            }
        }
    except Exception as e:
        logger.error(f"Error in advanced README generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream-generate")
async def stream_generate_readme(request: Request) -> StreamingResponse:
    """Generate a README with streaming output"""
    # Parse the request body
    body = await request.json()
    repo_url = body.get("repo_url", DEFAULT_REPO_URL)
    tone = body.get("tone", "professional")
    model = body.get("model", "gpt-4-1106-preview")
    max_files = body.get("max_files")
    
    logger.info(f"Received request for streaming README generation for: {repo_url}")
    
    async def generate_stream():
        try:
            # First get repository understanding and file summaries using the standard method
            result = generate_readme_for_repo(
                repo_url=repo_url,
                tone=tone,
                model="gpt-3.5-turbo",  # Use faster model for initial analysis
                mode="standard",
                max_files=max_files
            )
            
            if not result["success"]:
                yield f"Error: {result.get('error', 'Unknown error')}"
                return
                
            # Extract repository understanding and file summaries
            repo_understanding = result["metadata"].get("repo_understanding", "")
            file_summaries = {file_path: summary for file_path, summary in 
                             zip(result["metadata"].get("included_files", []), 
                                 result["metadata"].get("file_summaries", []))}
            
            # Use advanced generator with streaming
            generator = AdvancedReadmeGenerator(model=model)
            async for chunk in generator.stream_generate_readme(
                repo_url=repo_url,
                repo_understanding=repo_understanding,
                file_summaries=file_summaries,
                tone=tone
            ):
                yield chunk
                # Small delay to avoid overwhelming the client
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in streaming README generation: {e}")
            yield f"Error: {str(e)}"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )
