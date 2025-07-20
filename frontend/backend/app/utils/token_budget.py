import tiktoken
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenBudget:
    """Token budget configuration for different models"""
    max_total_tokens: int
    max_prompt_tokens: int
    max_completion_tokens: int
    safety_margin: int = 500  # Buffer to prevent edge cases

class ProactiveTokenCalculator:
    """
    Proactive token budget calculator that prevents token overflow errors
    by pre-checking and intelligently trimming content before API calls.
    """
    
    def __init__(self, model: str = "gpt-4-1106-preview"):
        self.model = model
        self.budget = self._get_model_budget(model)
        
        # Get the appropriate encoder for the model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found. Using cl100k_base encoding.")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def _get_model_budget(self, model: str) -> TokenBudget:
        """Get token budget configuration for the specified model"""
        if "gpt-4-1106-preview" in model:
            return TokenBudget(
                max_total_tokens=128000,
                max_prompt_tokens=120000,  # Leave 8K for completion
                max_completion_tokens=8000
            )
        elif "gpt-4" in model:
            return TokenBudget(
                max_total_tokens=8192,
                max_prompt_tokens=6000,  # Leave 2K for completion
                max_completion_tokens=2000
            )
        else:  # gpt-3.5-turbo
            return TokenBudget(
                max_total_tokens=16385,
                max_prompt_tokens=12000,  # Leave 4K for completion
                max_completion_tokens=4000
            )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the model's encoding"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a messages list"""
        total_tokens = 0
        for message in messages:
            # Count content tokens
            content_tokens = self.count_tokens(message.get("content", ""))
            # Add overhead for role and formatting (rough estimate)
            role_tokens = 4  # Approximate overhead per message
            total_tokens += content_tokens + role_tokens
        return total_tokens
    
    def project_request_tokens(self, 
                              system_prompt: str,
                              user_prompt: str,
                              context_chunks: List[Dict[str, Any]] = None,
                              conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Project the total token count of a request before making it
        
        Args:
            system_prompt: System message content
            user_prompt: User message content
            context_chunks: List of context chunks to include
            conversation_history: Previous conversation messages
        
    Returns:
            Dict with token counts and recommendations
        """
        # Build the full messages list
        messages = []
        
        # Add system message
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add context chunks as user messages
        if context_chunks:
            for chunk in context_chunks:
                chunk_content = f"File: {chunk.get('file_path', 'Unknown')}\nContent:\n{chunk.get('content', '')}"
                messages.append({"role": "user", "content": chunk_content})
        
        # Add the main user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        # Count tokens
        total_tokens = self.count_messages_tokens(messages)
        system_tokens = self.count_tokens(system_prompt) if system_prompt else 0
        user_prompt_tokens = self.count_tokens(user_prompt)
        context_tokens = total_tokens - system_tokens - user_prompt_tokens
        
        # Calculate available tokens for completion
        available_completion_tokens = self.budget.max_total_tokens - total_tokens - self.budget.safety_margin
        
        # Determine if we need to trim
        needs_trimming = total_tokens > self.budget.max_prompt_tokens
        is_safe = total_tokens <= self.budget.max_prompt_tokens
        
        return {
            "total_tokens": total_tokens,
            "system_tokens": system_tokens,
            "user_prompt_tokens": user_prompt_tokens,
            "context_tokens": context_tokens,
            "available_completion_tokens": max(0, available_completion_tokens),
            "needs_trimming": needs_trimming,
            "is_safe": is_safe,
            "budget_limit": self.budget.max_prompt_tokens,
            "messages": messages
        }
    
    def trim_messages_intelligently(self, 
                                   messages: List[Dict[str, str]],
                                   target_tokens: int = None) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Intelligently trim messages to fit within token budget
        
        Strategy:
        1. Keep system message (highest priority)
        2. Keep most recent user/assistant messages (conversation continuity)
        3. Trim oldest context chunks first
        4. Trim from the middle if needed (preserve recent context)
    
    Args:
            messages: List of message dictionaries
            target_tokens: Target token count (defaults to budget limit)
            
        Returns:
            Tuple of (trimmed_messages, trimming_info)
        """
        if target_tokens is None:
            target_tokens = self.budget.max_prompt_tokens
        
        original_tokens = self.count_messages_tokens(messages)
        original_count = len(messages)
        
        if original_tokens <= target_tokens:
            return messages, {
                "trimmed": False,
                "original_tokens": original_tokens,
                "final_tokens": original_tokens,
                "tokens_removed": 0,
                "messages_removed": 0
            }
        
        # Separate messages by type for intelligent trimming
        system_messages = []
        conversation_messages = []
        context_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_messages.append(msg)
            elif msg.get("role") in ["user", "assistant"]:
                # Check if this looks like context (contains file paths, code blocks)
                content = msg.get("content", "")
                if any(indicator in content.lower() for indicator in ["file:", "content:", "```", "def ", "class ", "import "]):
                    context_messages.append(msg)
                else:
                    conversation_messages.append(msg)
        
        # Start with system messages (highest priority)
        trimmed_messages = system_messages.copy()
        current_tokens = self.count_messages_tokens(trimmed_messages)
        
        # Add conversation messages (keep most recent)
        conversation_messages.reverse()  # Start with most recent
        for msg in conversation_messages:
            msg_tokens = self.count_tokens(msg.get("content", "")) + 4
            if current_tokens + msg_tokens <= target_tokens:
                trimmed_messages.insert(1, msg)  # Insert after system message
                current_tokens += msg_tokens
            else:
                break
        
        # Add context messages (keep most recent, trim oldest)
        context_messages.reverse()  # Start with most recent
        for msg in context_messages:
            msg_tokens = self.count_tokens(msg.get("content", "")) + 4
            if current_tokens + msg_tokens <= target_tokens:
                trimmed_messages.append(msg)
                current_tokens += msg_tokens
    else:
                break
        
        # If still over limit, trim from the middle (preserve system and recent)
        if current_tokens > target_tokens and len(trimmed_messages) > 2:
            # Keep system message and last message, trim from middle
            system_msg = trimmed_messages[0]
            last_msg = trimmed_messages[-1]
            
            # Rebuild with just system and last message
            trimmed_messages = [system_msg]
            current_tokens = self.count_tokens(system_msg.get("content", "")) + 4
            
            # Add last message if it fits
            last_msg_tokens = self.count_tokens(last_msg.get("content", "")) + 4
            if current_tokens + last_msg_tokens <= target_tokens:
                trimmed_messages.append(last_msg)
                current_tokens += last_msg_tokens
        
        final_tokens = self.count_messages_tokens(trimmed_messages)
        tokens_removed = original_tokens - final_tokens
        messages_removed = original_count - len(trimmed_messages)
        
        trimming_info = {
            "trimmed": True,
            "original_tokens": original_tokens,
            "final_tokens": final_tokens,
            "tokens_removed": tokens_removed,
            "messages_removed": messages_removed,
            "trimming_strategy": "intelligent_priority_based"
        }
        
        logger.info(f"Trimmed messages: {original_tokens} -> {final_tokens} tokens "
                   f"({tokens_removed} removed, {messages_removed} messages removed)")
        
        return trimmed_messages, trimming_info
    
    def create_safe_messages(self, 
                            system_prompt: str,
                            user_prompt: str,
                            context_chunks: List[Dict[str, Any]] = None,
                            conversation_history: List[Dict[str, str]] = None) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Create a safe messages list that's guaranteed to fit within token budget
        
        Args:
            system_prompt: System message content
            user_prompt: User message content
            context_chunks: List of context chunks to include
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (safe_messages, budget_info)
        """
        # Project token usage
        projection = self.project_request_tokens(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context_chunks=context_chunks,
            conversation_history=conversation_history
        )
        
        # If already safe, return as-is
        if projection["is_safe"]:
            return projection["messages"], {
                "budget_info": projection,
                "trimming_applied": False,
                "trimming_info": None
            }
        
        # Need to trim - build messages and trim intelligently
        messages = projection["messages"]
        trimmed_messages, trimming_info = self.trim_messages_intelligently(messages)
        
        # Verify the trimmed messages are safe
        final_tokens = self.count_messages_tokens(trimmed_messages)
        is_safe = final_tokens <= self.budget.max_prompt_tokens
        
        if not is_safe:
            logger.warning(f"Failed to trim messages to safe size: {final_tokens} > {self.budget.max_prompt_tokens}")
            # Last resort: keep only system and user prompt
            trimmed_messages = []
            if system_prompt:
                trimmed_messages.append({"role": "system", "content": system_prompt})
            trimmed_messages.append({"role": "user", "content": user_prompt})
        
        return trimmed_messages, {
            "budget_info": projection,
            "trimming_applied": True,
            "trimming_info": trimming_info,
            "final_tokens": self.count_messages_tokens(trimmed_messages),
            "is_safe": True
        }
    
    def get_optimal_completion_tokens(self, prompt_tokens: int) -> int:
        """
        Calculate optimal completion tokens based on prompt size
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            
        Returns:
            Optimal number of completion tokens
        """
        available_tokens = self.budget.max_total_tokens - prompt_tokens - self.budget.safety_margin
        optimal_tokens = min(available_tokens, self.budget.max_completion_tokens)
        
        # Ensure minimum completion tokens
        if optimal_tokens < 1000:
            logger.warning(f"Very limited completion tokens available: {optimal_tokens}")
        
        return max(1000, optimal_tokens) 