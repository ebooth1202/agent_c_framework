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

Sent when tool calls are initiated or completed during agent interactions. This is a session event that maintains full session correlation.

**Event Type**: `tool_call`

**Payload**:

```json
{
  "type": "tool_call",
  "session_id": "sess_abc123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_abc123", 
  "active": true,
  "vendor": "anthropic",
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "name": "web_search",
      "input": {
        "query": "Python best practices"
      }
    }
  ],
  "tool_results": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "content": [
        {
          "type": "text",
          "text": "Search results found..."
        }
      ]
    }
  ]
}
```

**Fields**:

- `session_id` (string): Current session identifier
- `role` (string): Role that triggered the event
- `parent_session_id` (string, optional): Parent session ID for subsessions
- `user_session_id` (string, optional): Root user session ID
- `active` (boolean): If `true`, tools will be executed immediately after the event
- `vendor` (string): LLM provider format indicator ("anthropic", "openai")
- `tool_calls` (array): Tool calls in vendor-specific format (**CRITICAL**: Always vendor format, never generic)
- `tool_results` (array, optional): Tool execution results in vendor format (present when execution is complete)

**Vendor Format Notes**:
- **Anthropic**: Uses `type: "tool_use"` with `id`, `name`, and `input` fields
- **OpenAI**: Uses `type: "function"` with `id` and `function` object containing `name` and `arguments`

---

### ToolSelectDeltaEvent

Sent during streaming when tool calls are being assembled. Shows tools being selected and constructed in real-time during LLM completion.

**Event Type**: `tool_select_delta`

**Payload**:

```json
{
  "type": "tool_select_delta",
  "session_id": "sess_abc123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_abc123",
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "web_search",
      "input": {
        "query": "Python"
      }
    }
  ]
}
```

**Fields**:

- `session_id` (string): Current session identifier
- `role` (string): Role that triggered the event
- `parent_session_id` (string, optional): Parent session ID for subsessions
- `user_session_id` (string, optional): Root user session ID
- `tool_calls` (array): Current state of tool calls being assembled in vendor format

**Usage**: Multiple events show incremental tool call construction, followed by final `tool_call` event with complete tool calls ready for execution.

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

## Subsession Events

Subsession events manage agent-to-agent communication within the context of user sessions. These events enable complex multi-agent workflows while maintaining complete transparency for clients.

### SubsessionStartedEvent

Signals the beginning of a new subsession where agents will collaborate or delegate work to specialized assistants.

**Event Type**: `subsession_started`

**Payload**:

```json
{
  "type": "subsession_started",
  "session_id": "sess_parent_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_parent_123",
  "sub_session_type": "agent_collaboration",
  "sub_agent_type": "math_specialist",
  "prime_agent_key": "helpful_assistant",
  "sub_agent_key": "math_expert"
}
```

**Fields**:

- **`sub_session_type`** (string): Category of subsession for client styling and behavior
  - `"agent_collaboration"` - Agents working together on a problem
  - `"task_delegation"` - Primary agent delegating specific tasks
  - `"tool_execution"` - Complex tool usage requiring agent interaction
  - `"clone_execution"` - Agent spawning clones for parallel work

- **`sub_agent_type`** (string): Type of agent being used in the subsession
  - `"specialist"` - Domain-specific expert agent
  - `"clone"` - Copy of an existing agent for parallel processing
  - `"tool_agent"` - Agent specifically for tool interaction
  - `"coordinator"` - Agent for managing other agents

- **`prime_agent_key`** (string): The agent key that initiated the subsession

- **`sub_agent_key`** (string): The agent key for the subsession agent

**Client Handling**:
- Apply appropriate visual styling based on `sub_session_type`
- Track agent hierarchy for display purposes
- Prepare UI for receiving events with different `session_id` values
- Events following this will be from the subsession until `subsession_ended`

**Example**:

```json
{
  "type": "subsession_started",
  "session_id": "sess_user_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_user_123",
  "sub_session_type": "agent_collaboration",
  "sub_agent_type": "specialist", 
  "prime_agent_key": "helpful_assistant",
  "sub_agent_key": "math_expert"
}
```

---

### SubsessionEndedEvent

Signals the completion of a subsession and return to parent session context.

**Event Type**: `subsession_ended`

**Payload**:

```json
{
  "type": "subsession_ended",
  "session_id": "sess_parent_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_parent_123"
}
```

**Fields**:
- Standard session event fields (session_id, role, parent_session_id, user_session_id)
- No additional subsession-specific fields

**Client Handling**:
- Remove subsession visual indicators
- Return to parent session styling
- Update agent hierarchy displays
- Events following this will be from the parent session context

