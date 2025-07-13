from fastapi import Depends
from .models.token_usage import TokenUsage

def get_token_usage() -> TokenUsage:
    """
    Dependency to track token usage throughout a request
    
    Returns:
        TokenUsage: A token usage tracker
    """
    return TokenUsage() 