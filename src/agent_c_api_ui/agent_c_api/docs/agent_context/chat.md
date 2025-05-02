# Chat API

> **Documentation generated**: May 1, 2025

Endpoints for interacting with agents through chat.

## Chat with Agent

```
POST /api/v1/chat
```

Sends a message to the agent and receives a streaming response.

### Form Data Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |
| `message` | string | Yes | The message to send to the agent |
| `file_ids` | string (JSON array) | No | JSON string array of file IDs to include with the message |

#### Request Example

```
POST /api/v1/chat
Content-Type: multipart/form-data

ui_session_id=ses_1234567890abcdef&message=Hello, can you help me with a coding question?&file_ids=["file_123", "file_456"]
```

### Response

A streaming response containing the agent's reply. The response is streamed as plain text chunks.

**Content-Type**: `text/plain`

**Transfer-Encoding**: `chunked`

#### Response Example

```
Hello! I'd be happy to help with your coding question. What specific issue are you having trouble with?
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid file_ids format |
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error processing the request |

## Cancel Chat Interaction

```
POST /api/v1/cancel
```

Cancels an ongoing chat interaction.

### Form Data Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID of the interaction to cancel |

#### Request Example

```
POST /api/v1/cancel
Content-Type: multipart/form-data

ui_session_id=ses_1234567890abcdef
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `message` | string | Description of the result |

#### Response Example

```json
{
  "status": "success",
  "message": "Cancellation signal sent for session: ses_1234567890abcdef"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Failed to cancel interaction |