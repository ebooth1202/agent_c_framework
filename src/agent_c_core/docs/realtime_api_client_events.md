# Client Events Reference

This document describes all event types that clients can send to the Agent C Realtime API via WebSocket connection.

## Event Structure

All client events follow a consistent JSON structure:

```json
{
  "type": "event_type_name",
  // ... event-specific fields
}
```

The `type` field is required for all events and determines how the event will be processed by the API.

## Authentication Events

### Connection Authentication

Authentication is handled during the WebSocket handshake via JWT token. No separate authentication events are required once connected.

## Agent Management Events

### GetAgentsEvent

Requests a list of available agents from the API.

**Event Type**: `get_agents`

**Payload**:

```json
{
  "type": "get_agents"
}
```

**Fields**: None (this event requires no additional data)

**Response**: The API will respond with an `AgentListEvent` containing available agents.

**Example**:

```json
{
  "type": "get_agents"
}
```

---

### SetAgentEvent

Sets the active agent for the current session.

**Event Type**: `set_agent`

**Payload**:

```json
{
  "type": "set_agent",
  "agent_key": "string"
}
```

**Fields**:

- `agent_key` (string, required): The unique identifier of the agent to activate

**Validation**:

- `agent_key` must be a valid agent identifier from the available agents list
- Agent must exist in the system configuration

**Response**: The API will respond with an `AgentConfigurationChangedEvent` if successful, or an `ErrorEvent` if the agent is not found.

**Example**:

```json
{
  "type": "set_agent",
  "agent_key": "helpful_assistant"
}
```

## Avatar Management Events

### GetAvatarsEvent

Requests a list of available avatars from the HeyGen service.

**Event Type**: `get_avatars`

**Payload**:

```json
{
  "type": "get_avatars"
}
```

**Fields**: None (this event requires no additional data)

**Response**: The API will respond with an `AvatarListEvent` containing available avatars.

**Example**:

```json
{
  "type": "get_avatars"
}
```

---

### SetAvatarEvent

Sets the active avatar for the current session and establishes a HeyGen streaming session.

**Event Type**: `set_avatar`

**Payload**:

```json
{
  "type": "set_avatar",
  "avatar_id": "string",
  "quality": "string",
  "video_encoding": "string"
}
```

**Fields**:

- `avatar_id` (string, required): The unique identifier of the avatar to activate
- `quality` (string, optional): Video quality setting. Default: `"medium"`
- `video_encoding` (string, optional): Video encoding format. Default: `"VP8"`

**Validation**:

- `avatar_id` must be a valid avatar identifier from the available avatars list
- `quality` must be one of: `"low"`, `"medium"`, `"high"`
- `video_encoding` must be one of: `"VP8"`, `"H264"`

**Response**: The API will respond with an `AvatarConnectionChangedEvent` containing session details if successful, or an `ErrorEvent` if the avatar setup fails.

**Example**:

```json
{
  "type": "set_avatar",
  "avatar_id": "anna_public_3_20240108",
  "quality": "high",
  "video_encoding": "H264"
}
```

## Interaction Events

### TextInputEvent

Sends text input to the active agent for processing.

**Event Type**: `text_input`

**Payload**:

```json
{
  "type": "text_input",
  "text": "string",
  "file_ids": ["string"]
}
```

**Fields**:

- `text` (string, required): The text message to send to the agent
- `file_ids` (array of strings, optional): List of file IDs to include with the message. Default: `[]`

**Validation**:

- `text` must be a non-empty string
- `file_ids` must be an array of valid file identifiers (if provided)
- An agent must be set before sending text input

**Response**: The API will respond with a series of runtime events including `InteractionEvent`, `CompletionEvent`, `TextDeltaEvent`, and others as the agent processes the input.

**Example**:

```json
{
  "type": "text_input",
  "text": "Hello, can you help me understand quantum physics?",
  "file_ids": []
}
```

**Example with files**:

```json
{
  "type": "text_input",
  "text": "Please analyze this document",
  "file_ids": ["file_12345", "file_67890"]
}
```

## Event Flow Examples

### Typical Session Setup Flow

1. **Connect to WebSocket** with JWT token
2. **Receive initial events** (agent list and avatar list sent automatically)
3. **Set agent**:
   
   ```json
   {"type": "set_agent", "agent_key": "helpful_assistant"}
   ```
4. **Set avatar**:
   
   ```json
   {"type": "set_avatar", "avatar_id": "anna_public_3_20240108"}
   ```
5. **Send text input**:
   
   ```json
   {"type": "text_input", "text": "Hello!"}
   ```

### Requesting Lists Manually

If you need to refresh the available agents or avatars:

```json
{"type": "get_agents"}
```

```json
{"type": "get_avatars"}
```

## Error Handling

### Invalid Event Type

If you send an event with an unknown `type`, you'll receive an `ErrorEvent`:

```json
{
  "type": "error",
  "message": "Unknown event type: invalid_event"
}
```

### Malformed JSON

If the JSON is malformed, you'll receive an `ErrorEvent`:

```json
{
  "type": "error",
  "message": "Invalid JSON received"
}
```

### Validation Errors

If required fields are missing or invalid, you'll receive an `ErrorEvent`:

```json
{
  "type": "error",
  "message": "Agent 'nonexistent_agent' not found"
}
```

## Best Practices

1. **Wait for responses**: After setting an agent or avatar, wait for the confirmation event before proceeding
2. **Handle errors gracefully**: Always listen for `ErrorEvent` responses and handle them appropriately
3. **Validate locally**: Validate event structure client-side before sending to reduce errors
4. **Set agent first**: Always set an agent before sending text input
5. **File handling**: Ensure files are uploaded and available before referencing them in `file_ids`

## Rate Limiting

The API does not currently implement explicit rate limiting, but clients should:

- Avoid sending rapid-fire events
- Wait for completion events before sending new text input
- Implement reasonable delays between requests

## Session State

Remember that the Realtime API maintains session state:

- Agent selection persists throughout the session
- Avatar selection persists throughout the session
- Chat history is maintained across interactions
- File uploads are session-scoped