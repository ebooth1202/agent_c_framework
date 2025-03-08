@echo off
REM Script to generate requirements.txt for the base Docker image

setlocal enabledelayedexpansion

set "REPO_ROOT=%CD%"
set "OUTPUT_DIR=%REPO_ROOT%\dockerfiles\base\python"
set "OUTPUT_FILE=%OUTPUT_DIR%\requirements.txt"

REM Default subfolders to scan
set "SUBFOLDERS=agent_c_core agent_c_api_ui agent_c_tools"

if not "%~1"=="" (
    REM Override default subfolders if specified
    set "SUBFOLDERS="
    :parse_args
    if not "%~1"=="" (
        set "SUBFOLDERS=!SUBFOLDERS! %~1"
        shift
        goto :parse_args
    )
)

REM Run the dependency scanner with the specified subfolders
python "%REPO_ROOT%\ci\dependency_scanner.py" "%REPO_ROOT%" "%OUTPUT_FILE%" %SUBFOLDERS%

echo Base dependencies have been written to %OUTPUT_FILE%
echo You can now use this in your Dockerfile:
echo COPY requirements.txt /tmp/
echo RUN pip install --no-cache-dir -r /tmp/requirements.txt
