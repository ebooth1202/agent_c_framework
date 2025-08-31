@echo off
SETLOCAL

IF "%1"=="" (
    SET PORT=8000
) ELSE (
    SET PORT=%1
)

python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port %PORT% --log-level info --ssl-keyfile agent_c_config/localhost_self_signed-key.pem --ssl-certfile agent_c_config/localhost_self_signed.pem
pause