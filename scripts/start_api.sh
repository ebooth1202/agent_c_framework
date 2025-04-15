#!/bin/bash

# python src/agent_c_api_ui/agent_c_api/src/agent_c_api/main.py --host 0.0.0.0 --port 8000 --log-level info
python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8000 --log-level info