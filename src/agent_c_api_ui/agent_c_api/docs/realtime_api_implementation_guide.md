# Agent C Realtime API Implementation Guide

## Overview

The Agent C Realtime API provides a WebSocket-based interface for real-time communication with AI agents, integrated with HeyGen streaming avatars. This guide covers the complete event system, authentication, and payload structures for implementing clients.

## Architecture

The realtime API consists of:

- **REST Authentication Endpoints** - Initial authentication and configuration
- **WebSocket Bridge** - Bidirectional event streaming
- **Event System** - Command/response event handling
- **Avatar Integration** - HeyGen streaming avatar support

---

## REST API Endpoints

### Authentication & Configuration

#### `POST /rt/login`

Authenticate user and get initial configuration.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "agent_c_token": "jwt_token_string",
  "heygen_token": "heygen_access_token",
  "user": {
    "user_id": "string",
    "user_name": "string",
    "email": "string|null",
    "first_name": "string|null",
    "last_name": "string|null", 
    "is_active": true,
    "roles": ["array_of_strings"],
    "groups": ["array_of_strings"],
    "created_at": "iso_timestamp|null",
    "last_login": "iso_timestamp|null"
  },
  "agents": [
    {
      "name": "Agent Name",
      "key": "agent_key", 
      "agent_description": "Agent description|null",
      "category": ["array_of_categories"]
    }
  ],
  "avatars": [
    {
      "avatar_id": "string",
      "created_at": 1234567890,
      "default_voice": "voice_id",
      "is_public": true,
      "normal_preview": "preview_url",
      "pose_name": "pose_name",
      "status": "status_string"
    }
  ],
  "toolsets": [
    {
      "name": "toolset_name",
      "description": "Description of the toolset functionality",
      "schemas": {
        "tool_name": {
          "type": "function",
          "function": {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": {
              "type": "object",
              "properties": {
                "param_name": {
                  "type": "string",
                  "description": "Parameter description"
                }
              },
              "required": ["param_name"]
            }
          }
        }
      }
    }
  ],
  "voices": [
    {
      "voice_id": "none",
      "vendor": "system",
      "description": "No Voice (text only)",
      "output_format": "none"
    },
    {
      "voice_id": "avatar",
      "vendor": "heygen",
      "description": "HeyGen Avatar Voice Model",
      "output_format": "special"
    },
    {
      "voice_id": "alloy",
      "vendor": "openai",
      "description": "OpenAI Alloy voice",
      "output_format": "pcm16"
    }
  ],
  "ui_session_id": "three-word-slug"
}
```

#### `GET /rt/refresh_token`

Refresh JWT and HeyGen tokens.

**Headers:** `Authorization: Bearer <jwt_token>`

**Response:**

```json
{
  "agent_c_token": "new_jwt_token",
  "heygen_token": "new_heygen_token"
}
```

## WebSocket Connection

### Connection Endpoint

`wss://host/rt/ws?token={jwt_token}&session_id={optional_session_id}`

**HTTPS Requirement:** The API requires HTTPS even in development environments to ensure proper audio support for web clients. This is necessary for WebRTC audio features and secure WebSocket connections.

**Parameters:**

- `token` (required) - JWT token from login
- `session_id` (optional) - Resume existing UI session

### Session Management

The system uses two types of session identifiers:

#### UI Session IDs

- **Purpose:** Represent a client connection to the server
- **Scope:** Each unique WebSocket connection gets one UI session ID
- **Usage:** Used for internal caching and session resumption after network issues
- **Persistence:** Temporary - tied to active connections
- **Format:** Three-word mnemonic slug (e.g., "tiger-castle-moon")

#### Chat Session IDs

- **Purpose:** Represent persistent chat conversations between user and agent
- **Scope:** Multiple UI sessions can access the same chat session
- **Usage:** Used for chat history persistence, session switching, and resumption
- **Persistence:** Permanent - stored in database
- **Format:** Mnemonic slug format

**Example Workflow:**

1. Client connects → receives `ui_session_id: "tiger-castle-moon"`
2. Client starts chat → receives `chat_session_id: "purple-river-sky"`
3. Network drops → client reconnects with same `ui_session_id`
4. Client can resume `chat_session_id: "purple-river-sky"` or switch to different chat

### Connection Flow

1. **Authentication** - JWT token validation
2. **Session Creation/Resume** - Initialize or load chat session
3. **Bridge Initialization** - Setup event handlers
4. **Initialization Events** - Server sends configuration data to client
5. **Event Loop** - Bidirectional event processing

#### Initialization Event Sequence

