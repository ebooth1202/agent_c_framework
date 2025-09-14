#!/usr/bin/env python3
"""
Phase 3: Cache Investigation & System Analysis
Based on mystery_world_final_configuration_complete.md
"""

import sys
import os
import glob

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_core', 'src'))

def run_phase3_investigation():
    print("=== Phase 3: Cache Investigation & System Analysis ===")
    
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        print("\n1. Checking Agent Config Loader Status:")
        loader = AgentConfigLoader()
        catalog = loader.catalog if hasattr(loader, 'catalog') else {}
        print(f"   Agents in catalog: {list(catalog.keys())}")
        
        # Check migration report
        try:
            migration_report = loader.get_migration_report() if hasattr(loader, 'get_migration_report') else None
            print(f"   Migration report: {migration_report}")
        except Exception as e:
            print(f"   Migration report not available: {e}")
        
    except ImportError as e:
        print(f"❌ Failed to import AgentConfigLoader: {e}")
        return False
        
    print("\n2. Verifying File Discovery:")
    agent_folder = os.path.join(os.path.dirname(__file__), "..", "agent_c_config", "agents")
    if os.path.exists(agent_folder):
        files = glob.glob(os.path.join(agent_folder, "**/*.yaml"), recursive=True)
        mystery_files = [f for f in files if any(name in f for name in ['shadow_pines', 'space_station', 'victorian'])]
        print(f"   Mystery world agent files found:")
        for f in mystery_files:
            print(f"   - {f}")
            # Check if file exists and is readable
            if os.path.exists(f) and os.path.isfile(f):
                print(f"     ✅ File exists and is readable")
            else:
                print(f"     ❌ File access issue")
    else:
        print(f"   ❌ Agent config folder not found at: {agent_folder}")
    
    print("\n3. Checking Configuration Loading:")
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        loader = AgentConfigLoader()
        
        for agent_key in ['shadow_pines_game_master', 'space_station_game_master', 'victorian_game_master']:
            try:
                # Try different loading methods that might exist
                if hasattr(loader, '_fetch_agent_config'):
                    config = loader._fetch_agent_config(agent_key)
                elif hasattr(loader, 'get_agent_config'):
                    config = loader.get_agent_config(agent_key)
                elif hasattr(loader, 'load_agent_config'):
                    config = loader.load_agent_config(agent_key)
                else:
                    config = None
                    print(f"   {agent_key}: No loading method found")
                    continue
                    
                if config:
                    version = getattr(config, 'version', 'unknown') if config else 'Failed to load'
                    print(f"   {agent_key}: Version {version}")
                else:
                    print(f"   {agent_key}: Failed to load (config is None)")
                    
            except Exception as e:
                print(f"   {agent_key}: Error - {e}")
    except Exception as e:
        print(f"   Error in configuration loading test: {e}")
    
    return True

if __name__ == "__main__":
    success = run_phase3_investigation()
    if success:
        print("\n✅ Phase 3 investigation completed")
    else:
        print("\n❌ Phase 3 investigation had critical errors")
        sys.exit(1)