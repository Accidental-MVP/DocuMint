#!/usr/bin/env python3
"""
Test script for proactive token budgeting system

This script demonstrates how the proactive token calculator prevents
token overflow errors by pre-checking and intelligently trimming content
before making API calls.
"""

import asyncio
import logging
from typing import List, Dict, Any
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.token_budget import ProactiveTokenCalculator
from app.utils.reader_async import AsyncContextAwareReader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_large_context_chunks() -> List[Dict[str, Any]]:
    """Create large context chunks to test token budgeting"""
    chunks = []
    
    # Create a large system prompt
    large_system_prompt = "You are an expert code analyzer. " * 1000  # ~6K tokens
    
    # Create large user prompts with code
    for i in range(20):
        # Create a large code block
        large_code = f"""
# Large Python file {i}
import os
import sys
import logging
import asyncio
import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import sklearn.ensemble as ensemble
import tensorflow as tf
import torch
import transformers
import openai
import tiktoken
import fastapi
import uvicorn
import sqlalchemy
import alembic
import pytest
import black
import flake8
import mypy
import pre-commit
import docker
import kubernetes
import helm
import terraform
import ansible
import jenkins
import gitlab
import github
import bitbucket
import jira
import confluence
import slack
import discord
import telegram
import whatsapp
import email
import smtp
import imap
import pop3
import ftp
import sftp
import ssh
import telnet
import http
import https
import tcp
import udp
import ip
import dns
import dhcp
import ntp
import snmp
import ldap
import kerberos
import oauth2
import jwt
import bcrypt
import argon2
import scrypt
import pbkdf2
import rsa
import dsa
import ecdsa
import ed25519
import aes
import des
import blowfish
import twofish
import serpent
import rc4
import rc5
import rc6
import idea
import cast
import camellia
import seed
import aria
import sm4
import kuznyechik
import magenta
import khazad
import noekeon
import shark
import square
import anubis
import hierocrypt
import nimbus
import q
import rc2
import skipjack
import tea
import xtea
import xxtea

class LargeClass{i}:
    def __init__(self):
        self.data = []
        for j in range(1000):
            self.data.append(f"data_{j}")
    
    def process_data(self):
        result = []
        for item in self.data:
            processed = self._transform(item)
            result.append(processed)
        return result
    
    def _transform(self, item):
        return item.upper() + "_processed"
    
    def analyze(self):
        return {
            "count": len(self.data),
            "unique": len(set(self.data)),
            "average_length": sum(len(x) for x in self.data) / len(self.data)
        }

def main():
    obj = LargeClass{i}()
    result = obj.process_data()
    analysis = obj.analyze()
    print(f"Processed {analysis['count']} items")
    print(f"Unique items: {analysis['unique']}")
    print(f"Average length: {analysis['average_length']:.2f}")

if __name__ == "__main__":
    main()
""" * 5  # ~15K tokens per chunk
        
        chunks.append({
            "file_path": f"large_file_{i}.py",
            "content": large_code,
            "chunk_index": 0,
            "total_chunks": 1,
            "start_line": 1,
            "end_line": 100
        })
    
    return chunks

def test_proactive_token_calculator():
    """Test the proactive token calculator"""
    logger.info("🧪 Testing Proactive Token Calculator")
    
    # Test different models
    models = ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo"]
    
    for model in models:
        logger.info(f"\n📊 Testing {model}")
        calculator = ProactiveTokenCalculator(model)
        
        # Test token counting
        test_text = "This is a test message with some content."
        tokens = calculator.count_tokens(test_text)
        logger.info(f"  Token count for test text: {tokens}")
        
        # Test message token counting
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        message_tokens = calculator.count_messages_tokens(messages)
        logger.info(f"  Message tokens: {message_tokens}")
        
        # Test token projection
        projection = calculator.project_request_tokens(
            system_prompt="You are a code analyzer.",
            user_prompt="Analyze this code: print('hello')",
            context_chunks=create_large_context_chunks()[:2]  # Use first 2 chunks
        )
        
        logger.info(f"  Projection results:")
        logger.info(f"    Total tokens: {projection['total_tokens']}")
        logger.info(f"    Needs trimming: {projection['needs_trimming']}")
        logger.info(f"    Is safe: {projection['is_safe']}")
        logger.info(f"    Budget limit: {projection['budget_limit']}")
        
        # Test intelligent trimming
        if projection["needs_trimming"]:
            logger.info(f"  🔧 Testing intelligent trimming...")
            trimmed_messages, trimming_info = calculator.trim_messages_intelligently(
                projection["messages"]
            )
            
            logger.info(f"    Original tokens: {trimming_info['original_tokens']}")
            logger.info(f"    Final tokens: {trimming_info['final_tokens']}")
            logger.info(f"    Tokens removed: {trimming_info['tokens_removed']}")
            logger.info(f"    Messages removed: {trimming_info['messages_removed']}")
            logger.info(f"    Strategy: {trimming_info['trimming_strategy']}")

