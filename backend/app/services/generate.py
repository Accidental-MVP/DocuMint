import logging
from typing import Dict, Optional, List

from ..utils.parser import clone_repository, get_chunked_repository_content, cleanup_repository, analyze_repository
from ..utils.reader import ContextAwareReader
from ..utils.reader_async import AsyncContextAwareReader
from ..utils.llm import generate_readme
from ..config import DEFAULT_REPO_URL, AVAILABLE_MODELS, GENERATION_MODES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_readme_for_repo(repo_url: str = DEFAULT_REPO_URL, 
                            tone: str = "professional",
                            model: str = "gpt-4",
                            mode: str = "standard",
                            max_files: Optional[int] = None) -> Dict:
    """
    Generate a README for a GitHub repository
    
    Args:
        repo_url: URL of the GitHub repository
        tone: Tone for the README (professional, startup, meme)
        model: Model to use for generation
        mode: Generation mode (standard, detailed, concise, creative)
        max_files: Maximum number of files to analyze (optional)
        
    Returns:
        Dict: Generated README and metadata
    """
    repo_path = None
    
    try:
        # Clone the repository
        logger.info(f"Starting README generation for: {repo_url}")
        repo_path = clone_repository(repo_url)
        
        # Analyze the repository
        repo_analysis = analyze_repository(repo_path)
        
        # Get chunked content from important files
        logger.info("Analyzing repository and chunking files")
        chunks = get_chunked_repository_content(repo_path, client_max_files=max_files)
        
        # Track which files were included
        included_files = list(set(chunk["file_path"] for chunk in chunks))
        included_files.sort()
        
        # Process chunks with context-aware reader
        logger.info("Processing file chunks with context")
        reader = ContextAwareReader(model="gpt-3.5-turbo")  # Use faster model for analysis
        file_summaries = reader.process_repository_chunks(chunks)
        
        # Generate repository understanding
        logger.info("Generating repository understanding")
        repo_understanding = reader.generate_repository_understanding(file_summaries)
        
        # Get processing metadata
        processing_metadata = reader.get_processing_metadata()
        
        # Get model and mode settings
        model_settings = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4"])
        mode_settings = GENERATION_MODES.get(mode, GENERATION_MODES["standard"])
        
        # Build prompt for the README generation
        prompt = _build_prompt(repo_url, repo_understanding, file_summaries, tone, mode)
        
        # Calculate a safe max_tokens value (leaving room for the prompt)
        # For GPT-4, we'll use a conservative estimate to avoid token limit errors
        prompt_token_estimate = len(prompt.split()) * 1.3  # Rough estimate: words * 1.3
        max_tokens = min(model_settings["max_tokens"] - int(prompt_token_estimate) - 500, 4000)
        max_tokens = max(1000, max_tokens)  # Ensure we have at least 1000 tokens for output
        
        logger.info(f"Using max_tokens={max_tokens} for README generation")
        
        # Generate README using LLM
        logger.info(f"Generating README with {model}")
        readme_content = generate_readme(
            prompt=prompt,
            model=model,
            temperature=mode_settings["temperature"],
            max_tokens=max_tokens
        )
        
        # Create file preview information
        file_preview = []
        for file_path in included_files:
            if file_path == "dummy.txt":
                continue
                
            # Get file summary if available
            summary = file_summaries.get(file_path, "")
            preview = summary[:100] + "..." if len(summary) > 100 else summary
            
            file_preview.append({
                "path": file_path,
                "preview": preview
            })
        
        return {
            "success": True,
            "readme": readme_content,
            "metadata": {
                "repo_url": repo_url,
                "tone": tone,
                "model": model,
                "mode": mode,
                "files_analyzed": len(file_summaries),
                "chunks_processed": len(chunks),
                "included_files": included_files,
                "file_preview": file_preview,
                "processing": processing_metadata,
                "chunk_errors": processing_metadata.get("chunk_errors", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error generating README: {e}")
        return {
            "success": False,
            "error": str(e),
            "readme": "# Error\n\nFailed to generate README."
        }
    finally:
        # Clean up the cloned repository
        if repo_path:
            cleanup_repository(repo_path)

def _build_prompt(repo_url: str, repo_understanding: str, file_summaries: Dict[str, str], tone: str, mode: str) -> str:
    """
    Build a prompt for the LLM to generate a README
    
    Args:
        repo_url: URL of the GitHub repository
        repo_understanding: Overall understanding of the repository
        file_summaries: Summaries of important files
        tone: Tone for the README
        mode: Generation mode
        
    Returns:
        str: Prompt for the LLM
    """
    # Extract repo name from URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Start with the base prompt
    prompt = f"""You are a technical writer creating a README.md file for the GitHub repository: {repo_url}
Repository name: {repo_name}

I have analyzed the repository and here is my understanding:

{repo_understanding}

Here are summaries of the most important files:

"""
    
    # Add file summaries to the prompt (limit to top 3 files if there are many)
    file_paths = list(file_summaries.keys())
    if len(file_paths) > 3:
        logger.info(f"Limiting file summaries to top 3 (out of {len(file_paths)})")
        file_paths = file_paths[:3]
        
    for file_path in file_paths:
        summary = file_summaries[file_path]
        # Truncate very long summaries
        if len(summary) > 1000:
            summary = summary[:1000] + "... [summary truncated]"
        prompt += f"\n## {file_path}\n{summary}\n"
    
    # Add tone instructions
    tone_instructions = {
        "professional": "Use a professional and straightforward tone.",
        "startup": "Use an enthusiastic startup-like tone with emojis and modern language.",
        "meme": "Use a humorous tone with internet memes and jokes, while still being informative."
    }
    
    # Add mode-specific instructions
    mode_instructions = {
        "standard": "Create a balanced README with all essential sections.",
        "detailed": "Create a comprehensive README with extensive documentation and detailed explanations.",
        "concise": "Create a brief README with only the most important information, focusing on clarity and brevity.",
        "creative": "Create an engaging and creative README that stands out while still being informative."
    }
    
    prompt += f"\n\nTone: {tone_instructions.get(tone, tone_instructions['professional'])}"
    prompt += f"\n\nStyle: {mode_instructions.get(mode, mode_instructions['standard'])}"
    
    # Add structure instructions
    prompt += """

Create a README.md with the following sections:
1. Title and brief description
2. Features
3. Installation instructions
4. Usage examples
5. Project structure
6. License information (if available)
7. Contributing guidelines (optional)

Use proper Markdown formatting including headers, code blocks, lists, and emphasis where appropriate.
"""
    
    return prompt
