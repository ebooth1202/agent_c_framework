@echo off
setlocal enabledelayedexpansion

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click on this batch file and select "Run as administrator".
    pause
    exit /b 1
)

:: Get the current user's username (even when running as admin)
for /f "tokens=*" %%a in ('whoami') do set CURRENT_USER=%%a
set CURRENT_USER=%CURRENT_USER:*\=%

:: Since this script is in the scripts subfolder, we can determine the project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\\"
:: Resolve the absolute path (handle potential relative paths)
for %%i in ("%PROJECT_ROOT%\.") do set "PROJECT_ROOT=%%~fi"

:: Set default link name - use the folder name of the project root
for %%i in ("%PROJECT_ROOT%") do set "DEFAULT_LINK_NAME=%%~ni"

:: Allow optional custom link name
set "LINK_NAME=%DEFAULT_LINK_NAME%"
if not "%~1"=="" (
    set "LINK_NAME=%~1"
)

echo Project location detected as: "%PROJECT_ROOT%"
echo.

:: Get the desktop path for the ACTUAL USER (not admin)
if exist "C:\Users\%CURRENT_USER%\Desktop" (
    set "DESKTOP_PATH=C:\Users\%CURRENT_USER%\Desktop"
) else if exist "C:\Users\%CURRENT_USER%\OneDrive\Desktop" (
    set "DESKTOP_PATH=C:\Users\%CURRENT_USER%\OneDrive\Desktop"
) else (
    echo Could not locate Desktop folder. Using default path.
    set "DESKTOP_PATH=%USERPROFILE%\Desktop"
)

echo Using Desktop location: "%DESKTOP_PATH%"
echo Creating symbolic link on desktop as: %LINK_NAME%

:: Check if link already exists
if exist "%DESKTOP_PATH%\%LINK_NAME%" (
    echo Warning: A folder or link named "%LINK_NAME%" already exists on the desktop.
    choice /C YN /M "Do you want to replace it"
    if errorlevel 2 goto :CANCELLED
    if errorlevel 1 (
        rmdir "%DESKTOP_PATH%\%LINK_NAME%" 2>nul
        del "%DESKTOP_PATH%\%LINK_NAME%" 2>nul
    )
)

:: Create the symbolic link
mklink /D "%DESKTOP_PATH%\%LINK_NAME%" "%PROJECT_ROOT%"

if %errorlevel% equ 0 (
    echo.
    echo Success! Symbolic link created on desktop.
    echo Link: "%DESKTOP_PATH%\%LINK_NAME%"
    echo Target: "%PROJECT_ROOT%"
) else (
    echo.
    echo Error: Failed to create symbolic link.
    echo Please make sure you have the necessary permissions.
)
goto :END

:CANCELLED
echo Operation cancelled by user.

:END
pause