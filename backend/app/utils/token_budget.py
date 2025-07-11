import os
import logging
from typing import List, Dict, Tuple, Optional
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token estimation constants
CHARS_PER_TOKEN = 4  # Rough estimate: 1 token ≈ 4 characters
MAX_TOKENS_PER_REQUEST = 8192  # OpenAI's context window limit for GPT-4
PROMPT_OVERHEAD = 1000  # Reserved for prompts, instructions, and overhead
MAX_SAFE_FILES = 20  # Maximum number of files we'll process regardless of budget

def count_files_in_repo(repo_path: str) -> int:
    """
    Count the total number of files in a repository
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        int: Total number of files
    """
    file_count = 0
    for root, _, files in os.walk(repo_path):
        # Skip .git directory
        if '.git' in root:
            continue
        file_count += len(files)
    
    return file_count

def estimate_tokens_for_file(file_path: str) -> int:
    """
    Estimate the number of tokens in a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: Estimated token count
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Rough estimate: 1 token ≈ 4 characters
        return math.ceil(len(content) / CHARS_PER_TOKEN)
    except Exception as e:
        logger.warning(f"Error estimating tokens for {file_path}: {e}")
        # Return a conservative estimate for files we can't read
        return 1000  # Assume ~1K tokens for files we can't read

def calculate_dynamic_max_files(repo_path: str) -> int:
    """
    Calculate the maximum number of files to process based on repository size
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        int: Recommended maximum number of files
    """
    file_count = count_files_in_repo(repo_path)
    
    # Dynamic scaling based on repository size
    if file_count <= 50:
        return 5  # Small repo: 5 files
    elif file_count <= 200:
        return 10  # Medium repo: 10 files
    else:
        return 15  # Large repo: 15 files

def select_files_with_budget(
    repo_path: str, 
    scored_files: List[Dict], 
    max_token_budget: int = MAX_TOKENS_PER_REQUEST - PROMPT_OVERHEAD,
    client_max_files: Optional[int] = None
) -> Tuple[List[str], int]:
    """
    Select files to process based on importance and token budget
    
    Args:
        repo_path: Path to the repository
        scored_files: List of files with importance scores
        max_token_budget: Maximum token budget
        client_max_files: Client-specified maximum number of files
        
    Returns:
        Tuple[List[str], int]: Selected file paths and estimated token usage
    """
    # Sort files by importance
    sorted_files = sorted(scored_files, key=lambda x: x["importance"], reverse=True)
    
    # Calculate dynamic max files based on repo size
    dynamic_max_files = calculate_dynamic_max_files(repo_path)
    
    # Use client-specified limit if provided, capped by MAX_SAFE_FILES
    if client_max_files is not None:
        max_files = min(client_max_files, MAX_SAFE_FILES)
    else:
        max_files = dynamic_max_files
    
    logger.info(f"Repository has {len(sorted_files)} scorable files, using max_files={max_files}")
    
    # Select files based on token budget
    selected_files = []
    tokens_used = 0
    
    for file_info in sorted_files:
        file_path = os.path.join(repo_path, file_info["path"])
        
        # Estimate tokens for this file
        file_tokens = estimate_tokens_for_file(file_path)
        
        # Check if adding this file would exceed our budget
        if tokens_used + file_tokens > max_token_budget:
            # If we haven't selected any files yet, take at least one
            if not selected_files:
                selected_files.append(file_info["path"])
                tokens_used += file_tokens
            # Otherwise, skip this file
            logger.info(f"Skipping {file_info['path']} - would exceed token budget")
            continue
            
        # Check if we've reached our file count limit
        if len(selected_files) >= max_files:
            logger.info(f"Reached max file limit of {max_files}")
            break
            
        # Add file to selected files
        selected_files.append(file_info["path"])
        tokens_used += file_tokens
        
    logger.info(f"Selected {len(selected_files)} files with estimated {tokens_used} tokens")
    return selected_files, tokens_used 