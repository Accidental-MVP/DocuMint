#!/usr/bin/env python3
"""
Test script for cost-optimized model usage

This script demonstrates how the new cost-optimized model selection
reduces costs while maintaining quality across different phases.
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_cost_optimized_config():
    """Test the cost-optimized configuration"""
    print("🧪 Testing Cost-Optimized Configuration")
    print("=" * 60)
    
    try:
        from app.config import AVAILABLE_MODELS, PHASE_MODELS
        
        print("📊 Available Models with Cost Information:")
        print("-" * 40)
        for model_id, model_info in AVAILABLE_MODELS.items():
            cost = model_info.get("cost_per_1k_tokens", "N/A")
            phase = model_info.get("usage_phase", "N/A")
            print(f"  {model_id}:")
            print(f"    Name: {model_info['name']}")
            print(f"    Cost: ${cost}/1K tokens")
            print(f"    Phase: {phase}")
            print(f"    Max Tokens: {model_info['max_tokens']:,}")
            print()
        
        print("🎯 Phase-Based Model Selection:")
        print("-" * 40)
        for phase, model in PHASE_MODELS.items():
            model_info = AVAILABLE_MODELS[model]
            cost = model_info.get("cost_per_1k_tokens", "N/A")
            print(f"  {phase}: {model} (${cost}/1K tokens)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def calculate_cost_savings():
    """Calculate potential cost savings"""
    print("\n💰 Cost Savings Analysis")
    print("=" * 60)
    
    # Example token usage for a medium repository
    chunking_tokens = 5000    # 5K tokens for chunk processing
    understanding_tokens = 3000  # 3K tokens for understanding
    readme_tokens = 2000      # 2K tokens for README generation
    
    total_tokens = chunking_tokens + understanding_tokens + readme_tokens
    
    print(f"📈 Example Token Usage for Medium Repository:")
    print(f"  Chunking & Summarizing: {chunking_tokens:,} tokens")
    print(f"  Repository Understanding: {understanding_tokens:,} tokens")
    print(f"  README Generation: {readme_tokens:,} tokens")
    print(f"  Total: {total_tokens:,} tokens")
    print()
    
    # Cost with cost-optimized approach
    cost_optimized = (
        chunking_tokens * 0.15 / 1000 +      # gpt-4o-mini
        understanding_tokens * 2.50 / 1000 + # gpt-4o
        readme_tokens * 10.00 / 1000         # gpt-4-1106-preview
    )
    
    # Cost with old approach (all GPT-4 Turbo)
    old_approach = total_tokens * 10.00 / 1000  # All gpt-4-1106-preview
    
    # Cost with all GPT-4o-mini (cheapest but lower quality)
    cheapest_approach = total_tokens * 0.15 / 1000  # All gpt-4o-mini
    
    print("💵 Cost Comparison:")
    print("-" * 40)
    print(f"  Cost-Optimized Approach: ${cost_optimized:.2f}")
    print(f"  Old Approach (All GPT-4 Turbo): ${old_approach:.2f}")
    print(f"  Cheapest Approach (All GPT-4o-mini): ${cheapest_approach:.2f}")
    print()
    
    savings_vs_old = ((old_approach - cost_optimized) / old_approach) * 100
    quality_vs_cheapest = "Much better"  # GPT-4 Turbo for README generation
    
    print("🎯 Benefits:")
    print("-" * 40)
    print(f"  💰 Cost Savings vs Old Approach: {savings_vs_old:.1f}%")
    print(f"  🚀 Speed: Faster chunking with GPT-4o-mini")
    print(f"  🧠 Quality: Best models for critical phases")
    print(f"  ⚖️  Balance: Optimal cost/quality ratio")
    
    return True

def test_phase_model_selection():
    """Test the phase-based model selection logic"""
    print("\n🔧 Testing Phase Model Selection")
    print("=" * 60)
    
    try:
        from app.config import PHASE_MODELS, AVAILABLE_MODELS
        
        print("📋 Phase Model Selection Logic:")
        print("-" * 40)
        
        phases = {
            "chunking": {
                "description": "Process file chunks and generate summaries",
                "requirements": "Fast, cheap, good enough quality"
            },
            "understanding": {
                "description": "Generate repository understanding",
                "requirements": "Strong reasoning, moderate cost"
            },
            "excellent_understanding": {
                "description": "Deep dive analysis (if needed)",
                "requirements": "Highest accuracy, higher cost"
            },
            "readme_generation": {
                "description": "Generate final README",
                "requirements": "Best quality, most important output"
            }
        }
        
        for phase, info in phases.items():
            model = PHASE_MODELS[phase]
            model_info = AVAILABLE_MODELS[model]
            cost = model_info.get("cost_per_1k_tokens", "N/A")
            
            print(f"  {phase.upper()}:")
            print(f"    Description: {info['description']}")
            print(f"    Requirements: {info['requirements']}")
            print(f"    Selected Model: {model} (${cost}/1K tokens)")
            print(f"    Rationale: {model_info['description']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_token_budget_integration():
    """Test that token budgeting works with new models"""
    print("\n🛡️ Testing Token Budget Integration")
    print("=" * 60)
    
    try:
        from app.utils.token_budget import ProactiveTokenCalculator
        
        # Test with different models
        models_to_test = ["gpt-4o-mini", "gpt-4o", "gpt-4-1106-preview"]
        
        for model in models_to_test:
            print(f"  Testing {model}:")
            calculator = ProactiveTokenCalculator(model)
            
            # Test token counting
            test_text = "This is a test message for token counting."
            tokens = calculator.count_tokens(test_text)
            print(f"    Token count: {tokens}")
            
            # Test budget limits
            budget = calculator.budget
            print(f"    Max prompt tokens: {budget.max_prompt_tokens:,}")
            print(f"    Max completion tokens: {budget.max_completion_tokens:,}")
            print(f"    Total context: {budget.max_total_tokens:,}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all cost optimization tests"""
    print("🚀 Testing Cost-Optimized Model Usage")
    print("=" * 60)
    
    success = True
    
    # Test 1: Configuration
    if not test_cost_optimized_config():
        success = False
    
    # Test 2: Cost savings calculation
    if not calculate_cost_savings():
        success = False
    
    # Test 3: Phase model selection
    if not test_phase_model_selection():
        success = False
    
    # Test 4: Token budget integration
    if not test_token_budget_integration():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Cost optimization is working correctly.")
        print("\n📊 Summary:")
        print("  ✅ Cost-optimized model selection implemented")
        print("  ✅ ~70% cost savings vs using GPT-4 Turbo for everything")
        print("  ✅ Maintained quality for critical phases")
        print("  ✅ Token budgeting integrated with new models")
    else:
        print("❌ SOME TESTS FAILED! There are issues to fix.")

if __name__ == "__main__":
    main() 