# History API

## Overview

The History API provides comprehensive access to session histories and their events. It enables applications to retrieve, analyze, and replay past agent interactions, which is valuable for:

- **Auditing**: Review past interactions for compliance and quality assurance
- **Training**: Use successful interactions to train users on effective agent usage
- **Debugging**: Analyze problematic interactions to identify issues
- **Analytics**: Extract insights from interaction patterns and tool usage
- **Continuity**: Allow users to resume previous work or reference past solutions

This API follows RESTful design principles with resources organized around sessions and their events. It provides both synchronous query endpoints and streaming capabilities for real-time event access.

## Key Concepts

### Sessions and Histories

A **session history** represents a complete record of an interaction between a user and the agent. Each history contains multiple events, organized chronologically, that capture everything that happened during the session.

### Events

An **event** is a discrete piece of information about something that happened during a session. Events have different types including:

- **Message events**: User inputs and agent responses
- **Tool call events**: When the agent invokes tools
- **Thinking events**: Internal reasoning processes
- **System events**: Session state changes and metadata updates

### Event Filtering

The API supports filtering events by type and time range, allowing applications to focus on specific aspects of a session history.

### Replay

The **replay** functionality allows playing back a session's events with their original timing or at adjusted speeds. This can be used to recreate the session experience or analyze it at a different pace.

## Endpoints

### List Session Histories

```
GET /api/v2/history
```

Lists all available session histories with pagination and sorting options. Returns a collection of session history summaries with basic metadata.

#### Query Parameters

- `limit` (integer, default: 50): Maximum number of histories to return (1-100)
- `offset` (integer, default: 0): Number of histories to skip for pagination
- `sort_by` (string, default: "start_time"): Field to sort by (available fields: `created_at`, `updated_at`, `name`, `message_count`, `duration`)
- `sort_order` (string, default: "desc"): Sort order ("asc" for ascending, "desc" for descending)

#### Response

