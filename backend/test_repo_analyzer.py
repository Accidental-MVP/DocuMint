#!/usr/bin/env python3
"""
Test script for the Repo Analyzer

This script demonstrates the six-phase repository analysis pipeline
by analyzing the current DocuMint project.
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.repo_analyzer import RepoAnalyzer


def main():
    """Run the repository analysis on the current project."""
    print("🚀 DocuMint Repository Analyzer")
    print("=" * 50)
    
    # Get the current directory (should be the DocuMint root)
    current_dir = os.getcwd()
    print(f"Analyzing repository: {current_dir}")
    print()
    
    # Initialize the analyzer
    analyzer = RepoAnalyzer()
    
    try:
        # Run the complete analysis
        print("Starting six-phase analysis...")
        results = analyzer.analyze_repository(current_dir, include_narrative=True)
        
        # Display summary
        print("\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)
        
        summary = results['summary']
        print(f"Project Name: {summary.get('project_name', 'Unknown')}")
        print(f"Project Type: {summary.get('project_type', 'unknown')}")
        print(f"Type Confidence: {summary.get('type_confidence', 0):.2f}")
        print(f"Features Detected: {summary.get('feature_count', 0)}")
        print(f"High-Signal Files: {summary.get('high_signal_files', 0)}")
        print(f"Total Files Analyzed: {summary.get('total_files_analyzed', 0)}")
        print(f"Complexity Score: {summary.get('complexity_score', 0):.2f}")
        print(f"Architecture Pattern: {summary.get('architecture_pattern', 'unknown')}")
        
        # Display tech stack
        tech_stack = summary.get('tech_stack', {})
        if tech_stack:
            print(f"\nTech Stack:")
            for category, technologies in tech_stack.items():
                if technologies:
                    print(f"  {category.title()}: {', '.join(technologies)}")
        
        # Display external services
        external_services = summary.get('external_services', [])
        if external_services:
            print(f"\nExternal Services: {', '.join(external_services)}")
        
        # Display insights
        print("\n" + "=" * 50)
        print("💡 ANALYSIS INSIGHTS")
        print("=" * 50)
        
        insights = analyzer.get_analysis_insights()
        
        if insights.get('key_findings'):
            print("\n🔍 Key Findings:")
            for finding in insights['key_findings']:
                print(f"  • {finding}")
        
        if insights.get('architecture_insights'):
            print("\n🏗️  Architecture Insights:")
            for insight in insights['architecture_insights']:
                print(f"  • {insight}")
        
        if insights.get('feature_insights'):
            print("\n🎯 Feature Insights:")
            for insight in insights['feature_insights']:
                print(f"  • {insight}")
        
        if insights.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in insights['recommendations']:
                print(f"  • {rec}")
        
        # Display detected features
        print("\n" + "=" * 50)
        print("🎯 DETECTED FEATURES")
        print("=" * 50)
        
        features = results['results'].get('features', {})
        inferred_features = features.get('inferred_features', {})
        
        if inferred_features:
            # Sort by confidence
            sorted_features = sorted(
                inferred_features.items(),
                key=lambda x: x[1].get('confidence', 0),
                reverse=True
            )
            
            for feature_name, feature_data in sorted_features:
                confidence = feature_data.get('confidence', 0)
                evidence = feature_data.get('evidence', [])
                
                print(f"\n{feature_name.replace('_', ' ').title()}")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  Evidence:")
                for ev in evidence[:3]:  # Show top 3 pieces of evidence
                    print(f"    • {ev}")
        else:
            print("No specific features detected.")
        
        # Display high-signal files
        print("\n" + "=" * 50)
        print("📊 HIGH-SIGNAL FILES")
        print("=" * 50)
        
        signal_data = results['results'].get('signal', {})
        high_signal_files = signal_data.get('high_signal_files', [])
        
        if high_signal_files:
            print("Top 10 most important files:")
            for i, file_info in enumerate(high_signal_files[:10], 1):
                path = file_info.get('path', 'Unknown')
                score = file_info.get('score', 0)
                category = file_info.get('category', 'unknown')
                print(f"  {i:2d}. {path} (score: {score:.2f}, category: {category})")
        else:
            print("No high-signal files detected.")
        
        # Export results
        print("\n" + "=" * 50)
        print("💾 EXPORTING RESULTS")
        print("=" * 50)
        
        # Export as JSON
        json_path = analyzer.export_results('repo_analysis_results.json', 'json')
        print(f"JSON results exported to: {json_path}")
        
        # Export as Markdown
        markdown_path = analyzer.export_results('generated_readme.md', 'markdown')
        print(f"Markdown README exported to: {markdown_path}")
        
        # Export as HTML
        html_path = analyzer.export_results('repo_analysis_report.html', 'html')
        print(f"HTML report exported to: {html_path}")
        
        print("\n✅ Analysis completed successfully!")
        print(f"Total analysis time: {results['metadata']['analysis_duration']:.2f} seconds")
        
        # Show a preview of the generated README
        print("\n" + "=" * 50)
        print("📝 GENERATED README PREVIEW")
        print("=" * 50)
        
        narrative = results['results'].get('narrative', {})
        readme_content = narrative.get('readme_content', '')
        
        # Show first 500 characters
        preview = readme_content[:500] + "..." if len(readme_content) > 500 else readme_content
        print(preview)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 