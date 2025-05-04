@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)

:: Start the backend server (in a new window)
start cmd /k ".venv\scripts\activate.bat && python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8000 --log-level info"
:: Start RAG Backend
:: start cmd /k ".venv\scripts\activate.bat && python -m uvicorn agent_c_rag_api.main:app --host 0.0.0.0 --port 8001 --log-level info"
:: Start the frontend dev server (in a new window)
start cmd /k "cd src\agent_c_api_ui\agent_c_react_client && npm run dev"

:: Return to original directory
popd

ENDLOCAL