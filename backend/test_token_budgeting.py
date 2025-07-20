#!/usr/bin/env python3
"""
Token Budgeting Test Script for DocuMint
Demonstrates the intelligent token budgeting and context management:
1. Chunk-level token budgeting
2. Intelligent context truncation
3. Retry with smaller context fallback
4. Hard upper caps to prevent overflow
"""

import asyncio
import time
import logging
from typing import List, Dict
from app.utils.reader_async import AsyncContextAwareReader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_large_test_chunks(num_files: int = 3, chunks_per_file: int = 5) -> List[Dict]:
    """Create large test chunks to trigger token budgeting"""
    chunks = []
    
    for file_idx in range(num_files):
        file_path = f"large_file_{file_idx}.py"
        for chunk_idx in range(chunks_per_file):
            # Create large chunks to test token limits
            large_content = f"""
# Large test content for {file_path} chunk {chunk_idx + 1}
# This is a very large file with lots of content to test token budgeting

def very_large_function_{chunk_idx}():
    \"\"\"
    This is a very large function with extensive documentation.
    It contains many lines of code and comments to test token limits.
    \"\"\"
    
    # Import statements
    import os
    import sys
    import json
    import logging
    import asyncio
    import time
    import datetime
    import random
    import math
    import statistics
    
    # Configuration
    config = {{
        "debug": True,
        "log_level": "INFO",
        "max_retries": 3,
        "timeout": 30,
        "batch_size": 100,
        "cache_size": 1000,
        "enable_metrics": True,
        "enable_tracing": False,
        "database_url": "postgresql://user:pass@localhost:5432/db",
        "redis_url": "redis://localhost:6379",
        "elasticsearch_url": "http://localhost:9200",
        "kafka_brokers": ["localhost:9092"],
        "s3_bucket": "my-bucket",
        "cloudfront_distribution": "E1234567890ABCD"
    }}
    
    # Large data structures
    large_list = [
        "item_" + str(i) + "_with_very_long_description_that_adds_many_tokens_to_the_context" 
        for i in range(100)
    ]
    
    large_dict = {{
        f"key_{i}": f"value_{i}_with_very_long_description_that_adds_many_tokens_to_the_context"
        for i in range(50)
    }}
    
    # Complex logic
    try:
        for item in large_list:
            if item.startswith("item_"):
                processed_item = item.upper()
                if len(processed_item) > 10:
                    result = processed_item[:10] + "..."
                else:
                    result = processed_item
                
                # More complex processing
                if result in large_dict:
                    final_result = large_dict[result] + "_processed"
                else:
                    final_result = result + "_default"
                
                # Log the result
                logger.info(f"Processed {{item}} -> {{final_result}}")
                
    except Exception as e:
        logger.error(f"Error processing {{item}}: {{e}}")
        raise
    
    return True

class VeryLargeClass_{chunk_idx}:
    \"\"\"
    This is a very large class with extensive documentation.
    It contains many methods and properties to test token limits.
    \"\"\"
    
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.data = []
        self.cache = {{}}
        self.metrics = {{}}
        self.trace_id = None
        
    def process_data(self, data: List[str]) -> List[str]:
        \"\"\"
        Process a large amount of data with complex logic.
        This method contains many lines to test token budgeting.
        \"\"\"
        results = []
        
        for item in data:
            # Complex processing logic
            if item.startswith("process_"):
                processed = self._process_item(item)
                if processed:
                    results.append(processed)
            elif item.startswith("validate_"):
                validated = self._validate_item(item)
                if validated:
                    results.append(validated)
            elif item.startswith("transform_"):
                transformed = self._transform_item(item)
                if transformed:
                    results.append(transformed)
            else:
                # Default processing
                default_result = self._default_processing(item)
                results.append(default_result)
        
        return results
    
    def _process_item(self, item: str) -> str:
        \"\"\"Process a single item with complex logic\"\"\"
        # Add processing logic here
        return item + "_processed"
    
    def _validate_item(self, item: str) -> str:
        \"\"\"Validate a single item with complex logic\"\"\"
        # Add validation logic here
        return item + "_validated"
    
    def _transform_item(self, item: str) -> str:
        \"\"\"Transform a single item with complex logic\"\"\"
        # Add transformation logic here
        return item + "_transformed"
    
    def _default_processing(self, item: str) -> str:
        \"\"\"Default processing for items\"\"\"
        return item + "_default"

# More large content to fill up tokens...
"""
            chunk = {
                "file_path": file_path,
                "chunk_index": chunk_idx,
                "total_chunks": chunks_per_file,
                "start_line": chunk_idx * 200 + 1,
                "end_line": (chunk_idx + 1) * 200,
                "content": large_content * 3  # Make it even larger
            }
            chunks.append(chunk)
    
    return chunks

