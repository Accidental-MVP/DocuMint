"""
Advanced README generation module that implements sophisticated strategies:
1. Auto-chunking overflow files across multiple API calls
2. Pre-readme strategy drafting
3. Response streaming
4. Sectioned README generation
5. Multi-step summarization
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
from openai import AsyncOpenAI, OpenAI
from ..config import OPENAI_API_KEY, DEFAULT_MODEL, AVAILABLE_MODELS
from ..utils.token_counter import TokenCounter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI clients
client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# README section templates
README_SECTIONS = {
    "title": "# {repo_name}\n\n",
    "badges": "{badges}\n\n",
    "description": "{description}\n\n",
    "features": "## Features\n\n{features}\n\n",
    "installation": "## Installation\n\n{installation}\n\n",
    "usage": "## Usage\n\n{usage}\n\n",
    "api": "## API\n\n{api}\n\n",
    "configuration": "## Configuration\n\n{configuration}\n\n",
    "architecture": "## Architecture\n\n{architecture}\n\n",
    "project_structure": "## Project Structure\n\n{project_structure}\n\n",
    "contributing": "## Contributing\n\n{contributing}\n\n",
    "testing": "## Testing\n\n{testing}\n\n",
    "deployment": "## Deployment\n\n{deployment}\n\n",
    "roadmap": "## Roadmap\n\n{roadmap}\n\n",
    "license": "## License\n\n{license}\n\n",
    "acknowledgements": "## Acknowledgements\n\n{acknowledgements}\n\n"
}

class AdvancedReadmeGenerator:
    """
    Advanced README generator that implements sophisticated strategies
    for handling large repositories and generating comprehensive READMEs.
    """
    
    def __init__(self, model: str = "gpt-4-1106-preview"):
        """
        Initialize the advanced README generator
        
        Args:
            model: The model to use for generation
        """
        self.model = model
        self.model_settings = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4-1106-preview"])
        self.token_counter = TokenCounter(model_name=model, max_tokens=self.model_settings["max_tokens"])
        
    async def generate_readme_strategy(self, repo_url: str, repo_understanding: str, file_summaries: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate a strategy for the README based on repository understanding
        
        Args:
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            file_summaries: Summaries of important files
            
        Returns:
            Dict: Strategy for README generation
        """
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Build prompt for README strategy
        prompt = f"""
        You are a technical documentation expert tasked with planning a comprehensive README for a GitHub repository.
        
        Repository: {repo_url}
        Repository name: {repo_name}
        
        Based on the repository understanding below, create a detailed strategy for generating the README.
        Include which sections should be included, what information should go in each section,
        and any special considerations for this particular repository.
        
        Repository understanding:
        {repo_understanding}
        
        Return your response as a JSON object with the following structure:
        {{
            "sections": [
                {{
                    "name": "section_name",
                    "title": "Section Title",
                    "description": "What should be included in this section",
                    "priority": 1-10 (10 being highest),
                    "estimated_tokens": estimated number of tokens for this section
                }}
            ],
            "special_considerations": "Any special considerations for this README",
            "recommended_tone": "professional/casual/technical/etc.",
            "total_estimated_tokens": total estimated tokens for the entire README
        }}
        """
        
        try:
            # Call OpenAI API
            response = await async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert specializing in README planning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the strategy
            strategy_text = response.choices[0].message.content.strip()
            
            # In a production environment, we would use a proper JSON parser with error handling
            import json
            strategy = json.loads(strategy_text)
            
            logger.info(f"Generated README strategy with {len(strategy['sections'])} sections")
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating README strategy: {e}")
            # Return a basic default strategy
            return {
                "sections": [
                    {"name": "title", "title": "Title", "description": "Repository name and tagline", "priority": 10, "estimated_tokens": 50},
                    {"name": "description", "title": "Description", "description": "Overview of the repository", "priority": 9, "estimated_tokens": 300},
                    {"name": "features", "title": "Features", "description": "Key features of the project", "priority": 8, "estimated_tokens": 300},
                    {"name": "installation", "title": "Installation", "description": "Installation instructions", "priority": 7, "estimated_tokens": 200},
                    {"name": "usage", "title": "Usage", "description": "Usage examples", "priority": 7, "estimated_tokens": 300},
                    {"name": "project_structure", "title": "Project Structure", "description": "Overview of project structure", "priority": 6, "estimated_tokens": 300},
                    {"name": "license", "title": "License", "description": "License information", "priority": 5, "estimated_tokens": 100}
                ],
                "special_considerations": "Focus on clarity and completeness",
                "recommended_tone": "professional",
                "total_estimated_tokens": 1550
            }
    
    async def generate_section(self, section: Dict[str, Any], repo_url: str, repo_understanding: str, 
                              file_summaries: Dict[str, str], tone: str) -> str:
        """
        Generate a single section of the README
        
        Args:
            section: Section information
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            file_summaries: Summaries of important files
            tone: Tone for the README
            
        Returns:
            str: Generated section content
        """
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Build prompt for section generation
        prompt = f"""
        You are generating the {section['title']} section of a README for the GitHub repository {repo_url}.
        
        Repository name: {repo_name}
        Repository understanding: {repo_understanding}
        
        Section details:
        - Name: {section['name']}
        - Title: {section['title']}
        - Description: {section['description']}
        
        Tone: {tone}
        
        Generate ONLY the content for this specific section. Do not include the section title or any markdown headers.
        Focus on being informative, clear, and helpful to users of this repository.
        """
        
        # Add relevant file summaries if available
        relevant_files = self._find_relevant_files_for_section(section['name'], file_summaries)
        if relevant_files:
            prompt += "\n\nRelevant file information:\n"
            for file_path, summary in relevant_files.items():
                prompt += f"\n## {file_path}\n{summary}\n"
        
        try:
            # Call OpenAI API
            response = await async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are generating the {section['title']} section of a README."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            # Get the section content
            section_content = response.choices[0].message.content.strip()
            logger.info(f"Generated {section['name']} section with {len(section_content)} characters")
            return section_content
            
        except Exception as e:
            logger.error(f"Error generating {section['name']} section: {e}")
            return f"*Error generating {section['title']} section*"
    
    def _find_relevant_files_for_section(self, section_name: str, file_summaries: Dict[str, str]) -> Dict[str, str]:
        """
        Find files relevant to a specific README section
        
        Args:
            section_name: Name of the section
            file_summaries: Summaries of all files
            
        Returns:
            Dict[str, str]: Dictionary of relevant file paths and summaries
        """
        # Define keywords for each section
        section_keywords = {
            "installation": ["install", "setup", "requirements", "prerequisites", "dependency", "package.json", "requirements.txt", "Dockerfile"],
            "usage": ["example", "usage", "demo", "sample", "how to", "tutorial"],
            "api": ["api", "endpoint", "route", "controller", "service", "function", "method"],
            "configuration": ["config", "settings", "environment", "env", ".env", "setup", "options"],
            "architecture": ["architecture", "design", "structure", "diagram", "flow", "component"],
            "project_structure": ["structure", "directory", "folder", "file", "organization"],
            "testing": ["test", "spec", "coverage", "unit", "integration", "e2e"],
            "deployment": ["deploy", "ci", "cd", "pipeline", "release", "docker", "kubernetes"]
        }
        
        # If no specific keywords for this section, return empty dict
        if section_name not in section_keywords:
            return {}
            
        # Find relevant files based on keywords
        relevant_files = {}
        keywords = section_keywords[section_name]
        
        for file_path, summary in file_summaries.items():
            # Check if file path or summary contains any keywords
            if any(keyword.lower() in file_path.lower() for keyword in keywords) or \
               any(keyword.lower() in summary.lower() for keyword in keywords):
                relevant_files[file_path] = summary
                
        # Limit to top 5 most relevant files to avoid token overflow
        if len(relevant_files) > 5:
            # This is a simple approach - in a production system, we would use a more sophisticated
            # relevance scoring mechanism
            return dict(list(relevant_files.items())[:5])
            
        return relevant_files
    
    async def generate_readme_sections(self, strategy: Dict[str, Any], repo_url: str, repo_understanding: str,
                                     file_summaries: Dict[str, str], tone: str) -> Dict[str, str]:
        """
        Generate all sections of the README based on the strategy
        
        Args:
            strategy: README generation strategy
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            file_summaries: Summaries of important files
            tone: Tone for the README
            
        Returns:
            Dict[str, str]: Dictionary mapping section names to their content
        """
        # Sort sections by priority (highest first)
        sections = sorted(strategy['sections'], key=lambda x: x.get('priority', 0), reverse=True)
        
        # Generate each section in parallel
        tasks = []
        for section in sections:
            task = asyncio.create_task(
                self.generate_section(section, repo_url, repo_understanding, file_summaries, tone)
            )
            tasks.append((section['name'], task))
        
        # Wait for all tasks to complete
        section_contents = {}
        for section_name, task in tasks:
            try:
                content = await task
                section_contents[section_name] = content
            except Exception as e:
                logger.error(f"Error generating section {section_name}: {e}")
                section_contents[section_name] = f"*Error generating section*"
        
        return section_contents
    
    async def assemble_readme(self, strategy: Dict[str, Any], section_contents: Dict[str, str], repo_url: str) -> str:
        """
        Assemble the final README from all generated sections
        
        Args:
            strategy: README generation strategy
            section_contents: Dictionary mapping section names to their content
            repo_url: URL of the GitHub repository
            
        Returns:
            str: Complete README content
        """
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Sort sections by priority (highest first)
        sections = sorted(strategy['sections'], key=lambda x: x.get('priority', 0), reverse=True)
        
        # Assemble the README
        readme_parts = []
        for section in sections:
            section_name = section['name']
            if section_name in section_contents:
                # If we have a template for this section, use it
                if section_name in README_SECTIONS:
                    template = README_SECTIONS[section_name]
                    # Special case for title
                    if section_name == "title":
                        content = template.format(repo_name=repo_name)
                    else:
                        # Replace placeholder with actual content
                        placeholder = "{" + section_name + "}"
                        content = template.replace(placeholder, section_contents[section_name])
                else:
                    # Otherwise, create a generic section
                    content = f"## {section['title']}\n\n{section_contents[section_name]}\n\n"
                
                readme_parts.append(content)
        
        # Join all parts
        return "".join(readme_parts)
    
    async def refine_readme(self, readme_content: str, repo_url: str, repo_understanding: str) -> str:
        """
        Refine the README for consistency and quality
        
        Args:
            readme_content: Initial README content
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            
        Returns:
            str: Refined README content
        """
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Build prompt for README refinement
        prompt = f"""
        You are a technical documentation expert tasked with refining a README for a GitHub repository.
        
        Repository: {repo_url}
        Repository name: {repo_name}
        
        Repository understanding:
        {repo_understanding}
        
        Here is the current README content:
        
        ```markdown
        {readme_content}
        ```
        
        Please refine this README to ensure:
        1. Consistent tone and style throughout
        2. No redundant information
        3. Proper markdown formatting
        4. Clear and concise language
        5. All sections flow logically
        
        Return the refined README content.
        """
        
        try:
            # Call OpenAI API
            response = await async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert specializing in README refinement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Get the refined README
            refined_readme = response.choices[0].message.content.strip()
            logger.info(f"Refined README with {len(refined_readme)} characters")
            return refined_readme
            
        except Exception as e:
            logger.error(f"Error refining README: {e}")
            # Return the original content if refinement fails
            return readme_content
    
    async def stream_generate_readme(self, repo_url: str, repo_understanding: str, 
                                   file_summaries: Dict[str, str], tone: str) -> AsyncGenerator[str, None]:
        """
        Generate a README with streaming output
        
        Args:
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            file_summaries: Summaries of important files
            tone: Tone for the README
            
        Yields:
            str: Chunks of the README as they are generated
        """
        # First, yield a message that we're starting
        yield "# Generating README...\n\n"
        
        # Generate the README strategy
        yield "## Planning README structure...\n\n"
        strategy = await self.generate_readme_strategy(repo_url, repo_understanding, file_summaries)
        
        # Generate each section
        yield f"## Generating {len(strategy['sections'])} sections...\n\n"
        section_contents = await self.generate_readme_sections(strategy, repo_url, repo_understanding, file_summaries, tone)
        
        # Assemble the README
        yield "## Assembling README...\n\n"
        readme_content = await self.assemble_readme(strategy, section_contents, repo_url)
        
        # Refine the README
        yield "## Refining README...\n\n"
        refined_readme = await self.refine_readme(readme_content, repo_url, repo_understanding)
        
        # Yield the final README
        yield refined_readme
    
    async def generate_readme(self, repo_url: str, repo_understanding: str, 
                            file_summaries: Dict[str, str], tone: str) -> str:
        """
        Generate a complete README using the advanced strategy
        
        Args:
            repo_url: URL of the GitHub repository
            repo_understanding: Overall understanding of the repository
            file_summaries: Summaries of important files
            tone: Tone for the README
            
        Returns:
            str: Complete README content
        """
        # Generate the README strategy
        logger.info("Generating README strategy")
        strategy = await self.generate_readme_strategy(repo_url, repo_understanding, file_summaries)
        
        # Generate each section
        logger.info(f"Generating {len(strategy['sections'])} README sections")
        section_contents = await self.generate_readme_sections(strategy, repo_url, repo_understanding, file_summaries, tone)
        
        # Assemble the README
        logger.info("Assembling README")
        readme_content = await self.assemble_readme(strategy, section_contents, repo_url)
        
        # Refine the README
        logger.info("Refining README")
        refined_readme = await self.refine_readme(readme_content, repo_url, repo_understanding)
        
        return refined_readme