When a client successfully connects to the WebSocket, the server automatically sends a series of initialization events to provide the client with current configuration and state:

1. **`chat_user_data`** - Current user information and profile data
2. **`avatar_list`** - Available HeyGen avatars for the user
3. **`voice_list`** - Available TTS voice models and configurations
4. **`agent_list`** - Available AI agents the user can interact with
5. **`tool_catalog`** - Available tools and their schemas for the current session
6. **`chat_session_changed`** - Current or newly created chat session state

These events provide all the necessary information for the client to render its UI and be ready for user interaction. Clients should handle these events during the connection setup phase to ensure proper initialization.

---

## Client → Server Events (Commands)

These are events sent from the client to control the server.

### Agent Management

#### `get_agents`

Request list of available agents.

```json
{
  "type": "get_agents"
}
```

#### `set_agent`

Set the active agent for the session.

```json
{
  "type": "set_agent",
  "agent_key": "default_realtime"
}
```

### Avatar Management

#### `get_avatars`

Request list of available avatars.

```json
{
  "type": "get_avatars"
}
```

#### `set_avatar_session`

Connect to existing avatar session.

```json
{
  "type": "set_avatar_session",
  "access_token": "heygen_session_token",
  "avatar_session_id": "session_uuid"
}
```

### Voice Management

#### `get_voices`

Request list of available voices.

```json
{
  "type": "get_voices"
}
```

#### `set_agent_voice`

Set the TTS voice for the current agent.

```json
{
  "type": "set_agent_voice",
  "voice_id": "alloy"
}
```

### Tool Management

#### `get_tool_catalog`

Request the tool catalog.

```json
{
  "type": "get_tool_catalog"
}
```

### Session Management

#### `get_user_sessions`

Request list of user chat sessions.

```json
{
  "type": "get_user_sessions",
  "offset": 0,
  "limit": 50
}
```

### Connection Health

#### `ping`

Check if the connection is alive.

```json
{
  "type": "ping"
}
```

### Chat Management

#### `text_input`

Send text message to agent.

```json
{
  "type": "text_input",
  "text": "Hello, how are you?",
  "file_ids": ["file-id-1", "file-id-2"] // optional
}
```

#### `new_chat_session`

Create a new chat session.

```json
{
  "type": "new_chat_session",
  "agent_key": "optional_agent_key" // defaults to current agent
}
```

#### `resume_chat_session`

Resume an existing chat session.

```json
{
  "type": "resume_chat_session",
  "session_id": "existing-session-id"
}
```

#### `set_chat_session_name`

Set the name/title for the current session.

```json
{
  "type": "set_chat_session_name",
  "session_name": "My Conversation"
}
```

#### `set_session_metadata`

Update session metadata.

