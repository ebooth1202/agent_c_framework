@echo off
SETLOCAL

:: Check for Python and print the version
python --version >NUL 2>&1
if errorlevel 9009 (
    echo Python is not installed or not in the PATH.
    exit /b 1
)

:: Check if the virtual environment already exists
if exist .venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    :: Create a virtual environment
    echo Creating virtual environment.
    python -m .venv venv
    if errorlevel 1 (
        echo Failed to create a virtual environment.
        exit /b 1
    )
)

:: Activate the virtual environment
echo Activating virtual environment.
CALL .venv\scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate the virtual environment.
    exit /b 1
)

:: Install the requirements
echo Installing dependencies.
call scripts/install_deps.bat

if errorlevel 1 (
    echo Failed to install the required packages.
    exit /b 1
)


echo Initial setup completed successfully.
echo Remember to activate the virtual environment with ',venv\scripts\activate.bat' before you start working.
ENDLOCAL
