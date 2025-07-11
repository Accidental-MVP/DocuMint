import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import logging
from typing import Dict, List, Tuple
import glob
import stat
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.util import ClassNotFound
import git
from datetime import datetime, timedelta, timezone

from ..config import GITHUB_TEMP_DIR
from .chunker import FileChunker, chunk_repository_files
from .token_budget import select_files_with_budget, calculate_dynamic_max_files

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
    
    # Extract repo name from URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Create a temporary directory with the repo name as prefix
    repo_path = tempfile.mkdtemp(prefix=f"{repo_name}_", dir=GITHUB_TEMP_DIR)
    
    try:
        logger.info(f"Cloning repository: {repo_url} to {repo_path}")
        
        # Clone the repository
        subprocess.run(['git', 'clone', '--depth=1', repo_url, repo_path], 
                      check=True, capture_output=True)
        
        return repo_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e}")
        error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
        # Clean up the empty directory if clone failed
        try:
            shutil.rmtree(repo_path)
        except:
            pass
        raise Exception(f"Failed to clone repository: {error_message}")
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        # Clean up the empty directory if clone failed
        try:
            shutil.rmtree(repo_path)
        except:
            pass
        raise

def analyze_git_history(repo_path: str, max_commits: int = 100) -> Dict:
    """
    Analyze the git history of a repository
    
    Args:
        repo_path: Path to the repository
        max_commits: Maximum number of commits to analyze
        
    Returns:
        Dict: Git history analysis
    """
    try:
        # Open the repository
        repo = git.Repo(repo_path)
        
        # Get basic repository info
        try:
            default_branch = repo.active_branch.name
        except:
            default_branch = "unknown"
        
        # Get commit history
        commits = list(repo.iter_commits(max_count=max_commits))
        
        # Calculate commit frequency
        if len(commits) > 1:
            # Ensure both dates are timezone-aware for comparison
            first_commit_date = ensure_timezone_aware(commits[-1].committed_datetime)
            last_commit_date = ensure_timezone_aware(commits[0].committed_datetime)
            
            days_diff = (last_commit_date - first_commit_date).days or 1  # Avoid division by zero
            commits_per_day = len(commits) / days_diff
        else:
            commits_per_day = 0
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_commits = [c for c in commits if ensure_timezone_aware(c.committed_datetime) > thirty_days_ago]
        
        # Get contributor information
        contributors = {}
        for commit in commits:
            author = commit.author.name
            contributors[author] = contributors.get(author, 0) + 1
        
        # Get file change frequency
        file_changes = {}
        for commit in commits[:50]:  # Limit to 50 most recent commits for performance
            try:
                # Get parent commit
                parent = commit.parents[0] if commit.parents else None
                if parent:
                    # Get changes between parent and this commit
                    diffs = parent.diff(commit)
                    for diff in diffs:
                        if diff.a_path:
                            file_changes[diff.a_path] = file_changes.get(diff.a_path, 0) + 1
                        if diff.b_path and diff.b_path != diff.a_path:
                            file_changes[diff.b_path] = file_changes.get(diff.b_path, 0) + 1
            except Exception as e:
                logger.warning(f"Error analyzing commit {commit.hexsha}: {e}")
        
        # Get most frequently changed files
        most_changed_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "default_branch": default_branch,
            "total_commits": len(commits),
            "recent_commits": len(recent_commits),
            "commits_per_day": round(commits_per_day, 2),
            "total_contributors": len(contributors),
            "top_contributors": sorted(contributors.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_changed_files": most_changed_files,
            "last_commit_date": ensure_timezone_aware(commits[0].committed_datetime).isoformat() if commits else None,
            "first_commit_date": ensure_timezone_aware(commits[-1].committed_datetime).isoformat() if commits else None
        }
    except Exception as e:
        logger.warning(f"Error analyzing git history: {e}")
        return {
            "error": str(e),
            "total_commits": 0,
            "recent_commits": 0,
            "commits_per_day": 0,
            "total_contributors": 0
        }

