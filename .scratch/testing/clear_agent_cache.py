#!/usr/bin/env python3
"""
Script to clear Agent C configuration caches and verify configuration loading.
"""

import os
import sys
from pathlib import Path

# Add the agent_c_core to Python path
project_root = Path(__file__).parent.parent
agent_c_core_path = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(agent_c_core_path))

try:
    from agent_c.config.agent_config_loader import AgentConfigLoader
    from agent_c.config.config_loader import ConfigLoader
    
    print("🧹 Clearing Agent C Configuration Caches...")
    
    # Clear all caches
    agent_results = AgentConfigLoader.clear_agent_caches()
    config_results = ConfigLoader.clear_path_cache()
    
    print(f"✅ Agent config cache cleared: {agent_results}")
    print(f"✅ Path resolution cache cleared: {config_results} entries")
    
    # Force reload with explicit path
    config_path = str(project_root / "agent_c_config")
    print(f"🔍 Using config path: {config_path}")
    
    # Create new loader instance
    loader = AgentConfigLoader(config_path=config_path)
    
    # Get catalog
    catalog = loader.catalog
    print(f"📋 Found {len(catalog)} total agents")
    
    # Filter for domo agents (what UI shows)
    domo_agents = [agent for agent in catalog.values() if 'domo' in (agent.category or [])]
    print(f"🎭 Found {len(domo_agents)} domo agents:")
    
    for agent in domo_agents:
        print(f"  - {agent.key}: {agent.name}")
        
    # Check for the specific agent
    if 'agent_c_realtime_lead' in catalog:
        agent = catalog['agent_c_realtime_lead']
        print(f"✅ Found agent_c_realtime_lead: {agent.name}")
        print(f"   Categories: {agent.category}")
    else:
        print("❌ agent_c_realtime_lead NOT found in catalog")
        
    print("\n🔧 Cache clearing complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root with the virtual environment activated")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()