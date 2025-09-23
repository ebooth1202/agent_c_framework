#!/usr/bin/env python3
"""
Investigation after configuration fixes to see current error status
"""

import sys
import os
import yaml

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_core', 'src'))

def post_fix_investigation():
    print("=== POST-FIX INVESTIGATION ===")
    
    # Check our corrected YAML files
    print("\n1. Verifying Fixed YAML Files:")
    agent_files = {
        "shadow_pines_game_master.yaml": "shadow_pines_game_master",
        "space_station_game_master.yaml": "space_station_game_master", 
        "victorian_game_master.yaml": "victorian_game_master",
        "mystery_world_director.yaml": "mystery_world_director"
    }
    
    for filename, agent_key in agent_files.items():
        filepath = os.path.join("../..", "agent_c_config", "agents", filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                # Check key fields
                key = config.get('key', 'MISSING')
                version = config.get('version', 'MISSING')
                categories = config.get('categories', 'NONE')  # Old field name
                category = config.get('category', 'NONE')     # New field name
                tools = config.get('tools', [])
                model_id = config.get('model_id', 'MISSING')
                
                print(f"   📄 {filename}:")
                print(f"      key: {key}")
                print(f"      version: {version}")
                print(f"      category: {category}")
                print(f"      categories: {categories}")
                print(f"      tools: {len(tools)} tools")
                print(f"      model_id: {model_id}")
                
            except Exception as e:
                print(f"   ❌ {filename}: YAML parse error - {e}")
        else:
            print(f"   ❌ {filename}: FILE NOT FOUND at {filepath}")
    
    # Try AgentConfigLoader with detailed error reporting
    print("\n2. Detailed AgentConfigLoader Testing:")
    try:
        from agent_c.config.agent_config_loader import AgentConfigLoader
        
        loader = AgentConfigLoader()
        print("   ✅ AgentConfigLoader created successfully")
        
        # Test loading each agent with error capture
        target_agents = ['shadow_pines_game_master', 'space_station_game_master', 'victorian_game_master', 'mystery_world_director']
        
        for agent_key in target_agents:
            print(f"\n   Testing {agent_key}:")
            try:
                # Try the most direct loading method we found working
                config = loader._fetch_agent_config(agent_key)
                if config:
                    print(f"      ✅ SUCCESS: Loaded successfully")
                    print(f"         Name: {getattr(config, 'name', 'no name')}")
                    print(f"         Version: {getattr(config, 'version', 'no version')}")
                    print(f"         Key: {getattr(config, 'key', 'no key')}")
                else:
                    print(f"      ❌ FAILED: No config returned")
            except Exception as e:
                print(f"      ❌ EXCEPTION: {type(e).__name__}: {str(e)}")
                # Try to get more details about validation errors
                if hasattr(e, 'errors') and callable(e.errors):
                    try:
                        errors = e.errors()
                        print(f"         Validation errors: {errors}")
                    except:
                        pass
        
    except ImportError as e:
        print(f"   ❌ Failed to import AgentConfigLoader: {e}")
    
    # Check system logs for any recent errors
    print("\n3. Recent System Activity:")
    log_files = [
        "../logs/agent_c_core.log",
        "../logs/agent_c_api.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Get last few lines of log file
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    
                print(f"   📋 {os.path.basename(log_file)} (last 10 lines):")
                for line in recent_lines:
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'shadow_pines', 'space_station', 'victorian']):
                        print(f"      {line.strip()}")
            except Exception as e:
                print(f"   ❌ Could not read {log_file}: {e}")
        else:
            print(f"   ❌ Log file not found: {log_file}")

if __name__ == "__main__":
    post_fix_investigation()
    print("\n✅ Post-fix investigation completed")