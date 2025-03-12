@echo off
SETLOCAL

:: Change to the directory containing this script
cd /d "%~dp0"

:: Set environment variables for agent_c config and directories
:: %USERPROFILE% is equivalent to HOME on Windows
set AGENT_C_CONFIG_PATH=%USERPROFILE%\.agent_c
set AGENT_C_IMAGES_PATH=%USERPROFILE%\.agent_c\images
set AGENT_C_PERSONAS_PATH=%USERPROFILE%\.agent_c\personas

:: Add mappings for workspace folders (Documents, Desktop, and Downloads)
set DOCUMENTS_WORKSPACE=%USERPROFILE%\Documents
set DESKTOP_WORKSPACE=%USERPROFILE%\Desktop
set DOWNLOADS_WORKSPACE=%USERPROFILE%\Downloads

:: Create directories if they don't exist
if not exist "%AGENT_C_CONFIG_PATH%" mkdir "%AGENT_C_CONFIG_PATH%"
if not exist "%AGENT_C_IMAGES_PATH%" mkdir "%AGENT_C_IMAGES_PATH%"
if not exist "%AGENT_C_PERSONAS_PATH%" mkdir "%AGENT_C_PERSONAS_PATH%"

:: Check if config file exists
if not exist "%AGENT_C_CONFIG_PATH%\agent_c.config" (
    copy agent_c.config.example "%AGENT_C_CONFIG_PATH%\agent_c.config"
    echo ** Warning**: Configuration file not found at %AGENT_C_CONFIG_PATH%\agent_c.config
    echo An example file has been added to %AGENT_C_CONFIG_PATH%
    echo.
    echo Please edit the configuration fil and rerun this script.
    echo.
    pause
    start notepad "%AGENT_C_CONFIG_PATH%\agent_c.config"
    exit /b 1
)

:: Run in detached mode (background):
docker-compose -f docker-compose.yml -p agent_c up -d --pull always

:: Wait a few seconds for the containers to start
timeout /t 5 /nobreak > nul

:: Open the browser to view Agent C
call view_agent_c.bat

ENDLOCAL