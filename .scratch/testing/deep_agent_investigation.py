#!/usr/bin/env python3
"""
Deep investigation into why game masters aren't loading after cache clearing
"""

import sys
import os
import yaml

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_core', 'src'))

def deep_investigation():
    print("=== DEEP AGENT INVESTIGATION ===")
    
    # Check if agent files exist and are parseable
    print("\n1. Direct YAML File Validation:")
    agent_files = [
        "agent_c_config/agents/shadow_pines_game_master.yaml",
        "agent_c_config/agents/space_station_game_master.yaml", 
        "agent_c_config/agents/victorian_game_master.yaml",
        "agent_c_config/agents/mystery_world_director.yaml"
    ]
    
    for agent_file in agent_files:
        full_path = os.path.join("../..", agent_file)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    key = config.get('key', 'NO KEY')
                    version = config.get('version', 'NO VERSION')
                    tools = config.get('tools', [])
                    print(f"   ✅ {os.path.basename(agent_file)}: key='{key}' version={version} tools={len(tools)}")
            except Exception as e:
                print(f"   ❌ {os.path.basename(agent_file)}: YAML parse error - {e}")
        else:
            print(f"   ❌ {os.path.basename(agent_file)}: FILE NOT FOUND")
    
    # Try to import and investigate AgentConfigLoader
    print("\n2. AgentConfigLoader Investigation:")
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        # Check if we can create an instance
        print("   Creating AgentConfigLoader instance...")
        loader = AgentConfigLoader()
        print("   ✅ AgentConfigLoader instance created successfully")
        
        # Try to list what agents it knows about
        if hasattr(loader, 'catalog'):
            catalog_keys = list(loader.catalog.keys()) if loader.catalog else []
            print(f"   📋 Agents in catalog: {catalog_keys}")
            
            # Check specifically for our mystery world agents
            mystery_agents = [key for key in catalog_keys if any(mystery in key for mystery in ['shadow_pines', 'space_station', 'victorian', 'mystery_world'])]
            print(f"   🎭 Mystery world agents in catalog: {mystery_agents}")
        else:
            print("   ⚠️  No 'catalog' attribute found on AgentConfigLoader")
            
        # Try to load specific agents
        print("\n   Attempting to load specific agents:")
        target_agents = ['shadow_pines_game_master', 'space_station_game_master', 'victorian_game_master', 'mystery_world_director']
        
        for agent_key in target_agents:
            try:
                # Try different loading methods
                config = None
                method_used = "unknown"
                
                if hasattr(loader, 'get_agent_config'):
                    config = loader.get_agent_config(agent_key)
                    method_used = "get_agent_config"
                elif hasattr(loader, 'load_agent_config'):
                    config = loader.load_agent_config(agent_key) 
                    method_used = "load_agent_config"
                elif hasattr(loader, '_fetch_agent_config'):
                    config = loader._fetch_agent_config(agent_key)
                    method_used = "_fetch_agent_config"
                    
                if config:
                    version = getattr(config, 'version', 'no version attr')
                    name = getattr(config, 'name', 'no name attr') 
                    print(f"      ✅ {agent_key}: Loaded via {method_used} - version={version}, name={name}")
                else:
                    print(f"      ❌ {agent_key}: No config returned by {method_used}")
                    
            except Exception as e:
                print(f"      ❌ {agent_key}: Exception during loading - {e}")
        
    except ImportError as e:
        print(f"   ❌ Failed to import AgentConfigLoader: {e}")
        
    # Check for any agent-related environment variables
    print("\n3. Environment Check:")
    agent_env_vars = [var for var in os.environ.keys() if 'AGENT' in var.upper() or 'CONFIG' in var.upper()]
    if agent_env_vars:
        print(f"   Agent-related environment variables: {agent_env_vars}")
        for var in agent_env_vars:
            print(f"      {var} = {os.environ[var]}")
    else:
        print("   No agent-related environment variables found")
        
    # Try to find other config files or registries
    print("\n4. Configuration System Investigation:")
    config_paths = [
        "agent_c_config",
        ".agent_c.meta.yaml", 
        "local_workspaces.json",
        "compose_workspaces.json"
    ]
    
    for config_path in config_paths:
        full_path = os.path.join("../..", config_path)
        if os.path.exists(full_path):
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:200]  # First 200 chars
                        print(f"   📄 {config_path}: EXISTS (preview: {repr(content)}...)")
                except Exception as e:
                    print(f"   📄 {config_path}: EXISTS but unreadable - {e}")
            else:
                print(f"   📁 {config_path}: EXISTS (directory)")
        else:
            print(f"   ❌ {config_path}: NOT FOUND")

if __name__ == "__main__":
    deep_investigation()
    print("\n✅ Deep investigation completed")