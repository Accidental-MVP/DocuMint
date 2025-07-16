import logging
from typing import List, Dict, Any
from openai import OpenAI

from ..config import OPENAI_API_KEY
from ..models.token_usage import TokenUsage, add_token_usage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Constants for context management
MAX_CONTEXT_CHUNKS = 5  # Increased from 3 to take advantage of larger context window
MAX_CONTEXT_TOKENS = 32000  # Increased from 14000 to take advantage of larger context window

class ContextAwareReader:
    """
    Processes file chunks while maintaining context between chunks
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", token_usage = None):
        self.model = model
        self.token_usage = token_usage
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.chunk_errors = []
    
    def reset(self):
        """Reset the conversation histories and summaries"""
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.chunk_errors = []
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _manage_context_window(self, file_path: str, new_messages: List[Dict[str, str]]) -> None:
        """
        Manage the context window to prevent exceeding token limits
        
        Args:
            file_path: Path to the file
            new_messages: New messages to add to the conversation
        """
        history = self.conversation_histories[file_path]
        
        # Add new messages
        history.extend(new_messages)
        
        # Estimate current token count
        estimated_tokens = sum(self._estimate_tokens(msg["content"]) for msg in history)
        
        # If we're approaching the limit, trim the context
        if estimated_tokens > MAX_CONTEXT_TOKENS:
            logger.info(f"Context window for {file_path} approaching limit ({estimated_tokens} tokens). Trimming...")
            
            # Always keep system messages and the most recent user/assistant pairs
            system_messages = [msg for msg in history if msg["role"] == "system"]
            
            # Group user and assistant messages into pairs (chunks)
            chunks = []
            current_chunk = []
            
            for msg in history:
                if msg["role"] == "system":
                    continue
                    
                current_chunk.append(msg)
                if len(current_chunk) == 2:  # User + assistant pair
                    chunks.append(current_chunk)
                    current_chunk = []
            
            # Add any remaining messages
            if current_chunk:
                chunks.append(current_chunk)
            
            # Keep only the most recent chunks
            recent_chunks = chunks[-MAX_CONTEXT_CHUNKS:] if len(chunks) > MAX_CONTEXT_CHUNKS else chunks
            
            # Flatten the chunks back into a list
            recent_messages = []
            for chunk in recent_chunks:
                recent_messages.extend(chunk)
            
            # Update the history with system messages + recent messages
            self.conversation_histories[file_path] = system_messages + recent_messages
            
            # Log the trimming
            new_count = sum(self._estimate_tokens(msg["content"]) for msg in self.conversation_histories[file_path])
            logger.info(f"Trimmed context window for {file_path} from {estimated_tokens} to ~{new_count} tokens")
    
    def process_chunk(self, chunk: Dict, summarize: bool = True) -> str:
        """
        Process a single chunk of code with context from previous chunks
        
        Args:
            chunk: The chunk to process
            summarize: Whether to generate a summary
            
        Returns:
            str: The summary or understanding of the chunk
        """
        file_path = chunk["file_path"]
        chunk_index = chunk["chunk_index"]
        total_chunks = chunk["total_chunks"]
        content = chunk["content"]
        
        # Initialize conversation history for this file if it doesn't exist
        if file_path not in self.conversation_histories:
            self.conversation_histories[file_path] = []
        
        # Check if this is a dummy chunk
        if file_path == "dummy.txt" and content == "No readable files found in the repository.":
            logger.warning("Processing dummy chunk for empty repository")
            return "No readable files found in the repository."
        
        # Build prompt based on chunk position and history
        if chunk_index == 0:
            # First chunk of the file
            system_message = f"""You are analyzing code from the file {file_path}. 
This is chunk {chunk_index + 1} of {total_chunks}.
Understand the code structure and purpose."""
            
            user_message = f"""Here is the beginning of the file {file_path} (lines {chunk['start_line']}-{chunk['end_line']}):

```
{content}
```

