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

async def generate_readme_for_repo(repo_url: str = DEFAULT_REPO_URL, 
                            tone: str = "professional",
                            model: str = "gpt-4-1106-preview",
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
        
        # Process chunks with MASSIVE PERFORMANCE IMPROVEMENTS using parallel processing
        logger.info("Processing file chunks with optimized parallel processing")
        
        # Create async reader with optimized concurrency
        reader = AsyncContextAwareReader(model="gpt-3.5-turbo", concurrency_limit=15)
        
        # Process chunks in parallel for massive speed improvements
        file_summaries = await reader.process_repository_chunks(chunks)
        
        # Generate repository understanding
        logger.info("Generating repository understanding")
        # Use GPT-4 Turbo for the final repository understanding to handle larger context
        understanding_reader = AsyncContextAwareReader(model="gpt-4-1106-preview", concurrency_limit=15)
        repo_understanding = await understanding_reader.generate_repository_understanding(file_summaries)
        
        # Combine processing metadata from async readers
        processing_metadata = {
            "total_prompt_tokens": reader.total_prompt_tokens + understanding_reader.total_prompt_tokens,
            "total_completion_tokens": reader.total_completion_tokens + understanding_reader.total_completion_tokens,
            "total_tokens": (reader.total_prompt_tokens + reader.total_completion_tokens + 
                           understanding_reader.total_prompt_tokens + understanding_reader.total_completion_tokens),
            "chunk_errors": 0,  # Async reader doesn't track chunk errors the same way
            "error_details": []
        }
        
        # Get model and mode settings
        model_settings = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4-1106-preview"])
        mode_settings = GENERATION_MODES.get(mode, GENERATION_MODES["standard"])
        
        # Build prompt for the README generation with real-time token tracking
        logger.info(f"Building prompt with real-time token tracking for {model}")
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
        
        # Adjust max_tokens if it's too small
        if max_tokens < 2000:
            logger.warning(f"Remaining tokens ({max_tokens}) is too small, using minimum of 2000")
            max_tokens = 2000
            
        # Cap max_tokens for GPT-4 Turbo to respect the completion token limit
        if model == "gpt-4-1106-preview" and max_tokens > 4000:
            logger.info(f"Capping max_tokens from {max_tokens} to 4000 for {model} due to completion token limit")
            max_tokens = 4000
        
        logger.info(f"Using max_tokens={max_tokens} for README generation")
        
        # Generate README using LLM
        logger.info(f"Generating README with {model}")
        readme_content = generate_readme(
            prompt=prompt,
            model=model,
            temperature=mode_settings["temperature"],
            max_tokens=max_tokens
        )
        
        # Create file preview information with token usage details
        file_preview = []
        for file_path in included_files:
            if file_path == "dummy.txt":
                continue
                
            # Get file summary if available
            summary = file_summaries.get(file_path, "")
            preview = summary[:100] + "..." if len(summary) > 100 else summary
            
            # Check if this file was included in the prompt
            was_included = False
            was_truncated = False
            section_name = f"file_{file_path}"
            
            if "section_stats" in token_metadata and section_name in token_metadata["section_stats"]:
                was_included = True
                # If the tokens used is significantly less than what would be needed for the full summary,
                # it was likely truncated
                full_tokens = len(summary) // 4  # Rough estimate
                actual_tokens = token_metadata["section_stats"][section_name]["tokens"]
                was_truncated = actual_tokens < full_tokens * 0.8
            
            file_preview.append({
                "path": file_path,
                "preview": preview,
                "included_in_prompt": was_included,
                "truncated": was_truncated
            })
        
        # Enhanced metadata
        enhanced_metadata = {
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
            "chunk_errors": processing_metadata.get("chunk_errors", 0),
            "prompt_assembly": {
                "total_files": len(included_files),
                "files_in_prompt": token_metadata.get("included_files", 0),
                "files_truncated": token_metadata.get("truncated_files", 0),
                "files_skipped": token_metadata.get("skipped_files", 0),
                "prompt_tokens_used": token_metadata.get("prompt_tokens", 0),
                "prompt_tokens_available": token_metadata.get("available_tokens", 0),
                "prompt_usage_percentage": token_metadata.get("usage_percentage", 0),
                "section_breakdown": token_metadata.get("section_stats", {})
            }
        }
        
        return {
            "success": True,
            "readme": readme_content,
            "metadata": enhanced_metadata
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
                 tone: str, mode: str, model_name: str = "gpt-4-1106-preview", 
                 model_max_tokens: int = 128000) -> tuple[str, Dict]:
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
    # For GPT-4 Turbo, use the maximum completion token limit as the buffer
    buffer = 4096 if model_name == "gpt-4-1106-preview" else 2000
    
    token_counter = TokenCounter(
        model_name=model_name,
        max_tokens=model_max_tokens,
        buffer=buffer
    )
    
    # Extract repo name from URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Define section priorities (1-10, 10 being highest)
    priorities = {
        "base_prompt": 10,  # Essential, cannot be removed
        "file_summaries_header": 9,
        "file_summaries": 5,  # Medium priority, can be pruned if needed
        "tone_instructions": 8,
        "style_instructions": 8,
        "structure_instructions": 7
    }
    
    # Start with the base prompt (highest priority)
    base_prompt = f"""You are a senior technical writer hired to create a compelling, helpful, and user-focused README.md for the following GitHub repository. Your goal is to make it useful for developers evaluating whether to use this repo.

Repository: {repo_url}
Repository name: {repo_name}

Based on the repository's structure and files, here is an internal summary of its purpose and functionality:

{repo_understanding}

"""
    
    # Add base prompt to token counter with section tracking
    success, base_tokens = token_counter.add_to_prompt(
        base_prompt, 
        section_name="base_prompt",
        priority=priorities["base_prompt"]
    )
    
    # Initialize the final prompt
    prompt_sections = {"base_prompt": base_prompt}
    
    # Prepare file summaries section
    file_summaries_header = "Here are summaries of the most important files:\n\n"
    success, header_tokens = token_counter.add_to_prompt(
        file_summaries_header, 
        section_name="file_summaries_header",
        priority=priorities["file_summaries_header"]
    )
    prompt_sections["file_summaries_header"] = file_summaries_header
    
    # Add file summaries to the prompt with dynamic allocation and real-time tracking
    file_paths = list(file_summaries.keys())
    
    # First, identify essential files that must be included
    # This could be main entry points, README, configuration files, etc.
    essential_patterns = [
        "main", "index", "app", "server", "config", "setup", "requirements.txt", 
        "package.json", "Dockerfile", "docker-compose", "README", "LICENSE"
    ]
    
    # Categorize files by importance
    essential_files = []
    standard_files = []
    
    for file_path in file_paths:
        # Check if this is an essential file
        is_essential = any(pattern in file_path.lower() for pattern in essential_patterns)
        
        if is_essential:
            essential_files.append(file_path)
        else:
            standard_files.append(file_path)
    
    # Sort files by path for consistent output
    essential_files.sort()
    standard_files.sort()
    
    # Process essential files first
    files_included = 0
    files_truncated = 0
    files_skipped = 0
    
    # Function to add file summary with fallback handling
    def file_summary_fallback(text, available_tokens):
        # Extract file path from the text
        lines = text.split('\n')
        file_path = lines[0].replace('File: ', '').strip()
        
        # If we have very limited tokens, just include the file path
        if available_tokens < 100:
            return f"File: {file_path}\n(Summary truncated due to token limits)\n\n"
            
        # Otherwise, truncate the content
        max_summary_tokens = available_tokens - 50  # Leave some buffer
        
        # Keep the file path and truncate the rest
        truncated_text = f"File: {file_path}\n"
        
        # Add as much of the summary as we can
        remaining_text = '\n'.join(lines[1:])
        encoded_remaining = token_counter.encoding.encode(remaining_text)
        
        if len(encoded_remaining) <= max_summary_tokens:
            truncated_text += remaining_text
        else:
            # Decode only the tokens we can fit
            truncated_summary = token_counter.encoding.decode(encoded_remaining[:max_summary_tokens])
            truncated_text += truncated_summary + "...\n"
            
        return truncated_text
    
    # Process essential files first
    for file_path in essential_files:
        if file_path not in file_summaries:
            continue
            
        summary = file_summaries[file_path]
        file_text = f"File: {file_path}\n{summary}\n\n"
        
        # Try to add to prompt with fallback handling
        success, tokens, added_text = token_counter.add_with_fallback(
            file_text, 
            section_name=f"file_{file_path}",
            priority=priorities["file_summaries"],
            fallback_handler=file_summary_fallback
        )
        
        if success:
            prompt_sections[f"file_{file_path}"] = added_text
            files_included += 1
            if added_text != file_text:
                files_truncated += 1
        else:
            files_skipped += 1
            
        # Check if we're approaching the token limit
        if token_counter.get_remaining_tokens() < 3000:
            logger.warning(f"Approaching token limit after essential files. Stopping file additions.")
            break
    
    # Then process standard files if we still have room
    if token_counter.get_remaining_tokens() >= 3000:
        for file_path in standard_files:
            if file_path not in file_summaries:
                continue
                
            summary = file_summaries[file_path]
            file_text = f"File: {file_path}\n{summary}\n\n"
            
            # Try to add to prompt with fallback handling
            success, tokens, added_text = token_counter.add_with_fallback(
                file_text, 
                section_name=f"file_{file_path}",
                priority=priorities["file_summaries"],
                fallback_handler=file_summary_fallback
            )
            
            if success:
                prompt_sections[f"file_{file_path}"] = added_text
                files_included += 1
                if added_text != file_text:
                    files_truncated += 1
            else:
                files_skipped += 1
                
            # Check if we're approaching the token limit
            if token_counter.get_remaining_tokens() < 3000:
                logger.warning(f"Approaching token limit. Stopping file additions.")
                break
    
    # Add tone instructions based on the selected tone
    tone_instructions = ""
    if tone == "professional":
        tone_instructions = """
TONE: Write in a professional, clear, and concise tone. Use technical language appropriately but ensure the README remains accessible to developers of various experience levels. Maintain a helpful, informative voice throughout.
"""
    elif tone == "startup":
        tone_instructions = """
TONE: Write in an energetic, modern startup tone that's friendly but still professional. Emphasize innovation and problem-solving. Use conversational language, occasional humor, and convey excitement about the project's potential while maintaining technical accuracy.
"""
    elif tone == "meme":
        tone_instructions = """
TONE: Write in a fun, meme-friendly tone that will appeal to developers who enjoy internet culture. Include appropriate emoji, clever headings, and occasional pop culture references. Keep the technical information accurate but present it in a lighthearted, engaging way that makes the README entertaining to read.
"""
    
    # Add tone instructions if we have room
    success, tone_tokens = token_counter.add_to_prompt(
        tone_instructions,
        section_name="tone_instructions",
        priority=priorities["tone_instructions"]
    )
    if success:
        prompt_sections["tone_instructions"] = tone_instructions
    
    # Add style instructions based on the selected mode
    style_instructions = ""
    if mode == "standard":
        style_instructions = """
STYLE: Create a balanced README with all essential sections. Include enough detail to be helpful without overwhelming the reader. Focus on what makes this repository useful and how to get started quickly.
"""
    elif mode == "detailed":
        style_instructions = """
STYLE: Create a comprehensive README with extensive documentation. Include detailed explanations, examples, and thorough installation and usage instructions. Document architecture, design decisions, and advanced usage scenarios where appropriate.
"""
    elif mode == "concise":
        style_instructions = """
STYLE: Create a minimal README focused on the essentials. Keep it brief but informative. Prioritize quick start information and core features. Use bullet points and short paragraphs to maximize readability.
"""
    elif mode == "creative":
        style_instructions = """
STYLE: Create an engaging README with creative formatting and structure. Feel free to use novel section organization, diagrams, or presentation styles that help the content stand out while remaining informative and useful.
"""
    
    # Add style instructions if we have room
    success, style_tokens = token_counter.add_to_prompt(
        style_instructions,
        section_name="style_instructions",
        priority=priorities["style_instructions"]
    )
    if success:
        prompt_sections["style_instructions"] = style_instructions
    
    # Add structure instructions to enforce README format
    structure_instructions = """
STRUCTURE: Include the following sections in your README:

1. Title and Description - Clear project name and concise description
2. Features - Key capabilities and benefits
3. Installation - Step-by-step instructions
4. Usage - How to use the project with examples
5. Configuration (if applicable)
6. API Documentation (if applicable)
7. Contributing (if applicable)
8. License

Format the README using proper Markdown syntax, including headers, code blocks, lists, and links.
"""
    
    # Add structure instructions if we have room
    success, structure_tokens = token_counter.add_to_prompt(
        structure_instructions,
        section_name="structure_instructions",
        priority=priorities["structure_instructions"]
    )
    if success:
        prompt_sections["structure_instructions"] = structure_instructions
    
    # Final instruction
    final_instruction = "\nNow, write a complete README.md for this repository:\n"
    token_counter.add_to_prompt(final_instruction)
    
    # Assemble the final prompt
    final_prompt = ""
    for section_name in ["base_prompt", "file_summaries_header"]:
        if section_name in prompt_sections:
            final_prompt += prompt_sections[section_name]
    
    # Add file summaries
    for section_name in prompt_sections:
        if section_name.startswith("file_"):
            final_prompt += prompt_sections[section_name]
    
    # Add instructions
    for section_name in ["tone_instructions", "style_instructions", "structure_instructions"]:
        if section_name in prompt_sections:
            final_prompt += prompt_sections[section_name]
    
    # Add final instruction
    final_prompt += final_instruction
    
    # Get token counter stats
    section_stats = token_counter.get_section_stats()
    
    # Create token metadata
    token_metadata = {
        "prompt_tokens": token_counter.current_count,
        "available_tokens": token_counter.available_tokens,
        "remaining_tokens": token_counter.get_remaining_tokens(),
        "usage_percentage": token_counter.get_usage_percentage(),
        "included_files": files_included,
        "truncated_files": files_truncated,
        "skipped_files": files_skipped,
        "section_stats": section_stats
    }
    
    return final_prompt, token_metadata
