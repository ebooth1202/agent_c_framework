#!/usr/bin/env python3
"""
Script to test AgentConfigLoader cache clearing methods.
Demonstrates the usage of:
- AgentConfigLoader.get_cache_stats()
- AgentConfigLoader.clear_agent_caches()  
- AgentConfigLoader.invalidate_cache()
"""

import sys
import os
import json
from pathlib import Path

# Add the agent_c_core source to Python path
project_root = Path(__file__).parent.parent
agent_c_core_src = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(agent_c_core_src))

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_json_result(title, data):
    """Print JSON data in a formatted way."""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def main():
    print_header("AgentConfigLoader Cache Operations Test")
    
    print(f"Python path includes: {agent_c_core_src}")
    print(f"Agent C Core source exists: {agent_c_core_src.exists()}")
    
    try:
        # Import AgentConfigLoader
        print("\n🔄 Step 1: Importing AgentConfigLoader...")
        from agent_c.config.agent_config_loader import AgentConfigLoader
        print("✅ Successfully imported AgentConfigLoader")
        
        # Get initial cache statistics
        print("\n🔄 Step 2: Getting initial cache statistics...")
        initial_stats = AgentConfigLoader.get_cache_stats()
        print_json_result("Initial cache statistics", initial_stats)
        
        # Clear all agent caches
        print("\n🔄 Step 3: Clearing all agent caches...")
        clear_results = AgentConfigLoader.clear_agent_caches()
        print_json_result("Cache clear results", clear_results)
        
        # Invalidate singleton cache (no parameters - clears everything)
        print("\n🔄 Step 4: Invalidating singleton cache...")
        invalidate_results = AgentConfigLoader.invalidate_cache()
        print_json_result("Cache invalidation results", invalidate_results)
        
        # Get final cache statistics
        print("\n🔄 Step 5: Getting final cache statistics...")
        final_stats = AgentConfigLoader.get_cache_stats()
        print_json_result("Final cache statistics", final_stats)
        
        print_header("Summary")
        print("✅ All cache operations completed successfully!")
        print("\nOperations performed:")
        print("  • Retrieved initial cache statistics")
        print("  • Cleared agent configuration caches")
        print("  • Invalidated singleton caches")
        print("  • Retrieved final cache statistics")
        
        # Compare before/after if possible
        if 'agent_config_stats' in initial_stats and 'agent_config_stats' in final_stats:
            print(f"\nCache items before: {initial_stats['agent_config_stats'].get('items', 'N/A')}")
            print(f"Cache items after: {final_stats['agent_config_stats'].get('items', 'N/A')}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTrying to diagnose import issues...")
        try:
            # Check if agent_c package exists
            import agent_c
            print(f"✅ agent_c package found: {agent_c}")
            
            # Check agent_c.config
            import agent_c.config
            print(f"✅ agent_c.config found: {dir(agent_c.config)}")
            
        except Exception as e2:
            print(f"❌ Could not import agent_c components: {e2}")
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()