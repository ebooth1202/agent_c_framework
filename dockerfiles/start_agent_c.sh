#!/bin/bash
set -e

# Go to the directory containing this script
cd "$(dirname "$0")"

# Set environment variables for agent_c config and directories
export AGENT_C_CONFIG_PATH=$HOME/.agent_c
export AGENT_C_IMAGES_PATH=$HOME/.agent_c/images
export AGENT_C_PERSONAS_PATH=$HOME/.agent_c/personas

# Add mappings for workspace folders (Documents, Desktop, and Downloads)
export DOCUMENTS_WORKSPACE=$HOME/Documents
export DESKTOP_WORKSPACE=$HOME/Desktop
export DOWNLOADS_WORKSPACE=$HOME/Downloads

# Create directories if they don't exist
mkdir -p "$AGENT_C_CONFIG_PATH"
mkdir -p "$AGENT_C_IMAGES_PATH"
mkdir -p "$AGENT_C_PERSONAS_PATH"

# Check if config file exists
if [ ! -f "$AGENT_C_CONFIG_PATH/agent_c.config" ]; then
    cp agent_c.config.example "$AGENT_C_CONFIG_PATH/agent_c.config"
    echo "** Warning**:  Configuration file not found at $AGENT_C_CONFIG_PATH/agent_c.config"
    echo "An example configuration file is being copied to $AGENT_C_CONFIG_PATH"
    echo ""
    echo "Please edit the configuration file with a text editor and rerun this script."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Run in detached mode (background):
docker-compose -f docker-compose.yml -p agent_c up --build -d

# Wait a few seconds for the containers to start
sleep 5

# Open the browser to view Agent C
bash ./view_agent_c.sh