def ensure_timezone_aware(dt):
    """
    Ensure a datetime object is timezone-aware
    
    Args:
        dt: Datetime object
        
    Returns:
        Timezone-aware datetime object
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def detect_language(file_path: str) -> str:
    """
    Detect the programming language of a file using pygments
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Detected language name
    """
    try:
        # Try to read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Skip empty files
        if not content.strip():
            return "Unknown"
            
        # Try to guess lexer based on filename first
        try:
            lexer = guess_lexer_for_filename(file_path, content)
            return lexer.name
        except ClassNotFound:
            # If that fails, try to guess based on content
            try:
                lexer = guess_lexer(content)
                return lexer.name
            except ClassNotFound:
                # Fall back to extension-based detection
                ext = os.path.splitext(file_path)[1].lower()
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
                    '.hpp': 'C++',
                    '.md': 'Markdown',
                    '.html': 'HTML',
                    '.css': 'CSS',
                    '.json': 'JSON',
                    '.yml': 'YAML',
                    '.yaml': 'YAML',
                    '.rb': 'Ruby',
                    '.php': 'PHP',
                    '.sh': 'Shell'
                }
                return language_map.get(ext, "Unknown")
    except Exception as e:
        logger.warning(f"Error detecting language for {file_path}: {e}")
        return "Unknown"

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

def get_repository_languages(repo_path: str, files: List[str]) -> Dict[str, int]:
    """
    Analyze the repository to determine language distribution
    
    Args:
        repo_path: Path to the repository
        files: List of files to analyze
        
    Returns:
        Dict[str, int]: Dictionary mapping language names to file counts
    """
    languages = {}
    
    for file in files:
        file_path = os.path.join(repo_path, file)
        language = detect_language(file_path)
        languages[language] = languages.get(language, 0) + 1
    
    return languages

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
    
    # Get language distribution
    language_distribution = get_repository_languages(repo_path, code_files[:50])  # Limit to 50 files for performance
    
    # Find the most common language
    main_language = max(language_distribution.items(), key=lambda x: x[1])[0] if language_distribution else "Unknown"
    
    # Get git history analysis
    git_history = analyze_git_history(repo_path)
    
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
    
    # Get most changed files from git history
    most_changed_files = {path: count for path, count in git_history.get("most_changed_files", [])}
    
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
            
        # Boost score for frequently changed files
        if file in most_changed_files:
            change_count = most_changed_files[file]
            # Add up to 3 points based on change frequency
            score += min(3, change_count // 2)
        
        scored_files.append({"path": file, "importance": score})
    
    # Sort by importance and limit to top 50
    scored_files = sorted(scored_files, key=lambda x: x["importance"], reverse=True)[:50]
    
    return {
        "language": main_language,
        "language_distribution": language_distribution,
        "git_history": git_history,
        "files": scored_files,
        "structure": {
            "has_readme": has_readme,
            "has_setup_py": has_setup_py,
            "has_package_json": has_package_json,
            "has_requirements": has_requirements
        }
    }

def get_important_files(repo_path: str, max_files: int = None, client_max_files: int = None) -> List[str]:
    """
    Get the most important files from a repository based on token budget
    
    Args:
        repo_path: Path to the cloned repository
        max_files: Maximum number of files to return (if None, will be calculated dynamically)
        client_max_files: Client-specified maximum number of files
        
    Returns:
        List[str]: List of important file paths (relative to repo_path)
    """
    # Analyze the repository
    analysis = analyze_repository(repo_path)
    
    # If max_files is not specified, calculate it dynamically
    if max_files is None:
        max_files = calculate_dynamic_max_files(repo_path)
    
    # Use token budget to select files
    file_paths, estimated_tokens = select_files_with_budget(
        repo_path, 
        analysis["files"], 
        client_max_files=client_max_files
    )
    
    logger.info(f"Selected {len(file_paths)} important files with estimated {estimated_tokens} tokens")
    return file_paths

def get_chunked_repository_content(repo_path: str, max_files: int = None, client_max_files: int = None) -> List[Dict]:
    """
    Get chunked content from important files in a repository
    
    Args:
        repo_path: Path to the cloned repository
        max_files: Maximum number of files to process (if None, will be calculated dynamically)
        client_max_files: Client-specified maximum number of files
        
    Returns:
        List[Dict]: List of chunks with metadata
    """
    # Get important file paths using token budget
    important_files = get_important_files(repo_path, max_files, client_max_files)
    
    # Chunk the files
    chunks = chunk_repository_files(repo_path, important_files)
    
    return chunks

def handle_readonly_files(func, path, exc_info):
    """
    Error handler for shutil.rmtree to handle read-only files
    
    Args:
        func: Function that raised the exception
        path: Path to the file
        exc_info: Exception information
    """
    # Check if the error is due to read-only files
    if not os.access(path, os.W_OK):
        # Change file permissions
        os.chmod(path, stat.S_IWUSR)
        # Try again
        func(path)
    else:
        # If it's not a permission error, re-raise the exception
        raise

def cleanup_repository(repo_path: str) -> None:
    """
    Clean up a cloned repository
    
    Args:
        repo_path: Path to the cloned repository
    """
    try:
        if os.path.exists(repo_path):
            # Use error handler for read-only files
            shutil.rmtree(repo_path, onerror=handle_readonly_files)
            logger.info(f"Cleaned up repository: {repo_path}")
    except Exception as e:
        logger.error(f"Error cleaning up repository: {e}")
        # Try to remove as many files as possible
        try:
            for root, dirs, files in os.walk(repo_path, topdown=False):
                for name in files:
                    try:
                        file_path = os.path.join(root, name)
                        os.chmod(file_path, stat.S_IWUSR)
                        os.remove(file_path)
                    except:
                        pass
                for name in dirs:
                    try:
                        dir_path = os.path.join(root, name)
                        os.rmdir(dir_path)
                    except:
                        pass
            # Try to remove the main directory
            try:
                os.rmdir(repo_path)
            except:
                pass
            logger.info(f"Partially cleaned up repository: {repo_path}")
        except Exception as e2:
            logger.error(f"Failed to partially clean up repository: {e2}")
            # Just log the error and continue - we'll rely on periodic cleanup
