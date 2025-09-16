#!/usr/bin/env python3
"""
Direct execution of cache clearing operations for the mystery world caching issue.
This script directly imports and executes the requested AgentConfigLoader methods.
"""

import sys
from pathlib import Path


def setup_python_path():
    """Set up Python path for agent_c imports."""
    project_root = Path(__file__).parent.parent
    agent_c_core_src = project_root / "src" / "agent_c_core" / "src"
    
    if agent_c_core_src.exists():
        if str(agent_c_core_src) not in sys.path:
            sys.path.insert(0, str(agent_c_core_src))
        return True
    return False


def main():
    """Execute the cache clearing operations directly."""
    print("=== Agent Cache Clearing Operations (Mystery World Fix) ===")
    print("Executing the specific operations requested by the prime agent:")
    print("1. AgentConfigLoader.clear_agent_caches()")
    print("2. AgentConfigLoader.invalidate_cache()")
    print("3. AgentConfigLoader.get_cache_stats() (verification)")
    print()
    
    # Set up Python path
    if not setup_python_path():
        print("❌ Could not set up Python path for agent_c_core")
        return 1
    
    try:
        # Import AgentConfigLoader
        from agent_c.config.agent_config_loader import AgentConfigLoader
        print("✅ Successfully imported AgentConfigLoader")
        print()
        
        # Operation 1: Get initial cache stats
        print("📊 Step 1: Getting initial cache statistics...")
        try:
            initial_stats = AgentConfigLoader.get_cache_stats()
            print(f"   ✅ Initial cache stats: {initial_stats}")
        except Exception as e:
            print(f"   ❌ Error getting initial stats: {e}")
            initial_stats = None
        print()
        
        # Operation 2: Execute clear_agent_caches()
        print("🧹 Step 2: Executing AgentConfigLoader.clear_agent_caches()...")
        try:
            clear_result = AgentConfigLoader.clear_agent_caches()
            print(f"   ✅ Cache clearing result: {clear_result}")
            clear_success = True
        except Exception as e:
            print(f"   ❌ Error clearing agent caches: {e}")
            clear_result = None
            clear_success = False
        print()
        
        # Operation 3: Execute invalidate_cache()
        print("🗑️ Step 3: Executing AgentConfigLoader.invalidate_cache()...")
        try:
            invalidate_result = AgentConfigLoader.invalidate_cache()
            print(f"   ✅ Cache invalidation result: {invalidate_result}")
            invalidate_success = True
        except Exception as e:
            print(f"   ❌ Error invalidating cache: {e}")
            invalidate_result = None
            invalidate_success = False
        print()
        
        # Operation 4: Get final cache stats for verification
        print("📋 Step 4: Getting final cache statistics for verification...")
        try:
            final_stats = AgentConfigLoader.get_cache_stats()
            print(f"   ✅ Final cache stats: {final_stats}")
            stats_success = True
        except Exception as e:
            print(f"   ❌ Error getting final stats: {e}")
            final_stats = None
            stats_success = False
        print()
        
        # Summary
        print("=" * 60)
        print("📋 EXECUTION SUMMARY:")
        print(f"   Clear agent caches: {'✅ SUCCESS' if clear_success else '❌ FAILED'}")
        print(f"   Invalidate cache: {'✅ SUCCESS' if invalidate_success else '❌ FAILED'}")
        print(f"   Stats verification: {'✅ SUCCESS' if stats_success else '❌ FAILED'}")
        print()
        
        if clear_result:
            print(f"🧹 Clear caches result: {clear_result}")
        if invalidate_result:
            print(f"🗑️ Invalidate cache result: {invalidate_result}")
        
        # Determine overall success
        overall_success = clear_success and invalidate_success
        
        print()
        if overall_success:
            print("🎉 ALL CACHE CLEARING OPERATIONS COMPLETED SUCCESSFULLY!")
            print("✅ The mystery world caching issue should now be resolved.")
        else:
            print("⚠️ Some cache clearing operations failed!")
            print("❌ The mystery world caching issue may not be fully resolved.")
        
        print()
        print("📊 CACHE COMPARISON:")
        if initial_stats and final_stats:
            print(f"   Initial stats: {initial_stats}")
            print(f"   Final stats:   {final_stats}")
        
        return 0 if overall_success else 1
        
    except ImportError as e:
        print(f"❌ Failed to import AgentConfigLoader: {e}")
        print("   This may indicate a missing dependency or incorrect Python path.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print()
    print(f"Script completed with exit code: {exit_code}")
    sys.exit(exit_code)