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
        
        # Process chunks with context-aware reader
        logger.info("Processing file chunks with context")
        reader = ContextAwareReader(model="gpt-3.5-turbo")  # Use faster model for analysis
        file_summaries = reader.process_repository_chunks(chunks)
        
        # Generate repository understanding
        logger.info("Generating repository understanding")
        # Use GPT-4 Turbo for the final repository understanding to handle larger context
        understanding_reader = ContextAwareReader(model="gpt-4-1106-preview")
        repo_understanding = understanding_reader.generate_repository_understanding(file_summaries)
        
        # Combine processing metadata
        processing_metadata = reader.get_processing_metadata()
        understanding_metadata = understanding_reader.get_processing_metadata()
        processing_metadata["total_prompt_tokens"] += understanding_metadata["total_prompt_tokens"]
        processing_metadata["total_completion_tokens"] += understanding_metadata["total_completion_tokens"]
        processing_metadata["total_tokens"] += understanding_metadata["total_tokens"]
        if understanding_metadata["chunk_errors"]:
            processing_metadata["chunk_errors"] += understanding_metadata["chunk_errors"]
            if understanding_metadata["error_details"]:
                if not processing_metadata.get("error_details"):
                    processing_metadata["error_details"] = []
                processing_metadata["error_details"].extend(understanding_metadata["error_details"])
        
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
    important_files = []
    other_files = []
    
    for file_path in file_paths:
        file_lower = file_path.lower()
        # Check if this is an essential file
        if any(pattern in file_lower for pattern in essential_patterns):
            essential_files.append(file_path)
        # Important files are typically shorter and thus more token-efficient
        elif len(file_summaries[file_path]) < 500:
            important_files.append(file_path)
        else:
            other_files.append(file_path)
    
    # Sort each category by length for efficiency
    essential_files.sort(key=lambda path: len(file_summaries[path]))
    important_files.sort(key=lambda path: len(file_summaries[path]))
    other_files.sort(key=lambda path: len(file_summaries[path]))
    
    # Process files in priority order
    all_files_by_priority = essential_files + important_files + other_files
    
    # Track how many files we've included
    included_files = 0
    skipped_files = 0
    truncated_files = 0
    file_sections = {}
    
    # Define a custom fallback handler for file summaries
    def file_summary_fallback(text, available_tokens):
        # Extract file path from the text
        lines = text.split('\n', 1)
        if len(lines) < 2 or not lines[0].startswith('## '):
            return token_counter.truncate_text(text, available_tokens)
        
        file_path = lines[0][3:]  # Remove '## ' prefix
        summary = lines[1]
        
        # Try with a truncated summary
        if len(summary) > 300:
            truncated_summary = summary[:300] + "... [summary truncated due to token limits]"
            return f"## {file_path}\n{truncated_summary}"
        else:
            return token_counter.truncate_text(text, available_tokens)
    
    # First pass: try to include all essential files
    for file_path in essential_files:
        summary = file_summaries[file_path]
        file_section = f"## {file_path}\n{summary}\n\n"
        section_name = f"file_{file_path}"
        
        # Try to add with fallback options
        success, tokens, added_text = token_counter.add_with_fallback(
            file_section,
            section_name=section_name,
            priority=priorities["file_summaries"] + 2,  # Higher priority for essential files
            fallback_handler=file_summary_fallback
        )
        
        if success:
            file_sections[file_path] = added_text
            included_files += 1
            if added_text != file_section:
                truncated_files += 1
        else:
            # If we can't even add essential files, we need to make space
            needed_tokens = token_counter.count_tokens(file_summary_fallback(file_section, 300))
            if token_counter.make_space(needed_tokens, ["base_prompt"]):
                # Try again with the space we freed
                success, tokens, added_text = token_counter.add_with_fallback(
                    file_section,
                    section_name=section_name,
                    priority=priorities["file_summaries"] + 2,
                    fallback_handler=file_summary_fallback
                )
                
                if success:
                    file_sections[file_path] = added_text
                    included_files += 1
                    if added_text != file_section:
                        truncated_files += 1
                else:
                    skipped_files += 1
            else:
                skipped_files += 1
    
    # Second pass: try to include important files
    for file_path in important_files + other_files:
        # Check if we're approaching the token limit (leave room for instructions)
        remaining_tokens = token_counter.get_remaining_tokens()
        if remaining_tokens < 500:  # Reserve space for instructions
            logger.info(f"Approaching token limit, stopping file inclusion. Remaining: {remaining_tokens}")
            break
            
        summary = file_summaries[file_path]
        file_section = f"## {file_path}\n{summary}\n\n"
        section_name = f"file_{file_path}"
        
        # For non-essential files, use lower priority
        priority = priorities["file_summaries"] + 1 if file_path in important_files else priorities["file_summaries"]
        
        # Try to add with fallback options
        success, tokens, added_text = token_counter.add_with_fallback(
            file_section,
            section_name=section_name,
            priority=priority,
            fallback_handler=file_summary_fallback
        )
        
        if success:
            file_sections[file_path] = added_text
            included_files += 1
            if added_text != file_section:
                truncated_files += 1
        else:
            skipped_files += 1
    
    # Combine all file sections in the original order they appeared
    file_summaries_content = ""
    for file_path in all_files_by_priority:
        if file_path in file_sections:
            file_summaries_content += file_sections[file_path]
    
    prompt_sections["file_summaries"] = file_summaries_content
    
    logger.info(f"Included {included_files} file summaries, truncated {truncated_files}, skipped {skipped_files} due to token limits")
    
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
    success, _ = token_counter.add_to_prompt(
        tone_section, 
        section_name="tone_instructions",
        priority=priorities["tone_instructions"]
    )
    prompt_sections["tone_instructions"] = tone_section
    
    style_section = f"\n\nStyle: {mode_instructions.get(mode, mode_instructions['standard'])}"
    success, _ = token_counter.add_to_prompt(
        style_section, 
        section_name="style_instructions",
        priority=priorities["style_instructions"]
    )
    prompt_sections["style_instructions"] = style_section
    
    # Add structure instructions with fallback options
    full_structure_instructions = """

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
    
    medium_structure_instructions = """

