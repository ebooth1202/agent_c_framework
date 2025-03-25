import sys
import os

# Base project directory
base_dir = os.path.dirname(__file__)

# Add the main src directory to the path
sys.path.insert(0, os.path.join(base_dir, 'src'))

# Add the agent_c_tools/src directory to the path
sys.path.insert(0, os.path.join(base_dir, 'src', 'agent_c_tools', 'src'))

# Add the agent_c_api path
sys.path.insert(0, os.path.join(base_dir, 'src', 'agent_c_api_ui', 'agent_c_api', 'src'))

# Add the agent_c path
sys.path.insert(0, os.path.join(base_dir, 'src', 'agent_c_core', 'src'))

# Add the agent_c path
#sys.path.insert(0, os.path.join(base_dir, 'src', 'agent_c_reference_apps', 'src'))
