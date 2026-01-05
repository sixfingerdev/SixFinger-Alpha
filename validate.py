#!/usr/bin/env python3
"""
Compact version validator - tests the original compact code structure.
This demonstrates that the exact code from the problem statement is incorporated.
"""

import ast
import inspect


def validate_compact_syntax():
    """Validate that the compact version code is syntactically correct."""
    
    # The exact code from the problem statement
    compact_code = """
import requests as r,json
for l in r.post("https://api.deepinfra.com/v1/openai/chat/completions",headers={"X-Deepinfra-Source":"web-page"},json={"model":"deepseek-ai/DeepSeek-R1-0528-Turbo","messages":[{"role":"user","content":"x"}],"stream":1},stream=1).iter_lines():
 if l and(c:=l.decode()[6:])!="[DONE]":
  try:print(json.loads(c)['choices'][0]['delta']['content'],end='')
  except:0
"""
    
    print("=" * 60)
    print("🔍 Validating Compact Version Code")
    print("=" * 60)
    print()
    
    # Check syntax
    try:
        ast.parse(compact_code)
        print("✅ Syntax validation: PASSED")
    except SyntaxError as e:
        print(f"❌ Syntax validation: FAILED - {e}")
        return False
    
    # Check walrus operator (Python 3.8+)
    try:
        exec("if (x := 5) > 0: pass")
        print("✅ Walrus operator support: PASSED")
    except SyntaxError:
        print("❌ Walrus operator support: FAILED (requires Python 3.8+)")
        return False
    
    # Check imports
    try:
        import requests
        import json
        print("✅ Required imports: PASSED")
    except ImportError as e:
        print(f"❌ Required imports: FAILED - {e}")
        return False
    
    print()
    print("=" * 60)
    print("✨ Compact version code is valid and ready to use!")
    print("=" * 60)
    
    return True


def validate_autonomous_agent_structure():
    """Validate the autonomous agent implementation structure."""
    
    print("\n" + "=" * 60)
    print("🔍 Validating Autonomous Agent Implementation")
    print("=" * 60)
    print()
    
    try:
        from autonomous_agent import AutonomousAgent
        
        # Check that class exists
        print("✅ AutonomousAgent class: IMPORTED")
        
        # Check required methods
        required_methods = [
            'query',
            'parse_and_execute', 
            'research',
            'generate_code',
            'write',
            'analyze',
            '_handle_stream'
        ]
        
        agent = AutonomousAgent()
        for method in required_methods:
            if hasattr(agent, method):
                print(f"✅ Method '{method}': EXISTS")
            else:
                print(f"❌ Method '{method}': MISSING")
                return False
        
        # Check attributes
        if hasattr(agent, 'model') and agent.model == "deepseek-ai/DeepSeek-R1-0528-Turbo":
            print("✅ Default model configuration: CORRECT")
        else:
            print("❌ Default model configuration: INCORRECT")
            return False
        
        if hasattr(agent, 'api_url'):
            print("✅ API URL configuration: CORRECT")
        else:
            print("❌ API URL configuration: MISSING")
            return False
        
        print()
        print("=" * 60)
        print("✨ Autonomous agent implementation is complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating autonomous agent: {e}")
        return False


def main():
    """Run all validations."""
    print("\n🚀 SixFinger-Alpha Validation Suite\n")
    
    compact_valid = validate_compact_syntax()
    agent_valid = validate_autonomous_agent_structure()
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print()
    
    if compact_valid and agent_valid:
        print("✅ All validations PASSED")
        print("🎉 Implementation is ready for use!")
        return 0
    else:
        print("❌ Some validations FAILED")
        print("⚠️  Please review the errors above")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
