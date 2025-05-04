# Interactions API

> **Documentation generated**: May 1, 2025

Endpoints for managing and accessing recorded agent interaction sessions.

## List Interaction Sessions

```
GET /api/v1/interactions
```

Lists all available interaction sessions with pagination and sorting.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | number | No | Maximum number of sessions to return (default: 50) |
| `offset` | number | No | Number of sessions to skip (default: 0) |
| `sort_by` | string | No | Field to sort by (default: "timestamp") |
| `sort_order` | string | No | Sort order, "asc" or "desc" (default: "desc") |

### Response

| Field | Type | Description |
|-------|------|-------------|
| (array) | array | List of session summary objects |
| [].id | string | Session ID |
| [].start_time | string | ISO 8601 timestamp of session start time |
| [].end_time | string | ISO 8601 timestamp of session end time (if completed) |
| [].duration_seconds | number | Session duration in seconds |
| [].event_count | number | Number of events in the session |
| [].file_count | number | Number of files in the session |

#### Response Example

```json
[
  {
    "id": "ses_1234567890abcdef",
    "start_time": "2025-04-30T08:40:00.000Z",
    "end_time": "2025-04-30T08:45:00.000Z",
    "duration_seconds": 300,
    "event_count": 156,
    "file_count": 3
  },
  {
    "id": "ses_0987654321fedcba",
    "start_time": "2025-04-30T09:00:00.000Z",
    "end_time": "2025-04-30T09:12:00.000Z",
    "duration_seconds": 720,
    "event_count": 214,
    "file_count": 5
  }
]
```

## Get Interaction Details

```
GET /api/v1/interactions/{session_id}
```

Gets detailed information about a specific interaction session.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Session ID |
| `start_time` | string | ISO 8601 timestamp of session start time |
| `end_time` | string | ISO 8601 timestamp of session end time (if completed) |
| `duration_seconds` | number | Session duration in seconds |
| `event_count` | number | Number of events in the session |
| `file_count` | number | Number of files in the session |
| `files` | array | List of JSONL filenames in the session |
| `event_types` | object | Count of each event type |
| `event_types.{type_name}` | number | Count of events of a specific type |
| `metadata` | object | Additional metadata if available |
| `metadata.model` | string | Model used in the session |
| `metadata.backend` | string | Backend used in the session |
| `user_id` | string | User ID if available |
| `has_thinking` | boolean | Whether the session has thinking events |
| `tool_calls` | array | List of tools used in the session |

#### Response Example

```json
{
  "id": "ses_1234567890abcdef",
  "start_time": "2025-04-30T08:40:00.000Z",
  "end_time": "2025-04-30T08:45:00.000Z",
  "duration_seconds": 300,
  "event_count": 156,
  "file_count": 3,
  "files": ["file1.jsonl", "file2.jsonl", "file3.jsonl"],
  "event_types": {
    "user_request": 5,
    "completion": 5,
    "tool_call": 8,
    "thought_delta": 35
  },
  "metadata": {
    "model": "gpt-4o",
    "backend": "openai"
  },
  "user_id": "user_12345",
  "has_thinking": true,
  "tool_calls": ["WorkspaceTools.read", "WorkspaceTools.write", "ThinkTools.think"]
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |

## Get Session Files

```
GET /api/v1/interactions/{session_id}/files
```

Gets a list of all JSONL files associated with a specific session.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Response

An array of filenames (strings) in the session directory.

#### Response Example

```json
["file1.jsonl", "file2.jsonl", "file3.jsonl"]
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - No files found for session |

## Delete Session

```
DELETE /api/v1/interactions/{session_id}
```

Deletes a session directory and all its files.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | The session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `message` | string | Description of the result |

#### Response Example

```json
{
  "status": "success",
  "message": "Session ses_1234567890abcdef deleted successfully"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found or could not be deleted |