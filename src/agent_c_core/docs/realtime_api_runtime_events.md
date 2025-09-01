# Runtime Events Reference

This document describes all event types that the Agent C Realtime API sends to clients via WebSocket connection.

## Event Structure

All runtime events follow a consistent JSON structure:

```json
{
  "type": "event_type_name",
  "session_id": "string",
  "role": "string",
  // ... event-specific fields
}
```

Most events include `session_id` and `role` fields for context, though some system events may omit these.

## Session Management Events

### AgentListEvent

Sent automatically when a client connects, or in response to a `GetAgentsEvent`.

**Event Type**: `agent_list`

**Payload**:

```json
{
  "type": "agent_list",
  "agents": [
    {
      "key": "string",
      "name": "string",
      "description": "string",
      "tools": ["string"]
    }
  ]
}
```

**Fields**:

- `agents` (array): List of available agent configurations
  - `key` (string): Unique identifier for the agent
  - `name` (string): Display name of the agent
  - `description` (string): Description of the agent's capabilities
  - `tools` (array): List of tool names available to this agent

**Example**:

```json
{
  "type": "agent_list",
  "agents": [
    {
      "key": "helpful_assistant",
      "name": "Helpful Assistant",
      "description": "A general-purpose AI assistant",
      "tools": ["WebSearch", "Calculator"]
    }
  ]
}
```

---

### AgentConfigurationChangedEvent

Sent when an agent is successfully set for the session.

**Event Type**: `agent_configuration_changed`

**Payload**:

```json
{
  "type": "agent_configuration_changed",
  "agent_config": {
    "key": "string",
    "name": "string",
    "description": "string",
    "tools": ["string"],
    // ... additional configuration fields
  }
}
```

**Fields**:

- `agent_config` (object): Complete configuration of the active agent

**Example**:

```json
{
  "type": "agent_configuration_changed",
  "agent_config": {
    "key": "helpful_assistant",
    "name": "Helpful Assistant",
    "description": "A general-purpose AI assistant",
    "tools": ["WebSearch", "Calculator"]
  }
}
```

---

### AvatarListEvent

Sent automatically when a client connects, or in response to a `GetAvatarsEvent`.

**Event Type**: `avatar_list`

**Payload**:

```json
{
  "type": "avatar_list",
  "avatars": [
    {
      "avatar_id": "string",
      "avatar_name": "string",
      "preview_image": "string",
      "gender": "string"
    }
  ]
}
```

**Fields**:

- `avatars` (array): List of available HeyGen avatars
  - `avatar_id` (string): Unique identifier for the avatar
  - `avatar_name` (string): Display name of the avatar
  - `preview_image` (string): URL to avatar preview image
  - `gender` (string): Avatar gender

**Example**:

```json
{
  "type": "avatar_list",
  "avatars": [
    {
      "avatar_id": "anna_public_3_20240108",
      "avatar_name": "Anna",
      "preview_image": "https://example.com/avatar.jpg",
      "gender": "female"
    }
  ]
}
```

---

### AvatarConnectionChangedEvent

Sent when an avatar is successfully set and a HeyGen session is established.

**Event Type**: `avatar_connection_changed`

**Payload**:

```json
{
  "type": "avatar_connection_changed",
  "avatar_session": {
    "session_id": "string",
    "session_token": "string",
    "url": "string",
    "avatar_id": "string",
    "quality": "string",
    "video_encoding": "string"
  }
}
```

**Fields**:

- `avatar_session` (object): HeyGen session details for client-side avatar connection
  - `session_id` (string): HeyGen session identifier
  - `session_token` (string): Authentication token for HeyGen connection
  - `url` (string): WebSocket URL for HeyGen avatar stream
  - `avatar_id` (string): Selected avatar identifier
  - `quality` (string): Video quality setting
  - `video_encoding` (string): Video encoding format

**Usage**: Clients use this data to establish their own connection to HeyGen for avatar video/audio streaming.

**Example**:

```json
{
  "type": "avatar_connection_changed",
  "avatar_session": {
    "session_id": "heygen_session_123",
    "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "url": "wss://api.heygen.com/v1/streaming.start",
    "avatar_id": "anna_public_3_20240108",
    "quality": "medium",
    "video_encoding": "VP8"
  }
}
```

## Interaction Events

### InteractionEvent

Signals the start or end of an agent interaction.

