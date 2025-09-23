#!/usr/bin/env python3
"""
Quick test to verify the realtime session import is working
"""

import sys
import os

# Add the agent_c_api source path to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent_c_api_path = os.path.join(project_root, 'src', 'agent_c_api_ui', 'agent_c_api', 'src')
agent_c_core_path = os.path.join(project_root, 'src', 'agent_c_core', 'src')
agent_c_tools_path = os.path.join(project_root, 'src', 'agent_c_tools', 'src')

for path in [agent_c_api_path, agent_c_core_path, agent_c_tools_path]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

print("🧪 Testing realtime API imports...")

try:
    from agent_c_api.api.rt.session import router
    print("✅ SUCCESS: Realtime session router imported successfully!")
    
    from agent_c_api.api.rt import router as rt_router
    print("✅ SUCCESS: Main realtime router imported successfully!")
    
    print("🎉 Import fix is working! The realtime API should now be accessible.")
    
except Exception as e:
    print(f"❌ FAILED: Import still failing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)