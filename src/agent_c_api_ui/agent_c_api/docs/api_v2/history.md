# History API

The History API provides access to session histories and their events. This allows you to list available session histories, retrieve details about specific sessions, and manage history data.

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