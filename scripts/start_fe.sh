#!/bin/bash

export VITE_API_URL=http://localhost:8000/api/v1
export VITE_RAG_API_URL=http://localhost:8000/api/v1
cd src/agent_c_api_ui/agent_c_react_client
npm run dev