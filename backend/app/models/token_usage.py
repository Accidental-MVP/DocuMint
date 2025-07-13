from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class TokenUsage(BaseModel):
    """Model for tracking token usage"""
    user_id: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    last_updated: datetime = datetime.now()
    
    model_config = {
        "arbitrary_types_allowed": True
    }

def add_token_usage(token_usage: TokenUsage, new_usage: Dict[str, int]) -> None:
    """Add token usage to the existing counter"""
    token_usage.prompt_tokens += new_usage.get("prompt_tokens", 0)
    token_usage.completion_tokens += new_usage.get("completion_tokens", 0)
    token_usage.total_tokens += new_usage.get("total_tokens", 0)
    token_usage.last_updated = datetime.now() 