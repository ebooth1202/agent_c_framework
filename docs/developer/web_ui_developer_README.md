# Agent C Web UI - Developer Guide

## Overview
This guide is intended for developers working ON Agent C who need to set up the web UI using the source code in this repository.

## Running from Source

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- Access to the Agent C repository

### API Server

The API server provides the backend functionality for the Agent C web UI.

#### Starting the API Server

**On Linux/macOS:**
```bash
# Navigate to the project directory and run
./scripts/start_api.sh
```

**On Windows:**
```batch
# Navigate to the project directory and run
scripts\start_api.bat
```

### Frontend

The frontend provides the user interface for Agent C.

#### Starting the Frontend

**On Linux/macOS:**
```bash
# Navigate to the project directory and run
./scripts/start_fe.sh
```

**On Windows:**
```batch
# Navigate to the project directory and run
scripts\start_fe.bat
```

## Configuration

### Workspace Configuration

When running from source, the system uses the `.local_workspaces.json` file in the project root to create workspaces for the agents. This file defines the available workspaces, their locations, and permissions.

### Development Notes

- The frontend runs on port 3000 by default
- The API server runs on port 5000 by default
- Changes to the frontend code will trigger automatic recompilation
- Changes to the API server code require a restart of the server

## Integration Testing

If you need to test both components together during development, launch both the API server and frontend using their respective scripts.