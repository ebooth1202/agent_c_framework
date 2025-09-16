#!/usr/bin/env python3
"""
Script to check what configuration path Agent C is actually using.
"""

import os
import sys
from pathlib import Path

# Add the agent_c_core to Python path
project_root = Path(__file__).parent.parent
agent_c_core_path = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(agent_c_core_path))

print("🔍 Agent C Configuration Path Diagnostics")
print("=" * 50)

print(f"📂 Current working directory: {os.getcwd()}")
print(f"📂 Project root: {project_root}")
print(f"📂 Expected config path: {project_root / 'agent_c_config'}")

# Check environment variable
env_path = os.environ.get("AGENT_C_CONFIG_PATH", None)
if env_path:
    print(f"🌍 AGENT_C_CONFIG_PATH environment variable: {env_path}")
else:
    print("🌍 AGENT_C_CONFIG_PATH environment variable: NOT SET")

try:
    from agent_c.config.config_loader import ConfigLoader
    
    # Test the path resolution
    loader = ConfigLoader()
    print(f"🎯 ConfigLoader resolved path: {loader.config_path}")
    
    # Check if the path exists and list contents
    config_path = Path(loader.config_path)
    if config_path.exists():
        print(f"✅ Config path exists")
        
        agents_path = config_path / "agents"
        if agents_path.exists():
            agent_files = list(agents_path.glob("*.yaml"))
            print(f"📋 Found {len(agent_files)} agent YAML files:")
            
            # Look for the specific agent
            realtime_lead_path = agents_path / "agent_c_realtime_lead.yaml"
            if realtime_lead_path.exists():
                print(f"✅ agent_c_realtime_lead.yaml found at: {realtime_lead_path}")
            else:
                print(f"❌ agent_c_realtime_lead.yaml NOT found")
                
            # List first 10 agents
            for i, agent_file in enumerate(sorted(agent_files)[:10]):
                print(f"  - {agent_file.name}")
            if len(agent_files) > 10:
                print(f"  ... and {len(agent_files) - 10} more")
        else:
            print(f"❌ Agents directory not found at: {agents_path}")
    else:
        print(f"❌ Config path does not exist: {config_path}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()