@echo off
SETLOCAL

IF "%1"=="" (
    SET PORT=8000
) ELSE (
    SET PORT=%1
)

python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port %PORT%
PORT% --log-level info