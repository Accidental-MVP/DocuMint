import tiktoken
import logging
from typing import Dict, List, Optional, Union, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenCounter:
    """
    Handles real-time token counting for prompt assembly
    """
    
    def __init__(self, model_name: str = "gpt-4", max_tokens: int = 8192, buffer: int = 500):
        """
        Initialize the TokenCounter
        
        Args:
            model_name: The name of the model to use for encoding
            max_tokens: Maximum tokens allowed for the model
            buffer: Buffer to leave for the response
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.buffer = buffer
        self.available_tokens = max_tokens - buffer
        self.current_count = 0
        
        # Get the appropriate encoder for the model
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning(f"Model {model_name} not found. Using cl100k_base encoding.")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string
        
        Args:
            text: The text to count tokens for
            
        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Count the number of tokens in a list of chat messages
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            int: Number of tokens
        """
        num_tokens = 0
        
        # Per message overhead
        for message in messages:
            # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            
            for key, value in message.items():
                num_tokens += self.count_tokens(value)
                
                # If there's a name, the role is omitted
                if key == "name":
                    num_tokens -= 1  # Role is omitted
        
        # Every reply is primed with <im_start>assistant
        num_tokens += 2
        
        return num_tokens
    
    def add_to_prompt(self, text: str) -> Tuple[bool, int]:
        """
        Add text to the prompt and track tokens
        
        Args:
            text: Text to add to the prompt
            
        Returns:
            Tuple[bool, int]: (Success, Token count of the text)
        """
        token_count = self.count_tokens(text)
        
        # Check if adding this would exceed our limit
        if self.current_count + token_count > self.available_tokens:
            logger.warning(f"Adding text would exceed token limit. Current: {self.current_count}, Adding: {token_count}, Limit: {self.available_tokens}")
            return False, token_count
        
        # Update the count
        self.current_count += token_count
        logger.info(f"Added {token_count} tokens. Total: {self.current_count}/{self.available_tokens}")
        
        return True, token_count
    
    def will_fit(self, text: str) -> Tuple[bool, int]:
        """
        Check if text will fit in the remaining token budget without adding it
        
        Args:
            text: Text to check
            
        Returns:
            Tuple[bool, int]: (Will fit, Token count of the text)
        """
        token_count = self.count_tokens(text)
        return self.current_count + token_count <= self.available_tokens, token_count
    
    def get_remaining_tokens(self) -> int:
        """
        Get the number of tokens remaining in the budget
        
        Returns:
            int: Remaining tokens
        """
        return self.available_tokens - self.current_count
    
    def get_usage_percentage(self) -> float:
        """
        Get the percentage of the token budget used
        
        Returns:
            float: Percentage of token budget used (0-100)
        """
        return (self.current_count / self.available_tokens) * 100
    
    def reset(self) -> None:
        """Reset the token counter"""
        self.current_count = 0 