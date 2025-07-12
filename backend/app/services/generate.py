import logging
from typing import Dict, Optional, List

from ..utils.parser import clone_repository, get_chunked_repository_content, cleanup_repository, analyze_repository
from ..utils.reader import ContextAwareReader
from ..utils.reader_async import AsyncContextAwareReader
from ..utils.llm import generate_readme
from ..utils.token_counter import TokenCounter
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
        
        # Build prompt for the README generation with real-time token tracking
        prompt, token_metadata = _build_prompt(
            repo_url=repo_url,
            repo_understanding=repo_understanding,
            file_summaries=file_summaries,
            tone=tone,
            mode=mode,
            model_name=model,
            model_max_tokens=model_settings["max_tokens"]
        )
        
        # Use the token counter's calculation for max_tokens
        max_tokens = token_metadata["remaining_tokens"]
        
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
                "token_usage": token_metadata,
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

def _build_prompt(repo_url: str, repo_understanding: str, file_summaries: Dict[str, str], 
                 tone: str, mode: str, model_name: str = "gpt-4", 
                 model_max_tokens: int = 8192) -> tuple[str, Dict]:
    """
    Build a prompt for the LLM to generate a README with real-time token tracking
    
    Args:
        repo_url: URL of the GitHub repository
        repo_understanding: Overall understanding of the repository
        file_summaries: Summaries of important files
        tone: Tone for the README
        mode: Generation mode
        model_name: Name of the model to use
        model_max_tokens: Maximum tokens for the model
        
    Returns:
        tuple[str, Dict]: (Prompt for the LLM, Token metadata)
    """
    # Initialize token counter with appropriate model and buffer
    token_counter = TokenCounter(
        model_name=model_name,
        max_tokens=model_max_tokens,
        buffer=500  # Buffer for the response
    )
    
    # Extract repo name from URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Start with the base prompt
    base_prompt = f"""You are a senior technical writer hired to create a compelling, helpful, and user-focused README.md for the following GitHub repository. Your goal is to make it useful for developers evaluating whether to use this repo.

Repository: {repo_url}
Repository name: {repo_name}

Based on the repository's structure and files, here is an internal summary of its purpose and functionality:

{repo_understanding}

"""
    
    # Add base prompt to token counter
    success, base_tokens = token_counter.add_to_prompt(base_prompt)
    prompt = base_prompt
    
    # Prepare file summaries section
    file_summaries_header = "Here are summaries of the most important files:\n\n"
    success, header_tokens = token_counter.add_to_prompt(file_summaries_header)
    prompt += file_summaries_header
    
    # Add file summaries to the prompt with dynamic allocation
    file_paths = list(file_summaries.keys())
    
    # Sort files by summary length (shortest first)
    # This helps ensure we include more files rather than a few large ones
    file_paths.sort(key=lambda path: len(file_summaries[path]))
    
    # Track how many files we've included
    included_files = 0
    skipped_files = 0
    
    for file_path in file_paths:
        summary = file_summaries[file_path]
        file_section = f"## {file_path}\n{summary}\n\n"
        
        # Check if this file will fit in our token budget
        will_fit, file_tokens = token_counter.will_fit(file_section)
        
        if will_fit:
            # Add the file to our prompt
            token_counter.add_to_prompt(file_section)
            prompt += file_section
            included_files += 1
        else:
            # Try with a truncated summary
            if len(summary) > 500:
                truncated_summary = summary[:500] + "... [summary truncated]"
                truncated_section = f"## {file_path}\n{truncated_summary}\n\n"
                
                will_fit, _ = token_counter.will_fit(truncated_section)
                if will_fit:
                    token_counter.add_to_prompt(truncated_section)
                    prompt += truncated_section
                    included_files += 1
                else:
                    skipped_files += 1
            else:
                skipped_files += 1
    
    logger.info(f"Included {included_files} file summaries, skipped {skipped_files} due to token limits")
    
    # Add tone instructions
    tone_instructions = {
        "professional": "Use a professional and straightforward tone that would appeal to enterprise developers.",
        "startup": "Use an enthusiastic startup-like tone with emojis and modern language. Be energetic but still informative.",
        "meme": "Use a humorous tone with internet memes and jokes, while still being informative and helpful to developers."
    }
    
    # Add mode-specific instructions
    mode_instructions = {
        "standard": "Create a balanced README with all essential sections. Keep the total length under 1500 words.",
        "detailed": "Create a comprehensive README with extensive documentation and detailed explanations. Include more examples and technical details.",
        "concise": "Create a brief README with only the most important information, focusing on clarity and brevity. Keep it under 800 words.",
        "creative": "Create an engaging and creative README that stands out while still being informative. Use metaphors, analogies or storytelling techniques where appropriate."
    }
    
    # Add tone and style instructions
    tone_section = f"\n\nTone: {tone_instructions.get(tone, tone_instructions['professional'])}"
    style_section = f"\n\nStyle: {mode_instructions.get(mode, mode_instructions['standard'])}"
    
    token_counter.add_to_prompt(tone_section)
    token_counter.add_to_prompt(style_section)
    prompt += tone_section + style_section
    
    # Add structure instructions
    structure_instructions = """

Create a README.md with the following sections:
1. Title and a compelling introduction explaining what the project does, who it is for, and what problem it solves.
2. Features that highlight the key capabilities and benefits of the project.
3. Installation instructions that are clear, concise, and complete.
4. Usage examples that show developers how to use the project effectively.
5. Project structure with a brief explanation of what each major folder/file does.
6. License information (if available).
7. Contributing guidelines (optional).

Additional guidelines:
- Use proper Markdown formatting including headers, code blocks, lists, and emphasis where appropriate.
- If any important library, tool, or dependency is clearly central to the project, mention it in the introduction or Features section.
- Avoid repeating content from one section in another unless necessary.
- Do not invent features or sections that are not supported by the provided summaries.
- Write as if a human developer who deeply understands the project is explaining it to a colleague.
"""
    
    # Check if structure instructions will fit
    will_fit, _ = token_counter.will_fit(structure_instructions)
    if will_fit:
        token_counter.add_to_prompt(structure_instructions)
        prompt += structure_instructions
    else:
        # Add a simplified version if we're running out of tokens
        simplified_instructions = """

Create a README.md with essential sections including introduction, features, installation, usage, and project structure.
Use proper Markdown formatting and focus on clarity and accuracy.
"""
        token_counter.add_to_prompt(simplified_instructions)
        prompt += simplified_instructions
    
    # Collect token usage metadata
    token_metadata = {
        "prompt_tokens": token_counter.current_count,
        "max_tokens": token_counter.max_tokens,
        "available_tokens": token_counter.available_tokens,
        "remaining_tokens": token_counter.get_remaining_tokens(),
        "usage_percentage": token_counter.get_usage_percentage(),
        "included_files": included_files,
        "skipped_files": skipped_files
    }
    
    return prompt, token_metadata
