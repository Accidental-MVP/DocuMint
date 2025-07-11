import os
import logging
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileChunker:
    """
    Chunks large files into smaller pieces for processing
    """
    
    def __init__(self, max_chunk_size: int = 4000, overlap: int = 200):
        """
        Initialize the FileChunker
        
        Args:
            max_chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_file(self, file_path: str, file_content: Optional[str] = None) -> List[Dict]:
        """
        Split a file into chunks
        
        Args:
            file_path: Path to the file
            file_content: Optional pre-loaded file content
            
        Returns:
            List[Dict]: List of chunks with metadata
        """
        # Read file if content not provided
        if file_content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return []
        
        # Skip empty files
        if not file_content.strip():
            return []
        
        # For very small files, just return a single chunk
        if len(file_content) <= self.max_chunk_size:
            return [{
                "file_path": os.path.basename(file_path),
                "chunk_index": 0,
                "total_chunks": 1,
                "start_line": 1,
                "end_line": file_content.count('\n') + 1,
                "content": file_content
            }]
        
        # For larger files, split into chunks
        chunks = []
        lines = file_content.split('\n')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        start_line = 1
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for the newline
            
            # If adding this line would exceed the chunk size and we already have content,
            # save the current chunk and start a new one
            if current_size + line_size > self.max_chunk_size and current_chunk:
                # Join the current chunk into a string
                chunk_content = '\n'.join(current_chunk)
                
                # Calculate end line
                end_line = start_line + len(current_chunk) - 1
                
                # Save the chunk
                chunks.append({
                    "file_path": os.path.basename(file_path),
                    "chunk_index": chunk_index,
                    "total_chunks": 0,  # Will be updated later
                    "start_line": start_line,
                    "end_line": end_line,
                    "content": chunk_content
                })
                
                # Start a new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.get_line_overlap(current_chunk))
                current_chunk = current_chunk[overlap_start:]
                current_size = sum(len(l) + 1 for l in current_chunk)
                
                # Update for next chunk
                chunk_index += 1
                start_line = end_line - len(current_chunk) + 1
            
            # Add the current line to the chunk
            current_chunk.append(line)
            current_size += line_size
        
        # Don't forget the last chunk
        if current_chunk:
            end_line = start_line + len(current_chunk) - 1
            chunks.append({
                "file_path": os.path.basename(file_path),
                "chunk_index": chunk_index,
                "total_chunks": 0,  # Will be updated later
                "start_line": start_line,
                "end_line": end_line,
                "content": '\n'.join(current_chunk)
            })
        
        # Update total_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk["total_chunks"] = total_chunks
        
        return chunks
    
    def get_line_overlap(self, lines: List[str]) -> int:
        """
        Calculate how many lines to overlap based on content
        
        Args:
            lines: List of lines in the current chunk
            
        Returns:
            int: Number of lines to overlap
        """
        # Target overlap in characters
        target_overlap = self.overlap
        
        # Count backwards until we reach the target overlap
        overlap_size = 0
        overlap_lines = 0
        
        for line in reversed(lines):
            line_size = len(line) + 1  # +1 for newline
            if overlap_size + line_size > target_overlap * 2:  # Allow up to 2x the target for complete context
                break
                
            overlap_size += line_size
            overlap_lines += 1
            
            # Stop if we've reached a reasonable minimum
            if overlap_lines >= 5 and overlap_size >= target_overlap:
                break
        
        # Ensure we have at least 2 lines of overlap for context
        return max(2, overlap_lines)

def chunk_repository_files(repo_path: str, file_paths: List[str], max_chunk_size: int = 4000) -> List[Dict]:
    """
    Chunk multiple files from a repository
    
    Args:
        repo_path: Path to the repository
        file_paths: List of file paths to chunk (relative to repo_path)
        max_chunk_size: Maximum size of each chunk in characters
        
    Returns:
        List[Dict]: List of chunks with metadata
    """
    chunker = FileChunker(max_chunk_size=max_chunk_size)
    all_chunks = []
    
    # Adjust chunk size based on number of files
    # More files = smaller chunks to fit within token limits
    if len(file_paths) > 10:
        max_chunk_size = 3000
    elif len(file_paths) > 5:
        max_chunk_size = 3500
    
    for file_path in file_paths:
        full_path = os.path.join(repo_path, file_path)
        
        try:
            chunks = chunker.chunk_file(full_path)
            
            # Update file_path to include the relative path within the repo
            for chunk in chunks:
                chunk["file_path"] = file_path
                
            all_chunks.extend(chunks)
            logger.info(f"Successfully chunked {file_path} into {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error chunking file {file_path}: {e}")
    
    # If no chunks were created, add a dummy chunk
    if not all_chunks:
        all_chunks.append({
            "file_path": "dummy.txt",
            "chunk_index": 0,
            "total_chunks": 1,
            "start_line": 1,
            "end_line": 1,
            "content": "No readable files found in the repository."
        })
    
    logger.info(f"Processed {len(file_paths)} files into {len(all_chunks)} chunks")
    return all_chunks 