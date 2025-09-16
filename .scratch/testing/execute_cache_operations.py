#!/usr/bin/env python3
"""
Simple wrapper to execute cache clearing operations for the mystery world caching issue.
This script executes the specific operations requested by the prime agent.
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Execute the cache clearing operations as requested."""
    print("=== Agent Cache Clearing Operations (Mystery World Fix) ===")
    print("Executing cache operations requested by prime agent...")
    print()
    
    # Get the path to our cache CLI script
    cache_cli_script = Path(__file__).parent / "cache_cli.py"
    
    if not cache_cli_script.exists():
        print(f"❌ Cache CLI script not found at {cache_cli_script}")
        return 1
    
    try:
        # Execute the full reset operation which includes:
        # 1. Get initial cache stats
        # 2. Execute AgentConfigLoader.clear_agent_caches()
        # 3. Execute AgentConfigLoader.invalidate_cache()
        # 4. Get final cache stats for verification
        print("🚀 Executing full cache reset operation...")
        
        result = subprocess.run([
            sys.executable, str(cache_cli_script), "reset"
        ], capture_output=False, text=True)
        
        print()
        if result.returncode == 0:
            print("✅ All cache clearing operations completed successfully!")
            print("📋 Operations executed:")
            print("   ✓ AgentConfigLoader.clear_agent_caches()")
            print("   ✓ AgentConfigLoader.invalidate_cache()")
            print("   ✓ AgentConfigLoader.get_cache_stats() (verification)")
        else:
            print("❌ Some cache clearing operations failed!")
            print(f"   Exit code: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error executing cache operations: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)