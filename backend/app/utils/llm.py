import logging
from openai import OpenAI
from ..config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_readme(prompt: str, model: str = DEFAULT_MODEL, 
                    temperature: float = DEFAULT_TEMPERATURE,
                    max_tokens: int = DEFAULT_MAX_TOKENS):
    """
    Generate README content using OpenAI API
    
    Args:
        prompt: The prompt to send to the OpenAI API
        model: The model to use for generation
        temperature: Controls randomness (0-1)
        max_tokens: Maximum tokens to generate
        
    Returns:
        str: Generated README content
    """
    try:
        if not OPENAI_API_KEY:
            logger.warning("No OpenAI API key found. Using mock README.")
            return _get_mock_readme()
            
        # Use the modern OpenAI client approach
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical writer specializing in creating clear, concise README files for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Track token usage for billing purposes
        _track_token_usage(response)
        
        # Add response structure check
        try:
            return response.choices[0].message.content.strip()
        except (AttributeError, IndexError) as e:
            logger.warning(f"Error parsing OpenAI response: {e}")
            return _get_mock_readme()
            
    except Exception as e:
        logger.warning(f"Error calling OpenAI API: {e}")
        # Fallback to mock response in case of errors
        return _get_mock_readme()

def _track_token_usage(response):
    """
    Track token usage for billing purposes
    
    Args:
        response: OpenAI API response
    """
    try:
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
        
        # TODO: Store token usage in database for Stripe integration
        # Example: db.save_token_usage(user_id, prompt_tokens, completion_tokens, total_tokens)
    except Exception as e:
        logger.warning(f"Failed to track token usage: {e}")

def _get_mock_readme():
    """Return a mock README for testing purposes"""
    return """# Sample Project

A simple project demonstrating various features and functionalities.

## Features

- Feature 1: Description of feature 1
- Feature 2: Description of feature 2
- Feature 3: Description of feature 3

## Installation

```bash
pip install sample-project
```

## Usage

```python
from sample_project import main

main.run()
```

## Project Structure

- `/src`: Source code
- `/tests`: Test files
- `/docs`: Documentation

## License

MIT
"""