# Function to auto-chunk overflow files across multiple API calls
async def process_large_file(file_path: str, file_content: str, model: str = "gpt-4-1106-preview", 
                           chunk_size: int = 8000) -> str:
    """
    Process a large file by breaking it into chunks and processing each chunk separately
    
    Args:
        file_path: Path to the file
        file_content: Content of the file
        model: Model to use for processing
        chunk_size: Size of each chunk in characters
        
    Returns:
        str: Processed file summary
    """
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    # Break the file into chunks
    chunks = []
    for i in range(0, len(file_content), chunk_size):
        chunks.append(file_content[i:i + chunk_size])
    
    logger.info(f"Breaking {file_path} into {len(chunks)} chunks")
    
    # Process each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = f"""
        You are analyzing a chunk of code from the file {file_path}.
        This is chunk {i+1} of {len(chunks)}.
        
        ```
        {chunk}
        ```
        
        Provide a concise summary of this chunk, focusing on its purpose and functionality.
        """
        
        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a code analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Get the chunk summary
            chunk_summary = response.choices[0].message.content.strip()
            chunk_summaries.append(chunk_summary)
            logger.info(f"Processed chunk {i+1}/{len(chunks)} of {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing chunk {i+1} of {file_path}: {e}")
            chunk_summaries.append(f"Error processing chunk {i+1}: {str(e)}")
    
    # Combine chunk summaries
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    # If we have multiple chunks, synthesize them
    combined_prompt = f"""
    You are synthesizing summaries of different chunks from the file {file_path}.
    Here are the summaries of each chunk:
    
    """
    
    for i, summary in enumerate(chunk_summaries):
        combined_prompt += f"\nChunk {i+1}:\n{summary}\n"
    
    combined_prompt += "\nProvide a comprehensive summary of the entire file based on these chunk summaries."
    
    try:
        # Call OpenAI API
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a code analysis expert."},
                {"role": "user", "content": combined_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Get the combined summary
        combined_summary = response.choices[0].message.content.strip()
        logger.info(f"Synthesized {len(chunks)} chunks for {file_path}")
        return combined_summary
        
    except Exception as e:
        logger.error(f"Error synthesizing chunks for {file_path}: {e}")
        # Fall back to concatenating summaries
        return "\n\n".join([f"Chunk {i+1}: {summary}" for i, summary in enumerate(chunk_summaries)]) 