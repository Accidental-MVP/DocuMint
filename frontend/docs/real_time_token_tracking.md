# Real-Time Token Tracking During Prompt Assembly

This document explains the implementation of real-time token tracking and dynamic content adjustment during prompt assembly in DocuMint.

## Overview

DocuMint now implements true real-time token tracking during prompt assembly, which allows for:

1. Dynamic adjustment of content as the prompt is being built
2. Intelligent prioritization of content based on importance
3. Fallback mechanisms when content exceeds token limits
4. Section-based token management with priority levels

## Key Components

### Enhanced TokenCounter Class

The `TokenCounter` class has been enhanced with the following features:

- **Section Tracking**: Keeps track of different sections of the prompt and their token counts
- **Priority System**: Assigns priorities to different sections (1-10, with 10 being highest)
- **Dynamic Space Management**: Can remove low-priority sections to make space for more important content
- **Intelligent Truncation**: Can truncate content while preserving meaning
- **Fallback Mechanisms**: Provides multiple fallback options when content doesn't fit

### Real-Time Pruning

The system now implements true real-time pruning:

- As each section is added to the prompt, its token count is tracked
- If a section would exceed the token limit, fallback options are tried:
  1. Custom fallback handlers specific to the content type
  2. Intelligent truncation of the content
  3. Removal of lower-priority sections to make space

### Dynamic Content Adjustment

Content is dynamically adjusted based on available tokens:

- Files are categorized by importance (essential, important, other)
- Essential files are given higher priority and included first
- If token limits are approached, less important files are skipped
- Structure instructions have multiple versions (full, medium, minimal) based on available tokens

### Fallback Mechanisms

Multiple fallback mechanisms are implemented:

- **File Summaries**: Can be truncated to fit within token limits
- **Structure Instructions**: Three levels of detail based on available tokens
- **Section Removal**: Low-priority sections can be removed to make space for high-priority content
- **Custom Handlers**: Content-specific fallback handlers for intelligent truncation

## Implementation Details

### File Prioritization

Files are now prioritized based on:

1. **Essential Files**: Main entry points, configuration files, etc.
2. **Important Files**: Shorter files that are token-efficient
3. **Other Files**: Remaining files

### Token Budget Management

The token budget is managed by:

1. Tracking tokens for each section
2. Reserving space for essential instructions
3. Dynamically adjusting content based on remaining tokens
4. Providing detailed token usage statistics

### Enhanced Metadata

The system now provides detailed metadata about token usage:

- Total files analyzed vs. files included in prompt
- Number of files truncated or skipped
- Token usage breakdown by section
- Percentage of token budget used

## Benefits

This implementation provides several benefits:

1. **Maximum Information**: Ensures the most important information is always included
2. **Optimal Token Usage**: Makes the most efficient use of available tokens
3. **Graceful Degradation**: Provides fallback options rather than failing
4. **Transparency**: Detailed metadata about what was included/excluded

## Example

When processing a large repository:

1. Essential files like main.py, config.py are included first
2. If token limits are approached, less important files are truncated
3. If still not enough space, low-priority sections might be removed
4. If necessary, structure instructions are simplified to fit within limits

The result is a prompt that makes optimal use of available tokens while ensuring the most important information is included. 