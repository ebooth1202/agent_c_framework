#!/bin/bash
cd src/agent_c_api_ui/agent_c_api
uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8001 --reload
