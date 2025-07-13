import os
import logging
from typing import List, Dict, Tuple, Optional
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token estimation constants
CHARS_PER_TOKEN = 4.5  # Chars per token estimation
MAX_TOKENS_PER_REQUEST = 128000  # Total context window for GPT-4 Turbo
MAX_COMPLETION_TOKENS = 4096  # Hard limit on completion tokens for GPT-4 Turbo
AVAILABLE_PROMPT_TOKENS = MAX_TOKENS_PER_REQUEST - MAX_COMPLETION_TOKENS  # ~123,904 tokens for prompt
PROMPT_OVERHEAD = 1000  # Base overhead for prompt structure
MAX_SAFE_FILES = 100  # Maximum number of files to process

# Minimum number of important files to include regardless of token budget
MIN_FILES_TO_INCLUDE = 5  # Ensure we include at least this many files

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
        
        # More accurate token estimation for code files
        # Code tends to use fewer tokens than natural language
        return math.ceil(len(content) / CHARS_PER_TOKEN)
    except Exception as e:
        logger.warning(f"Error estimating tokens for {file_path}: {e}")
        # Return a conservative estimate for files we can't read
        return 500  # Reduced from 1000 to be less conservative

def calculate_dynamic_max_files(repo_path: str) -> int:
    """
    Calculate the maximum number of files to process based on repository size
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        int: Recommended maximum number of files
    """
    file_count = count_files_in_repo(repo_path)
    
    # Dynamic scaling based on repository size with higher limits for larger context
    if file_count <= 50:
        return 10  # Small repo: 10 files (increased from 5)
    elif file_count <= 200:
        return 25  # Medium repo: 25 files (increased from 10)
    else:
        return 50  # Large repo: 50 files (increased from 15)

def select_files_with_budget(
    repo_path: str, 
    scored_files: List[Dict], 
    max_token_budget: int = AVAILABLE_PROMPT_TOKENS - PROMPT_OVERHEAD,
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
    
    # First, include the most important files up to MIN_FILES_TO_INCLUDE
    # regardless of token budget (to ensure we have at least some content)
    min_files_to_process = min(MIN_FILES_TO_INCLUDE, len(sorted_files))
    for i in range(min_files_to_process):
        if i < len(sorted_files):
            file_info = sorted_files[i]
            file_path = os.path.join(repo_path, file_info["path"])
            file_tokens = estimate_tokens_for_file(file_path)
            selected_files.append(file_info["path"])
            tokens_used += file_tokens
            logger.info(f"Including essential file {file_info['path']} with {file_tokens} tokens")
    
    # Then process remaining files within budget
    for file_info in sorted_files[min_files_to_process:]:
        file_path = os.path.join(repo_path, file_info["path"])
        
        # Estimate tokens for this file
        file_tokens = estimate_tokens_for_file(file_path)
        
        # Check if adding this file would exceed our budget
        if tokens_used + file_tokens > max_token_budget:
            logger.info(f"Skipping {file_info['path']} - would exceed token budget (est. {file_tokens} tokens)")
            continue
            
        # Check if we've reached our file count limit
        if len(selected_files) >= max_files:
            logger.info(f"Reached max file limit of {max_files}")
            break
            
        # Add file to selected files
        selected_files.append(file_info["path"])
        tokens_used += file_tokens
        logger.info(f"Including {file_info['path']} with {file_tokens} tokens")
        
    logger.info(f"Selected {len(selected_files)} files with estimated {tokens_used} tokens")
    return selected_files, tokens_used 