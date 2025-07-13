import tiktoken
import logging
from typing import Dict, List, Optional, Union, Tuple, Any, Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenCounter:
    """
    Handles real-time token counting for prompt assembly
    """
    
    def __init__(self, model_name: str = "gpt-4-1106-preview", max_tokens: int = 128000, buffer: int = 4096):
        """
        Initialize the TokenCounter
        
        Args:
            model_name: The name of the model to use for encoding
            max_tokens: Maximum tokens allowed for the model (total context window)
            buffer: Buffer to leave for the response (should be the max completion tokens)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.buffer = buffer
        
        # For GPT-4 Turbo, ensure we respect the hard completion token limit
        if model_name == "gpt-4-1106-preview" and buffer > 4096:
            logger.warning(f"Reducing buffer from {buffer} to 4096 for {model_name} due to completion token limit")
            self.buffer = 4096
            
        self.available_tokens = max_tokens - self.buffer
        self.current_count = 0
        self.sections = {}  # Track sections and their token counts
        self.section_priorities = {}  # Track section priorities
        
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
    
    def add_to_prompt(self, text: str, section_name: str = None, priority: int = 5) -> Tuple[bool, int]:
        """
        Add text to the prompt and track tokens
        
        Args:
            text: Text to add to the prompt
            section_name: Optional name to track this section
            priority: Priority of this section (1-10, 10 being highest)
            
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
        
        # Track section if name provided
        if section_name:
            self.sections[section_name] = {
                "tokens": token_count,
                "text": text
            }
            self.section_priorities[section_name] = priority
            
        logger.info(f"Added {token_count} tokens{' for section ' + section_name if section_name else ''}. Total: {self.current_count}/{self.available_tokens}")
        
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
        self.sections = {}
        self.section_priorities = {}
    
    def remove_section(self, section_name: str) -> int:
        """
        Remove a section from the token count
        
        Args:
            section_name: Name of the section to remove
            
        Returns:
            int: Number of tokens freed
        """
        if section_name not in self.sections:
            return 0
        
        tokens_freed = self.sections[section_name]["tokens"]
        self.current_count -= tokens_freed
        del self.sections[section_name]
        if section_name in self.section_priorities:
            del self.section_priorities[section_name]
        
        logger.info(f"Removed section '{section_name}', freed {tokens_freed} tokens. New total: {self.current_count}")
        return tokens_freed
    
    def make_space(self, needed_tokens: int, protected_sections: List[str] = None) -> bool:
        """
        Try to make space by removing low-priority sections
        
        Args:
            needed_tokens: Number of tokens needed
            protected_sections: List of section names that should not be removed
            
        Returns:
            bool: Whether enough space was freed
        """
        if not self.sections:
            return False
        
        protected_sections = protected_sections or []
        tokens_freed = 0
        
        # Get removable sections sorted by priority (lowest first)
        removable = [(name, self.section_priorities.get(name, 5)) 
                    for name in self.sections 
                    if name not in protected_sections]
        
        removable.sort(key=lambda x: x[1])
        
        # Remove sections until we have enough space
        for section_name, _ in removable:
            if tokens_freed >= needed_tokens:
                break
                
            tokens_freed += self.remove_section(section_name)
            
        return tokens_freed >= needed_tokens
    
    def truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within max_tokens
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            
        Returns:
            str: Truncated text
        """
        if self.count_tokens(text) <= max_tokens:
            return text
            
        # Encode the text to tokens
        tokens = self.encoding.encode(text)
        
        # Keep only max_tokens - 3 tokens to leave room for ellipsis
        truncated_tokens = tokens[:max_tokens - 3]
        
        # Decode back to text
        truncated_text = self.encoding.decode(truncated_tokens)
        
        # Add ellipsis
        return truncated_text + "..."
    
    def add_with_fallback(self, text: str, section_name: str = None, priority: int = 5,
                         fallback_handler: Callable[[str, int], str] = None) -> Tuple[bool, int, str]:
        """
        Add text to prompt with fallback options if it doesn't fit
        
        Args:
            text: Text to add
            section_name: Optional section name
            priority: Priority of this section
            fallback_handler: Custom function to handle fallback (receives text and available tokens)
            
        Returns:
            Tuple[bool, int, str]: (Success, Token count, Text that was added)
        """
        will_fit, token_count = self.will_fit(text)
        
        if will_fit:
            success, _ = self.add_to_prompt(text, section_name, priority)
            return success, token_count, text
            
        # Text won't fit, try fallback options
        remaining = self.get_remaining_tokens()
        logger.warning(f"Text for {section_name or 'unnamed section'} won't fit. Needs {token_count}, have {remaining}")
        
        # Check if we're approaching the token limit
        if remaining < 3000:
            logger.warning(f"Approaching token limit. Only {remaining} tokens left. Stopping file additions.")
            return False, token_count, ""
            
        # If custom handler provided, use it
        if fallback_handler:
            modified_text = fallback_handler(text, remaining)
            if modified_text != text:
                will_fit, new_count = self.will_fit(modified_text)
                if will_fit:
                    success, _ = self.add_to_prompt(modified_text, section_name, priority)
                    return success, new_count, modified_text
        
        # Default fallback: truncate
        truncated = self.truncate_text(text, remaining)
        success, actual_count = self.add_to_prompt(truncated, section_name, priority)
        return success, actual_count, truncated
        
    def get_section_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics about the sections in the token counter
        
        Returns:
            Dict: Dictionary of section statistics
        """
        stats = {}
        for name, data in self.sections.items():
            stats[name] = {
                "tokens": data["tokens"],
                "percentage": (data["tokens"] / self.available_tokens) * 100,
                "priority": self.section_priorities.get(name, 5)
            }
        return stats 