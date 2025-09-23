#!/bin/bash

echo "🚀 Agent C API Server Startup (HTTP Mode)"
echo "=========================================="

cd "$(dirname "$0")/.."
echo "📁 Working directory: $(pwd)"

# Run the Python startup script
python .scratch/start_server_http.py