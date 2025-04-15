@echo off
SETLOCAL
SET VITE_API_URL=http://localhost:8000/api/v1
SET VITE_RAG_API_URL=http://localhost:8001/api/v1
cd src\agent_c_api_ui\agent_c_react_client
npm run dev