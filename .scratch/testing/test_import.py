#!/usr/bin/env python3
"""
Test script to validate that we can import AgentConfigLoader and see its methods.
This helps verify our approach before trying to execute the cache operations.
"""

import sys
from pathlib import Path


def setup_python_path():
    """Set up Python path for agent_c imports."""
    project_root = Path(__file__).parent.parent
    agent_c_core_src = project_root / "src" / "agent_c_core" / "src"
    
    print(f"Project root: {project_root}")
    print(f"Looking for agent_c_core at: {agent_c_core_src}")
    print(f"Exists: {agent_c_core_src.exists()}")
    
    if agent_c_core_src.exists():
        if str(agent_c_core_src) not in sys.path:
            sys.path.insert(0, str(agent_c_core_src))
        print(f"Added to Python path: {agent_c_core_src}")
        return True
    return False


def main():
    """Test the import and inspect the methods."""
    print("=== AgentConfigLoader Import Test ===")
    
    # Set up Python path
    if not setup_python_path():
        print("❌ Could not set up Python path for agent_c_core")
        return 1
    
    print(f"Current Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    try:
        # Test import
        print("Attempting to import AgentConfigLoader...")
        from agent_c.config.agent_config_loader import AgentConfigLoader
        print("✅ Successfully imported AgentConfigLoader")
        
        # Inspect the class
        print("\n📋 Available class methods:")
        methods = [method for method in dir(AgentConfigLoader) if not method.startswith('_')]
        for method in methods:
            print(f"   - {method}")
        
        # Check specifically for our target methods
        target_methods = ['clear_agent_caches', 'invalidate_cache', 'get_cache_stats']
        print(f"\n🎯 Target methods status:")
        for method in target_methods:
            if hasattr(AgentConfigLoader, method):
                print(f"   ✅ {method} - Available")
                try:
                    method_obj = getattr(AgentConfigLoader, method)
                    print(f"      Type: {type(method_obj)}")
                    if hasattr(method_obj, '__doc__') and method_obj.__doc__:
                        doc_lines = method_obj.__doc__.strip().split('\n')
                        print(f"      Doc: {doc_lines[0].strip()}")
                except Exception as e:
                    print(f"      Error inspecting: {e}")
            else:
                print(f"   ❌ {method} - NOT FOUND")
        
        print("\n✅ Import test completed successfully!")
        return 0
        
    except ImportError as e:
        print(f"❌ Failed to import AgentConfigLoader: {e}")
        print("\n🔍 Debugging info:")
        
        # Try to find the module step by step
        try:
            import agent_c
            print("   ✅ Successfully imported agent_c")
            print(f"   agent_c location: {agent_c.__file__}")
        except ImportError as e2:
            print(f"   ❌ Failed to import agent_c: {e2}")
            
        try:
            from agent_c import config
            print("   ✅ Successfully imported agent_c.config")
        except ImportError as e3:
            print(f"   ❌ Failed to import agent_c.config: {e3}")
            
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\nTest completed with exit code: {exit_code}")
    sys.exit(exit_code)