```json
{
  "type": "set_session_metadata",
  "meta": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

#### `set_session_messages`

Replace all messages in the current session.

```json
{
  "type": "set_session_messages",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "role": "assistant", 
      "content": "Hello! How can I help you?",
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ]
}
```

---

## Server → Client Events (Responses & Updates)

These are events sent from the server to update the client.

### Agent Updates

#### `agent_list`

Response to `get_agents` with available agents.

```json
{
  "type": "agent_list",
  "agents": [
    {
      "name": "Agent Name",
      "key": "agent_key", 
      "agent_description": "Agent description|null",
      "category": ["array_of_categories"]
    }
  ]
}
```

#### `agent_configuration_changed`

Notification that agent configuration has changed.

```json
{
  "type": "agent_configuration_changed",
  "agent_config": {
    "version": 2,
    "name": "Agent Name",
    "key": "agent_key",
    "model_id": "model_identifier",
    "agent_description": "Agent description|null",
    "tools": ["tool1", "tool2"],
    "agent_params": { /* CompletionParams object */ },
    "prompt_metadata": { /* metadata object */ },
    "persona": "Agent personality description",
    "uid": "unique_id|null",
    "category": ["array_of_categories"]
  }
}
```

### Avatar Updates

#### `avatar_list`

Response to `get_avatars` with available avatars.

```json
{
  "type": "avatar_list", 
  "avatars": [
    {
      "avatar_id": "string",
      "created_at": 1234567890,
      "default_voice": "voice_id",
      "is_public": true,
      "normal_preview": "preview_url",
      "pose_name": "pose_name",
      "status": "status_string"
    }
  ]
}
```

#### `avatar_connection_changed`

Notification that avatar connection status has changed.

```json
{
  "type": "avatar_connection_changed",
  "avatar_session_request": {
    "avatar_id": "string|null",
    "quality": "string|null", 
    "voice": { /* VoiceSettings object */ },
    "language": "string|null",
    "version": "string|null",
    "video_encoding": "string|null",
    "source": "string|null",
    "stt_settings": { /* STTSettings object */ },
    "ia_is_livekit_transport": "boolean|null",
    "knowledge_base": "string|null",
    "knowledge_base_id": "string|null",
    "disable_idle_timeout": "boolean|null",
    "activity_idle_timeout": "integer|null"
  },
  "avatar_session": {
    "session_id": "string",
    "url": "string",
    "access_token": "string",
    "session_duration_limit": 0,
    "is_paid": true,
    "realtime_endpoint": "string",
    "sdp": "string|null",
    "ice_servers": "array|null",
    "ice_servers2": "array|null"
  }
}
```

### Chat Events

#### `chat_session_changed`

Notification that chat session has been updated.

```json
{
  "type": "chat_session_changed",
  "chat_session": {
    "session_id": "session-id",
    "token_count": 0,
    "context_window_size": 0,
    "session_name": "Session Name|null",
    "created_at": "iso_timestamp|null",
    "updated_at": "iso_timestamp|null",
    "deleted_at": "iso_timestamp|null",
    "user_id": "user-id|null",
    "metadata": { /* session metadata dict */ },
    "messages": [ /* array of message dicts */ ],
    "agent_config": { /* CurrentAgentConfiguration object */ }
  }
}
```

#### `chat_session_name_changed`

Notification that session name was updated.

```json
{
  "type": "chat_session_name_changed",
  "session_name": "New Session Name"
}
```

#### `session_metadata_changed`

Notification that session metadata was updated.

```json
{
  "type": "session_metadata_changed", 
  "meta": {
    "key1": "updated_value1",
    "key2": "new_value2"
  }
}
```

### Runtime Events (Forwarded from Core)

These events are generated by the agent runtime and forwarded to clients.

#### `text_delta`

Streaming text content from the agent.

```json
{
  "type": "text_delta",
  "session_id": "session-id",
  "role": "assistant",
  "content": "chunk of text",
  "format": "markdown"
}
```

#### `thought_delta`

Streaming thought content from the agent (when using thinking tools).

```json
{
  "type": "thought_delta", 
  "session_id": "session-id",
  "role": "assistant (thought)",
  "content": "agent thinking process",
  "format": "markdown"
}
```

#### `completion`

Completion status updates.

```json
{
  "type": "completion",
  "session_id": "session-id", 
  "role": "assistant",
  "running": false,
  "completion_options": { /* vendor-specific options */ },
  "stop_reason": "stop|length|tool_calls",
  "input_tokens": 150,
  "output_tokens": 75
}
```

#### `interaction`

Interaction lifecycle events.

```json
{
  "type": "interaction",
  "session_id": "session-id",
  "role": "assistant",
  "started": true, // false when completed
  "id": "interaction-uuid"
}
```

#### `history`

Complete message history update.

```json
{
  "type": "history",
  "session_id": "session-id", 
  "role": "system",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help you?", 
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ]
}
```

#### `tool_call`

Tool execution events.

```json
{
  "type": "tool_call",
  "session_id": "session-id",
  "role": "assistant", 
  "active": true, // false when completed
  "vendor": "openai",
  "tool_calls": [
    {
      "id": "call_uuid",
      "type": "function",
      "function": {
        "name": "tool_name",
        "arguments": "{\"param\": \"value\"}"
      }
    }
  ],
  "tool_results": [
    {
      "call_id": "call_uuid",
      "output": "tool execution result"
    }
  ]
}
```

#### `system_message`

System notifications and errors.

```json
{
  "type": "system_message",
  "session_id": "session-id",
  "role": "system",
  "content": "System message content",
  "format": "markdown",
  "severity": "info|warning|error"
}
```

### Turn Management Events

#### `user_turn_start`

Notification that the server is ready to accept user input (text or audio).

```json
{
  "type": "user_turn_start"
}
```

#### `user_turn_end`

Notification that the server has received user input and is no longer accepting input.

```json
{
  "type": "user_turn_end"
}
```

### Voice Events

#### `voice_list`

Response to `get_voices` with available voices.

```json
{
  "type": "voice_list",
  "voices": [
    {
      "voice_id": "none",
      "vendor": "system",
      "description": "No Voice (text only)",
      "output_format": "none"
    },
    {
      "voice_id": "avatar",
      "vendor": "heygen",
      "description": "HeyGen Avatar Voice Model",
      "output_format": "special"
    },
    {
      "voice_id": "alloy",
      "vendor": "openai",
      "description": "OpenAI Alloy voice",
      "output_format": "pcm16"
    }
  ]
}
```

#### `agent_voice_changed`

Notification that the agent's voice has been updated.

```json
{
  "type": "agent_voice_changed",
  "voice": {
    "voice_id": "alloy",
    "vendor": "openai",
    "description": "OpenAI Alloy voice",
    "output_format": "pcm16"
  }
}
```

### Tool Events

#### `tool_catalog`

Response to `get_tool_catalog` with available tools.

```json
{
  "type": "tool_catalog",
  "tools": [
    {
      "name": "toolset_name",
      "description": "Description of the toolset functionality",
      "schemas": {
        "tool_name": {
          "type": "function",
          "function": {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": {
              "type": "object",
              "properties": {
                "param_name": {
                  "type": "string",
                  "description": "Parameter description"
                }
              },
              "required": ["param_name"]
            }
          }
        }
      }
    }
  ]
}
```

### User Events

#### `chat_user_data`

Sent during initialization with current user information.

```json
{
  "type": "chat_user_data",
  "user": {
    "user_id": "string",
    "user_name": "string",
    "email": "string|null",
    "first_name": "string|null",
    "last_name": "string|null",
    "is_active": true,
    "roles": ["array_of_strings"],
    "groups": ["array_of_strings"],
    "created_at": "iso_timestamp|null",
    "last_login": "iso_timestamp|null"
  }
}
```

#### `get_user_sessions_response`

Response to `get_user_sessions` with user's chat sessions.

```json
{
  "type": "get_user_sessions_response",
  "sessions": {
    "sessions": [
      {
        "session_id": "session-id",
        "session_name": "Session Name|null",
        "created_at": "iso_timestamp",
        "updated_at": "iso_timestamp",
        "agent_config": { /* agent configuration */ }
      }
    ],
    "total": 10,
    "offset": 0,
    "limit": 50
  }
}
```

### Connection Events

#### `pong`

Response to `ping` event for connection health check.

```json
{
  "type": "pong"
}
```

### Error Events

#### `error`

Error notifications.

```json
{
  "type": "error",
  "message": "Error description",
  "source": "component_name" // optional
}
```

---

## Binary Audio Streaming

The WebSocket API supports binary audio packets for low-latency voice interaction:

### Audio Input

- **Binary data sent to server** via WebSocket is interpreted as PCM audio chunks for agent input
- **Format:** Raw PCM audio data (16-bit, mono, 16kHz recommended)
- **Processing:** Audio is processed in real-time for speech-to-text conversion

### Audio Output

- **Binary data from server** contains TTS audio chunks being streamed from the text-to-speech engine
- **Format:** Depends on the selected voice model's `output_format` field
  - OpenAI voices: `pcm16` format
  - HeyGen avatar: handled by HeyGen SDK (no binary output)
  - No voice: no audio output

### Implementation Example

```javascript
// Send audio input
const audioData = new Uint8Array(pcmBuffer);
websocket.send(audioData);