Please understand this code. If this is the only chunk, provide a comprehensive summary of the file's purpose and structure."""
            
        else:
            # Subsequent chunk of the file
            system_message = f"""You are continuing to analyze code from the file {file_path}.
This is chunk {chunk_index + 1} of {total_chunks}.
You have already seen the previous part(s) of this file."""
            
            user_message = f"""Here is the next part of the file {file_path} (lines {chunk['start_line']}-{chunk['end_line']}):

```
{content}
```

Continue building your understanding of this file based on what you've seen so far."""
        
        # If this is the last chunk and we want a summary
        if chunk_index == total_chunks - 1 and summarize:
            user_message += "\n\nThis is the last chunk of the file. Please provide a comprehensive summary of the entire file's purpose, structure, and key functionality."
        
        # Create new messages to add
        new_messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Manage context window before adding new messages
        self._manage_context_window(file_path, new_messages)
        
        try:
            # Determine appropriate max_tokens based on model
            max_tokens = 1000
            if self.model == "gpt-4-1106-preview":
                # Cap max_tokens for GPT-4 Turbo
                max_tokens = 4000
                
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=self.conversation_histories[file_path],
                temperature=0.3,
                max_tokens=max_tokens
            )
            
            # Track token usage
            self.total_prompt_tokens += response.usage.prompt_tokens
            self.total_completion_tokens += response.usage.completion_tokens
            
            # Update token usage if provided
            if self.token_usage:
                add_token_usage(self.token_usage, {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.prompt_tokens + response.usage.completion_tokens
                })
            
            # Get the response content
            assistant_message = response.choices[0].message.content.strip()
            
            # Add to conversation history
            self.conversation_histories[file_path].append({"role": "assistant", "content": assistant_message})
            
            # If this is the last chunk, save the summary
            if chunk_index == total_chunks - 1:
                self.summaries[file_path] = assistant_message
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index} of {file_path}: {e}")
            # Record the error
            self.chunk_errors.append({
                "file_path": file_path,
                "chunk_index": chunk_index,
                "error": str(e)
            })
            
            # For the last chunk, ensure we have at least some summary
            if chunk_index == total_chunks - 1:
                if file_path not in self.summaries:
                    # Create a simple summary from what we've seen so far
                    self.summaries[file_path] = f"Error processing final chunk: {str(e)}. Partial understanding available from previous chunks."
            
            return f"Error processing chunk: {str(e)}"
    
    def process_file_chunks(self, chunks: List[Dict]) -> str:
        """
        Process all chunks of a file and return a comprehensive understanding
        
        Args:
            chunks: List of chunks from a single file
            
        Returns:
            str: Comprehensive understanding of the file
        """
        if not chunks:
            return ""
            
        file_path = chunks[0]["file_path"]
        logger.info(f"Processing {len(chunks)} chunks from {file_path}")
        
        # Process each chunk sequentially to maintain context
        for i, chunk in enumerate(chunks):
            # Only generate a summary for the last chunk
            summarize = (i == len(chunks) - 1)
            self.process_chunk(chunk, summarize=summarize)
        
        # Return the final summary
        return self.summaries.get(file_path, "No summary generated")
    
    def process_repository_chunks(self, all_chunks: List[Dict]) -> Dict[str, str]:
        """
        Process all chunks from a repository and generate file summaries
        
        Args:
            all_chunks: List of chunks from all files
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their summaries
        """
        # Check if we have any chunks
        if not all_chunks:
            logger.warning("No chunks to process")
            return {"dummy.txt": "No files were found in the repository."}
        
        # Check if we only have a dummy chunk
        if len(all_chunks) == 1 and all_chunks[0]["file_path"] == "dummy.txt":
            logger.warning("Only dummy chunk found")
            return {"dummy.txt": "No readable files were found in the repository."}
        
        # Group chunks by file path
        file_chunks = {}
        for chunk in all_chunks:
            file_path = chunk["file_path"]
            if file_path not in file_chunks:
                file_chunks[file_path] = []
            file_chunks[file_path].append(chunk)
        
        # Process files sequentially
        file_summaries = {}
        for file_path, chunks in file_chunks.items():
            # Sort chunks by index
            chunks.sort(key=lambda x: x["chunk_index"])
            # Process the file
            file_summaries[file_path] = self.process_file_chunks(chunks)
        
        return file_summaries
    
    def generate_repository_understanding(self, file_summaries: Dict[str, str]) -> str:
        """
        Generate a comprehensive understanding of the repository based on file summaries
        
        Args:
            file_summaries: Dictionary mapping file paths to their summaries
            
        Returns:
            str: Comprehensive understanding of the repository
        """
        if not file_summaries:
            return "No files analyzed in the repository."
        
        # Check if we only have a dummy file
        if len(file_summaries) == 1 and "dummy.txt" in file_summaries:
            return "No readable files were found in the repository. Unable to generate a comprehensive understanding."
        
        # Build prompt for repository understanding
        system_message = "You are analyzing a GitHub repository based on summaries of its key files."
        
        user_message = "Based on the following file summaries, provide a comprehensive understanding of the repository's purpose, structure, and functionality:\n\n"
        
        # Add error notice if any chunks failed
        if self.chunk_errors:
            user_message += "⚠️ Note: Some file chunks could not be fully processed due to size limitations. The analysis below is based on the available content.\n\n"
        
        for file_path, summary in file_summaries.items():
            # Skip dummy files
            if file_path == "dummy.txt":
                continue
            user_message += f"## {file_path}\n{summary}\n\n"
        
        try:
            # Determine appropriate max_tokens based on model
            max_tokens = 2000
            if self.model == "gpt-4-1106-preview":
                # Cap max_tokens for GPT-4 Turbo
                max_tokens = 4000
                
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            
            # Track token usage
            self.total_prompt_tokens += response.usage.prompt_tokens
            self.total_completion_tokens += response.usage.completion_tokens
            
            # Get the response content
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating repository understanding: {e}")
            return f"Error generating repository understanding: {str(e)}"
    
    def get_processing_metadata(self) -> Dict:
        """
        Get metadata about the processing
        
        Returns:
            Dict: Processing metadata
        """
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "chunk_errors": len(self.chunk_errors),
            "error_details": self.chunk_errors if self.chunk_errors else None
        } 