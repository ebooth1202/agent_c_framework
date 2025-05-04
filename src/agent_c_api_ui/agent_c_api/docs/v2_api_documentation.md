# Agent C API v2 Documentation

## Overview

The Agent C API v2 provides a clean, RESTful interface for interacting with Agent C. It's organized around resource types with consistent HTTP methods and status codes.

## API Resources

### Configuration Resources

- `/api/v2/config/models` - Available LLM models
- `/api/v2/config/personas` - Available personas
- `/api/v2/config/tools` - Available tools
- `/api/v2/config/system` - Combined system configuration

### Session Resources

- `/api/v2/sessions` - Chat session management
- `/api/v2/sessions/{session_id}` - Individual session operations
- `/api/v2/sessions/{session_id}/agent` - Agent configuration
- `/api/v2/sessions/{session_id}/tools` - Session tools management
- `/api/v2/sessions/{session_id}/chat` - Chat messaging
- `/api/v2/sessions/{session_id}/files` - File management

### History Resources

- `/api/v2/history` - Session history listing
- `/api/v2/history/{session_id}` - Session history management
- `/api/v2/history/{session_id}/events` - Event access
- `/api/v2/history/{session_id}/stream` - Event streaming
- `/api/v2/history/{session_id}/replay` - Replay controls

### Debug Resources

- `/api/v2/debug/sessions/{session_id}` - Session debugging
- `/api/v2/debug/agent/{session_id}` - Agent state debugging

## Implementation Status

- [x] Configuration Resources
- [x] Session Management
  - [x] Session CRUD operations
  - [x] Agent configuration
  - [x] Chat messaging
  - [ ] File management
- [x] History Resources
  - [x] History management
  - [x] Event access
  - [x] Replay control
- [ ] Debug Resources

## Migration from v1

See the migration guide for details on transitioning from v1 to v2 API.