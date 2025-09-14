#!/usr/bin/env python3
"""
Test importing AgentConfigLoader and related components.
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test importing AgentConfigLoader step by step."""
    
    print("=" * 80)
    print("TESTING AGENT CONFIG LOADER IMPORTS")
    print("=" * 80)
    
    # Get project root and add to path
    project_root = Path(__file__).parent.parent.absolute()
    agent_c_path = project_root / "src" / "agent_c_core" / "src"
    
    print(f"Project root: {project_root}")
    print(f"Agent C path: {agent_c_path}")
    print(f"Agent C path exists: {agent_c_path.exists()}")
    
    if not agent_c_path.exists():
        print("✗ Agent C source path does not exist!")
        return
    
    sys.path.insert(0, str(agent_c_path))
    print("✓ Added Agent C to Python path")
    
    # Test imports step by step
    imports_to_test = [
        "agent_c",
        "agent_c.models",
        "agent_c.config", 
        "agent_c.util",
        "agent_c.models.agent_config",
        "agent_c.config.config_loader",
        "agent_c.config.model_config_loader",
        "agent_c.config.agent_config_loader"
    ]
    
    for import_name in imports_to_test:
        print(f"\nTesting import: {import_name}")
        try:
            module = __import__(import_name, fromlist=[''])
            print(f"✓ Successfully imported {import_name}")
            
            # If this is the agent config loader, try to instantiate it
            if import_name == "agent_c.config.agent_config_loader":
                try:
                    config_path = str(project_root / "agent_c_config")
                    AgentConfigLoader = getattr(module, 'AgentConfigLoader')
                    print(f"  ✓ Found AgentConfigLoader class")
                    
                    # Try to instantiate with the config path
                    loader = AgentConfigLoader(config_path=config_path)
                    print(f"  ✓ Successfully instantiated AgentConfigLoader")
                    
                    # Try basic operations
                    catalog = loader.catalog
                    print(f"  ✓ Successfully accessed catalog with {len(catalog)} agents")
                    
                    migration_report = loader.get_migration_report()
                    print(f"  ✓ Successfully got migration report")
                    
                    return loader  # Return for further testing
                    
                except Exception as e:
                    print(f"  ✗ Failed to use AgentConfigLoader: {e}")
                    import traceback
                    print(f"  Traceback: {traceback.format_exc()}")
                    
        except Exception as e:
            print(f"✗ Failed to import {import_name}: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            
    return None

def test_specific_agents(loader):
    """Test loading specific agents."""
    
    print("\n" + "=" * 80)
    print("TESTING SPECIFIC AGENT LOADING")
    print("=" * 80)
    
    target_agents = [
        'shadow_pines_game_master',
        'space_station_game_master',
        'victorian_game_master',
        'mystery_world_director'
    ]
    
    for agent_name in target_agents:
        print(f"\nTesting agent: {agent_name}")
        try:
            # Try different loading methods
            if hasattr(loader, '_fetch_agent_config'):
                config = loader._fetch_agent_config(agent_name)
                if config:
                    print(f"✓ Successfully loaded via _fetch_agent_config")
                    print(f"  - Agent ID: {getattr(config, 'agent_id', getattr(config, 'key', 'unknown'))}")
                    print(f"  - Version: {getattr(config, 'version', 'unknown')}")
                else:
                    print(f"✗ _fetch_agent_config returned None")
            
            # Check if it's in the catalog
            catalog = loader.catalog
            if agent_name in catalog:
                print(f"✓ Found in catalog")
            else:
                print(f"✗ Not found in catalog")
                print(f"  Available agents: {list(catalog.keys())}")
                
        except Exception as e:
            print(f"✗ Failed to load {agent_name}: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    loader = test_imports()
    if loader:
        test_specific_agents(loader)