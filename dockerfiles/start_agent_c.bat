@echo off
SETLOCAL

:: Change to the directory containing this script
cd /d "%~dp0"

:: Run in detached mode (background):
docker-compose -f docker-compose.yml -p agent_c up --build -d

ENDLOCAL
