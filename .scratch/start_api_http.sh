#!/bin/bash
# HTTP version of the API startup script for testing
# This removes the SSL configuration to run on plain HTTP

cd "$(dirname "$0")/.."

echo "🚀 Starting Agent C API server on HTTP (port 8000)..."
echo "📁 Working directory: $(pwd)"
echo "🔧 Testing imports first..."

# Test imports before starting server
python .scratch/test_imports.py
if [ $? -ne 0 ]; then
    echo "❌ Import test failed - cannot start server"
    exit 1
fi

echo "✅ Imports successful - starting server..."

# Set Python path to include Agent C API
export PYTHONPATH="$PWD/src/agent_c_api_ui/agent_c_api/src:$PYTHONPATH"

# Start server without SSL
python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8000 --log-level info