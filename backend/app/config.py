import os
from dotenv import load_dotenv
from datetime import timedelta
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App settings
APP_NAME = "DocuMint"
APP_VERSION = "0.1.0"

# GitHub settings
GITHUB_TEMP_DIR = os.getenv("GITHUB_TEMP_DIR", "./temp_repos")

# Authentication settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# LLM settings
DEFAULT_MODEL = "gpt-4-1106-preview"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 4000

# Available models
AVAILABLE_MODELS = {
    "gpt-4-1106-preview": {
        "name": "GPT-4 Turbo (128k)",
        "max_tokens": 128000,
        "description": "Massive context, perfect for large-scale README generation"
    },
    "gpt-4": {
        "name": "GPT-4",
        "max_tokens": 8192,
        "description": "Powerful model for complex README generation"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "max_tokens": 16385,
        "description": "Faster and more cost-effective model"
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
