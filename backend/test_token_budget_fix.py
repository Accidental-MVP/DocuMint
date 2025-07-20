#!/usr/bin/env python3
"""
Simple test to verify the AsyncContextAwareReader fix
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_async_reader_initialization():
    """Test that AsyncContextAwareReader can be initialized without errors"""
    try:
        # Mock the config to avoid dependency issues
        import types
        mock_config = types.ModuleType('config')
        mock_config.OPENAI_API_KEY = "test_key"
        
        # Mock the token_budget module
        mock_token_budget = types.ModuleType('token_budget')
        
        class MockTokenBudget:
            def __init__(self, model):
                self.max_total_tokens = 8192
                self.max_prompt_tokens = 6000
                self.max_completion_tokens = 2000
                self.safety_margin = 500
        
        class MockProactiveTokenCalculator:
            def __init__(self, model):
                self.model = model
                self.budget = MockTokenBudget(model)
            
            def count_tokens(self, text):
                return len(text) // 4
            
            def count_messages_tokens(self, messages):
                return sum(len(msg.get("content", "")) // 4 for msg in messages)
            
            def project_request_tokens(self, **kwargs):
                return {
                    "total_tokens": 1000,
                    "needs_trimming": False,
                    "is_safe": True,
                    "budget_limit": 6000
                }
            
            def trim_messages_intelligently(self, messages):
                return messages, {"trimmed": False, "final_tokens": 1000}
            
            def get_optimal_completion_tokens(self, prompt_tokens):
                return 2000
        
        mock_token_budget.ProactiveTokenCalculator = MockProactiveTokenCalculator
        
        # Mock the modules
        sys.modules['app.config'] = mock_config
        sys.modules['app.utils.token_budget'] = mock_token_budget
        
        # Now try to import and initialize
        from app.utils.reader_async import AsyncContextAwareReader
        
        # Test initialization
        reader = AsyncContextAwareReader(model="gpt-4", concurrency_limit=15)
        
        print("✅ SUCCESS: AsyncContextAwareReader initialized without errors!")
        print(f"   Model: {reader.model}")
        print(f"   Concurrency limit: {reader.concurrency_limit}")
        print(f"   Token calculator: {type(reader.token_calculator).__name__}")
        
        # Test that the old attributes are not accessible
        try:
            _ = reader.max_prompt_tokens
            print("❌ ERROR: max_prompt_tokens still accessible!")
            return False
        except AttributeError:
            print("✅ SUCCESS: max_prompt_tokens properly removed")
        
        try:
            _ = reader.max_completion_tokens
            print("❌ ERROR: max_completion_tokens still accessible!")
            return False
        except AttributeError:
            print("✅ SUCCESS: max_completion_tokens properly removed")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_token_calculator():
    """Test the ProactiveTokenCalculator directly"""
    try:
        from app.utils.token_budget import ProactiveTokenCalculator
        
        calculator = ProactiveTokenCalculator("gpt-4")
        print("✅ SUCCESS: ProactiveTokenCalculator initialized!")
        print(f"   Model: {calculator.model}")
        print(f"   Budget limit: {calculator.budget.max_prompt_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in token calculator: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AsyncContextAwareReader Fix")
    print("=" * 50)
    
    success = True
    
    # Test 1: AsyncContextAwareReader initialization
    print("\n1. Testing AsyncContextAwareReader initialization...")
    if not test_async_reader_initialization():
        success = False
    
    # Test 2: ProactiveTokenCalculator
    print("\n2. Testing ProactiveTokenCalculator...")
    if not test_token_calculator():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! There are still issues to fix.") 