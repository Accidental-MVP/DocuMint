"""
Enhanced README Generation Service

This service integrates the oracle-level repository analyzer into the existing
DocuMint README generation workflow, providing much deeper repository understanding
and more intelligent README generation.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
from openai import AsyncOpenAI, OpenAI

from ..config import OPENAI_API_KEY, DEFAULT_MODEL, AVAILABLE_MODELS, PHASE_MODELS
from ..utils.token_counter import TokenCounter
from ..utils.repo_analyzer import RepoAnalyzer
from ..utils.parser import clone_repository, cleanup_repository
from ..utils.reader_async import AsyncContextAwareReader
from ..utils.llm import generate_readme

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI clients
client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class EnhancedReadmeGenerator:
    """
    Enhanced README generator that uses the oracle-level repository analyzer
    to provide much deeper understanding and more intelligent README generation.
    """
    
    def __init__(self, model: str = "gpt-4-1106-preview"):
        """
        Initialize the enhanced README generator
        
        Args:
            model: The model to use for generation
        """
        self.model = model
        self.model_settings = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4-1106-preview"])
        self.token_counter = TokenCounter(model_name=model, max_tokens=self.model_settings["max_tokens"])
        self.repo_analyzer = RepoAnalyzer()
    
    async def generate_readme_with_analyzer(self, repo_url: str, tone: str = "professional", 
                                          max_files: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a README using the oracle-level repository analyzer
        
        Args:
            repo_url: URL of the GitHub repository
            tone: Tone for the README
            max_files: Maximum number of files to analyze
            
        Returns:
            Dict: Generated README and comprehensive analysis
        """
        repo_path = None
        
        try:
            logger.info(f"Starting enhanced README generation for: {repo_url}")
            
            # Clone the repository
            repo_path = clone_repository(repo_url)
            
            # Run the oracle-level repository analysis
            logger.info("Running oracle-level repository analysis...")
            analysis_results = self.repo_analyzer.analyze_repository(repo_path, include_narrative=True)
            
            # Extract key insights from the analysis
            repo_type = analysis_results['results']['repo_type']
            dependencies = analysis_results['results']['dependencies']
            structure = analysis_results['results']['structure']
            features = analysis_results['results']['features']
            signal = analysis_results['results']['signal']
            narrative = analysis_results['results']['narrative']
            
            # Get insights and recommendations
            insights = self.repo_analyzer.get_analysis_insights()
            
            # Generate enhanced repository understanding using the analyzer insights
            enhanced_understanding = self._create_enhanced_understanding(
                analysis_results, insights, repo_url
            )
            
            # Get high-signal files for detailed analysis
            high_signal_files = signal.get('high_signal_files', [])
            if max_files:
                file_paths = [file_info['path'] for file_info in high_signal_files[:max_files]]
            else:
                file_paths = [file_info['path'] for file_info in high_signal_files]
            
            # Process high-signal files with async reader
            logger.info(f"Processing {len(file_paths)} high-signal files...")
            chunks = self._create_chunks_from_files(repo_path, file_paths)
            
            # Use cost-optimized model for file processing
            chunking_model = PHASE_MODELS.get("chunking", "gpt-4o-mini")
            reader = AsyncContextAwareReader(model=chunking_model, concurrency_limit=15)
            file_summaries = await reader.process_repository_chunks(chunks)
            
            # Generate final README using the enhanced understanding
            logger.info("Generating enhanced README...")
            readme_content = await self._generate_enhanced_readme(
                repo_url, enhanced_understanding, file_summaries, 
                analysis_results, insights, tone
            )
            
            # Prepare comprehensive metadata
            metadata = self._prepare_enhanced_metadata(
                analysis_results, insights, file_summaries, 
                reader, repo_url, tone
            )
            
            return {
                "success": True,
                "readme": readme_content,
                "metadata": metadata,
                "analysis": analysis_results
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced README generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "readme": "# Error\n\nFailed to generate enhanced README."
            }
        finally:
            # Clean up the cloned repository
            if repo_path:
                cleanup_repository(repo_path)
    
    def _create_enhanced_understanding(self, analysis_results: Dict, insights: Dict, repo_url: str) -> str:
        """Create enhanced repository understanding from analyzer results."""
        summary = analysis_results['summary']
        results = analysis_results['results']
        
        understanding_parts = [
            f"# Repository Analysis for {repo_url}\n\n",
            f"## Project Overview\n",
            f"- **Project Type**: {summary.get('project_type', 'Unknown')} (confidence: {summary.get('type_confidence', 0):.2f})\n",
            f"- **Architecture Pattern**: {summary.get('architecture_pattern', 'Unknown')}\n",
            f"- **Complexity Score**: {summary.get('complexity_score', 0):.2f}\n",
            f"- **Features Detected**: {summary.get('feature_count', 0)}\n",
            f"- **High-Signal Files**: {summary.get('high_signal_files', 0)}\n\n"
        ]
        
        # Add tech stack information
        tech_stack = summary.get('tech_stack', {})
        if tech_stack:
            understanding_parts.append("## Technology Stack\n")
            for category, technologies in tech_stack.items():
                if technologies:
                    understanding_parts.append(f"- **{category.title()}**: {', '.join(technologies)}\n")
            understanding_parts.append("\n")
        
        # Add detected features
        inferred_features = results.get('features', {}).get('inferred_features', {})
        if inferred_features:
            understanding_parts.append("## Detected Features\n")
            for feature, data in sorted(inferred_features.items(), 
                                      key=lambda x: x[1].get('confidence', 0), reverse=True):
                confidence = data.get('confidence', 0)
                evidence = data.get('evidence', [])
                understanding_parts.append(f"- **{feature.replace('_', ' ').title()}** (confidence: {confidence:.2f})\n")
                for ev in evidence[:3]:  # Show top 3 pieces of evidence
                    understanding_parts.append(f"  - {ev}\n")
            understanding_parts.append("\n")
        
        # Add insights
        if insights.get('key_findings'):
            understanding_parts.append("## Key Findings\n")
            for finding in insights['key_findings']:
                understanding_parts.append(f"- {finding}\n")
            understanding_parts.append("\n")
        
        if insights.get('architecture_insights'):
            understanding_parts.append("## Architecture Insights\n")
            for insight in insights['architecture_insights']:
                understanding_parts.append(f"- {insight}\n")
            understanding_parts.append("\n")
        
        if insights.get('recommendations'):
            understanding_parts.append("## Recommendations\n")
            for rec in insights['recommendations']:
                understanding_parts.append(f"- {rec}\n")
            understanding_parts.append("\n")
        
        return ''.join(understanding_parts)
    
    def _create_chunks_from_files(self, repo_path: str, file_paths: List[str]) -> List[Dict]:
        """Create chunks from high-signal files."""
        chunks = []
        
        for file_path in file_paths:
            full_path = os.path.join(repo_path, file_path)
            
            if not os.path.exists(full_path):
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Create chunks (simple chunking for now)
                chunk_size = 4000  # characters
                for i in range(0, len(content), chunk_size):
                    chunk_content = content[i:i + chunk_size]
                    chunks.append({
                        "file_path": file_path,
                        "content": chunk_content,
                        "chunk_index": i // chunk_size,
                        "total_chunks": (len(content) + chunk_size - 1) // chunk_size,
                        "start_line": 1,  # Add missing start_line field
                        "end_line": 1     # Add missing end_line field
                    })
                    
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")
                continue
        
        return chunks
    
    async def _generate_enhanced_readme(self, repo_url: str, enhanced_understanding: str, 
                                      file_summaries: Dict[str, str], analysis_results: Dict, 
                                      insights: Dict, tone: str) -> str:
        """Generate the final enhanced README."""
        
        # Build a comprehensive prompt using analyzer insights
        prompt = self._build_enhanced_prompt(
            repo_url, enhanced_understanding, file_summaries, 
            analysis_results, insights, tone
        )
        
        # Use the best model for final README generation
        readme_model = PHASE_MODELS.get("readme_generation", "gpt-4-1106-preview")
        
        # Generate the README
        readme_content = generate_readme(
            prompt=prompt,
            model=readme_model,
            temperature=0.7,
            max_tokens=4000
        )
        
        return readme_content
    
    def _build_enhanced_prompt(self, repo_url: str, enhanced_understanding: str, 
                              file_summaries: Dict[str, str], analysis_results: Dict, 
                              insights: Dict, tone: str) -> str:
        """Build an enhanced prompt using analyzer insights."""
        
        summary = analysis_results['summary']
        results = analysis_results['results']
        
        # Get project name
        project_name = summary.get('project_name', repo_url.split('/')[-1].replace('.git', ''))
        
        # Build tone-specific instructions
        tone_instructions = {
            "professional": "Write in a professional, business-like tone suitable for enterprise software.",
            "startup": "Write in an energetic, startup-friendly tone that emphasizes innovation and growth.",
            "meme": "Write in a fun, casual tone with humor and personality.",
            "technical": "Write in a technical, detailed tone focused on implementation specifics.",
            "friendly": "Write in a warm, approachable tone that welcomes contributors."
        }.get(tone, "Write in a professional tone.")
        
        # Get detected features for the prompt
        inferred_features = results.get('features', {}).get('inferred_features', {})
        feature_list = [f"- {feature.replace('_', ' ').title()}" for feature in inferred_features.keys()]
        features_text = '\n'.join(feature_list) if feature_list else "- Modern application functionality"
        
        # Get tech stack for the prompt
        tech_stack = summary.get('tech_stack', {})
        tech_stack_text = ""
        for category, technologies in tech_stack.items():
            if technologies:
                tech_stack_text += f"- **{category.title()}**: {', '.join(technologies)}\n"
        
        prompt = f"""
You are an expert technical writer creating a comprehensive README for a {summary.get('project_type', 'software')} project.

## Project Information
- **Project Name**: {project_name}
- **Repository URL**: {repo_url}
- **Project Type**: {summary.get('project_type', 'Unknown')} (confidence: {summary.get('type_confidence', 0):.2f})
- **Architecture Pattern**: {summary.get('architecture_pattern', 'Unknown')}
- **Complexity Score**: {summary.get('complexity_score', 0):.2f}

## Technology Stack
{tech_stack_text}

## Detected Features
{features_text}

## Repository Analysis
{enhanced_understanding}

## Key Insights
{chr(10).join([f"- {finding}" for finding in insights.get('key_findings', [])])}

## Architecture Insights
{chr(10).join([f"- {insight}" for insight in insights.get('architecture_insights', [])])}

## File Summaries
{chr(10).join([f"### {file_path}\n{summary}" for file_path, summary in list(file_summaries.items())[:10]])}

## Instructions
{tone_instructions}

Create a comprehensive, well-structured README that includes:

1. **Project Overview**: Clear description of what the project does
2. **Features**: Based on the detected features above
3. **Technology Stack**: Based on the detected technologies
4. **Installation**: Step-by-step setup instructions
5. **Usage**: How to use the project
6. **Architecture**: Based on the detected architecture pattern
7. **API Documentation**: If applicable
8. **Contributing**: Guidelines for contributors
9. **License**: License information

Make the README engaging, informative, and tailored to the specific project type and features detected. Use the insights from the repository analysis to provide accurate, contextual information.
"""
        
        return prompt
    
    def _prepare_enhanced_metadata(self, analysis_results: Dict, insights: Dict, 
                                  file_summaries: Dict[str, str], reader: AsyncContextAwareReader,
                                  repo_url: str, tone: str) -> Dict[str, Any]:
        """Prepare comprehensive metadata for the response."""
        
        summary = analysis_results['summary']
        
        return {
            "repo_url": repo_url,
            "tone": tone,
            "model": self.model,
            "enhanced_analysis": {
                "project_type": summary.get('project_type', 'unknown'),
                "type_confidence": summary.get('type_confidence', 0),
                "architecture_pattern": summary.get('architecture_pattern', 'unknown'),
                "complexity_score": summary.get('complexity_score', 0),
                "feature_count": summary.get('feature_count', 0),
                "high_signal_files": summary.get('high_signal_files', 0),
                "total_files_analyzed": summary.get('total_files_analyzed', 0)
            },
            "tech_stack": summary.get('tech_stack', {}),
            "external_services": summary.get('external_services', []),
            "detected_features": list(analysis_results['results'].get('features', {}).get('inferred_features', {}).keys()),
            "insights": insights,
            "files_analyzed": len(file_summaries),
            "processing": {
                "total_prompt_tokens": reader.total_prompt_tokens,
                "total_completion_tokens": reader.total_completion_tokens,
                "total_tokens": reader.total_prompt_tokens + reader.total_completion_tokens
            },
            "analysis_duration": analysis_results['metadata'].get('analysis_duration', 0),
            "phases_completed": analysis_results['metadata'].get('phases_completed', [])
        }
    
    async def stream_generate_enhanced_readme(self, repo_url: str, tone: str = "professional",
                                            max_files: Optional[int] = None) -> AsyncGenerator[str, None]:
        """
        Generate an enhanced README with streaming output
        
        Args:
            repo_url: URL of the GitHub repository
            tone: Tone for the README
            max_files: Maximum number of files to analyze
            
        Yields:
            str: Chunks of the README as they are generated
        """
        repo_path = None
        
        try:
            yield "# Starting Enhanced README Generation...\n\n"
            
            # Clone the repository
            yield "## Cloning Repository...\n\n"
            repo_path = clone_repository(repo_url)
            
            # Run repository analysis
            yield "## Running Oracle-Level Repository Analysis...\n\n"
            analysis_results = self.repo_analyzer.analyze_repository(repo_path, include_narrative=True)
            
            # Show analysis results
            summary = analysis_results['summary']
            yield f"### Analysis Results\n\n"
            yield f"- **Project Type**: {summary.get('project_type', 'Unknown')}\n"
            yield f"- **Confidence**: {summary.get('type_confidence', 0):.2f}\n"
            yield f"- **Features Detected**: {summary.get('feature_count', 0)}\n"
            yield f"- **Architecture**: {summary.get('architecture_pattern', 'Unknown')}\n\n"
            
            # Process high-signal files
            yield "## Processing High-Signal Files...\n\n"
            signal = analysis_results['results']['signal']
            high_signal_files = signal.get('high_signal_files', [])
            if max_files:
                file_paths = [file_info['path'] for file_info in high_signal_files[:max_files]]
            else:
                file_paths = [file_info['path'] for file_info in high_signal_files]
            
            chunks = self._create_chunks_from_files(repo_path, file_paths)
            chunking_model = PHASE_MODELS.get("chunking", "gpt-4o-mini")
            reader = AsyncContextAwareReader(model=chunking_model, concurrency_limit=15)
            file_summaries = await reader.process_repository_chunks(chunks)
            
            yield f"Processed {len(file_summaries)} files with {len(chunks)} chunks.\n\n"
            
            # Generate enhanced understanding
            yield "## Creating Enhanced Understanding...\n\n"
            insights = self.repo_analyzer.get_analysis_insights()
            enhanced_understanding = self._create_enhanced_understanding(
                analysis_results, insights, repo_url
            )
            
            # Generate final README
            yield "## Generating Enhanced README...\n\n"
            readme_content = await self._generate_enhanced_readme(
                repo_url, enhanced_understanding, file_summaries, 
                analysis_results, insights, tone
            )
            
            # Yield the final README
            yield readme_content
            
        except Exception as e:
            yield f"## Error\n\nFailed to generate enhanced README: {str(e)}"
        finally:
            if repo_path:
                cleanup_repository(repo_path)


# Convenience function for easy integration
async def generate_enhanced_readme_for_repo(repo_url: str, tone: str = "professional",
                                           model: str = "gpt-4-1106-preview",
                                           max_files: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate an enhanced README using the oracle-level repository analyzer
    
    Args:
        repo_url: URL of the GitHub repository
        tone: Tone for the README
        model: Model to use for generation
        max_files: Maximum number of files to analyze
        
    Returns:
        Dict: Generated README and comprehensive analysis
    """
    generator = EnhancedReadmeGenerator(model=model)
    return await generator.generate_readme_with_analyzer(repo_url, tone, max_files) 