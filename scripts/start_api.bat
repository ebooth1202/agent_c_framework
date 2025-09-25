@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)

IF "%1"=="" (
    SET PORT=8000
) ELSE (
    SET PORT=%1
)
call .venv\scripts\activate.bat
echo Starting Agent C API on port %PORT% ...
python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port %PORT% --log-level info --ssl-keyfile agent_c_config/localhost_self_signed-key.pem --ssl-certfile agent_c_config/localhost_self_signed.pem
pause