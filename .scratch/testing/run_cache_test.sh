#!/bin/bash
# Script to run the AgentConfigLoader cache test

echo "Running AgentConfigLoader cache test..."
echo "Project directory: $(pwd)"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
    echo "Python version: $(python --version)"
    echo "Python path: $(which python)"
else
    echo "⚠️  No virtual environment found at .venv/bin/activate"
    echo "Using system Python: $(which python)"
fi

echo "
Executing: python .scratch/test_agent_config_cache.py
"

# Run the test script
python .scratch/test_agent_config_cache.py