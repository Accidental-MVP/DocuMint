import logging
from typing import Dict, Optional

from ..utils.parser import clone_repository, get_important_files, cleanup_repository
from ..utils.llm import generate_readme
from ..config import DEFAULT_REPO_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_readme_for_repo(repo_url: str = DEFAULT_REPO_URL, 
                                  tone: str = "professional") -> Dict:
    """
    Generate a README for a GitHub repository
    
    Args:
        repo_url: URL of the GitHub repository
        tone: Tone for the README (professional, startup, meme)
        
    Returns:
        Dict: Generated README and metadata
    """
    repo_path = None
    
    try:
        # Clone the repository
        logger.info(f"Starting README generation for: {repo_url}")
        repo_path = clone_repository(repo_url)
        
        # Get important files from the repository
        important_files = get_important_files(repo_path)
        
        # Build prompt for the LLM
        prompt = _build_prompt(repo_url, important_files, tone)
        
        # Generate README using LLM
        readme_content = await generate_readme(prompt)
        
        return {
            "success": True,
            "readme": readme_content,
            "metadata": {
                "repo_url": repo_url,
                "tone": tone,
                "files_analyzed": len(important_files)
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

def _build_prompt(repo_url: str, important_files, tone: str) -> str:
    """
    Build a prompt for the LLM to generate a README
    
    Args:
        repo_url: URL of the GitHub repository
        important_files: List of important files with their content
        tone: Tone for the README
        
    Returns:
        str: Prompt for the LLM
    """
    # Extract repo name from URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Start with the base prompt
    prompt = f"""You are a technical writer creating a README.md file for the GitHub repository: {repo_url}
Repository name: {repo_name}

Based on the following files and their content, create a comprehensive README.md file:

"""
    
    # Add important files to the prompt
    for file_path, content in important_files:
        # Truncate content if it's too long
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
            
        prompt += f"\n--- File: {file_path} ---\n{content}\n"
    
    # Add tone instructions
    tone_instructions = {
        "professional": "Use a professional and straightforward tone.",
        "startup": "Use an enthusiastic startup-like tone with emojis and modern language.",
        "meme": "Use a humorous tone with internet memes and jokes, while still being informative."
    }
    
    prompt += f"\n\nTone: {tone_instructions.get(tone, tone_instructions['professional'])}"
    
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
