#!/usr/bin/env python3
"""
Test script to actually import and use AgentConfigLoader to investigate caching issues.
"""
import os
import sys
from pathlib import Path

def test_agent_config_loader():
    print("=" * 80)
    print("TESTING AGENTCONFIGLOADER DIRECTLY")
    print("=" * 80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent.absolute()
    agent_c_path = project_root / "src" / "agent_c_core" / "src"
    config_path = project_root / "agent_c_config"
    
    print(f"Project root: {project_root}")
    print(f"Agent C path: {agent_c_path}")
    print(f"Config path: {config_path}")
    print(f"Agent C path exists: {agent_c_path.exists()}")
    print(f"Config path exists: {config_path.exists()}")
    
    # Add to Python path
    sys.path.insert(0, str(agent_c_path))
    
    try:
        print("\n1. TESTING IMPORTS")
        print("-" * 40)
        
        # Test basic imports first
        print("Importing agent_c.config.agent_config_loader...")
        from agent_c.config.agent_config_loader import AgentConfigLoader
        print("✅ Successfully imported AgentConfigLoader")
        
        print("\n2. TESTING INSTANTIATION") 
        print("-" * 40)
        
        print(f"Creating AgentConfigLoader with config_path: {config_path}")
        loader = AgentConfigLoader(config_path=str(config_path))
        print("✅ Successfully created AgentConfigLoader instance")
        
        print("\n3. TESTING CATALOG ACCESS")
        print("-" * 40)
        
        print("Accessing loader.catalog...")
        catalog = loader.catalog
        print(f"✅ Successfully accessed catalog with {len(catalog)} agents")
        
        # Show all catalog keys
        all_keys = sorted(catalog.keys())
        print(f"All catalog keys ({len(all_keys)}):")
        for i, key in enumerate(all_keys):
            print(f"  {i+1:2d}. {key}")
        
        # Look for mystery world agents specifically
        mystery_keys = [key for key in all_keys if any(term in key.lower() for term in ['mystery', 'shadow', 'space', 'victorian'])]
        print(f"\nMystery world related agents found ({len(mystery_keys)}):")
        for key in mystery_keys:
            print(f"  ✅ {key}")
            
        print("\n4. TESTING MIGRATION REPORT")
        print("-" * 40)
        
        migration_report = loader.get_migration_report()
        print("Migration report:")
        if migration_report:
            for key, value in migration_report.items():
                print(f"  {key}: {value}")
        else:
            print("  (Empty migration report)")
            
        print("\n5. TESTING SPECIFIC AGENT LOADING")
        print("-" * 40)
        
        target_agents = [
            'shadow_pines_game_master',
            'space_station_game_master', 
            'victorian_game_master',
            'mystery_world_director'
        ]
        
        for agent_name in target_agents:
            print(f"\nTesting agent: {agent_name}")
            try:
                # Check if in catalog first
                if agent_name in catalog:
                    print(f"  ✅ Found in catalog")
                    config = catalog[agent_name]
                    print(f"  ✅ Agent ID: {getattr(config, 'agent_id', getattr(config, 'key', 'unknown'))}")
                    print(f"  ✅ Version: {getattr(config, 'version', 'unknown')}")
                    print(f"  ✅ Name: {getattr(config, 'name', 'unknown')}")
                else:
                    print(f"  ❌ NOT found in catalog")
                    
                # Also try direct fetch
                direct_config = loader._fetch_agent_config(agent_name)
                if direct_config:
                    print(f"  ✅ Direct fetch successful")
                else:
                    print(f"  ❌ Direct fetch returned None")
                    
            except Exception as e:
                print(f"  ❌ Error loading {agent_name}: {e}")
                import traceback
                print(f"     {traceback.format_exc()}")
        
        print("\n6. TESTING CACHE STATISTICS")
        print("-" * 40)
        
        try:
            cache_stats = loader.get_cache_stats()
            print("Cache statistics:")
            for key, value in cache_stats.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"❌ Error getting cache stats: {e}")
        
        print("\n" + "=" * 80)
        print("AGENTCONFIGLOADER TEST COMPLETE")
        print("=" * 80)
        
        return loader, catalog
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

if __name__ == "__main__":
    test_agent_config_loader()