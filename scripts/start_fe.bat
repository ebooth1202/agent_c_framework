@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)

IF "%1"=="" (
    SET PORT=5173
) ELSE (
    SET PORT=%1
)

IF "%2"=="" (
    SET API_PORT=8000
) ELSE (
    SET API_PORT=%2
)

IF "%3"=="" (
    SET RAG_PORT=8001
) ELSE (
    SET RAG_PORT=%2
)

SET VITE_API_URL=https://localhost:%API_PORT%/api/v1
SET VITE_RAG_API_URL=https://localhost:%RAG_PORT%/api/v1
cd src\agent_c_api_ui\agent_c_react_client

:: Run vite with the specified port
npx vite --port %PORT%
