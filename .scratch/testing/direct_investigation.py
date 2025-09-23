#!/usr/bin/env python3
"""
Direct investigation of agent config files without importing AgentConfigLoader.
"""
import os
import yaml
from pathlib import Path
import json

def investigate_agent_configs():
    """Directly investigate agent configuration files."""
    
    print("=" * 80)
    print("DIRECT AGENT CONFIG INVESTIGATION")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent.absolute()
    config_path = project_root / "agent_c_config" / "agents"
    
    print(f"Project root: {project_root}")
    print(f"Config path: {config_path}")
    print(f"Config path exists: {config_path.exists()}")
    
    if not config_path.exists():
        print("✗ Config path does not exist!")
        return
    
    print("\n" + "-" * 60)
    print("1. DISCOVERING AGENT FILES")
    print("-" * 60)
    
    # Find all YAML files in the agents directory
    yaml_files = list(config_path.glob("*.yaml"))
    print(f"Found {len(yaml_files)} YAML files")
    
    mystery_files = [f for f in yaml_files if any(term in f.stem.lower() for term in ['mystery', 'shadow_pines', 'space_station', 'victorian'])]
    print(f"\nMystery-related files: {[f.stem for f in mystery_files]}")
    
    print("\n" + "-" * 60)
    print("2. EXAMINING SPECIFIC TARGET AGENTS")
    print("-" * 60)
    
    target_agents = [
        'shadow_pines_game_master',
        'space_station_game_master',
        'victorian_game_master',
        'mystery_world_director'
    ]
    
    agent_data = {}
    
    for agent_name in target_agents:
        yaml_file = config_path / f"{agent_name}.yaml"
        print(f"\n--- {agent_name} ---")
        print(f"File path: {yaml_file}")
        print(f"File exists: {yaml_file.exists()}")
        
        if yaml_file.exists():
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    agent_data[agent_name] = data
                    print(f"✓ Successfully loaded YAML")
                    print(f"  - Agent ID/Key: {data.get('key', data.get('agent_id', 'missing'))}")
                    print(f"  - Name: {data.get('name', 'missing')}")
                    print(f"  - Version: {data.get('version', 'missing')}")
                    print(f"  - Model: {data.get('model_id', data.get('model', 'missing'))}")
                    print(f"  - Tools: {data.get('tools', 'missing')}")
                    
                    # Check for any special fields or configuration
                    special_fields = ['categories', 'prompt_metadata', 'agent_params']
                    for field in special_fields:
                        if field in data:
                            print(f"  - {field}: {type(data[field])}")
                            
            except Exception as e:
                print(f"✗ Failed to load YAML: {e}")
                import traceback
                print(f"  Traceback: {traceback.format_exc()}")
        else:
            print("✗ File does not exist")
    
    print("\n" + "-" * 60)
    print("3. STRUCTURE COMPARISON")
    print("-" * 60)
    
    if len(agent_data) > 1:
        # Compare structure of loaded agents
        all_keys = set()
        for data in agent_data.values():
            all_keys.update(data.keys())
        
        print(f"All unique keys across configs: {sorted(all_keys)}")
        
        print("\nKey presence matrix:")
        print(f"{'Agent':<25} | " + " | ".join(f"{key:<15}" for key in sorted(all_keys)))
        print("-" * (25 + len(all_keys) * 18))
        
        for agent_name, data in agent_data.items():
            row = f"{agent_name:<25} | "
            for key in sorted(all_keys):
                present = "✓" if key in data else "✗"
                row += f"{present:<15} | "
            print(row)
    
    print("\n" + "-" * 60)
    print("4. FILE SYSTEM INTEGRITY CHECK")
    print("-" * 60)
    
    # Check for any obvious file system issues
    all_yaml_files = list(config_path.glob("*.yaml"))
    print(f"Total YAML files in directory: {len(all_yaml_files)}")
    
    # Check for duplicates or naming issues
    file_stems = [f.stem for f in all_yaml_files]
    duplicates = [stem for stem in file_stems if file_stems.count(stem) > 1]
    if duplicates:
        print(f"✗ Duplicate file stems found: {duplicates}")
    else:
        print("✓ No duplicate file names found")
    
    # Check for files that might be related to mystery world but not in our target list
    other_mystery_files = [f.stem for f in all_yaml_files if any(term in f.stem.lower() for term in ['mystery', 'shadow', 'space', 'victorian']) and f.stem not in target_agents]
    if other_mystery_files:
        print(f"Other mystery-related files found: {other_mystery_files}")
    
    print("\n" + "-" * 60)
    print("5. YAML VALIDATION")
    print("-" * 60)
    
    # Validate YAML structure for common issues
    for agent_name, data in agent_data.items():
        print(f"\n--- Validating {agent_name} ---")
        
        # Check required fields for agent configs
        required_fields = ['key', 'name', 'model_id', 'version']
        missing_required = [field for field in required_fields if field not in data and (field != 'key' or 'agent_id' not in data)]
        
        if missing_required:
            print(f"✗ Missing required fields: {missing_required}")
        else:
            print("✓ All required fields present")
        
        # Check for common configuration issues
        if 'tools' in data and not isinstance(data['tools'], list):
            print(f"✗ Tools field is not a list: {type(data['tools'])}")
        elif 'tools' in data:
            print(f"✓ Tools field is properly formatted list with {len(data['tools'])} items")
        
        if 'version' in data and not isinstance(data['version'], int):
            print(f"✗ Version field is not an integer: {type(data['version'])}")
        else:
            print(f"✓ Version field is properly formatted")
    
    print("\n" + "=" * 80)
    print("DIRECT INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    investigate_agent_configs()