**Event Type**: `interaction`

**Payload**:

```json
{
  "type": "interaction",
  "session_id": "string",
  "started": boolean,
  "id": "string"
}
```

**Fields**:

- `started` (boolean): `true` when interaction begins, `false` when it ends
- `id` (string): Unique identifier for this interaction

**Usage**: Clients should disable input when `started: true` and re-enable when `started: false`.

**Example**:

```json
{
  "type": "interaction",
  "session_id": "session_123",
  "started": true,
  "id": "interaction_456"
}
```

---

### CompletionEvent

Provides information about the completion process and token usage.

**Event Type**: `completion`

**Payload**:

```json
{
  "type": "completion",
  "session_id": "string",
  "running": boolean,
  "completion_options": {},
  "stop_reason": "string",
  "input_tokens": number,
  "output_tokens": number
}
```

**Fields**:

- `running` (boolean): Whether the completion is currently active
- `completion_options` (object): LLM provider-specific options used
- `stop_reason` (string): Reason completion stopped ("stop", "length", "tool_calls", etc.)
- `input_tokens` (number): Number of input tokens consumed
- `output_tokens` (number): Number of output tokens generated

**Special Avatar Handling**: When `running: false` and there's remaining cached text, it's sent to the avatar for speech.

**Example**:

```json
{
  "type": "completion",
  "session_id": "session_123",
  "running": false,
  "completion_options": {"model": "gpt-4", "temperature": 0.7},
  "stop_reason": "stop",
  "input_tokens": 150,
  "output_tokens": 75
}
```

## Streaming Events

### TextDeltaEvent

Streams chunks of text content from the agent.

**Event Type**: `text_delta`

**Payload**:

```json
{
  "type": "text_delta",
  "session_id": "string",
  "role": "string",
  "content": "string",
  "format": "string"
}
```

**Fields**:

- `role` (string): Message role ("assistant", "user", "system")
- `content` (string): Text chunk/delta
- `format` (string): Content format (default: "markdown")

**Special Avatar Handling**: 

- Text deltas are cached until a newline (`\n`) is received
- Complete sentences are sent to HeyGen for avatar speech
- Larger text blocks are then sent to client for display

**Example**:

```json
{
  "type": "text_delta",
  "session_id": "session_123",
  "role": "assistant",
  "content": "Hello, I can help you with",
  "format": "markdown"
}
```

---

### ThoughtDeltaEvent

Streams the agent's thinking process (internal reasoning).

**Event Type**: `thought_delta`

**Payload**:

```json
{
  "type": "thought_delta",
  "session_id": "string",
  "role": "string",
  "content": "string",
  "format": "string"
}
```

**Fields**: Same as `TextDeltaEvent` but represents internal agent thoughts.

**Special Avatar Handling**:

- First thought delta triggers avatar to say a "thinking" message
- Helps maintain engagement while agent processes complex requests
- Thoughts are streamed to client but not spoken by avatar

**Example**:

```json
{
  "type": "thought_delta",
  "session_id": "session_123",
  "role": "assistant (thought)",
  "content": "I need to consider the user's question about quantum physics...",
  "format": "markdown"
}
```

---

### CompleteThoughtEvent

Indicates a complete thought has been processed.

**Event Type**: `complete_thought`

**Payload**: Same structure as `ThoughtDeltaEvent` but represents a complete thought block.

---

### AudioDeltaEvent

Streams audio content (when supported by the agent).

**Event Type**: `audio_delta`

**Payload**:

```json
{
  "type": "audio_delta",
  "session_id": "string",
  "id": "string",
  "content": "string",
  "content_type": "string"
}
```

**Fields**:

- `id` (string): Audio stream identifier
- `content` (string): Base64-encoded audio data
- `content_type` (string): Audio format (e.g., "audio/L16")

**Example**:

```json
{
  "type": "audio_delta",
  "session_id": "session_123",
  "id": "audio_stream_1",
  "content": "UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "content_type": "audio/L16"
}
```

## Message Events

### MessageEvent

Sends a complete message (typically for system announcements).

**Event Type**: `message`

**Payload**:

```json
{
  "type": "message",
  "session_id": "string",
  "content": "string",
  "format": "string"
}
```

**Fields**:

- `content` (string): Complete message content
- `format` (string): Content format (default: "markdown")

---

### SystemMessageEvent

Sends system-level messages with severity indicators.

