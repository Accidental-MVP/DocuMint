import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App settings
APP_NAME = "DocuMint"
APP_VERSION = "0.1.0"

# GitHub settings
GITHUB_TEMP_DIR = os.getenv("GITHUB_TEMP_DIR", "./temp_repos")

# LLM settings with cost-optimized defaults
DEFAULT_MODEL = "gpt-4-1106-preview"  # For README generation
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 4000

# Cost-optimized model selection for different phases
PHASE_MODELS = {
    "chunking": "gpt-4o-mini",      # Fastest + cheapest for chunk processing
    "understanding": "gpt-4o",      # Strong reasoning for general understanding
    "excellent_understanding": "gpt-4-1106-preview",  # Deep dive accuracy
    "readme_generation": "gpt-4-1106-preview"  # Best quality for final README
}

# Available models with cost-optimized usage
AVAILABLE_MODELS = {
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "max_tokens": 16385,
        "description": "Fastest and most cost-effective for chunking & summarizing",
        "cost_per_1k_tokens": 0.15,
        "usage_phase": "chunking"
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "max_tokens": 128000,
        "description": "Strong reasoning for general understanding",
        "cost_per_1k_tokens": 2.50,
        "usage_phase": "understanding"
    },
    "gpt-4-1106-preview": {
        "name": "GPT-4 Turbo (128k)",
        "max_tokens": 128000,
        "description": "Deep dive accuracy for excellent understanding and README generation",
        "cost_per_1k_tokens": 10.00,
        "usage_phase": "excellent_understanding"
    },
    "gpt-4": {
        "name": "GPT-4",
        "max_tokens": 8192,
        "description": "Legacy model for compatibility",
        "cost_per_1k_tokens": 30.00,
        "usage_phase": "legacy"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "max_tokens": 16385,
        "description": "Legacy model for compatibility",
        "cost_per_1k_tokens": 0.50,
        "usage_phase": "legacy"
    }
}

# Generation modes
GENERATION_MODES = {
    "standard": {
        "name": "Standard",
        "description": "Balanced README with all essential sections",
        "temperature": 0.3
    },
    "detailed": {
        "name": "Detailed",
        "description": "Comprehensive README with extensive documentation",
        "temperature": 0.2
    },
    "concise": {
        "name": "Concise",
        "description": "Brief README with only the most important information",
        "temperature": 0.3
    },
    "creative": {
        "name": "Creative",
        "description": "More creative and engaging README",
        "temperature": 0.7
    }
}

# Default repo URL for testing
DEFAULT_REPO_URL = "https://github.com/fastapi-users/fastapi-users"
