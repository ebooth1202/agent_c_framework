# Agent C Realtime API

## Overview

The Agent C Realtime API provides bi-directional event streaming over WebSocket connections, enabling real-time communication between clients and Agent C agents. This API is designed to support persistent connections that remain active throughout the entire client session, rather than just during individual chat interactions.

The initial implementation focuses on integration with HeyGen's streaming avatar API, allowing clients to create interactive avatar experiences powered by Agent C agents.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌───────────────────┐
│                 │      │                  │      │                   │
│   Client App    │◄────►│  AvatarBridge    │◄────►│  Agent Runtime    │
│                 │      │                  │      │                   │
└─────────────────┘      └────────┬─────────┘      └───────────────────┘
         │                         │                          │
         │ WebSocket               │                          │
         │ /api/avatar/ws          │                          │
         │                         ▼                          │
         │                ┌──────────────────┐                │
         │                │                  │                │
         └───────────────►│  FastAPI Router  │◄───────────────┘
                          │                  │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │                  │
                          │  HeyGen Client   │
                          │                  │
                          └──────────────────┘
```

### Key Components

- **WebSocket Endpoint**: `/api/avatar/ws` - Entry point for client connections
- **AvatarBridge**: Core component that manages the connection and routes events
- **Agent Runtime**: Executes agent logic and generates responses
- **HeyGen Integration**: Handles avatar session management and speech synthesis

## Connection Flow

1. **Authentication**: Client connects to `/api/avatar/ws` with JWT token
2. **Session Initialization**: API validates token and creates avatar session
3. **Initial Setup**: Bridge sends available agents and avatars to client
4. **Configuration**: Client selects agent and avatar via events
5. **Active Session**: Bi-directional event streaming begins
6. **Cleanup**: Connection cleanup when client disconnects

## Event System

The API uses a structured event system with two main categories:

### Client Events (Client → API)

Events sent by the client to control the session and send input:

- Agent selection and configuration
- Avatar selection and setup
- Text input for agent processing
- Session management commands

### Runtime Events (API → Client)

Events sent by the API to provide real-time updates:

- Agent response streaming (text deltas)
- Agent thinking process (thought deltas)
- Completion status updates
- Error notifications
- Session state changes

## Special Features

### Text Delta Caching

Text deltas from agents are cached until a newline character is received. This ensures:

- Complete statements are sent to HeyGen for avatar speech
- Clients receive coherent text blocks for display
- Avatar speech synchronization is maintained

### Thought Delta Handling

When agents begin thinking (first thought delta), the avatar is triggered to:

- Say a "thinking" message to maintain engagement
- Provide visual/audio feedback during processing
- Create natural conversation flow

### Persistent Connection

Unlike traditional chat APIs, this connection remains active:

- Throughout the entire client session
- Across multiple agent interactions
- Until explicitly closed by client or server

## Authentication

The API uses JWT token authentication for WebSocket connections:

- Token must be provided during WebSocket handshake
- Token is validated before session creation
- Invalid tokens result in connection rejection

## Error Handling

The API provides comprehensive error handling:

- Malformed JSON events result in error responses
- Unknown event types are logged and rejected
- Runtime errors are caught and reported to client
- Connection failures are logged and cleaned up

## Use Cases

### Primary Use Case: HeyGen Avatar Integration

- Interactive avatar conversations powered by Agent C agents
- Real-time speech synthesis and visual feedback
- Persistent avatar sessions with context retention

## Getting Started

To integrate with the Realtime API:

1. Obtain a valid JWT token for authentication
2. Establish WebSocket connection to `/api/avatar/ws`
3. Handle initial agent and avatar list events
4. Send configuration events to set up your session
5. Begin sending text input and handling responses

For detailed integration examples, see the [Integration Guide](realtime_api_integration_guide.md).

For complete event reference, see:

- [Client Events Reference](realtime_api_client_events.md)
- [Runtime Events Reference](realtime_api_runtime_events.md)
- [HeyGen Integration Guide](realtime_api_heygen_integration.md)