**Example**:

```json
{
  "type": "subsession_ended",
  "session_id": "sess_user_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_user_123"
}
```

### Subsession Event Correlation

**Critical Implementation Note**: Events that occur within subsessions will have different `session_id` values than the parent session. Clients must use the `parent_session_id` and `user_session_id` fields to properly correlate subsession events back to the user's chat session.

**Example Event Flow**:

```json
// 1. Subsession starts in parent session
{
  "type": "subsession_started",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123"
}

// 2. Subsequent events use different session_id but maintain correlation
{
  "type": "text_delta",
  "session_id": "sess_sub_456",  // Different session ID!
  "parent_session_id": "sess_user_123",  // Points to parent
  "user_session_id": "sess_user_123",    // Points to user session
  "role": "assistant",
  "content": "Calculating the integral..."
}

// 3. Subsession ends, back to parent session_id
{
  "type": "subsession_ended",
  "session_id": "sess_user_123",  // Back to parent session_id
  "parent_session_id": null,
  "user_session_id": "sess_user_123"
}
```

**Nesting Support**: Subsessions can be nested multiple levels deep. Each level maintains proper `parent_session_id` and `user_session_id` correlation, enabling complex agent hierarchies while preserving event traceability.

## Chat Streaming Event Sequences

This section provides the complete, precise event sequences that occur during user/agent interactions. Understanding these sequences is critical for proper client implementation.

### Basic Agent Turn Flow

When a user submits input and the agent responds, the following event sequence occurs **exactly** in this order:

1. **`interaction`** (with `started: true`) - Signals the beginning of agent processing
2. **Vendor-specific user message event** - Either `anthropic_user_message` or `open_ai_user_message` depending on the LLM provider
3. **`system_prompt`** - Contains the system prompt used for this interaction
4. **`completion`** (with `running: true`) - Indicates the LLM completion process has started
5. **Content streaming events** - Multiple `text_delta` and/or `thought_delta` events containing partial agent responses
6. **`completion`** (with `running: false`) - Indicates the LLM completion process has finished
7. **`history_delta`** - Contains the new messages added to the chat history
8. **`history`** - Contains the complete updated chat history
9. **`interaction`** (with `started: false`) - Signals the end of agent processing
10. **`user_turn_start`** - Indicates the client may now send input again

#### Example Basic Agent Turn

```json
// 1. Interaction start
{
  "type": "interaction",
  "session_id": "session_123",
  "started": true,
  "id": "interaction_456"
}

// 2. User message (vendor-specific)
{
  "type": "anthropic_user_message",
  "session_id": "session_123",
  "vendor": "anthropic",
  "message": {
    "role": "user",
    "content": "What is quantum entanglement?"
  }
}

// 3. System prompt
{
  "type": "system_prompt",
  "session_id": "session_123",
  "content": "You are a helpful AI assistant...",
  "format": "markdown"
}

// 4. Completion start
{
  "type": "completion",
  "session_id": "session_123",
  "running": true,
  "completion_options": {"model": "claude-3-sonnet", "temperature": 0.7}
}

// 5. Content streaming (multiple events)
{
  "type": "text_delta",
  "session_id": "session_123",
  "role": "assistant",
  "content": "Quantum entanglement is",
  "format": "markdown"
}

{
  "type": "text_delta",
  "session_id": "session_123",
  "role": "assistant",
  "content": " a fascinating phenomenon...",
  "format": "markdown"
}

// 6. Completion end
{
  "type": "completion",
  "session_id": "session_123",
  "running": false,
  "stop_reason": "stop",
  "input_tokens": 150,
  "output_tokens": 200
}

// 7. History delta
{
  "type": "history_delta",
  "session_id": "session_123",
  "vendor": "anthropic",
  "messages": [
    {
      "role": "user",
      "content": "What is quantum entanglement?",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Quantum entanglement is a fascinating phenomenon...",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ]
}

// 8. Complete history
{
  "type": "history",
  "session_id": "session_123",
  "vendor": "anthropic",
  "messages": [
    // ... complete conversation history
  ]
}

// 9. Interaction end
{
  "type": "interaction",
  "session_id": "session_123",
  "started": false,
  "id": "interaction_456"
}

// 10. User turn start
{
  "type": "user_turn_start",
  "session_id": "session_123"
}
```

### Tool-Enhanced Agent Turn Flow

When an agent needs to use tools during its response, additional events are inserted into the sequence:

#### Additional Tool Events

- **`tool_select_delta`** - Streamed while the agent is formulating tool calls. Contains the partially assembled tool call in vendor format. Clients can display "Agent is using [tool_name]" messages.
- **`tool_call`** (with `active: true`) - Indicates tool methods are being executed
- **`tool_call`** (with `active: false`) - Indicates tool execution is complete, with results in the `tool_results` field

