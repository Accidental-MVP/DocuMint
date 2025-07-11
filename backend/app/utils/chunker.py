import os
import logging
from typing import List, Dict, Tuple, Generator

# Set up logging
logger = logging.getLogger(__name__)

class FileChunker:
    """
    Handles breaking large files into manageable chunks for LLM processing
    """
    
    def __init__(self, 
                 chunk_size: int = 250,  # Lines per chunk
                 overlap: int = 20,      # Lines of overlap between chunks
                 max_file_size: int = 5000):  # Maximum file size in lines
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_file_size = max_file_size
    
    def should_chunk_file(self, content: str) -> bool:
        """
        Determine if a file needs to be chunked based on its size
        
        Args:
            content: File content
            
        Returns:
            bool: True if file should be chunked
        """
        line_count = content.count('\n') + 1
        return line_count > self.chunk_size
    
    def chunk_content(self, content: str, file_path: str) -> List[Dict]:
        """
        Break file content into overlapping chunks
        
        Args:
            content: File content
            file_path: Path to the file (for reference)
            
        Returns:
            List[Dict]: List of chunks with metadata
        """
        lines = content.split('\n')
        
        # Skip if file is too large to process
        if len(lines) > self.max_file_size:
            logger.warning(f"File {file_path} exceeds max size ({len(lines)} lines). Truncating.")
            lines = lines[:self.max_file_size]
            
        chunks = []
        
        # If file is small enough, return as a single chunk
        if len(lines) <= self.chunk_size:
            chunks.append({
                "content": content,
                "start_line": 1,
                "end_line": len(lines),
                "chunk_index": 0,
                "total_chunks": 1,
                "file_path": file_path
            })
            return chunks
        
        # Break into chunks with overlap
        for i in range(0, len(lines), self.chunk_size - self.overlap):
            # Make sure we don't go beyond the end of the file
            end_idx = min(i + self.chunk_size, len(lines))
            
            # Extract chunk content
            chunk_content = '\n'.join(lines[i:end_idx])
            
            # Add metadata
            chunk_index = len(chunks)
            total_chunks = (len(lines) - 1) // (self.chunk_size - self.overlap) + 1
            
            chunks.append({
                "content": chunk_content,
                "start_line": i + 1,  # 1-indexed line numbers
                "end_line": end_idx,
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "file_path": file_path
            })
            
            # If we've reached the end of the file, break
            if end_idx == len(lines):
                break
                
        return chunks
    
    def chunk_file(self, file_path: str) -> List[Dict]:
        """
        Read a file and break it into chunks
        
        Args:
            file_path: Path to the file
            
        Returns:
            List[Dict]: List of chunks with metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.chunk_content(content, file_path)
        except UnicodeDecodeError:
            try:
                # Try with a different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return self.chunk_content(content, file_path)
            except Exception as e:
                logger.warning(f"Could not read file {file_path} with latin-1 encoding: {e}")
                return []
        except Exception as e:
            logger.warning(f"Error chunking file {file_path}: {e}")
            return []
    
    def chunk_files(self, file_paths: List[str]) -> Dict[str, List[Dict]]:
        """
        Process multiple files and chunk them if needed
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dict[str, List[Dict]]: Dictionary mapping file paths to their chunks
        """
        result = {}
        
        for file_path in file_paths:
            chunks = self.chunk_file(file_path)
            if chunks:
                result[file_path] = chunks
                
        return result


def chunk_repository_files(repo_path: str, important_files: List[str], 
                          chunk_size: int = 250, overlap: int = 20) -> List[Dict]:
    """
    Process important files in a repository and chunk them for LLM processing
    
    Args:
        repo_path: Path to the repository
        important_files: List of important file paths (relative to repo_path)
        chunk_size: Number of lines per chunk
        overlap: Number of lines of overlap between chunks
        
    Returns:
        List[Dict]: List of all chunks from all files
    """
    chunker = FileChunker(chunk_size=chunk_size, overlap=overlap)
    all_chunks = []
    
    # Check if we have any files to process
    if not important_files:
        logger.warning("No important files found in repository")
        return []
        
    # Process each file
    files_processed = 0
    for file_path in important_files:
        full_path = os.path.join(repo_path, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                chunks = chunker.chunk_file(full_path)
                if chunks:
                    all_chunks.extend(chunks)
                    files_processed += 1
                    logger.info(f"Successfully chunked {file_path} into {len(chunks)} chunks")
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {e}")
        else:
            logger.warning(f"File {file_path} not found in repository")
    
    logger.info(f"Processed {files_processed} files into {len(all_chunks)} chunks")
    
    # If we didn't process any files, create a dummy chunk
    if not all_chunks:
        logger.warning("No files were successfully chunked. Creating a dummy chunk.")
        all_chunks.append({
            "content": "No readable files found in the repository.",
            "start_line": 1,
            "end_line": 1,
            "chunk_index": 0,
            "total_chunks": 1,
            "file_path": "dummy.txt"
        })
    
    return all_chunks 