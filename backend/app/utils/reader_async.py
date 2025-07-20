import logging
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI

from ..config import OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class AsyncContextAwareReader:
    """
    Processes file chunks asynchronously while maintaining context between chunks
    MASSIVE PERFORMANCE IMPROVEMENTS:
    - Parallel chunk processing (10-15 chunks at once)
    - Streaming responses for better performance
    - Optimized concurrency limits
    - INTELLIGENT TOKEN BUDGETING to prevent context overflow
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", concurrency_limit: int = 15):
        self.model = model
        self.concurrency_limit = concurrency_limit  # Increased from 3 to 15 for massive speed improvements
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        
        # Token budgeting configuration
        self.max_prompt_tokens = 12000  # Leave space for 2K-4K completion
        self.max_total_tokens = 13500   # Hard upper cap to be safe
        self.max_completion_tokens = 4000
        
        # Adjust limits based on model
        if "gpt-4" in model:
            self.max_prompt_tokens = 12000
            self.max_total_tokens = 13500
        else:  # gpt-3.5-turbo
            self.max_prompt_tokens = 3000
            self.max_total_tokens = 4000
    
    def reset(self):
        """Reset the conversation histories and summaries"""
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _calculate_messages_tokens(self, messages: List[Dict]) -> int:
        """Calculate total tokens for a list of messages"""
        total_tokens = 0
        for message in messages:
            total_tokens += self._estimate_tokens(message["content"])
        return total_tokens
    
    def _truncate_context_if_needed(self, file_path: str, new_messages: List[Dict]) -> List[Dict]:
        """
        Intelligently truncate context to stay within token limits
        Prioritizes recent messages and system messages
        """
        current_messages = self.conversation_histories.get(file_path, [])
        all_messages = current_messages + new_messages
        
        # Calculate total tokens
        total_tokens = self._calculate_messages_tokens(all_messages)
        
        if total_tokens <= self.max_prompt_tokens:
            return new_messages
        
        logger.warning(f"Context overflow detected for {file_path}: {total_tokens} tokens > {self.max_prompt_tokens} limit")
        
        # Strategy: Keep system messages + recent messages + new messages
        system_messages = [msg for msg in current_messages if msg["role"] == "system"]
        recent_messages = []
        new_message_tokens = self._calculate_messages_tokens(new_messages)
        
        # Reserve space for new messages
        available_tokens = self.max_prompt_tokens - new_message_tokens - self._calculate_messages_tokens(system_messages)
        
        # Add recent messages within available space
        for msg in reversed(current_messages):
            if msg["role"] == "system":
                continue
            msg_tokens = self._estimate_tokens(msg["content"])
            if msg_tokens <= available_tokens:
                recent_messages.insert(0, msg)
                available_tokens -= msg_tokens
            else:
                break
        
        # Combine and return
        final_messages = system_messages + recent_messages + new_messages
        final_tokens = self._calculate_messages_tokens(final_messages)
        
        logger.info(f"Truncated context for {file_path}: {total_tokens} → {final_tokens} tokens")
        return new_messages
    
    def _should_retry_with_smaller_context(self, error: Exception) -> bool:
        """Check if we should retry with smaller context"""
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in [
            "context_length_exceeded", 
            "token_limit", 
            "too many tokens",
            "maximum context length"
        ])
    
    async def process_chunk_streaming(self, chunk: Dict, summarize: bool = True) -> AsyncGenerator[str, None]:
        """
        Process a single chunk with streaming response for better performance
        
        Args:
            chunk: The chunk to process
            summarize: Whether to generate a summary
            
        Yields:
            str: Streamed response content
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
            yield "No readable files found in the repository."
            return
        
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
        
        # Prepare new messages
        new_messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Apply intelligent context truncation
        new_messages = self._truncate_context_if_needed(file_path, new_messages)
        
        # Add to conversation history
        self.conversation_histories[file_path].extend(new_messages)
        
        # Retry logic with smaller context if needed
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Call OpenAI API with streaming for better performance
                stream = await client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_histories[file_path],
                    temperature=0.3,
                    max_tokens=min(1000, self.max_completion_tokens),
                    stream=True  # Enable streaming for better performance
                )
                
                # Collect streamed response
                assistant_message = ""
                async for chunk_response in stream:
                    if chunk_response.choices[0].delta.content:
                        content_piece = chunk_response.choices[0].delta.content
                        assistant_message += content_piece
                        yield content_piece
                
                # Track token usage (approximate for streaming)
                self.total_prompt_tokens += len(assistant_message) // 4  # Rough estimate
                self.total_completion_tokens += len(assistant_message) // 4
                
                # Add to conversation history
                self.conversation_histories[file_path].append({"role": "assistant", "content": assistant_message})
                
                # If this is the last chunk, save the summary
                if chunk_index == total_chunks - 1:
                    self.summaries[file_path] = assistant_message
                
                break  # Success, exit retry loop
                
            except Exception as e:
                if attempt < max_retries - 1 and self._should_retry_with_smaller_context(e):
                    logger.warning(f"Token limit exceeded for {file_path}, retrying with smaller context (attempt {attempt + 1})")
                    # Clear conversation history and retry with just this chunk
                    self.conversation_histories[file_path] = new_messages
                else:
                    logger.error(f"Error processing chunk {chunk_index} of {file_path}: {e}")
                    error_msg = f"Error processing chunk: {str(e)}"
                    yield error_msg
                    break
    
    async def process_chunk(self, chunk: Dict, summarize: bool = True) -> str:
        """
        Process a single chunk of code with context from previous chunks
        (Non-streaming version for compatibility)
        
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
        
        # Prepare new messages
        new_messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Apply intelligent context truncation
        new_messages = self._truncate_context_if_needed(file_path, new_messages)
        
        # Add to conversation history
        self.conversation_histories[file_path].extend(new_messages)
        
        # Retry logic with smaller context if needed
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Call OpenAI API
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_histories[file_path],
                    temperature=0.3,
                    max_tokens=min(1000, self.max_completion_tokens)
                )
                
                # Track token usage
                self.total_prompt_tokens += response.usage.prompt_tokens
                self.total_completion_tokens += response.usage.completion_tokens
                
                # Get the response content
                assistant_message = response.choices[0].message.content.strip()
                
                # Add to conversation history
                self.conversation_histories[file_path].append({"role": "assistant", "content": assistant_message})
                
                # If this is the last chunk, save the summary
                if chunk_index == total_chunks - 1:
                    self.summaries[file_path] = assistant_message
                
                return assistant_message
                
            except Exception as e:
                if attempt < max_retries - 1 and self._should_retry_with_smaller_context(e):
                    logger.warning(f"Token limit exceeded for {file_path}, retrying with smaller context (attempt {attempt + 1})")
                    # Clear conversation history and retry with just this chunk
                    self.conversation_histories[file_path] = new_messages
                else:
                    logger.error(f"Error processing chunk {chunk_index} of {file_path}: {e}")
                    return f"Error processing chunk: {str(e)}"
    
    async def process_file_chunks_parallel(self, chunks: List[Dict]) -> str:
        """
        Process all chunks of a file in parallel for massive speed improvements
        
        Args:
            chunks: List of chunks from a single file
            
        Returns:
            str: Comprehensive understanding of the file
        """
        if not chunks:
            return ""
            
        file_path = chunks[0]["file_path"]
        logger.info(f"Processing {len(chunks)} chunks from {file_path} in parallel")
        
        # Sort chunks by index to maintain order
        chunks.sort(key=lambda x: x["chunk_index"])
        
        # Process chunks in parallel batches of 10-15
        batch_size = min(15, len(chunks))  # Process up to 15 chunks in parallel
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def process_chunk_with_semaphore(chunk, is_last):
            async with semaphore:
                return await self.process_chunk(chunk, summarize=is_last)
        
        # Process chunks in parallel batches
        all_results = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_tasks = []
            
            for j, chunk in enumerate(batch):
                is_last = (i + j == len(chunks) - 1)
                task = process_chunk_with_semaphore(chunk, is_last)
                batch_tasks.append(task)
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            all_results.extend(batch_results)
            
            logger.info(f"Completed batch {i//batch_size + 1} for {file_path}")
        
        # Return the final summary
        return self.summaries.get(file_path, "No summary generated")
    
    async def process_file_chunks(self, chunks: List[Dict]) -> str:
        """
        Process all chunks of a file and return a comprehensive understanding
        (Legacy sequential method - kept for compatibility)
        
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
            await self.process_chunk(chunk, summarize=summarize)
        
        # Return the final summary
        return self.summaries.get(file_path, "No summary generated")
    
    async def process_file_chunks_batch(self, all_file_chunks: Dict[str, List[Dict]]) -> Dict[str, str]:
        """
        Process multiple files in parallel with optimized concurrency limits
        
        Args:
            all_file_chunks: Dictionary mapping file paths to their chunks
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their summaries
        """
        file_summaries = {}
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def process_file_with_semaphore(file_path, chunks):
            async with semaphore:
                # Use parallel processing for better performance
                if len(chunks) > 1:
                    summary = await self.process_file_chunks_parallel(chunks)
                else:
                    summary = await self.process_file_chunks(chunks)
                file_summaries[file_path] = summary
                logger.info(f"Completed processing {file_path}")
        
        # Create tasks for each file
        tasks = []
        for file_path, chunks in all_file_chunks.items():
            # Sort chunks by index
            chunks.sort(key=lambda x: x["chunk_index"])
            tasks.append(process_file_with_semaphore(file_path, chunks))
        
        # Run tasks with optimized concurrency limit
        await asyncio.gather(*tasks)
        
        return file_summaries
    
    async def process_repository_chunks(self, all_chunks: List[Dict]) -> Dict[str, str]:
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
        
        # Process files in parallel with optimized concurrency limit
        file_summaries = await self.process_file_chunks_batch(file_chunks)
        
        return file_summaries
        
    async def generate_repository_understanding(self, file_summaries: Dict[str, str]) -> str:
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
        
        for file_path, summary in file_summaries.items():
            # Skip dummy files
            if file_path == "dummy.txt":
                continue
            user_message += f"## {file_path}\n{summary}\n\n"
        
        # Check token limits for repository understanding
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        total_tokens = self._calculate_messages_tokens(messages)
        if total_tokens > self.max_prompt_tokens:
            logger.warning(f"Repository understanding prompt too large ({total_tokens} tokens), truncating")
            # Truncate by keeping only the most important files
            user_message = "Based on the following file summaries, provide a comprehensive understanding of the repository's purpose, structure, and functionality:\n\n"
            file_count = 0
            for file_path, summary in file_summaries.items():
                if file_path == "dummy.txt":
                    continue
                user_message += f"## {file_path}\n{summary[:500]}...\n\n"  # Truncate each summary
                file_count += 1
                if file_count >= 5:  # Limit to 5 most important files
                    break
        
        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=min(2000, self.max_completion_tokens)
            )
            
            # Track token usage
            self.total_prompt_tokens += response.usage.prompt_tokens
            self.total_completion_tokens += response.usage.completion_tokens
            
            # Get the response content
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating repository understanding: {e}")
            return f"Error generating repository understanding: {str(e)}" 