// Receive audio output
websocket.onmessage = (event) => {
  if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
    // This is binary audio data from TTS
    playAudioChunk(event.data);
  } else {
    // This is JSON event data
    const jsonEvent = JSON.parse(event.data);
    handleEvent(jsonEvent);
  }
};
```

### Audio Processing Pipeline

1. **Client → Server:** Raw PCM audio chunks via binary WebSocket messages
2. **Server Processing:** Speech-to-text conversion using configured STT engine
3. **Agent Processing:** Text input processed by AI agent
4. **TTS Generation:** Agent response converted to speech (if voice enabled)
5. **Server → Client:** Binary audio chunks streamed back via WebSocket

### Special Voice Models

The system includes special voice models for specific use cases:

#### Avatar Voice Model (`voice_id: "avatar"`)

- **Purpose:** Indicates HeyGen streaming avatar handles both audio and video
- **Behavior:** No binary audio sent from server to client
- **Integration:** Agent C sends "repeat" tasks to HeyGen avatar for speech synthesis
- **Usage:** Automatically set when avatar session is active

```json
{
  "voice_id": "avatar",
  "vendor": "heygen",
  "description": "HeyGen Avatar Voice Model",
  "output_format": "special"
}
```

#### No Voice Model (`voice_id: "none"`)

- **Purpose:** Text-only mode with no TTS output
- **Behavior:** Agent responses displayed as text only
- **Usage:** For clients that don't want voice output

```json
{
  "voice_id": "none",
  "vendor": "system",
  "description": "No Voice (text only)",
  "output_format": "none"
}
```

---

## Implementation Patterns

### Client Connection Flow

```javascript
// 1. Authenticate
const loginResponse = await fetch('/rt/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});
const { agent_c_token, ui_session_id } = await loginResponse.json();

// 2. Connect WebSocket (HTTPS required)
const ws = new WebSocket(`wss://host/rt/ws?token=${agent_c_token}&session_id=${ui_session_id}`);

// 3. Handle events (both JSON and binary)
ws.onmessage = (event) => {
  if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
    // Binary audio data from TTS
    handleAudioOutput(event.data);
  } else {
    // JSON event data
    const data = JSON.parse(event.data);
    handleServerEvent(data);
  }
};

