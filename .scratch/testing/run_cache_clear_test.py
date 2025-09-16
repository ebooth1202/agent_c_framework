#!/usr/bin/env python3
"""
Cache clearing test script based on mystery_world_final_configuration_complete.md
Phase 1: Cache Clearing & Verification
"""

import sys
import os

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_core', 'src'))

try:
    print("=== Phase 1: Cache Clearing & Verification ===")
    print("Attempting to import AgentConfigLoader...")
    
    from agent_c.config.agent_config_loader import AgentConfigLoader
    
    print("✅ Successfully imported AgentConfigLoader")
    
    print("\n1. Clearing agent caches...")
    try:
        results = AgentConfigLoader.clear_agent_caches()
        print(f"   Agent caches cleared: {results}")
    except Exception as e:
        print(f"   ❌ Error clearing agent caches: {e}")
    
    print("\n2. Invalidating singleton cache...")
    try:
        invalidate_results = AgentConfigLoader.invalidate_cache()
        print(f"   Singleton cache invalidated: {invalidate_results}")
    except Exception as e:
        print(f"   ❌ Error invalidating singleton cache: {e}")
    
    print("\n3. Getting cache statistics...")
    try:
        stats = AgentConfigLoader.get_cache_stats()
        print(f"   Cache stats after clearing: {stats}")
    except Exception as e:
        print(f"   ❌ Error getting cache stats: {e}")
        
    print("\n✅ Phase 1 cache clearing attempts completed")
    
except ImportError as e:
    print(f"❌ Failed to import AgentConfigLoader: {e}")
    print("This might indicate the Agent C system isn't running or accessible")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)