#### Complete Tool Usage Sequence

1. **`interaction`** (with `started: true`)
2. **Vendor-specific user message event**
3. **`system_prompt`**
4. **`completion`** (with `running: true`)
5. **`text_delta`/`thought_delta`** events (agent reasoning)
6. **`tool_select_delta`** events (agent formulating tool calls)
7. **`tool_call`** (with `active: true`) - Tool execution begins
8. **`tool_call`** (with `active: false`) - Tool execution complete with results
9. **`text_delta`** events (agent incorporating tool results)
10. **`completion`** (with `running: false`)
11. **`history_delta`**
12. **`history`**
13. **`interaction`** (with `started: false`)
14. **`user_turn_start`**

#### Example Tool Usage

```json
// ... standard flow events 1-5 ...

// 6. Tool selection deltas
{
  "type": "tool_select_delta",
  "session_id": "session_123",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"latest quantum computing research\"}"
      }
    }
  ]
}

// 7. Tool execution start
{
  "type": "tool_call",
  "session_id": "session_123",
  "active": true,
  "vendor": "openai",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"latest quantum computing research\"}"
      }
    }
  ]
}

// 8. Tool execution complete
{
  "type": "tool_call",
  "session_id": "session_123",
  "active": false,
  "vendor": "openai",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"latest quantum computing research\"}"
      }
    }
  ],
  "tool_results": [
    {
      "tool_call_id": "call_abc123",
      "content": "Recent research shows..."
    }
  ]
}

// 9. Agent continues with tool results
{
  "type": "text_delta",
  "session_id": "session_123",
  "role": "assistant",
  "content": "Based on the latest research, ",
  "format": "markdown"
}

// ... remainder of standard flow ...
```

### User Turn Management

The system manages user/agent turns to ensure proper conversation flow:

#### User Input Processing

- **During user's turn**: Clients send input via audio data or `TextInputEvent`
- **Turn transition**: Clients receive `UserTurnEndEvent` when the server has received input and transitions to agent processing
- **Agent processing**: The complete agent turn flow executes (events 1-10 above)
- **Turn completion**: `user_turn_start` event signals the client may send input again

#### User Turn Event

```json
// Sent when server receives user input and starts agent processing
{
  "type": "user_turn_end",
  "session_id": "session_123"
}
```

### Implementation Guidance for Clients

#### Essential Event Handling

1. **Track Interaction State**
   ```javascript
   if (event.type === 'interaction' && event.started) {
     // Disable user input, show "Agent is thinking"
     setInputDisabled(true);
   } else if (event.type === 'interaction' && !event.started) {
     // Re-enable user input
     setInputDisabled(false);
   }
   ```

2. **Buffer Text Deltas**
   ```javascript
   if (event.type === 'text_delta') {
     // Accumulate deltas by role within current interaction
     appendToMessage(event.role, event.content);
   }
   ```

3. **Handle Tool Usage Feedback**
   ```javascript
   if (event.type === 'tool_select_delta' && event.tool_calls?.length > 0) {
     const toolName = event.tool_calls[0].function?.name;
     showToolUsage(`Agent is using ${toolName}...`);
   }
   ```

4. **Wait for Turn Signals**
   ```javascript
   if (event.type === 'user_turn_start') {
     // Safe to enable user input
     enableUserInput();
   }
   ```

#### Critical Implementation Rules

- **Never enable user input** until receiving `user_turn_start` event
- **Always buffer text deltas** by role within each interaction
- **Display tool usage feedback** from `tool_select_delta` events
- **Handle vendor differences** in user message events (`anthropic_user_message` vs `open_ai_user_message`)
- **Separate thought display** from regular message content
- **Track completion tokens** for usage monitoring

### Debugging and Validation

#### Expected Event Counts

For a basic agent turn without tools:
- Exactly **1** `interaction` event with `started: true`
- Exactly **1** vendor-specific user message event
- Exactly **1** `system_prompt` event
- Exactly **1** `completion` event with `running: true`
- **1 or more** `text_delta`/`thought_delta` events
- Exactly **1** `completion` event with `running: false`
- Exactly **1** `history_delta` event
- Exactly **1** `history` event
- Exactly **1** `interaction` event with `started: false`
- Exactly **1** `user_turn_start` event

#### Common Issues

- **Missing `user_turn_start`**: Client input remains disabled
- **Unhandled vendor differences**: User message events not processed correctly
- **Text delta buffer overflow**: Not clearing buffers between interactions
- **Tool feedback missing**: Users don't see tool usage indicators

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