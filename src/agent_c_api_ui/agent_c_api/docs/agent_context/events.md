# Events API

> **Documentation generated**: May 1, 2025

Endpoints for accessing and streaming events from agent interaction sessions.

## Get Session Events

```
GET /api/v1/events/{session_id}
```

Gets events for a specific session with filtering options.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_types` | string | No | Comma-separated list of event types to filter (e.g., `SYSTEM_PROMPT,INTERACTION,TOOL_CALL`) |
| `start_time` | string | No | Filter events after this ISO 8601 timestamp |
| `end_time` | string | No | Filter events before this ISO 8601 timestamp |
| `limit` | number | No | Maximum number of events to return (default: 1000) |

### Response

| Field | Type | Description |
|-------|------|-------------|
| (array) | array | List of event objects |
| [].timestamp | string | ISO 8601 timestamp of the event |
| [].type | string | Event type (e.g., "INTERACTION", "TOOL_CALL") |
| [].session_id | string | Session ID |
| [].role | string | Role (e.g., "user", "assistant", "system") |
| [].content | string | Event content |
| [].format | string | Content format (e.g., "text", "json") |
| [].running | boolean | Whether the interaction is running |
| [].active | boolean | Whether the interaction is active |
| [].vendor | string | Vendor name if applicable |
| [].tool_calls | array | Tool calls if applicable |
| [].tool_results | array | Tool results if applicable |
| [].raw | object | Original event data |

#### Response Example

```json
[
  {
    "timestamp": "2025-04-30T08:40:00.000Z",
    "type": "INTERACTION",
    "session_id": "ses_1234567890abcdef",
    "role": "user",
    "content": "Can you help me with a Python problem?",
    "format": "text",
    "running": false,
    "active": true,
    "vendor": null,
    "tool_calls": [],
    "tool_results": [],
    "raw": {}
  },
  {
    "timestamp": "2025-04-30T08:40:05.000Z",
    "type": "INTERACTION",
    "session_id": "ses_1234567890abcdef",
    "role": "assistant",
    "content": "Of course! I'd be happy to help with your Python problem. What specific issue are you facing?",
    "format": "text",
    "running": false,
    "active": true,
    "vendor": "openai",
    "tool_calls": [],
    "tool_results": [],
    "raw": {}
  },
  {
    "timestamp": "2025-04-30T08:40:30.000Z",
    "type": "TOOL_CALL",
    "session_id": "ses_1234567890abcdef",
    "role": "assistant",
    "content": null,
    "format": "json",
    "running": true,
    "active": true,
    "vendor": "openai",
    "tool_calls": [
      {
        "name": "think",
        "parameters": {
          "thought": "Let me analyze this Python code to understand the issue."
        }
      }
    ],
    "tool_results": [],
    "raw": {}
  }
]
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - No events found for session |

## Stream Session Events

```
GET /api/v1/events/{session_id}/stream
```

Streams events for a specific session, optionally in real-time.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_types` | string | No | Comma-separated list of event types to filter |
| `real_time` | boolean | No | Whether to replay events with original timing (default: false) |
| `speed_factor` | number | No | Speed multiplier for real-time replay (default: 1.0) |

### Response

A streaming response of events in the `text/event-stream` format.

**Content-Type**: `text/event-stream`

Each event is sent as a Server-Sent Event with JSON data.

#### Response Example

```
event: event
data: {"timestamp":"2025-04-30T08:40:00.000Z","type":"INTERACTION","session_id":"ses_1234567890abcdef","role":"user","content":"Can you help me with a Python problem?","format":"text","running":false,"active":true}

event: event
data: {"timestamp":"2025-04-30T08:40:05.000Z","type":"INTERACTION","session_id":"ses_1234567890abcdef","role":"assistant","content":"Of course! I'd be happy to help with your Python problem. What specific issue are you facing?","format":"text","running":false,"active":true,"vendor":"openai"}

```

## Get Replay Status

```
GET /api/v1/events/{session_id}/replay-status
```

Gets the current status of a session replay.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Session ID |
| `status` | string | Current replay status (e.g., "playing", "paused", "stopped") |
| `current_position` | string | ISO 8601 timestamp of current position in the replay |
| `start_time` | string | ISO 8601 timestamp of when the replay started |
| `speed_factor` | number | Current replay speed factor |
| `total_events` | number | Total number of events in the session |
| `current_event_index` | number | Index of the current event being replayed |

#### Response Example

```json
{
  "session_id": "ses_1234567890abcdef",
  "status": "playing",
  "current_position": "2025-04-30T08:42:15.000Z",
  "start_time": "2025-05-01T11:30:00.000Z",
  "speed_factor": 2.0,
  "total_events": 156,
  "current_event_index": 78
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - No active replay for session |

## Control Replay

```
POST /api/v1/events/{session_id}/replay/control
```

Controls a session replay (play, pause, stop, seek).

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | Action to perform: "play", "pause", "stop", or "seek" |
| `position` | string | No | ISO 8601 timestamp to seek to (required for "seek" action) |
| `speed_factor` | number | No | Speed factor for playback (optional for "play" action) |

#### Request Example

```json
{
  "action": "play",
  "speed_factor": 2.0
}
```

or

```json
{
  "action": "seek",
  "position": "2025-04-30T08:42:00.000Z"
}
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `action` | string | The action that was performed |

#### Response Example

```json
{
  "status": "success",
  "action": "play"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid replay control action |