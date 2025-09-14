# !/bin/bash


# Set workspace configuration file paths

export LOCAL_WORKSPACES_FILE=/Users/ethanbooth/agent_c_framework/local_workspaces.json
export COMPOSE_WORKSPACES_FILE=/Users/ethanbooth/agent_c_framework/compose_workspaces.json
export AGENT_C_WORKSPACE_CONFIG=/Users/ethanbooth/agent_c_framework/local_workspaces.json
export WORKSPACE_CONFIG_DIR=/Users/ethanbooth/agent_c_framework/

# Start the API server

python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8000 --log-level info --ssl-keyfile agent_c_config/localhost_self_signed-key.pem --ssl-certfile agent_c_config/localhost_self_signed.pem
