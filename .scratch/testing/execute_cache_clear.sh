#!/bin/bash
"""
Shell script to execute the agent cache clearing operations.
This activates the virtual environment and runs the Python cache clearing script.
"""

echo "=== Agent Cache Clearing Execution Script ==="
echo "Activating virtual environment and executing cache clearing operations..."
echo

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Set PYTHONPATH to include the agent_c_core source
export PYTHONPATH="$PROJECT_ROOT/src/agent_c_core/src:$PYTHONPATH"

echo "Virtual environment activated"
echo "PYTHONPATH set to: $PYTHONPATH"
echo

# Execute the cache clearing script
python "$PROJECT_ROOT/.scratch/clear_agent_caches.py"

RESULT=$?

echo
echo "Cache clearing script completed with exit code: $RESULT"

if [ $RESULT -eq 0 ]; then
    echo "✓ Cache clearing operations were successful!"
else
    echo "✗ Cache clearing operations encountered errors!"
fi

echo
echo "=== Execution Complete ==="