#!/usr/bin/env python3
"""
Debug script to investigate AgentConfigLoader state for mystery world game master caching issues.
"""
import sys
import os

# Add the Agent C core to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src', 'agent_c_core', 'src'))

from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models.agent_config import AgentConfiguration
import json
import yaml
from pathlib import Path

def debug_agent_config_loader():
    """Investigate AgentConfigLoader state for mystery world game master debugging."""
    
    print("=" * 80)
    print("AGENT CONFIG LOADER DEBUG INVESTIGATION")
    print("=" * 80)
    
    # Initialize the loader with the agent config path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, "agent_c_config")
    print(f"Initializing AgentConfigLoader with config_path: {config_path}")
    
    try:
        loader = AgentConfigLoader(config_path=config_path)
        print("✓ AgentConfigLoader initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize AgentConfigLoader: {e}")
        return
    
    print("\n" + "-" * 60)
    print("1. CHECKING CATALOG KEYS")
    print("-" * 60)
    
    try:
        catalog = loader.catalog
        catalog_keys = list(catalog.keys())
        print(f"Total agents in catalog: {len(catalog_keys)}")
        print(f"Catalog keys: {catalog_keys}")
        
        # Look for mystery world related agents
        mystery_agents = [key for key in catalog_keys if 'mystery' in key.lower() or 'shadow_pines' in key.lower() or 'space_station' in key.lower() or 'victorian' in key.lower()]
        print(f"\nMystery world related agents found: {mystery_agents}")
        
    except Exception as e:
        print(f"✗ Failed to get catalog: {e}")
        return
    
    print("\n" + "-" * 60)
    print("2. MIGRATION REPORT")
    print("-" * 60)
    
    try:
        migration_report = loader.get_migration_report()
        print("Migration report:")
        print(json.dumps(migration_report, indent=2, default=str))
    except Exception as e:
        print(f"✗ Failed to get migration report: {e}")
    
    print("\n" + "-" * 60)
    print("3. LOADING SPECIFIC MYSTERY WORLD AGENTS")
    print("-" * 60)
    
    target_agents = [
        'shadow_pines_game_master',
        'space_station_game_master',
        'victorian_game_master',
        'mystery_world_director'  # for comparison
    ]
    
    loaded_agents = {}
    
    for agent_name in target_agents:
        print(f"\nAttempting to load agent: {agent_name}")
        try:
            agent_config = loader._fetch_agent_config(agent_name)
            if agent_config:
                loaded_agents[agent_name] = agent_config
                print(f"✓ Successfully loaded {agent_name}")
                print(f"  - Agent ID: {agent_config.agent_id}")
                print(f"  - Version: {getattr(agent_config, 'version', 'unknown')}")
                print(f"  - Model: {getattr(agent_config, 'model', 'unknown')}")
            else:
                print(f"✗ Agent {agent_name} returned None")
        except Exception as e:
            print(f"✗ Failed to load {agent_name}: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
    
    print("\n" + "-" * 60)
    print("4. COMPARING WITH MYSTERY_WORLD_DIRECTOR")
    print("-" * 60)
    
    if 'mystery_world_director' in loaded_agents:
        director_config = loaded_agents['mystery_world_director']
        print("mystery_world_director config details:")
        print(f"  - Agent ID: {director_config.agent_id}")
        print(f"  - Version: {getattr(director_config, 'version', 'unknown')}")
        print(f"  - Model: {getattr(director_config, 'model', 'unknown')}")
        
        # Compare structure with other loaded agents
        print("\nComparison with game masters:")
        for name, config in loaded_agents.items():
            if name != 'mystery_world_director':
                print(f"\n{name}:")
                print(f"  - Agent ID: {config.agent_id}")
                print(f"  - Version: {getattr(config, 'version', 'unknown')}")
                print(f"  - Model: {getattr(config, 'model', 'unknown')}")
                
                # Check if they have similar structures
                director_attrs = set(dir(director_config))
                config_attrs = set(dir(config))
                missing_attrs = director_attrs - config_attrs
                extra_attrs = config_attrs - director_attrs
                
                if missing_attrs:
                    print(f"  - Missing attributes (vs director): {missing_attrs}")
                if extra_attrs:
                    print(f"  - Extra attributes (vs director): {extra_attrs}")
    
    print("\n" + "-" * 60)
    print("5. FILE SYSTEM VERIFICATION")
    print("-" * 60)
    
    agents_dir = Path(config_path) / "agents"
    print(f"Checking agents directory: {agents_dir}")
    
    for agent_name in target_agents:
        yaml_file = agents_dir / f"{agent_name}.yaml"
        print(f"\nChecking file: {yaml_file}")
        if yaml_file.exists():
            print(f"✓ File exists: {yaml_file}")
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    print(f"  - YAML loads successfully")
                    print(f"  - Agent ID in file: {data.get('agent_id', 'missing')}")
                    print(f"  - Version in file: {data.get('version', 'missing')}")
            except Exception as e:
                print(f"  ✗ Failed to parse YAML: {e}")
        else:
            print(f"✗ File does not exist: {yaml_file}")
    
    print("\n" + "-" * 60)
    print("6. CACHE STATISTICS")
    print("-" * 60)
    
    try:
        cache_stats = loader.get_cache_stats()
        print("Cache statistics:")
        print(json.dumps(cache_stats, indent=2, default=str))
    except Exception as e:
        print(f"✗ Failed to get cache stats: {e}")
    
    print("\n" + "=" * 80)
    print("DEBUG INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    debug_agent_config_loader()