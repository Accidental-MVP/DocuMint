import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import logging
from typing import Dict, List, Tuple
import glob

from ..config import GITHUB_TEMP_DIR
from .chunker import FileChunker, chunk_repository_files

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
        subprocess.run(['git', 'clone', '--depth=1', repo_url, repo_path], 
                      check=True, capture_output=True)
        
        # For testing, just create the directory if it doesn't exist
        # os.makedirs(repo_path, exist_ok=True)
        
        return repo_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e}")
        error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
        raise Exception(f"Failed to clone repository: {error_message}")
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        raise

def find_files_by_extension(repo_path: str, extensions: List[str] = None) -> List[str]:
    """
    Find files in a repository by extension
    
    Args:
        repo_path: Path to the repository
        extensions: List of file extensions to look for (e.g., ['.py', '.js'])
        
    Returns:
        List[str]: List of file paths (relative to repo_path)
    """
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp', '.md']
    
    all_files = []
    
    for ext in extensions:
        pattern = os.path.join(repo_path, '**', f'*{ext}')
        files = glob.glob(pattern, recursive=True)
        all_files.extend([os.path.relpath(f, repo_path) for f in files])
    
    return all_files

def analyze_repository(repo_path: str) -> Dict:
    """
    Analyze a repository to extract important information
    
    Args:
        repo_path: Path to the cloned repository
        
    Returns:
        Dict: Repository analysis results
    """
    # Find all code files
    code_files = find_files_by_extension(repo_path)
    
    # Check if the repository has common files
    has_readme = os.path.exists(os.path.join(repo_path, 'README.md'))
    has_setup_py = os.path.exists(os.path.join(repo_path, 'setup.py'))
    has_package_json = os.path.exists(os.path.join(repo_path, 'package.json'))
    has_requirements = os.path.exists(os.path.join(repo_path, 'requirements.txt'))
    
    # Determine main language (simple approach)
    extensions = {}
    for file in code_files:
        ext = os.path.splitext(file)[1]
        if ext:
            extensions[ext] = extensions.get(ext, 0) + 1
    
    # Find the most common extension
    main_language = max(extensions.items(), key=lambda x: x[1])[0] if extensions else '.py'
    
    # Map extension to language name
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'React TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C/C++',
        '.hpp': 'C++'
    }
    
    language = language_map.get(main_language, 'Unknown')
    
    # Score files by importance
    scored_files = []
    
    # Add common important files first
    if has_readme:
        scored_files.append({"path": "README.md", "importance": 10})
    
    if has_setup_py:
        scored_files.append({"path": "setup.py", "importance": 9})
    
    if has_package_json:
        scored_files.append({"path": "package.json", "importance": 9})
    
    if has_requirements:
        scored_files.append({"path": "requirements.txt", "importance": 8})
    
    # Score other files
    for file in code_files:
        # Skip files already added
        if file in [f["path"] for f in scored_files]:
            continue
        
        # Score based on file name and location
        score = 5  # Default score
        
        # Main files are more important
        if os.path.basename(file) in ['main.py', 'index.js', 'app.py', 'server.js', 'index.ts']:
            score += 4
        
        # Files in the root directory are more important
        if '/' not in file and '\\' not in file:
            score += 2
        
        # Files in test directories are less important
        if 'test' in file.lower() or 'tests' in file.lower():
            score -= 2
        
        # Files in doc directories are important for understanding
        if 'doc' in file.lower() or 'docs' in file.lower():
            score += 1
        
        scored_files.append({"path": file, "importance": score})
    
    # Sort by importance and limit to top 50
    scored_files = sorted(scored_files, key=lambda x: x["importance"], reverse=True)[:50]
    
    return {
        "language": language,
        "files": scored_files,
        "structure": {
            "has_readme": has_readme,
            "has_setup_py": has_setup_py,
            "has_package_json": has_package_json,
            "has_requirements": has_requirements
        }
    }

def get_important_files(repo_path: str, max_files: int = 5) -> List[str]:
    """
    Get the most important files from a repository
    
    Args:
        repo_path: Path to the cloned repository
        max_files: Maximum number of files to return
        
    Returns:
        List[str]: List of important file paths (relative to repo_path)
    """
    analysis = analyze_repository(repo_path)
    
    # Sort files by importance
    important_files = sorted(analysis["files"], 
                            key=lambda x: x["importance"], 
                            reverse=True)[:max_files]
    
    # Return just the file paths
    file_paths = [file_info["path"] for file_info in important_files]
    logger.info(f"Selected important files: {file_paths}")
    return file_paths

def get_chunked_repository_content(repo_path: str, max_files: int = 5) -> List[Dict]:
    """
    Get chunked content from important files in a repository
    
    Args:
        repo_path: Path to the cloned repository
        max_files: Maximum number of files to process
        
    Returns:
        List[Dict]: List of chunks with metadata
    """
    # Get important file paths
    important_files = get_important_files(repo_path, max_files)
    
    # Chunk the files
    chunks = chunk_repository_files(repo_path, important_files)
    
    return chunks

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
