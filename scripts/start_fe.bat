@echo off
SETLOCAL

:: Check if port parameter is provided
IF "%1"=="" (
    SET PORT=5173
) ELSE (
    SET PORT=%1
)

SET VITE_API_URL=http://localhost:8000/api/v1
SET VITE_RAG_API_URL=http://localhost:8001/api/v1
cd src\agent_c_api_ui\agent_c_react_client

:: Run vite with the specified port
npx vite --port %PORT%
