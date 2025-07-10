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

# LLM settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 4000

# Default repo URL for testing
DEFAULT_REPO_URL = "https://github.com/fastapi-users/fastapi-users"
