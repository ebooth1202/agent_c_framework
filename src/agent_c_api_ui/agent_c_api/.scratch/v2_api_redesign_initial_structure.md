# Agent C API V2 Design - Initial Structure

## Overview

After thoroughly analyzing the V1 API, we've identified several areas for improvement:

1. **Mixed API Styles**: The V1 API mixes REST-style and RPC-style endpoints inconsistently
2. **Terminology Confusion**: Particularly around "sessions" vs "agents"
3. **Scattered Concerns**: Related functionality is spread across multiple endpoints
4. **Inconsistent Naming**: Endpoints don't follow a consistent naming pattern

This document proposes a restructured V2 API that addresses these issues with a clean, RESTful design organized around clear resource boundaries.

## Core Design Principles

1. **RESTful Resources**: Organize around clear resource types with consistent HTTP methods
2. **Consistent Naming**: Use clear, descriptive resource names that accurately reflect the domain
3. **Logical Grouping**: Group related endpoints under appropriate resource paths
4. **Proper Status Codes**: Use appropriate HTTP status codes for different responses
5. **Strong Validation**: Use Pydantic models for request/response validation
6. **Comprehensive Documentation**: Include detailed OpenAPI documentation
7. **API Versioning**: Maintain clear version boundaries for long-term compatibility

## V2 API Structure

The V2 API will be organized into four main resource categories:

### 1. Configuration Resources

Read-only resources that provide system configuration information.

```
/api/v2/config
  /models          # GET: List available LLM models
  /personas        # GET: List available personas
  /tools           # GET: List available tools
  /system          # GET: Get combined system configuration (all of the above)
```

### 2. Chat Session Resources

Resources for managing chat sessions and interactions.

```
/api/v2/sessions
  /                # POST: Create a new session
                   # GET: List all sessions (with pagination)
  /{session_id}    # GET: Get session details
                   # DELETE: Delete a session
                   # PATCH: Update session properties
  /{session_id}/agent
                   # GET: Get agent configuration for this session
                   # PATCH: Update agent settings (model, parameters, etc.)
  /{session_id}/tools
                   # GET: Get tools enabled for this session
                   # PUT: Replace tools list
                   # PATCH: Update specific tools
  /{session_id}/chat
                   # POST: Send a message and get streaming response
                   # DELETE: Cancel ongoing interaction
  /{session_id}/files
                   # POST: Upload a file to the session
                   # GET: List files in the session
  /{session_id}/files/{file_id}
                   # GET: Get file metadata
                   # DELETE: Remove file from session
  /{session_id}/files/{file_id}/content
                   # GET: Download file content
```

### 3. History Resources

Resources for accessing and replaying past interactions.

```
/api/v2/history
  /                # GET: List available session histories (with pagination/filtering)
  /{session_id}    # GET: Get session history summary
                   # DELETE: Delete session history
  /{session_id}/events
                   # GET: List events (with filtering)
  /{session_id}/stream
                   # GET: Stream events (optionally in real-time)
  /{session_id}/replay
                   # GET: Get replay status
                   # POST: Control replay (play/pause/seek)
```

### 4. Debug Resources

Optional resources for debugging and development.

```
/api/v2/debug
  /sessions/{session_id}
                   # GET: Get detailed debug info for a session
  /agent/{session_id}
                   # GET: Get detailed agent state
```

## Models

The V2 API will use the following core model types:

### Session Models

- **SessionCreate**: Parameters for creating a new session
- **SessionSummary**: Basic session information for listings
- **SessionDetail**: Comprehensive session information
- **SessionUpdate**: Parameters for updating a session

### Agent Models

- **AgentConfig**: Current agent configuration in a session
- **AgentUpdate**: Parameters for updating agent settings

### Tool Models

- **ToolsList**: List of available tools with categories
- **SessionTools**: Tools currently enabled in a session
- **ToolsUpdate**: Parameters for updating session tools

### Chat Models

- **ChatMessage**: A message sent to or received from the agent
- **ChatRequest**: A request to send a chat message
- **ChatEvent**: A streaming event during chat (text/tool call/etc.)

### File Models

- **FileUpload**: Parameters for uploading a file
- **FileMeta**: Metadata about an uploaded file

### History Models

- **HistorySummary**: Summary of a recorded session history
- **EventFilter**: Parameters for filtering history events
- **Event**: A recorded event in session history
- **ReplayControl**: Parameters for controlling replay

## Migration Considerations

1. **Endpoint Mapping**: Each V1 endpoint will need to be mapped to its V2 equivalent
2. **Parameter Conversion**: Request/response parameters will need conversion logic
3. **Client Updates**: Clients will need to be updated to use the new API structure
4. **Transition Period**: Consider maintaining both V1 and V2 APIs during transition

## Implementation Plan

The implementation will be divided into phases:

1. **Foundational Structure**: Set up the V2 API package structure and core models
2. **Configuration Endpoints**: Implement the config resource endpoints
3. **Session Management**: Implement session creation and management
4. **Chat Functionality**: Implement chat and file handling
5. **History Access**: Implement history and replay functionality
6. **Testing & Documentation**: Comprehensive testing and documentation
7. **Client Migration**: Support for client migration from V1 to V2

## Next Steps

1. Review this initial design with stakeholders
2. Refine resource structure and models based on feedback
3. Create detailed implementation plan with specific tasks
4. Begin implementation of Phase 1 (Foundation)