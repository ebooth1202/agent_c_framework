#!/usr/bin/env python3
"""
CLI tool for cache management in the Agent C system.

This command-line interface allows administrators to clear, invalidate, and inspect
caches for the Agent C framework components.
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional


def setup_python_path():
    """Automatically find and add the correct Python path for agent_c imports."""
    script_path = Path(__file__).resolve()
    
    # Look for agent_c_core/src directory
    project_root = script_path.parent.parent
    agent_c_core_src = project_root / "src" / "agent_c_core" / "src"
    
    if agent_c_core_src.exists():
        if str(agent_c_core_src) not in sys.path:
            sys.path.insert(0, str(agent_c_core_src))
        return str(agent_c_core_src)
    
    raise RuntimeError("Could not find agent_c_core/src in project structure")

# Set up path automatically
setup_python_path()


async def clear_agent_caches() -> Dict[str, Any]:
    """
    Clear all agent configuration caches.
    
    Returns:
        Dictionary with clearing results
    """
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        print("🧹 Clearing agent configuration caches...")
        result = AgentConfigLoader.clear_agent_caches()
        
        print(f"✅ Agent caches cleared successfully!")
        print(f"   Result: {result}")
        
        return {"success": True, "result": result}
        
    except Exception as e:
        print(f"❌ Error clearing agent caches: {e}")
        return {"success": False, "error": str(e)}


async def invalidate_agent_cache(config_path: Optional[str] = None, default_model: Optional[str] = None) -> Dict[str, Any]:
    """
    Invalidate agent configuration caches.
    
    Args:
        config_path: Optional config path for specific cache invalidation
        default_model: Optional default model for specific cache invalidation
        
    Returns:
        Dictionary with invalidation results
    """
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        print("🗑️ Invalidating agent configuration caches...")
        
        kwargs = {}
        if config_path:
            kwargs['config_path'] = config_path
            print(f"   - Config path: {config_path}")
        if default_model:
            kwargs['default_model'] = default_model
            print(f"   - Default model: {default_model}")
            
        result = AgentConfigLoader.invalidate_cache(**kwargs)
        
        print(f"✅ Agent cache invalidation completed!")
        print(f"   Result: {result}")
        
        return {"success": True, "result": result}
        
    except Exception as e:
        print(f"❌ Error invalidating agent cache: {e}")
        return {"success": False, "error": str(e)}


async def get_cache_stats() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        print("📊 Retrieving cache statistics...")
        stats = AgentConfigLoader.get_cache_stats()
        
        print(f"✅ Cache statistics retrieved!")
        print(f"   Statistics: {json.dumps(stats, indent=2)}")
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        print(f"❌ Error retrieving cache stats: {e}")
        return {"success": False, "error": str(e)}


async def full_cache_reset() -> Dict[str, Any]:
    """
    Perform a complete cache reset - clear caches, invalidate, and verify.
    
    Returns:
        Dictionary with complete operation results
    """
    print("🚀 Starting full cache reset operation...")
    print("=" * 50)
    
    results = {
        "initial_stats": None,
        "clear_result": None,
        "invalidate_result": None,
        "final_stats": None,
        "success": False
    }
    
    # 1. Get initial stats
    print("\n1️⃣ Getting initial cache statistics...")
    initial_result = await get_cache_stats()
    results["initial_stats"] = initial_result
    
    # 2. Clear agent caches
    print("\n2️⃣ Clearing agent caches...")
    clear_result = await clear_agent_caches()
    results["clear_result"] = clear_result
    
    # 3. Invalidate caches
    print("\n3️⃣ Invalidating agent caches...")
    invalidate_result = await invalidate_agent_cache()
    results["invalidate_result"] = invalidate_result
    
    # 4. Get final stats
    print("\n4️⃣ Getting final cache statistics...")
    final_result = await get_cache_stats()
    results["final_stats"] = final_result
    
    # 5. Evaluate success
    success = (
        clear_result.get("success", False) and
        invalidate_result.get("success", False) and
        final_result.get("success", False)
    )
    results["success"] = success
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   Initial stats: {'✅' if initial_result.get('success') else '❌'}")
    print(f"   Cache clear: {'✅' if clear_result.get('success') else '❌'}")
    print(f"   Cache invalidate: {'✅' if invalidate_result.get('success') else '❌'}")
    print(f"   Final stats: {'✅' if final_result.get('success') else '❌'}")
    print(f"   Overall success: {'✅' if success else '❌'}")
    
    if success:
        print("\n🎉 Full cache reset completed successfully!")
    else:
        print("\n⚠️ Some cache operations had issues. Check the details above.")
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cache management CLI for Agent C system"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Clear caches command
    clear_parser = subparsers.add_parser('clear', help='Clear agent configuration caches')
    
    # Invalidate cache command
    invalidate_parser = subparsers.add_parser('invalidate', help='Invalidate agent configuration caches')
    invalidate_parser.add_argument('--config-path', help='Specific config path to invalidate')
    invalidate_parser.add_argument('--default-model', help='Specific default model to invalidate')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get cache statistics')
    
    # Full reset command
    reset_parser = subparsers.add_parser('reset', help='Perform complete cache reset (clear + invalidate + verify)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'clear':
            result = asyncio.run(clear_agent_caches())
            sys.exit(0 if result.get("success") else 1)
            
        elif args.command == 'invalidate':
            result = asyncio.run(invalidate_agent_cache(
                config_path=args.config_path,
                default_model=args.default_model
            ))
            sys.exit(0 if result.get("success") else 1)
            
        elif args.command == 'stats':
            result = asyncio.run(get_cache_stats())
            sys.exit(0 if result.get("success") else 1)
            
        elif args.command == 'reset':
            result = asyncio.run(full_cache_reset())
            sys.exit(0 if result.get("success") else 1)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()