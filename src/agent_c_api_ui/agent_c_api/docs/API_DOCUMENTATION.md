# Agent C API Documentation

This document provides comprehensive documentation for the Agent C API.

## API Versions

### V1 API (Current)
All V1 endpoints are prefixed with `/api/v1`. This is the current stable API.

### V2 API (New Architecture)
The V2 API (`/api/v2`) introduces a modernized architecture with:
- **Redis-based session management** with external Redis dependency
- **Enhanced health monitoring** with Kubernetes-compatible endpoints
- **Improved dependency injection** patterns
- **Better error handling** and graceful degradation

For V2 API documentation, see:
- [V2 API Documentation](v2_api_documentation.md)
- [Redis Architecture](redis_architecture.md)
- [Environment Configuration](environment_configuration.md)

## Infrastructure Requirements

### Redis Database
The API requires an external Redis server for session management and caching:
- **Redis 6.x or 7.x** recommended
- **External management** required (Docker, cloud service, etc.)
- **No embedded Redis** - must be provided as separate service

See [Environment Configuration](environment_configuration.md) for Redis setup instructions.

## Overview

The Agent C API provides endpoints for managing:
- Agent Sessions
- Models
- Tools
- Agent Configuration
- Chat Interactions
- File Operations
- Personas
- Interactions and Events

## Health Monitoring

The API provides comprehensive health monitoring endpoints:

### V2 Health Endpoints
- `GET /api/v2/health` - Main application health check
- `GET /api/v2/health/ready` - Kubernetes readiness probe
- `GET /api/v2/health/live` - Kubernetes liveness probe
- `GET /api/v2/debug/health/redis` - Detailed Redis diagnostics

See [Redis Architecture](redis_architecture.md) for detailed health monitoring information.

## Authentication

No explicit authentication mechanism was identified in the current codebase. Consider implementing authentication for production use.

## Endpoints

### Sessions

#### Initialize Agent Session

```
POST /api/v1/initialize
```

Creates a new agent session with the provided parameters.

**Request Body:**

```json
{
  "model_name": "string",               // Required: The model name to use
  "backend": "openai",                 // Optional: Backend provider (e.g., 'openai', 'claude')
  "persona_name": "default",           // Optional: Name of the persona to use
  "custom_prompt": "string",           // Optional: Custom prompt for persona
  "temperature": 0.7,                  // Optional: Temperature for chat models
  "reasoning_effort": "medium",         // Optional: Reasoning effort for OpenAI models; must be 'low', 'medium', or 'high'
  "budget_tokens": 0,                  // Optional: Budget tokens (used by some Claude models)
  "max_tokens": 8192,                  // Optional: Maximum tokens for the model output
  "ui_session_id": "string"            // Optional: Existing UI session ID for transferring chat history
}
```

**Model Validations:**
- For OpenAI models: `o1`, `o1-mini`, `o3-mini`:
  - If `reasoning_effort` is not provided or not one of ['low', 'medium', 'high'], it defaults to 'medium'
- For Claude model `claude-3-7-sonnet-latest`:
  - If `budget_tokens` is provided, `max_tokens` will default to 64000 if not specified
  - If `budget_tokens` is not provided, it will default to 0 and `max_tokens` will default to 8192
- For chat models like 'gpt-4o', 'gpt-4o-audio-preview', 'claude-3-5-sonnet-latest':
  - For 'claude-3-5-sonnet-latest', `max_tokens` defaults to 8192 if not specified

**Response:**

```json
{
  "ui_session_id": "string",          // UI session ID to use for future requests
  "agent_c_session_id": "string"      // Internal Agent C session ID
}
```

**Error Responses:**

- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Error during session initialization

#### Verify Session

```
GET /api/v1/verify_session/{ui_session_id}
```

Verifies if a session exists and is valid.

**Path Parameters:**

- `ui_session_id`: The UI session ID to verify

**Response:**

```json
{
  "valid": true  // Boolean indicating if the session is valid
}
```

#### Delete All Sessions

```
DELETE /api/v1/sessions
```

Deletes all active sessions and cleans up their resources.

**Response:**

```json
{
  "status": "success",
  "message": "Successfully deleted X sessions",
  "deleted_count": 5  // Number of sessions deleted
}
```

**Error Responses:**

- `500 Internal Server Error`: Failed to delete sessions

### Models

#### List Available Models

```
GET /api/v1/models
```

Retrieves a list of all available models with their capabilities and parameters.

**Response:**

