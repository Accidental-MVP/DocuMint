from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel
import logging
import os
import asyncio
from typing import Optional, Dict, Any

from ..utils.parser import clone_repository, get_chunked_repository_content, cleanup_repository, analyze_repository
from ..utils.reader import ContextAwareReader
from ..utils.reader_async import AsyncContextAwareReader
from ..utils.generator import generate_readme
from ..models.token_usage import TokenUsage, add_token_usage
from ..dependencies import get_token_usage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ReadmeRequest(BaseModel):
    repo_url: str
    use_async: bool = False
    model: str = "gpt-3.5-turbo"
    max_files: Optional[int] = None

class ReadmeResponse(BaseModel):
    readme: str
    token_usage: Dict[str, int]
    repo_analysis: Optional[Dict] = None
    files_processed: int

@router.post("/generate")
async def create_readme(
    request: ReadmeRequest,
    background_tasks: BackgroundTasks,
    token_usage: TokenUsage = Depends(get_token_usage)
):
    """
    Generate a README for a GitHub repository
    """
    repo_path = None
    
    try:
        # Clone the repository
        repo_path = clone_repository(request.repo_url)
        
        # Analyze the repository
        repo_analysis = analyze_repository(repo_path)
        
        # Get chunked content from important files with dynamic file selection
        # Pass client-specified max_files if provided
        chunks = get_chunked_repository_content(
            repo_path, 
            client_max_files=request.max_files
        )
        
        # Process chunks to understand the repository
        if request.use_async and len(chunks) > 10:  # Use async for larger repos
            logger.info(f"Using async processing for {len(chunks)} chunks")
            reader = AsyncContextAwareReader(model=request.model)
            file_summaries = await reader.process_repository_chunks(chunks)
            repo_understanding = await reader.generate_repository_understanding(file_summaries)
        else:
            logger.info(f"Using sync processing for {len(chunks)} chunks")
            reader = ContextAwareReader(model=request.model)
            file_summaries = reader.process_repository_chunks(chunks)
            repo_understanding = reader.generate_repository_understanding(file_summaries)
        
        # Generate README
        readme_content = generate_readme(repo_understanding, repo_analysis)
        
        # Schedule cleanup in the background
        background_tasks.add_task(cleanup_repository, repo_path)
        
        # Record token usage
        add_token_usage(token_usage, {
            "prompt_tokens": reader.total_prompt_tokens,
            "completion_tokens": reader.total_completion_tokens,
            "total_tokens": reader.total_prompt_tokens + reader.total_completion_tokens
        })
        
        return ReadmeResponse(
            readme=readme_content,
            token_usage={
                "prompt_tokens": reader.total_prompt_tokens,
                "completion_tokens": reader.total_completion_tokens,
                "total_tokens": reader.total_prompt_tokens + reader.total_completion_tokens
            },
            repo_analysis=repo_analysis,
            files_processed=len(file_summaries)
        )
    
    except Exception as e:
        logger.error(f"Error generating README: {e}")
        
        # Cleanup if needed
        if repo_path and os.path.exists(repo_path):
            background_tasks.add_task(cleanup_repository, repo_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate README: {str(e)}"
        ) 