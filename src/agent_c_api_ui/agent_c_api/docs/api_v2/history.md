# History API

The History API provides access to session histories and their events. This allows you to list available session histories, retrieve details about specific sessions, access and filter events, and manage history data.

## Endpoints

### List Session Histories

```
GET /api/v2/history
```

Lists all available session histories with pagination and sorting options.

#### Query Parameters

- `limit` (integer, default: 50): Maximum number of histories to return (1-100)
- `offset` (integer, default: 0): Number of histories to skip
- `sort_by` (string, default: "start_time"): Field to sort by
- `sort_order` (string, default: "desc"): Sort order ("asc" or "desc")

#### Response

```json
{
  "items": [
    {
      "id": "string",
      "start_time": "2023-01-01T12:00:00Z",
      "end_time": "2023-01-01T12:30:00Z",
      "duration_seconds": 1800,
      "event_count": 120,
      "file_count": 2
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

### Get Session History Details

```
GET /api/v2/history/{session_id}
```

Retrieve detailed information about a specific session history.

#### Path Parameters

- `session_id` (string, required): The ID of the session

#### Response

```json
{
  "id": "string",
  "start_time": "2023-01-01T12:00:00Z",
  "end_time": "2023-01-01T12:30:00Z",
  "duration_seconds": 1800,
  "event_count": 120,
  "file_count": 2,
  "files": ["events_1.jsonl", "events_2.jsonl"],
  "event_types": {
    "text_delta": 80,
    "tool_call": 10,
    "user_request": 5
  },
  "metadata": {
    "model": "gpt-4"
  },
  "user_id": "user123",
  "has_thinking": true,
  "tool_calls": ["tool1", "tool2"]
}
```

#### Error Responses

- `404 Not Found`: Session history not found

### Delete Session History

```
DELETE /api/v2/history/{session_id}
```

Delete a session history and all its files.

#### Path Parameters

- `session_id` (string, required): The ID of the session to delete

#### Response

```json
{
  "status": "success",
  "message": "Session history session1 deleted successfully"
}
```

#### Error Responses

- `404 Not Found`: Session history not found or could not be deleted

### Get Session Events

```
GET /api/v2/history/{session_id}/events
```

Get events for a specific session with filtering options.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Query Parameters

- `event_types` (array of strings, optional): Filter by event types (e.g., `user_request`, `text_delta`)
- `start_time` (datetime, optional): Filter events after this timestamp
- `end_time` (datetime, optional): Filter events before this timestamp
- `limit` (integer, default: 100): Maximum number of events to return (1-1000)

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
      "id": "session-id-1",
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "timestamp": "2023-01-01T12:00:00Z",
      "event_type": "user_request",
      "data": {
        "role": "user",
        "content": "Hello, agent",
        "format": "text"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_items": 1,
    "total_pages": 1
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

Stream events for a session, optionally in real-time. Returns a server-sent events (SSE) stream.

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Query Parameters

- `event_types` (array of strings, optional): Filter by event types
- `real_time` (boolean, default: false): Replay events with original timing
- `speed_factor` (float, default: 1.0): Speed multiplier for real-time replay (0.1-10.0)

#### Response

A text/event-stream response with JSON event data.

#### Error Responses

- `500 Internal Server Error`: Failed to stream events

### Get Replay Status

```
GET /api/v2/history/{session_id}/replay
```

Get the current status of a session replay.

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
    "current_position": "2023-01-01T12:00:10Z",
    "start_time": "2023-01-01T12:00:00Z",
    "end_time": "2023-01-01T12:30:00Z"
  }
}
```

#### Error Responses

- `404 Not Found`: No active replay for the session
- `500 Internal Server Error`: Failed to get replay status

### Control Replay

```
POST /api/v2/history/{session_id}/replay
```

Control a session replay (play, pause, seek).

#### Path Parameters

- `session_id` (UUID, required): The ID of the session

#### Request Body

```json
{
  "action": "play",  // "play", "pause", or "seek"
  "position": "2023-01-01T12:00:10Z",  // Required for "seek" action
  "speed": 1.5  // Optional playback speed multiplier
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

#### Error Responses

- `500 Internal Server Error`: Failed to control replay