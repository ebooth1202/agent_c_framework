@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%
CALL .venv\scripts\activate
:: Install the requirements
echo Installing dependencies.
python -m pip install --upgrade pip

cd src
pip install ace_proto/ts_tool-0.1.0-py3-none-any.whl
pip install -e agent_c_core
pip install -e agent_c_tools
playwright install
pip install -e agent_c_api_ui/agent_c_api[dev]
pip install -e ..\test\unit\agent_c_tools

echo Installing dependencies for realtime client and performing a clean build...
cd ..\..\realtime_client
call scripts\rebuild.bat
if errorlevel 1 (
    echo Failed to install the packages.
    popd
    exit /b 1
)

:: Return to the original directory
popd

ENDLOCAL