```json
{
  "models": [
    {
      "id": "gpt-4o",                     // Model identifier
      "label": "GPT-4o",                  // Display name
      "description": "GPT-4 OpenAI model for chat interactions.",
      "model_type": "chat",               // Model type (chat, reasoning, etc.)
      "backend": "openai",                // Backend provider
      "parameters": {                     // Available configuration parameters
        "temperature": {
          "default": 0.5,
          "min": 0,
          "max": 2,
          "required": true
        },
        "max_tokens": {
          "min": 1000,
          "max": 16384,
          "default": 16384,
          "required": false
        }
      },
      "capabilities": {                   // Model capabilities
        "supports_tools": true,
        "multi_modal": true
      },
      "allowed_inputs": {                 // Supported input types
        "image": true,
        "video": false,
        "audio": false,
        "file": false
      }
    }
  ]
}
```

**Error Responses:**

- `500 Internal Server Error`: Error reading model configuration

### Tools

#### List Available Tools

```
GET /api/v1/tools
```

Retrieves a list of all available tools categorized by type.

**Response:**

```json
{
  "essential_toolsets": [                // Tools always loaded with every agent
    {
      "name": "WorkspaceTools",
      "module": "agent_c_tools.tools.workspace_tools",
      "doc": "Tools for working with workspaces",
      "essential": true
    },
    // Additional essential tools...
  ],
  "groups": {                           // Tools categorized by groups
    "Core Tools": [
      {
        "name": "TextTools",
        "module": "agent_c_tools.tools.text_tools",
        "doc": "Tools for text manipulation",
        "essential": false
      },
      // Additional core tools...
    ],
    "Demo Tools": [
      // Demo tools if available
    ],
    "Voice Tools": [
      // Voice tools if available
    ],
    "RAG Tools": [
      // RAG tools if available
    ]
  },
  "categories": [                       // List of available categories
    "Core Tools",
    "Demo Tools",
    "Voice Tools",
    "RAG Tools"
  ],
  "tool_name_mapping": {}               // Mapping of tool names (if available)
}
```

**Error Responses:**

- `500 Internal Server Error`: Error retrieving tools

### Agent Configuration

#### Update Agent Settings

```
POST /api/v1/update_settings
```

Updates settings for an existing agent session.

**Request Body:**

```json
{
  "ui_session_id": "string",            // Required: The UI session ID to update
  "persona_name": "default",           // Optional: Name of the persona to use
  "custom_prompt": "string",           // Optional: Custom prompt for persona
  "temperature": 0.7,                  // Optional: Temperature for chat models
  "reasoning_effort": "medium",         // Optional: Reasoning effort for OpenAI models
  "budget_tokens": 0                   // Optional: Budget tokens (for Claude models)
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Settings updated successfully for Agent {ui_session_id}",
  "changes_made": {                      // Map of changes made
    "temperature": {
      "from": "0.5",
      "to": "0.7"
    }
  },
  "skipped_null_values": [              // Parameters that were not updated (null in request)
    "reasoning_effort"
  ],
  "failed_updates": []                  // Parameters that failed to update
}
```

**Error Responses:**

- `404 Not Found`: Invalid session ID
- `500 Internal Server Error`: Error updating settings

#### Get Agent Configuration

```
GET /api/v1/get_agent_config/{ui_session_id}
```

Retrieves the current configuration of an agent.

**Path Parameters:**

- `ui_session_id`: The UI session ID

**Response:**

