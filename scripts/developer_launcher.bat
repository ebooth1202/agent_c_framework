@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)
CALL .venv\scripts\activate.bat
start cmd /k "scripts\start_api.bat"
start cmd /k "scripts\start_fe.bat"
:: Return to original directory
popd

ENDLOCAL
