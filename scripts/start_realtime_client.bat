@echo off
SETLOCAL

:: Store the starting directory
pushd %CD%

:: Navigate to repo root if script is run from scripts directory
if "%CD:~-7%"=="scripts" (
    cd ..
)
cd src\realtime_client\packages\demo
pnpm run dev:docker