```json
{
  "config": {
    "user_id": "string",
    "custom_prompt": "string",
    "ui_session_id": "string",
    "agent_c_session_id": "string",
    "backend": "openai",
    "model_info": {
      "name": "gpt-4o",
      "temperature": 0.7,
      "reasoning_effort": "medium",
      "extended_thinking": false,
      "budget_tokens": 0,
      "max_tokens": 16384
    },
    "initialized_tools": [
      "WorkspaceTools",
      "ThinkTools"
    ]
  },
  "status": "success"
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error retrieving agent configuration

#### Update Agent Tools

```
POST /api/v1/update_tools
```

Updates the tools available to an agent.

**Request Body:**

```json
{
  "ui_session_id": "string",
  "tools": [                            // List of tool class names to enable
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Tools updated successfully",
  "active_tools": [                      // List of active tools after update
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ],
  "ui_session_id": "string",
  "agent_c_session_id": "string"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid tools format
- `404 Not Found`: Invalid session ID
- `500 Internal Server Error`: Error updating tools

#### Get Agent Tools

```
GET /api/v1/get_agent_tools/{ui_session_id}
```

Retrieves the currently active tools for an agent.

**Path Parameters:**

- `ui_session_id`: The UI session ID

**Response:**

```json
{
  "initialized_tools": [
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ],
  "status": "success"
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error retrieving tools

#### Debug Agent State

```
GET /api/v1/debug_agent_state/{ui_session_id}
```

Debug endpoint to check the state of an agent and its internal components.

**Path Parameters:**

- `ui_session_id`: The UI session ID

**Response:**

```json
{
  "status": "success",
  "agent_bridge_params": {
    "temperature": 0.7,
    "reasoning_effort": "medium",
    "extended_thinking": false,
    "budget_tokens": 0,
    "max_tokens": 16384
  },
  "internal_agent_params": {
    "type": "ReactJSAgent",
    "temperature": 0.7,
    "reasoning_effort": "medium",
    "budget_tokens": 0,
    "max_tokens": 16384
  }
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error debugging agent state

#### Debug Chat Session

```
GET /api/v1/chat_session_debug/{ui_session_id}
```

Provides debugging information for a chat session.

**Path Parameters:**

- `ui_session_id`: The UI session ID

**Response:**

Comprehensive diagnostic information about the chat session, including details about the agent, session manager, and message history.

**Error Responses:**

- `404 Not Found`: Invalid session ID
- `500 Internal Server Error`: Error debugging session

### Chat

#### Chat with Agent

```
POST /api/v1/chat
```

Sends a message to the agent and receives a streaming response.

**Form Parameters:**

- `ui_session_id`: (Required) The UI session ID
- `message`: (Required) The message to send to the agent
- `file_ids`: (Optional) JSON string array of file IDs to include with the message

**Response:**

A streaming response containing the agent's reply. The response is streamed as plain text chunks.

**Error Responses:**

- `400 Bad Request`: Invalid file_ids format
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error processing the request

#### Cancel Chat Interaction

```
POST /api/v1/cancel
```

Cancels an ongoing chat interaction.

**Form Parameters:**

- `ui_session_id`: (Required) The UI session ID of the interaction to cancel

**Response:**

```json
{
  "status": "success",
  "message": "Cancellation signal sent for session: {ui_session_id}"
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Failed to cancel interaction

### Files

#### Upload File

```
POST /api/v1/upload_file
```

Uploads a file for use in chat.

**Form Parameters:**

- `ui_session_id`: (Required) The UI session ID
- `file`: (Required) The file to upload

**Response:**

```json
{
  "id": "string",                     // File ID for referencing in chat
  "filename": "example.pdf",         // Original filename
  "mime_type": "application/pdf",    // MIME type of the file
  "size": 12345                      // File size in bytes
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error uploading file

#### List Session Files

```
GET /api/v1/files/{ui_session_id}
```

Lists all files uploaded for a specific session.

**Path Parameters:**

- `ui_session_id`: The UI session ID

**Response:**

```json
{
  "files": [
    {
      "id": "string",
      "filename": "example.pdf",
      "mime_type": "application/pdf",
      "size": 12345,
      "upload_time": "2025-04-30T08:40:00.000Z",
      "processed": true,
      "processing_status": "completed",
      "processing_error": null
    }
  ]
}
```

**Error Responses:**

- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error listing files

#### Get File

```
GET /api/v1/files/{ui_session_id}/{file_id}
```

Retrieves metadata for a specific file.

**Path Parameters:**

- `ui_session_id`: The UI session ID
- `file_id`: The file ID

**Response:**

```json
{
  "id": "string",
  "filename": "example.pdf", 
  "mime_type": "application/pdf",
  "size": 12345
}
```

**Error Responses:**

- `404 Not Found`: Session or file not found
- `500 Internal Server Error`: Error retrieving file

#### Delete File

```
DELETE /api/v1/files/{ui_session_id}/{file_id}
```

Deletes a specific file.

**Path Parameters:**

- `ui_session_id`: The UI session ID
- `file_id`: The file ID

**Response:**

```json
{
  "message": "File example.pdf deleted successfully"
}
```

**Error Responses:**

- `404 Not Found`: Session or file not found
- `500 Internal Server Error`: Error deleting file

### Personas

#### List Personas

```
GET /api/v1/personas
```

Retrieves a list of all available personas.

**Response:**

```json
[
  {
    "name": "default",                   // Persona name
    "content": "# Default Persona..."    // Full content of the persona markdown file
    "file": "default.md"                // Filename
  },
  {
    "name": "helpful - assistant",       // Subdirectory path converted to name with separator
    "content": "# Helpful Assistant..." // Full content of the persona markdown file
    "file": "assistant.md"              // Filename
  }
]
```

**Error Responses:**

- `500 Internal Server Error`: Error reading personas directory

### Interactions

#### List Interaction Sessions

```
GET /api/v1/interactions
```

Lists all available interaction sessions with pagination and sorting.

**Query Parameters:**

- `limit`: (Optional) Maximum number of sessions to return (default: 50)
- `offset`: (Optional) Number of sessions to skip (default: 0)
- `sort_by`: (Optional) Field to sort by (default: "timestamp")
- `sort_order`: (Optional) Sort order, "asc" or "desc" (default: "desc")

**Response:**

```json
[
  {
    "id": "string",                      // Session ID
    "start_time": "2025-04-30T08:40:00.000Z", // Session start time
    "end_time": "2025-04-30T08:45:00.000Z",   // Session end time (if completed)
    "duration_seconds": 300,             // Session duration in seconds
    "event_count": 156,                  // Number of events in the session
    "file_count": 3                      // Number of files in the session
  }
]
```

#### Get Interaction Details

```
GET /api/v1/interactions/{session_id}
```

Gets detailed information about a specific interaction session.

**Path Parameters:**

- `session_id`: The session ID

**Response:**

```json
{
  "id": "string",
  "start_time": "2025-04-30T08:40:00.000Z",
  "end_time": "2025-04-30T08:45:00.000Z",
  "duration_seconds": 300,
  "event_count": 156,
  "file_count": 3,
  "files": ["file1.jsonl", "file2.jsonl", "file3.jsonl"],
  "event_types": {                      // Count of each event type
    "user_request": 5,
    "completion": 5,
    "tool_call": 8,
    "thought_delta": 35
  },
  "metadata": {                         // Additional metadata if available
    "model": "gpt-4o",
    "backend": "openai"
  },
  "user_id": "string",                  // User ID if available
  "has_thinking": true,                 // Whether the session has thinking events
  "tool_calls": ["tool1", "tool2"]      // List of tools used in the session
}
```

**Error Responses:**

- `404 Not Found`: Session not found

#### Get Session Files

```
GET /api/v1/interactions/{session_id}/files
```

Gets a list of all JSONL files associated with a specific session.

**Path Parameters:**

- `session_id`: The session ID

**Response:**

```json
["file1.jsonl", "file2.jsonl", "file3.jsonl"]
```

**Error Responses:**

- `404 Not Found`: No files found for session

#### Delete Session

```
DELETE /api/v1/interactions/{session_id}
```

Deletes a session directory and all its files.

**Path Parameters:**

- `session_id`: The session ID

**Response:**

```json
{
  "status": "success",
  "message": "Session {session_id} deleted successfully"
}
```

**Error Responses:**

- `404 Not Found`: Session not found or could not be deleted

### Events

#### Get Session Events

```
GET /api/v1/events/{session_id}
```

Gets events for a specific session with filtering options.

**Path Parameters:**

- `session_id`: The session ID

**Query Parameters:**

- `event_types`: (Optional) Filter by event types (e.g., `SYSTEM_PROMPT`, `INTERACTION`, `TOOL_CALL`)
- `start_time`: (Optional) Filter events after this timestamp
- `end_time`: (Optional) Filter events before this timestamp
- `limit`: (Optional) Maximum number of events to return (default: 1000)

**Response:**

```json
[
  {
    "timestamp": "2025-04-30T08:40:00.000Z",
    "type": "INTERACTION",              // Event type
    "session_id": "string",             // Session ID
    "role": "user",                     // Role (user, assistant, system)
    "content": "User message",           // Event content
    "format": "text",                    // Content format
    "running": true,                     // Whether the interaction is running
    "active": true,                      // Whether the interaction is active
    "vendor": "openai",                  // Vendor name if applicable
    "tool_calls": [...],                 // Tool calls if applicable
    "tool_results": [...],               // Tool results if applicable
    "raw": {}                            // Original event data
  }
]
```

**Error Responses:**

- `404 Not Found`: No events found for session

#### Stream Session Events

```
GET /api/v1/events/{session_id}/stream
```

Streams events for a specific session, optionally in real-time.

**Path Parameters:**

- `session_id`: The session ID

**Query Parameters:**

- `event_types`: (Optional) Filter by event types
- `real_time`: (Optional) Whether to replay events with original timing (default: false)
- `speed_factor`: (Optional) Speed multiplier for real-time replay (default: 1.0)

**Response:**

A streaming response of events in the `text/event-stream` format.

#### Get Replay Status

```
GET /api/v1/events/{session_id}/replay-status
```

Gets the current status of a session replay.

**Path Parameters:**

- `session_id`: The session ID

**Response:**

Status information about the active replay.

**Error Responses:**

- `404 Not Found`: No active replay for session

#### Control Replay

```
POST /api/v1/events/{session_id}/replay/control
```

Controls a session replay (play, pause, stop, seek).

**Path Parameters:**

- `session_id`: The session ID

**Request Body:**

```json
{
  "action": "play",                     // Action: play, pause, stop, seek
  "position": "2025-04-30T08:42:00.000Z" // Timestamp to seek to (for seek action)
}
```

**Response:**

```json
{
  "status": "success",
  "action": "play"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid replay control action