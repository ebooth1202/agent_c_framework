@echo off
SETLOCAL

:: Install the requirements
echo Installing dependencies.
cd src
pip install -e agent_c_core
pip install -e agent_c_tools
pip install -e my_agent_c
pip install -e agent_c_reference_apps


if errorlevel 1 (
    echo Failed to install the required packages.
    exit /b 1
)

ENDLOCAL