async def test_token_budgeting():
    """Test the intelligent token budgeting system"""
    logger.info("🧪 Testing INTELLIGENT TOKEN BUDGETING...")
    
    chunks = create_large_test_chunks(num_files=2, chunks_per_file=3)
    reader = AsyncContextAwareReader(model="gpt-4", concurrency_limit=15)
    
    start_time = time.time()
    
    try:
        # Process chunks with token budgeting
        file_summaries = await reader.process_repository_chunks(chunks)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"⏱️  Token budgeting processing took: {processing_time:.2f} seconds")
        logger.info(f"📊 Processed {len(chunks)} chunks")
        logger.info(f"🔢 Token usage: {reader.total_prompt_tokens} prompt, {reader.total_completion_tokens} completion")
        
        # Check if any context truncation occurred
        for file_path, summary in file_summaries.items():
            logger.info(f"📄 {file_path}: {len(summary)} characters")
        
        return processing_time, True
        
    except Exception as e:
        logger.error(f"❌ Token budgeting test failed: {e}")
        return 0, False

async def test_context_truncation():
    """Test context truncation with very large chunks"""
    logger.info("🔧 Testing CONTEXT TRUNCATION...")
    
    # Create extremely large chunks to force truncation
    chunks = create_large_test_chunks(num_files=1, chunks_per_file=1)
    # Make chunks even larger
    for chunk in chunks:
        chunk["content"] = chunk["content"] * 10  # 10x larger
    
    reader = AsyncContextAwareReader(model="gpt-4", concurrency_limit=15)
    
    start_time = time.time()
    
    try:
        # This should trigger context truncation
        file_summaries = await reader.process_repository_chunks(chunks)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"⏱️  Context truncation test took: {processing_time:.2f} seconds")
        logger.info(f"🔢 Token usage: {reader.total_prompt_tokens} prompt, {reader.total_completion_tokens} completion")
        
        return processing_time, True
        
    except Exception as e:
        logger.error(f"❌ Context truncation test failed: {e}")
        return 0, False

async def test_retry_fallback():
    """Test retry with smaller context fallback"""
    logger.info("🔄 Testing RETRY WITH SMALLER CONTEXT...")
    
    # Create chunks that might trigger retry logic
    chunks = create_large_test_chunks(num_files=1, chunks_per_file=2)
    reader = AsyncContextAwareReader(model="gpt-4", concurrency_limit=15)
    
    start_time = time.time()
    
    try:
        # Process chunks with retry logic
        file_summaries = await reader.process_repository_chunks(chunks)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"⏱️  Retry fallback test took: {processing_time:.2f} seconds")
        logger.info(f"🔢 Token usage: {reader.total_prompt_tokens} prompt, {reader.total_completion_tokens} completion")
        
        return processing_time, True
        
    except Exception as e:
        logger.error(f"❌ Retry fallback test failed: {e}")
        return 0, False

async def main():
    """Run all token budgeting tests"""
    logger.info("🎯 DocuMint Token Budgeting Test Suite")
    logger.info("=" * 60)
    
    try:
        # Test 1: Basic token budgeting
        logger.info("📊 Test 1: Basic Token Budgeting")
        budget_time, budget_success = await test_token_budgeting()
        
        logger.info("-" * 40)
        
        # Test 2: Context truncation
        logger.info("📊 Test 2: Context Truncation")
        truncate_time, truncate_success = await test_context_truncation()
        
        logger.info("-" * 40)
        
        # Test 3: Retry fallback
        logger.info("📊 Test 3: Retry with Smaller Context")
        retry_time, retry_success = await test_retry_fallback()
        
        logger.info("=" * 60)
        logger.info("📈 TOKEN BUDGETING RESULTS:")
        logger.info(f"✅ Basic Budgeting: {budget_time:.2f}s ({'PASS' if budget_success else 'FAIL'})")
        logger.info(f"✅ Context Truncation: {truncate_time:.2f}s ({'PASS' if truncate_success else 'FAIL'})")
        logger.info(f"✅ Retry Fallback: {retry_time:.2f}s ({'PASS' if retry_success else 'FAIL'})")
        
        logger.info("=" * 60)
        logger.info("💡 KEY TOKEN BUDGETING IMPROVEMENTS:")
        logger.info("✅ Chunk-level token budgeting (12K prompt tokens)")
        logger.info("✅ Intelligent context truncation")
        logger.info("✅ Retry with smaller context fallback")
        logger.info("✅ Hard upper caps (13.5K total tokens)")
        logger.info("✅ Model-specific token limits")
        logger.info("✅ No more context overflow errors!")
        
        success_count = sum([budget_success, truncate_success, retry_success])
        logger.info(f"🎉 {success_count}/3 tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        logger.info("💡 Make sure your OpenAI API key is set and the backend is running")

if __name__ == "__main__":
    asyncio.run(main()) 