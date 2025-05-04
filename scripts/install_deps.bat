@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Install the requirements
echo Installing dependencies.
cd src
pip install ace_proto/ts_tool-0.1.0-py3-none-any.whl
pip install -e agent_c_core
pip install -e agent_c_tools
pip install -e agent_c_api_ui/agent_c_api[dev]
pip install -e ..\test\unit\agent_c_tools


if errorlevel 1 (
    echo Failed to install the required python packages.
    popd
    exit /b 1
)

:: Install NPM packages
echo Installing NPM dependencies...
cd agent_c_api_ui\agent_c_react_client
npm install

if errorlevel 1 (
    echo Failed to install the NPM packages.
    popd
    exit /b 1
)

:: Return to the original directory
popd

ENDLOCAL
