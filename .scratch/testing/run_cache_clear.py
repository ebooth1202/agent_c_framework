#!/usr/bin/env python3
"""
Execute the cache clearing operations directly
"""

import sys
import os
from pathlib import Path

# Add the src directories to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(src_path))

# Set up environment - check for .env file
env_file = project_root / ".env"
if env_file.exists():
    # Load environment variables if .env exists
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

try:
    # Import the AgentConfigLoader
    from agent_c.config.agent_config_loader import AgentConfigLoader
    
    print("=== Agent C Cache Clearing Operations ===")
    print("Resolving mystery world game master caching issues...\n")
    
    # Step 1: Get initial cache statistics
    print("1. Getting initial cache statistics...")
    try:
        initial_stats = AgentConfigLoader.get_cache_stats()
        print(f"   ✓ Initial stats retrieved: {initial_stats}")
    except Exception as e:
        print(f"   ⚠️ Could not get initial stats: {e}")
        initial_stats = {}
    
    # Step 2: Clear all agent configuration caches
    print("\n2. Clearing all agent configuration caches...")
    try:
        clear_results = AgentConfigLoader.clear_agent_caches()
        print(f"   ✓ Cache clear executed: {clear_results}")
    except Exception as e:
        print(f"   ❌ Error clearing caches: {e}")
        clear_results = {}
    
    # Step 3: Invalidate singleton cache  
    print("\n3. Invalidating singleton cache...")
    try:
        invalidate_results = AgentConfigLoader.invalidate_cache()
        print(f"   ✓ Cache invalidation executed: {invalidate_results}")
    except Exception as e:
        print(f"   ❌ Error invalidating cache: {e}")
        invalidate_results = {}
    
    # Step 4: Get final cache statistics
    print("\n4. Getting final cache statistics...")
    try:
        final_stats = AgentConfigLoader.get_cache_stats()
        print(f"   ✓ Final stats retrieved: {final_stats}")
    except Exception as e:
        print(f"   ⚠️ Could not get final stats: {e}")
        final_stats = {}
    
    # Summary
    print("\n" + "="*50)
    print("CACHE CLEARING SUMMARY")
    print("="*50)
    
    agent_cache_cleared = clear_results.get('agent_cache_cleared', 0) if clear_results else 0
    singleton_invalidated = invalidate_results.get('singleton_invalidated', False) if invalidate_results else False
    
    print(f"✅ Agent configuration caches cleared: {agent_cache_cleared} items")
    print(f"✅ Singleton cache invalidated: {'Yes' if singleton_invalidated else 'No'}")
    
    # Check cache size changes
    if initial_stats and final_stats:
        initial_agent_stats = initial_stats.get('agent_config_stats', {})
        final_agent_stats = final_stats.get('agent_config_stats', {})
        initial_size = initial_agent_stats.get('size', 0)
        final_size = final_agent_stats.get('size', 0)
        print(f"✅ Cache size: {initial_size} → {final_size} items")
    
    success = clear_results or invalidate_results
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Cache clearing operations {'completed' if success else 'failed'}")
    
    if success:
        print("🎉 Mystery world game master caching issues should now be resolved!")
    else:
        print("⚠️ Some operations may have failed - check error messages above")
        
except ImportError as e:
    print(f"❌ Import Error: Could not import AgentConfigLoader: {e}")
    print("   Make sure the agent_c_core package is properly installed")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Cache clearing script completed ===")