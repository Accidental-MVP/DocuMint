import openai
from ..config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

# Configure OpenAI API key
openai.api_key = OPENAI_API_KEY

async def generate_readme(prompt: str, model: str = DEFAULT_MODEL, 
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
            # Return mock response for testing without API key
            return _get_mock_readme()
            
        response = await openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical writer specializing in creating clear, concise README files for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to mock response in case of errors
        return _get_mock_readme()

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