// 4. Send text commands
ws.send(JSON.stringify({
  type: 'text_input',
  text: 'Hello!'
}));

// 5. Send binary audio (PCM format)
const audioData = new Uint8Array(pcmBuffer);
ws.send(audioData);
```

### Event Handling

```javascript
function handleServerEvent(event) {
  switch(event.type) {
    case 'text_delta':
      appendToMessage(event.content);
      break;
    case 'completion':
      if (!event.running) {
        enableUserInput();
      }
      break;
    case 'user_turn_start':
      enableUserInput();
      break;
    case 'user_turn_end':
      disableUserInput();
      showProcessingIndicator();
      break;
    case 'agent_voice_changed':
      updateVoiceSettings(event.voice);
      break;
    case 'avatar_connection_changed':
      // Handle avatar connection status change
      // Implementation depends on your avatar integration
      break;
    case 'error':
      showError(event.message);
      break;
    // ... handle other events
  }
}

function handleAudioOutput(audioData) {
  // Play received audio data from TTS
  playAudioChunk(audioData);
}

// Send audio input
function sendAudioInput(pcmAudioBuffer) {
  const audioData = new Uint8Array(pcmAudioBuffer);
  ws.send(audioData);
}
```

---

## Authentication & Security

### JWT Token Structure

```json
{
  "user_id": "user-uuid",
  "permissions": ["permission1", "permission2"],
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Token Refresh

- JWT tokens expire after a set time
- Use `/rt/refresh_token` endpoint to get new tokens
- HeyGen tokens also need periodic refresh
- Implement automatic token refresh in clients

---

## Error Handling

### Common Error Scenarios

1. **Authentication Failure**
   
   - Invalid credentials → 401 response
   - Expired token → WebSocket disconnect + 401

2. **Session Errors**
   
   - Invalid session_id → Error event
   - Session access denied → Error event  

3. **Avatar Errors**
   
   - Avatar creation failed → Error event
   - Avatar session timeout → Error event

4. **Runtime Errors**
   
   - Agent processing error → Error event with details
   - Tool execution failure → Error event

### Error Recovery

- Implement exponential backoff for reconnections
- Handle token refresh automatically  
- Gracefully degrade when avatar features fail
- Provide user feedback for all error states

---

## Performance Considerations

### Message Buffering

- `text_delta` events arrive rapidly during agent responses
- Implement client-side buffering to avoid UI blocking
- Consider debouncing UI updates for smooth rendering

### Connection Management

- Monitor WebSocket connection health
- Implement ping/pong heartbeat if needed
- Handle network disconnections gracefully
- Cache session state for reconnection

---

## Additional References

### Core Components

- **`//api/src/agent_c_api/core/realtime_bridge.py`** - WebSocket event handler and main bridge implementation
- **`//api/src/agent_c_api/core/voice/voice_io_manager.py`** - Voice input/output management and audio pipeline
- **`//api/src/agent_c_api/api/rt/session.py`** - Reduced footprint REST endpoints for authentication
- **`//api/src/agent_c_api/api/rt/models/client_events.py`** - Complete event model definitions

### Voice System

- **`//api/src/agent_c_api/core/voice/models.py`** - Available voice model definitions
- **`//api/src/agent_c_api/core/voice/rt_bridge_workflow.py`** - Voice processing workflow integration

### Client Tool Integration

- **`//core/src/agent_c/models/client_tool_info.py`** - Tool information models for client consumption

---

## Development Tips

1. **Event Registration** - All events auto-register with the EventRegistry
2. **Type Safety** - Use Pydantic models for strong typing
3. **Logging** - All components use structured logging
4. **Testing** - Mock WebSocket connections for testing
5. **Documentation** - Events are self-documenting via Pydantic

This guide provides the complete specification for implementing clients that interact with the Agent C Realtime API. The event-driven architecture allows for flexible, responsive real-time applications with avatar integration support.