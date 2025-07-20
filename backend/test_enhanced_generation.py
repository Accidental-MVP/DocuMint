#!/usr/bin/env python3
"""
Test script for enhanced README generation using the oracle-level repository analyzer.

This script demonstrates how the enhanced README generation works with deep repository analysis.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_generate import generate_enhanced_readme_for_repo, EnhancedReadmeGenerator

async def test_enhanced_generation():
    """Test the enhanced README generation with a sample repository."""
    
    # Test repository (you can change this to any public GitHub repo)
    test_repo_url = "https://github.com/facebook/react"
    
    print("🧠 Testing Oracle-Level README Generation")
    print("=" * 50)
    print(f"Repository: {test_repo_url}")
    print()
    
    try:
        # Test enhanced generation
        print("1. Running Enhanced README Generation...")
        result = await generate_enhanced_readme_for_repo(
            repo_url=test_repo_url,
            tone="professional",
            model="gpt-4-1106-preview",
            max_files=20
        )
        
        if result["success"]:
            print("✅ Enhanced README generation completed successfully!")
            print()
            
            # Display analysis summary
            metadata = result["metadata"]
            analysis = result["analysis"]
            
            print("📊 Analysis Summary:")
            print("-" * 30)
            enhanced_analysis = metadata["enhanced_analysis"]
            print(f"• Project Type: {enhanced_analysis['project_type']}")
            print(f"• Type Confidence: {enhanced_analysis['type_confidence']:.2f}")
            print(f"• Architecture Pattern: {enhanced_analysis['architecture_pattern']}")
            print(f"• Complexity Score: {enhanced_analysis['complexity_score']:.2f}")
            print(f"• Features Detected: {enhanced_analysis['feature_count']}")
            print(f"• High-Signal Files: {enhanced_analysis['high_signal_files']}")
            print(f"• Total Files Analyzed: {enhanced_analysis['total_files_analyzed']}")
            print()
            
            # Display tech stack
            tech_stack = metadata["tech_stack"]
            if tech_stack:
                print("🔧 Technology Stack:")
                print("-" * 30)
                for category, technologies in tech_stack.items():
                    if technologies:
                        print(f"• {category.title()}: {', '.join(technologies)}")
                print()
            
            # Display detected features
            detected_features = metadata["detected_features"]
            if detected_features:
                print("🎯 Detected Features:")
                print("-" * 30)
                for feature in detected_features[:10]:  # Show top 10
                    print(f"• {feature.replace('_', ' ').title()}")
                print()
            
            # Display insights
            insights = metadata["insights"]
            if insights.get("key_findings"):
                print("💡 Key Findings:")
                print("-" * 30)
                for finding in insights["key_findings"][:5]:  # Show top 5
                    print(f"• {finding}")
                print()
            
            if insights.get("architecture_insights"):
                print("🏗️ Architecture Insights:")
                print("-" * 30)
                for insight in insights["architecture_insights"][:3]:  # Show top 3
                    print(f"• {insight}")
                print()
            
            # Display processing stats
            processing = metadata["processing"]
            print("⚡ Processing Statistics:")
            print("-" * 30)
            print(f"• Files Analyzed: {metadata['files_analyzed']}")
            print(f"• Prompt Tokens: {processing['total_prompt_tokens']:,}")
            print(f"• Completion Tokens: {processing['total_completion_tokens']:,}")
            print(f"• Total Tokens: {processing['total_tokens']:,}")
            print(f"• Analysis Duration: {metadata['analysis_duration']:.2f}s")
            print(f"• Phases Completed: {', '.join(metadata['phases_completed'])}")
            print()
            
            # Show README preview
            readme_content = result["readme"]
            print("📝 Generated README Preview:")
            print("-" * 30)
            print(readme_content[:500] + "..." if len(readme_content) > 500 else readme_content)
            print()
            
            # Save README to file
            output_file = "enhanced_readme_generated.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(readme_content)
            print(f"💾 README saved to: {output_file}")
            
            # Save analysis to JSON file
            import json
            analysis_file = "enhanced_analysis_results.json"
            with open(analysis_file, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"📊 Analysis results saved to: {analysis_file}")
            
        else:
            print("❌ Enhanced README generation failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def test_streaming_generation():
    """Test the streaming enhanced README generation."""
    
    test_repo_url = "https://github.com/vercel/next.js"
    
    print("\n🌊 Testing Streaming Enhanced README Generation")
    print("=" * 50)
    print(f"Repository: {test_repo_url}")
    print()
    
    try:
        generator = EnhancedReadmeGenerator(model="gpt-4-1106-preview")
        
        print("2. Running Streaming Enhanced Generation...")
        async for chunk in generator.stream_generate_enhanced_readme(
            repo_url=test_repo_url,
            tone="startup",
            max_files=15
        ):
            print(chunk, end="", flush=True)
            
    except Exception as e:
        print(f"❌ Error during streaming test: {e}")

async def compare_generation_methods():
    """Compare different generation methods."""
    
    test_repo_url = "https://github.com/tailwindlabs/tailwindcss"
    
    print("\n🔄 Comparing Generation Methods")
    print("=" * 50)
    print(f"Repository: {test_repo_url}")
    print()
    
    tones = ["professional", "startup", "technical"]
    
    for tone in tones:
        print(f"Testing tone: {tone}")
        print("-" * 20)
        
        try:
            result = await generate_enhanced_readme_for_repo(
                repo_url=test_repo_url,
                tone=tone,
                model="gpt-4-1106-preview",
                max_files=10
            )
            
            if result["success"]:
                metadata = result["metadata"]
                processing = metadata["processing"]
                
                print(f"✅ Success - Tokens: {processing['total_tokens']:,}, "
                      f"Features: {metadata['enhanced_analysis']['feature_count']}")
                
                # Show a snippet of the README
                readme_preview = result["readme"][:100] + "..."
                print(f"   Preview: {readme_preview}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

async def main():
    """Main test function."""
    print("🚀 Enhanced README Generation Test Suite")
    print("=" * 60)
    
    # Test 1: Basic enhanced generation
    await test_enhanced_generation()
    
    # Test 2: Streaming generation
    await test_streaming_generation()
    
    # Test 3: Compare different tones
    await compare_generation_methods()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 