import logging
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI

from ..config import OPENAI_API_KEY
from .token_budget import ProactiveTokenCalculator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class AsyncContextAwareReader:
    """
    Processes file chunks asynchronously while maintaining context between chunks
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", concurrency_limit: int = 15):
        self.model = model
        self.concurrency_limit = concurrency_limit  # Increased from 3 to 15 for massive speed improvements
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        
        # Initialize proactive token calculator
        self.token_calculator = ProactiveTokenCalculator(model)
    
    def reset(self):
        """Reset the conversation histories and summaries"""
        self.conversation_histories = {}
        self.summaries = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
    
    async def process_chunk(self, chunk: Dict, summarize: bool = True) -> str:
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
        
        # Add to conversation history
        self.conversation_histories[file_path].append({"role": "system", "content": system_message})
        self.conversation_histories[file_path].append({"role": "user", "content": user_message})
        
        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=self.model,
                messages=self.conversation_histories[file_path],
                temperature=0.3,
                max_tokens=1000
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
            logger.error(f"Error processing chunk {chunk_index} of {file_path}: {e}")
            return f"Error processing chunk: {str(e)}"
    
    async def process_file_chunks(self, chunks: List[Dict]) -> str:
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
            await self.process_chunk(chunk, summarize=summarize)
        
        # Return the final summary
        return self.summaries.get(file_path, "No summary generated")
    
    async def process_file_chunks_batch(self, all_file_chunks: Dict[str, List[Dict]]) -> Dict[str, str]:
        """
        Process multiple files in parallel with a concurrency limit
        
        Args:
            all_file_chunks: Dictionary mapping file paths to their chunks
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their summaries
        """
        file_summaries = {}
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def process_file_with_semaphore(file_path, chunks):
            async with semaphore:
                summary = await self.process_file_chunks(chunks)
                file_summaries[file_path] = summary
                logger.info(f"Completed processing {file_path}")
        
        # Create tasks for each file
        tasks = []
        for file_path, chunks in all_file_chunks.items():
            # Sort chunks by index
            chunks.sort(key=lambda x: x["chunk_index"])
            tasks.append(process_file_with_semaphore(file_path, chunks))
        
        # Run tasks with concurrency limit
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
        
        # Process files in parallel with concurrency limit
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
        
        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Track token usage
            self.total_prompt_tokens += response.usage.prompt_tokens
            self.total_completion_tokens += response.usage.completion_tokens
            
            # Get the response content
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating repository understanding: {e}")
            return f"Error generating repository understanding: {str(e)}" 