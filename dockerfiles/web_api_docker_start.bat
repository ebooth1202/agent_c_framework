@echo off
SETLOCAL

:: Change to the directory containing this script
cd /d "%~dp0"

:: Build and start the containers in attached mode
:: docker-compose -f docker-compose.yml up --build

:: Run in detached mode (background):
docker-compose -f docker-compose.yml up --build -d

ENDLOCAL