Create a README.md with the following sections:
1. Title and introduction explaining what the project does and what problem it solves.
2. Key features and benefits.
3. Installation instructions.
4. Basic usage examples.
5. Brief project structure overview.
6. License information (if available).

Use proper Markdown formatting and focus on clarity and accuracy.
"""
    
    minimal_structure_instructions = """

Create a README.md with:
1. Title and brief introduction
2. Key features
3. Installation instructions
4. Basic usage
5. License (if available)

Use proper Markdown formatting.
"""
    
    # Try to add structure instructions with fallbacks based on available tokens
    structure_section = ""
    if token_counter.will_fit(full_structure_instructions)[0]:
        success, _ = token_counter.add_to_prompt(
            full_structure_instructions, 
            section_name="structure_instructions",
            priority=priorities["structure_instructions"]
        )
        structure_section = full_structure_instructions
    elif token_counter.will_fit(medium_structure_instructions)[0]:
        success, _ = token_counter.add_to_prompt(
            medium_structure_instructions, 
            section_name="structure_instructions",
            priority=priorities["structure_instructions"]
        )
        structure_section = medium_structure_instructions
    else:
        success, _ = token_counter.add_to_prompt(
            minimal_structure_instructions, 
            section_name="structure_instructions",
            priority=priorities["structure_instructions"]
        )
        structure_section = minimal_structure_instructions
    
    prompt_sections["structure_instructions"] = structure_section
    
    # Build the final prompt by combining all sections
    final_prompt = ""
    for section_name in ["base_prompt", "file_summaries_header", "file_summaries", 
                         "tone_instructions", "style_instructions", "structure_instructions"]:
        if section_name in prompt_sections:
            final_prompt += prompt_sections[section_name]
    
    # Collect token usage metadata with enhanced information
    token_metadata = {
        "prompt_tokens": token_counter.current_count,
        "max_tokens": token_counter.max_tokens,
        "available_tokens": token_counter.available_tokens,
        "remaining_tokens": token_counter.get_remaining_tokens(),
        "usage_percentage": token_counter.get_usage_percentage(),
        "included_files": included_files,
        "truncated_files": truncated_files,
        "skipped_files": skipped_files,
        "section_stats": token_counter.get_section_stats()
    }
    
    return final_prompt, token_metadata
