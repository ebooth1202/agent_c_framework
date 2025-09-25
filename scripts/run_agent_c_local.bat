@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)
CALL .venv\scripts\activate.bat
echo Launching API server in a new command window...
start cmd /k "scripts\start_api.bat"
echo Waiting a few to a allow server start...
timeout /t 12
echo Launching front end server in a new command window...
start cmd /k "scripts\start_realtime_client.bat"
echo Waiting a few to a allow server start...
timeout /t 3
start https://localhost:5173/chat
popd

ENDLOCAL
