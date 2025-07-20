"""
Repo Analyzer - Main Orchestrator

The main analyzer class that orchestrates the entire six-phase analysis loop:
1. Classification - Detect repo type
2. Dependency Mapping - Parse dependencies
3. Structure Mapping - Map folder structure
4. Signal Extraction - Rank files by importance
5. Flow + Feature Inference - Infer features and user flows
6. Narrative Synthesis - Generate human-readable summaries
"""

import os
import time
from typing import Dict, List, Set, Optional, Any
from pathlib import Path

from .detector import RepoTypeDetector
from .dependency_parser import DependencyParser
from .structure_mapper import StructureMapper
from .signal_ranker import SignalRanker
from .feature_inferer import FeatureInferer
from .narrative_writer import NarrativeWriter


class RepoAnalyzer:
    """Main orchestrator for the six-phase repository analysis pipeline."""
    
    def __init__(self):
        self.detector = RepoTypeDetector()
        self.dependency_parser = DependencyParser()
        self.structure_mapper = StructureMapper()
        self.signal_ranker = SignalRanker()
        self.feature_inferer = FeatureInferer()
        self.narrative_writer = NarrativeWriter()
        
        self.analysis_results = {}
        self.analysis_metadata = {}
    
    def analyze_repository(self, repo_path: str, include_narrative: bool = True) -> Dict[str, Any]:
        """
        Perform complete repository analysis using the six-phase pipeline.
        
        Args:
            repo_path: Path to the repository root
            include_narrative: Whether to include narrative generation
            
        Returns:
            Complete analysis results from all phases
        """
        start_time = time.time()
        
        # Validate repository path
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        if not os.path.isdir(repo_path):
            raise ValueError(f"Repository path is not a directory: {repo_path}")
        
        # Initialize results
        self.analysis_results = {}
        self.analysis_metadata = {
            'repo_path': repo_path,
            'analysis_start_time': start_time,
            'phases_completed': []
        }
        
        try:
            # Phase 1: Classification
            print("🔍 Phase 1: Classifying repository type...")
            repo_type = self.detector.detect_repo_type(repo_path)
            self.analysis_results['repo_type'] = repo_type
            self.analysis_metadata['phases_completed'].append('classification')
            print(f"   Detected: {repo_type['type']} (confidence: {repo_type['confidence']:.2f})")
            
            # Phase 2: Dependency Mapping
            print("📦 Phase 2: Parsing dependencies...")
            dependencies = self.dependency_parser.parse_dependencies(repo_path)
            self.analysis_results['dependencies'] = dependencies
            self.analysis_metadata['phases_completed'].append('dependency_mapping')
            print(f"   Found {len(dependencies.get('features', []))} features from dependencies")
            
            # Phase 3: Structure Mapping
            print("🗂️  Phase 3: Mapping project structure...")
            structure = self.structure_mapper.map_project_structure(repo_path)
            self.analysis_results['structure'] = structure
            self.analysis_metadata['phases_completed'].append('structure_mapping')
            print(f"   Mapped {len(structure.get('file_categories', {}))} file categories")
            
            # Phase 4: Signal Extraction
            print("📊 Phase 4: Extracting high-signal files...")
            signal_data = self.signal_ranker.score_files_by_signal(
                repo_path, 
                structure.get('file_categories', {})
            )
            self.analysis_results['signal'] = signal_data
            self.analysis_metadata['phases_completed'].append('signal_extraction')
            print(f"   Ranked {len(signal_data.get('ranked_files', []))} files by importance")
            
            # Phase 5: Flow + Feature Inference
            print("🎯 Phase 5: Inferring features and user flows...")
            features = self.feature_inferer.infer_features_and_user_flow(
                repo_path, structure, dependencies
            )
            self.analysis_results['features'] = features
            self.analysis_metadata['phases_completed'].append('feature_inference')
            print(f"   Inferred {len(features.get('inferred_features', {}))} features")
            
            # Phase 6: Narrative Synthesis (optional)
            if include_narrative:
                print("📝 Phase 6: Generating narrative...")
                narrative = self.narrative_writer.compose_readme_narrative(
                    repo_path, self.analysis_results
                )
                self.analysis_results['narrative'] = narrative
                self.analysis_metadata['phases_completed'].append('narrative_synthesis')
                print(f"   Generated comprehensive README narrative")
            
            # Calculate analysis metrics
            end_time = time.time()
            self.analysis_metadata['analysis_duration'] = end_time - start_time
            self.analysis_metadata['analysis_end_time'] = end_time
            self.analysis_metadata['success'] = True
            
            print(f"✅ Analysis completed in {self.analysis_metadata['analysis_duration']:.2f} seconds")
            
            return self._format_results()
            
        except Exception as e:
            # Handle analysis errors
            self.analysis_metadata['error'] = str(e)
            self.analysis_metadata['success'] = False
            self.analysis_metadata['analysis_duration'] = time.time() - start_time
            
            print(f"❌ Analysis failed: {e}")
            raise
    
    def analyze_phase(self, repo_path: str, phase: str) -> Dict[str, Any]:
        """
        Run a specific analysis phase.
        
        Args:
            repo_path: Path to the repository root
            phase: Phase to run ('classification', 'dependencies', 'structure', 'signal', 'features', 'narrative')
            
        Returns:
            Results from the specified phase
        """
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        phase_handlers = {
            'classification': lambda: self.detector.detect_repo_type(repo_path),
            'dependencies': lambda: self.dependency_parser.parse_dependencies(repo_path),
            'structure': lambda: self.structure_mapper.map_project_structure(repo_path),
            'signal': lambda: self.signal_ranker.score_files_by_signal(repo_path),
            'features': lambda: self._run_feature_inference(repo_path),
            'narrative': lambda: self._run_narrative_generation(repo_path)
        }
        
        if phase not in phase_handlers:
            raise ValueError(f"Unknown phase: {phase}. Available phases: {list(phase_handlers.keys())}")
        
        return phase_handlers[phase]()
    
    def _run_feature_inference(self, repo_path: str) -> Dict[str, Any]:
        """Run feature inference with minimal dependencies."""
        # Run structure and dependency analysis if not already done
        structure = self.structure_mapper.map_project_structure(repo_path)
        dependencies = self.dependency_parser.parse_dependencies(repo_path)
        
        return self.feature_inferer.infer_features_and_user_flow(repo_path, structure, dependencies)
    
    def _run_narrative_generation(self, repo_path: str) -> Dict[str, Any]:
        """Run narrative generation with minimal dependencies."""
        # Run all previous phases if not already done
        analysis_data = {
            'repo_type': self.detector.detect_repo_type(repo_path),
            'dependencies': self.dependency_parser.parse_dependencies(repo_path),
            'structure': self.structure_mapper.map_project_structure(repo_path),
            'features': self._run_feature_inference(repo_path)
        }
        
        return self.narrative_writer.compose_readme_narrative(repo_path, analysis_data)
    
    def _format_results(self) -> Dict[str, Any]:
        """Format the analysis results for output."""
        return {
            'metadata': self.analysis_metadata,
            'results': self.analysis_results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        results = self.analysis_results
        
        # Extract key metrics
        repo_type = results.get('repo_type', {})
        dependencies = results.get('dependencies', {})
        structure = results.get('structure', {})
        features = results.get('features', {})
        signal = results.get('signal', {})
        
        summary = {
            'project_type': repo_type.get('type', 'unknown'),
            'type_confidence': repo_type.get('confidence', 0),
            'feature_count': len(features.get('inferred_features', {})),
            'tech_stack': dependencies.get('stack', {}),
            'external_services': dependencies.get('external_services', []),
            'architecture_pattern': structure.get('structure_analysis', {}).get('architecture_pattern', 'unknown'),
            'high_signal_files': len(signal.get('high_signal_files', [])),
            'total_files_analyzed': signal.get('signal_analysis', {}).get('total_files', 0),
            'complexity_score': structure.get('structure_analysis', {}).get('complexity_indicators', {}).get('complexity_score', 0)
        }
        
        # Add narrative summary if available
        if 'narrative' in results:
            narrative = results['narrative']
            summary['project_name'] = narrative.get('metadata', {}).get('project_name', 'Unknown')
            summary['project_description'] = narrative.get('metadata', {}).get('project_description', '')
        
        return summary
    
    def get_analysis_insights(self) -> Dict[str, Any]:
        """Get insights and recommendations from the analysis."""
        if not self.analysis_results:
            return {}
        
        insights = {
            'key_findings': [],
            'recommendations': [],
            'architecture_insights': [],
            'feature_insights': []
        }
        
        results = self.analysis_results
        
        # Key findings
        repo_type = results.get('repo_type', {})
        if repo_type.get('confidence', 0) > 0.8:
            insights['key_findings'].append(f"High-confidence detection of {repo_type.get('type', 'unknown')} project")
        
        dependencies = results.get('dependencies', {})
        if dependencies.get('external_services'):
            insights['key_findings'].append(f"Integrates with {len(dependencies['external_services'])} external services")
        
        features = results.get('features', {})
        if features.get('inferred_features'):
            insights['key_findings'].append(f"Detected {len(features['inferred_features'])} distinct features")
        
        # Architecture insights
        structure = results.get('structure', {})
        structure_analysis = structure.get('structure_analysis', {})
        
        if structure_analysis.get('architecture_pattern'):
            insights['architecture_insights'].append(
                f"Follows {structure_analysis['architecture_pattern']} architecture pattern"
            )
        
        complexity_score = structure_analysis.get('complexity_indicators', {}).get('complexity_score', 0)
        if complexity_score > 0.7:
            insights['architecture_insights'].append("High complexity detected - consider refactoring")
        elif complexity_score < 0.3:
            insights['architecture_insights'].append("Low complexity - good maintainability")
        
        # Feature insights
        inferred_features = features.get('inferred_features', {})
        if inferred_features:
            top_features = sorted(
                inferred_features.items(),
                key=lambda x: x[1].get('confidence', 0),
                reverse=True
            )[:3]
            
            for feature, data in top_features:
                insights['feature_insights'].append(
                    f"Strong evidence for {feature.replace('_', ' ')} functionality"
                )
        
        # Recommendations
        if not dependencies.get('external_services'):
            insights['recommendations'].append("Consider integrating external services for enhanced functionality")
        
        if complexity_score > 0.7:
            insights['recommendations'].append("High complexity detected - consider refactoring for maintainability")
        
        if len(features.get('inferred_features', {})) < 3:
            insights['recommendations'].append("Limited feature detection - consider adding more functionality")
        
        return insights
    
    def export_results(self, output_path: str, format: str = 'json') -> str:
        """
        Export analysis results to a file.
        
        Args:
            output_path: Path to save the results
            format: Output format ('json', 'markdown', 'html')
            
        Returns:
            Path to the exported file
        """
        if not self.analysis_results:
            raise ValueError("No analysis results to export. Run analyze_repository() first.")
        
        if format == 'json':
            return self._export_json(output_path)
        elif format == 'markdown':
            return self._export_markdown(output_path)
        elif format == 'html':
            return self._export_html(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Supported formats: json, markdown, html")
    
    def _export_json(self, output_path: str) -> str:
        """Export results as JSON."""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self._format_results(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _export_markdown(self, output_path: str) -> str:
        """Export results as Markdown."""
        if 'narrative' not in self.analysis_results:
            raise ValueError("Narrative not available. Run analysis with include_narrative=True")
        
        narrative = self.analysis_results['narrative']
        readme_content = narrative.get('readme_content', '')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return output_path
    
    def _export_html(self, output_path: str) -> str:
        """Export results as HTML."""
        # This would generate a comprehensive HTML report
        # For now, just create a simple HTML wrapper around the markdown
        if 'narrative' not in self.analysis_results:
            raise ValueError("Narrative not available. Run analysis with include_narrative=True")
        
        narrative = self.analysis_results['narrative']
        readme_content = narrative.get('readme_content', '')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Repository Analysis - {narrative.get('metadata', {}).get('project_name', 'Unknown')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }}
        code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 3px; }}
        h1, h2, h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    </style>
</head>
<body>
{readme_content}
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path 