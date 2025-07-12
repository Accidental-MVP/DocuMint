#!/usr/bin/env python3
"""
Test script to demonstrate real-time token tracking functionality
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path so we can import the app modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.utils.token_counter import TokenCounter

def demonstrate_token_tracking():
    """
    Demonstrate the real-time token tracking functionality
    """
    print("DocuMint Real-Time Token Tracking Demo")
    print("-" * 50)
    
    # Initialize token counter with a small limit for demonstration
    counter = TokenCounter(model_name="gpt-4", max_tokens=2000, buffer=200)
    print(f"Initialized counter with {counter.available_tokens} available tokens")
    
    # Add base prompt (high priority)
    base_prompt = """You are a senior technical writer hired to create a compelling, helpful, and user-focused README.md for a GitHub repository. Your goal is to make it useful for developers evaluating whether to use this repo."""
    
    success, tokens = counter.add_to_prompt(base_prompt, "base_prompt", priority=10)
    print(f"Added base prompt: {tokens} tokens, {counter.get_usage_percentage():.1f}% used")
    
    # Add file summaries (medium priority)
    file_summaries = {
        "main.py": "This is the main entry point for the application. It initializes the FastAPI app, sets up middleware, and starts the server.",
        "config.py": "Configuration file that loads environment variables and sets up application settings.",
        "utils/helpers.py": "Contains utility functions used throughout the application.",
        "models/user.py": "Defines the User model and related database operations.",
        "services/auth.py": "Implements authentication and authorization services.",
        "very_long_file.py": "A" * 5000  # Simulate a very long file
    }
    
    # Add essential files first
    essential_files = ["main.py", "config.py"]
    for file in essential_files:
        content = f"## {file}\n{file_summaries[file]}\n\n"
        success, tokens = counter.add_to_prompt(content, f"file_{file}", priority=8)
        print(f"Added {file}: {tokens} tokens, {counter.get_usage_percentage():.1f}% used")
    
    # Try to add a very long file
    long_file = "very_long_file.py"
    content = f"## {long_file}\n{file_summaries[long_file]}\n\n"
    
    # First, check if it will fit
    will_fit, tokens = counter.will_fit(content)
    print(f"Will {long_file} fit? {will_fit} ({tokens} tokens)")
    
    # Try with fallback
    def custom_fallback(text, available):
        # Simple fallback: truncate to 100 chars
        file_path = text.split('\n')[0][3:]  # Extract file path
        return f"## {file_path}\n[Content truncated due to length]\n\n"
    
    success, tokens, added_text = counter.add_with_fallback(
        content, 
        f"file_{long_file}", 
        priority=5,
        fallback_handler=custom_fallback
    )
    
    print(f"Added {long_file} with fallback: {tokens} tokens, {counter.get_usage_percentage():.1f}% used")
    print(f"Fallback text: {added_text[:50]}...")
    
    # Add remaining files
    remaining_files = ["utils/helpers.py", "models/user.py", "services/auth.py"]
    for file in remaining_files:
        content = f"## {file}\n{file_summaries[file]}\n\n"
        success, tokens = counter.add_to_prompt(content, f"file_{file}", priority=5)
        if success:
            print(f"Added {file}: {tokens} tokens, {counter.get_usage_percentage():.1f}% used")
        else:
            print(f"Could not add {file}: would exceed token limit")
    
    # Try to make space for a new high-priority section
    new_section = "A" * 500  # Simulate a large new section
    will_fit, tokens = counter.will_fit(new_section)
    
    if not will_fit:
        print(f"New section won't fit ({tokens} tokens). Making space...")
        # Try to make space by removing low-priority sections
        made_space = counter.make_space(tokens, ["base_prompt"])
        
        if made_space:
            success, tokens = counter.add_to_prompt(new_section, "new_section", priority=9)
            print(f"Made space and added new section: {tokens} tokens, {counter.get_usage_percentage():.1f}% used")
        else:
            print("Could not make enough space")
    
    # Print final statistics
    print("\nFinal Token Statistics:")
    print("-" * 50)
    print(f"Total tokens used: {counter.current_count}")
    print(f"Available tokens: {counter.available_tokens}")
    print(f"Remaining tokens: {counter.get_remaining_tokens()}")
    print(f"Usage percentage: {counter.get_usage_percentage():.1f}%")
    
    # Print section statistics
    print("\nSection Statistics:")
    print("-" * 50)
    stats = counter.get_section_stats()
    for section, data in stats.items():
        print(f"{section}: {data['tokens']} tokens, {data['percentage']:.1f}%, priority {data['priority']}")

if __name__ == "__main__":
    demonstrate_token_tracking() 