**Event Type**: `system_message`

**Payload**:

```json
{
  "type": "system_message",
  "session_id": "string",
  "content": "string",
  "format": "string",
  "severity": "string"
}
```

**Fields**:

- `content` (string): System message content
- `format` (string): Content format (default: "markdown")
- `severity` (string): Message severity ("info", "warning", "error")

**Example**:

```json
{
  "type": "system_message",
  "session_id": "session_123",
  "content": "Connection to external service restored",
  "format": "markdown",
  "severity": "info"
}
```

## History Events

### HistoryEvent

Sends the complete chat history.

**Event Type**: `history`

**Payload**:

```json
{
  "type": "history",
  "session_id": "string",
  "messages": [
    {
      "role": "string",
      "content": "string",
      "timestamp": "string"
    }
  ]
}
```

**Fields**:

- `messages` (array): Complete list of chat messages

---

### HistoryDeltaEvent

Sends newly added messages to the history.

**Event Type**: `history_delta`

**Payload**:

```json
{
  "type": "history_delta",
  "session_id": "string",
  "messages": [
    {
      "role": "string",
      "content": "string",
      "timestamp": "string"
    }
  ]
}
```

**Fields**:

- `messages` (array): New messages added to history

## Tool Events

### ToolCallEvent

Indicates tool calls are being executed.

**Event Type**: `tool_call`

**Payload**:

```json
{
  "type": "tool_call",
  "session_id": "string",
  "tool_calls": [
    {
      "id": "string",
      "name": "string",
      "arguments": {}
    }
  ],
  "vendor": "string"
}
```

**Fields**:

- `tool_calls` (array): List of tools being called
- `vendor` (string): LLM provider ("open_ai", "anthropic", etc.)

---

### ToolCallDeltaEvent

Streams tool call execution progress.

**Event Type**: `tool_call_delta`

**Payload**: Similar to `ToolCallEvent` but for streaming updates.

## Error Events

### ErrorEvent

Reports errors and exceptional conditions.

**Event Type**: `error`

**Payload**:

```json
{
  "type": "error",
  "message": "string"
}
```

**Fields**:

- `message` (string): Human-readable error description

**Common Error Scenarios**:

- Invalid JSON received
- Unknown event types
- Agent/avatar not found
- Runtime exceptions
- Connection failures

**Example**:

```json
{
  "type": "error",
  "message": "Agent 'nonexistent_agent' not found"
}
```

## Event Flow Examples

### Typical Interaction Flow

1. **User sends text input**
2. **Interaction starts**:
   
   ```json
   {"type": "interaction", "started": true, "id": "int_123"}
   ```
3. **Completion begins**:
   
   ```json
   {"type": "completion", "running": true, ...}
   ```
4. **Agent thinks** (if using thinking tools):
   
   ```json
   {"type": "thought_delta", "content": "Let me analyze...", ...}
   ```
5. **Agent responds**:
   
   ```json
   {"type": "text_delta", "content": "Based on your question", ...}
   {"type": "text_delta", "content": " about quantum physics...", ...}
   ```
6. **Completion ends**:
   
   ```json
   {"type": "completion", "running": false, "stop_reason": "stop", ...}
   ```
7. **History updated**:
   
   ```json
   {"type": "history_delta", "messages": [...], ...}
   ```
8. **Interaction ends**:
   
   ```json
   {"type": "interaction", "started": false, "id": "int_123"}
   ```

### Avatar-Specific Behavior

**Text Delta Caching**: Instead of receiving many small text deltas, avatar clients receive larger, complete statements after newlines are detected.

**Thought Handling**: When the first thought delta arrives, the avatar says "Let me think about that..." to maintain engagement.

**Speech Synchronization**: Text sent to HeyGen for speech is also sent to the client as enhanced text deltas for display synchronization.

## Best Practices for Clients

1. **Handle All Event Types**: Implement handlers for all event types, even if just logging unknown ones
2. **Buffer Text Deltas**: Accumulate text deltas by role within each interaction
3. **Track Interaction State**: Use interaction events to manage UI state
4. **Display Thoughts Separately**: Show thought deltas in a different UI area from regular responses
5. **Handle Errors Gracefully**: Always implement error event handling
6. **Monitor Completion Events**: Use token counts for usage tracking and billing
7. **Maintain History**: Use history events to keep local chat state synchronized