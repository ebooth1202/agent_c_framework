#!/usr/bin/env python3
"""
Script to clear Agent Configuration caches for the mystery world caching issue.
This script executes the cache clearing operations requested by the prime agent.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(src_path))

def main():
    print("=== Agent Cache Clearing Operations ===")
    print()
    
    try:
        # Import the AgentConfigLoader
        from agent_c.config.agent_config_loader import AgentConfigLoader
        print("✓ Successfully imported AgentConfigLoader")
        
        # 1. Get initial cache stats
        print("\n1. Getting initial cache statistics...")
        try:
            initial_stats = AgentConfigLoader.get_cache_stats()
            print(f"✓ Initial cache stats retrieved: {initial_stats}")
        except Exception as e:
            print(f"✗ Error getting initial cache stats: {e}")
            initial_stats = None
        
        # 2. Execute clear_agent_caches()
        print("\n2. Executing AgentConfigLoader.clear_agent_caches()...")
        try:
            clear_result = AgentConfigLoader.clear_agent_caches()
            print(f"✓ Cache clearing completed: {clear_result}")
        except Exception as e:
            print(f"✗ Error clearing agent caches: {e}")
            clear_result = None
            
        # 3. Execute invalidate_cache()
        print("\n3. Executing AgentConfigLoader.invalidate_cache()...")
        try:
            invalidate_result = AgentConfigLoader.invalidate_cache()
            print(f"✓ Cache invalidation completed: {invalidate_result}")
        except Exception as e:
            print(f"✗ Error invalidating cache: {e}")
            invalidate_result = None
        
        # 4. Get final cache stats to verify clearing
        print("\n4. Getting final cache statistics to verify clearing...")
        try:
            final_stats = AgentConfigLoader.get_cache_stats()
            print(f"✓ Final cache stats retrieved: {final_stats}")
        except Exception as e:
            print(f"✗ Error getting final cache stats: {e}")
            final_stats = None
            
        # 5. Summary
        print("\n=== SUMMARY ===")
        print(f"Clear agent caches result: {clear_result}")
        print(f"Cache invalidation result: {invalidate_result}")
        print(f"Initial cache stats: {initial_stats}")
        print(f"Final cache stats: {final_stats}")
        
        # Determine if operations succeeded
        success = True
        if clear_result is None or invalidate_result is None:
            success = False
            
        if success:
            print("\n✓ All cache clearing operations completed successfully!")
        else:
            print("\n✗ Some cache clearing operations failed!")
            
        return 0 if success else 1
        
    except ImportError as e:
        print(f"✗ Failed to import AgentConfigLoader: {e}")
        print("This may indicate a missing dependency or incorrect Python path.")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)