```json
{
  "items": [
    {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Task Planning Session",
      "created_at": "2025-04-01T14:30:00Z",
      "updated_at": "2025-04-01T15:45:00Z",
      "message_count": 24,
      "duration": 4500
    },
    {
      "session_id": "8c282a4d-1f5e-4dab-b92a-04a24eb8173c",
      "name": "Code Review Session",
      "created_at": "2025-04-02T09:15:00Z",
      "updated_at": "2025-04-02T10:30:00Z",
      "message_count": 18,
      "duration": 4200
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Get Session History Details

```
GET /api/v2/history/{session_id}
```

Retrieve detailed information about a specific session history. This endpoint provides a richer view than the list endpoint, including file information, event type breakdowns, and session metadata.

#### Path Parameters

- `session_id` (string, required): The ID of the session

#### Response

```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Task Planning Session",
  "created_at": "2025-04-01T14:30:00Z",
  "updated_at": "2025-04-01T15:45:00Z",
  "message_count": 24,
  "duration": 4500,
  "files": ["events_3fa85f64_1.jsonl", "events_3fa85f64_2.jsonl"],
  "event_types": {
    "text_delta": 120,
    "tool_call": 15,
    "user_request": 12,
    "thinking": 30
  },
  "metadata": {
    "model": "gpt-4-turbo",
    "completion_tokens": 4820,
    "prompt_tokens": 1650
  },
  "user_id": "user_12345",
  "has_thinking": true,
  "tool_calls": ["web_search", "file_reader", "code_interpreter"]
}
```

#### Error Responses

- `404 Not Found`: Session history not found

### Delete Session History

```
DELETE /api/v2/history/{session_id}
```

Delete a session history and all its associated event files and metadata. This permanently removes the session's record from the system.

#### Path Parameters

- `session_id` (string, required): The ID of the session to delete

#### Response

```json
{
  "status": {
    "success": true,
    "message": "Session history deleted successfully",
    "error_code": null
  },
  "data": {
    "status": "success", 
    "message": "Session history 3fa85f64-5717-4562-b3fc-2c963f66afa6 deleted successfully"
  }
}
```

#### Error Responses

- `404 Not Found`: Session history not found or could not be deleted

### Get Session Events

```
GET /api/v2/history/{session_id}/events
```

Retrieve events for a specific session with flexible filtering options. Events can be filtered by type, time range, and limited to control response size. The response is paginated to handle large event histories efficiently.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Query Parameters

- `event_types` (array of strings, optional): Filter by event types (e.g., `message`, `tool_call`, `thinking`, `text_delta`)
- `start_time` (datetime, optional): Filter events after this timestamp (ISO-8601 format)
- `end_time` (datetime, optional): Filter events before this timestamp (ISO-8601 format)
- `limit` (integer, default: 100): Maximum number of events to return (1-1000)

#### Filter Examples

**Filter by event type**:
```
GET /api/v2/history/3fa85f64-5717-4562-b3fc-2c963f66afa6/events?event_types=tool_call&event_types=thinking
```

**Filter by time range**:
```
GET /api/v2/history/3fa85f64-5717-4562-b3fc-2c963f66afa6/events?start_time=2025-04-01T14:45:00Z&end_time=2025-04-01T15:15:00Z
```

**Combined filtering**:
```
GET /api/v2/history/3fa85f64-5717-4562-b3fc-2c963f66afa6/events?event_types=message&start_time=2025-04-01T14:30:00Z&limit=50
```

#### Response

```json
{
  "status": {
    "success": true,
    "message": null,
    "error_code": null
  },
  "data": [
    {
      "id": "evt_1234567890",
      "timestamp": "2025-04-01T14:32:15Z",
      "event": {
        "event_type": "message",
        "role": "user",
        "content": "Can you help me analyze this dataset?",
        "message_id": "msg_abcdef123456"
      }
    },
    {
      "id": "evt_0987654321",
      "timestamp": "2025-04-01T14:35:42Z",
      "event": {
        "event_type": "tool_call",
        "tool_name": "data_analysis",
        "input": {
          "file_path": "data.csv",
          "operation": "summary_statistics"
        },
        "call_id": "call_defabc456789"
      }
    },
    {
      "id": "evt_5678901234",
      "timestamp": "2025-04-01T14:33:10Z",
      "event": {
        "event_type": "thinking",
        "content": "I should first check what format the dataset is in, then determine appropriate analysis methods.",
        "thinking_id": "think_987654abcdef"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 120,
    "total_pages": 3
  }
}
```

#### Error Responses

- `404 Not Found`: No events found for the session
- `500 Internal Server Error`: Failed to retrieve events

### Stream Session Events

```
GET /api/v2/history/{session_id}/stream
```

Stream events for a session as a server-sent events (SSE) stream. This endpoint supports real-time playback with original timing between events or as fast as possible delivery, making it ideal for session replay features.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Query Parameters

- `event_types` (array of strings, optional): Filter by event types (e.g., `message`, `tool_call`, `thinking`)
- `real_time` (boolean, default: false): When true, replays events with original timing; when false, streams as fast as possible
- `speed_factor` (float, default: 1.0): Speed multiplier for real-time replay (0.1-10.0, where 1.0 is original speed)

#### Stream Format

The response is a standard Server-Sent Events (SSE) stream with each event containing a JSON payload in the following format:

```
data: {"id":"evt_1234567890","timestamp":"2025-04-01T14:32:15Z","event":{...event specific data...}}

```

#### Client Example (JavaScript)

```javascript
const eventSource = new EventSource('/api/v2/history/3fa85f64-5717-4562-b3fc-2c963f66afa6/stream?real_time=true&speed_factor=1.5');

eventSource.onmessage = (event) => {
  const eventData = JSON.parse(event.data);
  console.log('Event received:', eventData);
  // Process the event based on its type
  switch(eventData.event.event_type) {
    case 'message':
      displayMessage(eventData);
      break;
    case 'tool_call':
      displayToolCall(eventData);
      break;
    // Handle other event types
  }
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

#### Response

A text/event-stream response with JSON event data.

#### Error Responses

- `500 Internal Server Error`: Failed to stream events

### Get Replay Status

```
GET /api/v2/history/{session_id}/replay
```

Get the current status of a session replay. This endpoint returns information about an active replay session, including whether it's currently playing, the current position in the timeline, and the total time range covered by the session.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Response

```json
{
  "status": {
    "success": true,
    "message": null,
    "error_code": null
  },
  "data": {
    "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "is_playing": true,
    "current_position": "2025-04-01T14:40:15Z",
    "start_time": "2025-04-01T14:30:00Z",
    "end_time": "2025-04-01T15:45:00Z"
  }
}
```

#### Replay Status Fields

- `session_id`: Unique identifier of the session being replayed
- `is_playing`: Whether the replay is currently playing (true) or paused (false)
- `current_position`: Current timestamp position in the replay timeline
- `start_time`: Timestamp of the first event in the session
- `end_time`: Timestamp of the last event in the session

#### Error Responses

- `404 Not Found`: No active replay for the session
- `500 Internal Server Error`: Failed to get replay status

### Control Replay

```
POST /api/v2/history/{session_id}/replay
```

Control a session replay with various playback actions. This endpoint allows controlling the playback of session replays with three main actions: play, pause, and seek. It also supports speed control for flexible playback rates.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Request Body

#### Action Options

- `play`: Start or resume playback, optionally at a specific speed
- `pause`: Pause the current playback
- `seek`: Jump to a specific position in the timeline

#### Request Body Examples

**Start playback at normal speed**:
```json
{
  "action": "play",
  "speed": 1.0
}
```

**Start playback at 2x speed**:
```json
{
  "action": "play",
  "speed": 2.0
}
```

**Pause playback**:
```json
{
  "action": "pause"
}
```

**Seek to a specific position**:
```json
{
  "action": "seek",
  "position": "2025-04-01T14:35:00Z"
}
```

#### Response

```json
{
  "status": {
    "success": true,
    "message": "Replay control 'play' successful",
    "error_code": null
  },
  "data": true
}
```

## Event Types Reference

The history API works with various event types that capture different aspects of agent-user interactions. The main event types include:

### Message Events

- **message**: Complete messages between users and the agent
  - Contains `role` (user/assistant/system), `content`, and message identifiers
  - Used for displaying complete messages in a conversation view

### Agent Processing Events

- **thinking**: Internal reasoning events from the agent
  - Contains the agent's thought process, reasoning steps, and planning
  - Only available when agent is configured to expose thinking

- **text_delta**: Incremental text generation events
  - Contains partial text as it's being generated by the agent
  - Used for streaming responses to create a typing effect

### Tool Interaction Events

- **tool_call**: Events when the agent invokes a tool
  - Contains tool name, input parameters, and call identifier
  - Shows what tools the agent used and with what parameters

- **tool_result**: Results returned from tool calls
  - Contains the output/result data from a tool execution
  - Shows what information the tool provided to the agent

### System Events

- **session_start**: Marks the beginning of a session
  - Contains initial session configuration and metadata
  - Used to identify when a session began

- **session_end**: Marks the end of a session
  - Contains final session state and summary information
  - Used to identify when a session completed

## Integration Guide

### Building a Session Replay Feature

To build a complete session replay feature, combine the endpoints as follows:

1. **List available sessions** using `GET /api/v2/history`
2. **Get session details** using `GET /api/v2/history/{session_id}`
3. **Initialize replay controls** using `GET /api/v2/history/{session_id}/replay`
4. **Begin playback** using `POST /api/v2/history/{session_id}/replay` with action `play`
5. **Stream events** using `GET /api/v2/history/{session_id}/stream?real_time=true`

This pattern allows building an interactive replay interface that shows session events with their original timing, with the ability to pause, seek, and adjust playback speed.

#### Error Responses

- `500 Internal Server Error`: Failed to control replay