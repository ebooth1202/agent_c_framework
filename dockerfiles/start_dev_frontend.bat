@echo off
REM Script to start only the frontend container with port 5174

echo Stopping any existing frontend container...
docker stop agent_c_frontend_only 2>nul
docker rm agent_c_frontend_only 2>nul

echo Starting the frontend container...
docker run -d --name agent_c_frontend_only ^
  -p 5174:5173 ^
  -e VITE_API_URL=http://localhost:8000/api/v1 ^
  -e VITE_RAG_API_URL=http://localhost:8000/api/v1 ^
  ghcr.io/centricconsulting/agent_c_frontend_dev:latest

echo.
echo Frontend container is running!
echo Access the UI at: http://localhost:5174
echo.
echo To stop the container, run:
echo docker stop agent_c_frontend_only
echo docker rm agent_c_frontend_only