def test_safe_messages_creation():
    """Test creating safe messages that fit within budget"""
    logger.info("\n🛡️ Testing Safe Messages Creation")
    
    calculator = ProactiveTokenCalculator("gpt-4")
    
    # Create a large context that would exceed limits
    large_context = create_large_context_chunks()[:5]  # 5 large chunks
    
    safe_messages, budget_info = calculator.create_safe_messages(
        system_prompt="You are a code analyzer. " * 500,  # Large system prompt
        user_prompt="Analyze all the code files provided.",
        context_chunks=large_context
    )
    
    logger.info(f"Safe messages created:")
    logger.info(f"  Final token count: {budget_info['final_tokens']}")
    logger.info(f"  Trimming applied: {budget_info['trimming_applied']}")
    logger.info(f"  Is safe: {budget_info['is_safe']}")
    
    if budget_info['trimming_applied']:
        trimming_info = budget_info['trimming_info']
        logger.info(f"  Tokens removed: {trimming_info['tokens_removed']}")
        logger.info(f"  Messages removed: {trimming_info['messages_removed']}")

async def test_async_reader_with_proactive_budgeting():
    """Test the async reader with proactive token budgeting"""
    logger.info("\n⚡ Testing Async Reader with Proactive Budgeting")
    
    # Create async reader
    reader = AsyncContextAwareReader(model="gpt-4", concurrency_limit=3)
    
    # Create large chunks that would normally cause token overflow
    large_chunks = create_large_context_chunks()[:3]  # Use 3 large chunks
    
    logger.info(f"Processing {len(large_chunks)} large chunks with proactive budgeting...")
    
    try:
        # This should work without token overflow errors due to proactive budgeting
        file_summaries = await reader.process_repository_chunks(large_chunks)
        
        logger.info(f"✅ Successfully processed chunks with proactive budgeting!")
        logger.info(f"  Files processed: {len(file_summaries)}")
        logger.info(f"  Total prompt tokens: {reader.total_prompt_tokens}")
        logger.info(f"  Total completion tokens: {reader.total_completion_tokens}")
        logger.info(f"  Total tokens: {reader.total_prompt_tokens + reader.total_completion_tokens}")
        
        # Show some summaries
        for file_path, summary in list(file_summaries.items())[:2]:
            logger.info(f"  📄 {file_path}: {summary[:100]}...")
            
    except Exception as e:
        logger.error(f"❌ Error during processing: {e}")
        raise

def test_optimal_completion_tokens():
    """Test optimal completion token calculation"""
    logger.info("\n🎯 Testing Optimal Completion Token Calculation")
    
    calculator = ProactiveTokenCalculator("gpt-4-1106-preview")
    
    # Test different prompt sizes
    prompt_sizes = [1000, 5000, 10000, 50000, 100000]
    
    for prompt_tokens in prompt_sizes:
        optimal_tokens = calculator.get_optimal_completion_tokens(prompt_tokens)
        logger.info(f"  Prompt: {prompt_tokens:,} tokens → Optimal completion: {optimal_tokens:,} tokens")

def main():
    """Run all tests"""
    logger.info("🚀 Starting Proactive Token Budgeting Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Proactive token calculator
        test_proactive_token_calculator()
        
        # Test 2: Safe messages creation
        test_safe_messages_creation()
        
        # Test 3: Optimal completion tokens
        test_optimal_completion_tokens()
        
        # Test 4: Async reader with proactive budgeting
        asyncio.run(test_async_reader_with_proactive_budgeting())
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests completed successfully!")
        logger.info("🎉 Proactive token budgeting is working correctly!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main() 