#!/bin/bash

echo "🚀 Setting up demo users for Agent C API"
echo "========================================"

cd "$(dirname "$0")/.."

# Set up Python path
export PYTHONPATH="$PWD/src/agent_c_api_ui/agent_c_api/src:$PYTHONPATH"

echo "📁 Working directory: $(pwd)"
echo "🐍 PYTHONPATH: $PYTHONPATH"

echo ""
echo "👥 Creating demo users using CLI..."

# Use the existing CLI to create demo users
python src/agent_c_api_ui/agent_c_api/src/agent_c_api/cli/users.py create-demo

echo ""
echo "🧪 Testing authentication with demo credentials..."

# Test the demo user
echo "Testing demo/password123:"
curl -X POST http://localhost:8001/api/rt/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123"}' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "Testing admin/admin123:"
curl -X POST http://localhost:8001/api/rt/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -w "\nStatus: %{http_code}\n"