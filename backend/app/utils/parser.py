import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import logging
from typing import Dict, List, Tuple

from ..config import GITHUB_TEMP_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository to a temporary directory
    
    Args:
        repo_url: URL of the GitHub repository
        
    Returns:
        str: Path to the cloned repository
    """
    # Create temp directory if it doesn't exist
    os.makedirs(GITHUB_TEMP_DIR, exist_ok=True)
    
    # Create a unique directory name from the repo URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    unique_dir = f"{repo_name}_{tempfile.mktemp(dir='').split('/')[-1]}"
    repo_path = os.path.join(GITHUB_TEMP_DIR, unique_dir)
    
    try:
        # For testing, we can skip actual cloning and return a mock success
        # In production, uncomment the git clone command
        logger.info(f"Cloning repository: {repo_url} to {repo_path}")
        
        # Uncomment for actual cloning:
        # subprocess.run(['git', 'clone', '--depth=1', repo_url, repo_path], 
        #               check=True, capture_output=True)
        
        # For testing, just create the directory
        os.makedirs(repo_path, exist_ok=True)
        
        return repo_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e}")
        raise Exception(f"Failed to clone repository: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        raise

def analyze_repository(repo_path: str) -> Dict:
    """
    Analyze a repository to extract important information
    
    Args:
        repo_path: Path to the cloned repository
        
    Returns:
        Dict: Repository analysis results
    """
    # For now, return mock analysis results
    # In production, implement actual file scanning and analysis
    return {
        "language": "Python",
        "files": [
            {"path": "main.py", "importance": 10},
            {"path": "requirements.txt", "importance": 8},
            {"path": "README.md", "importance": 5},
            {"path": "setup.py", "importance": 7},
            {"path": "tests/test_main.py", "importance": 4}
        ],
        "structure": {
            "src": ["main.py", "utils.py"],
            "tests": ["test_main.py"],
            "docs": ["index.md"]
        }
    }

def get_important_files(repo_path: str, max_files: int = 5) -> List[Tuple[str, str]]:
    """
    Get the most important files from a repository with their content
    
    Args:
        repo_path: Path to the cloned repository
        max_files: Maximum number of files to return
        
    Returns:
        List[Tuple[str, str]]: List of (file_path, file_content) tuples
    """
    analysis = analyze_repository(repo_path)
    
    # Sort files by importance
    important_files = sorted(analysis["files"], 
                            key=lambda x: x["importance"], 
                            reverse=True)[:max_files]
    
    result = []
    for file_info in important_files:
        file_path = os.path.join(repo_path, file_info["path"])
        
        # For testing, generate mock content
        # In production, read actual file content
        content = f"Mock content for {file_info['path']}"
        
        # Uncomment for actual file reading:
        # try:
        #     with open(file_path, 'r', encoding='utf-8') as f:
        #         content = f.read()
        # except Exception as e:
        #     logger.warning(f"Could not read file {file_path}: {e}")
        #     content = f"Error reading file: {e}"
        
        result.append((file_info["path"], content))
    
    return result

def cleanup_repository(repo_path: str) -> None:
    """
    Clean up a cloned repository
    
    Args:
        repo_path: Path to the cloned repository
    """
    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            logger.info(f"Cleaned up repository: {repo_path}")
    except Exception as e:
        logger.error(f"Error cleaning up repository: {e}")
