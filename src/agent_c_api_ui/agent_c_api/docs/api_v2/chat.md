# Chat API

The chat API enables sending messages to agents and managing interactions within sessions.

## Send a Chat Message

```http
POST /api/v2/sessions/{session_id}/chat
```

Sends a message to the agent and receives a streaming response.

### Request

```json
{
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Hello, can you help me with a Python question?"
      }
    ]
  },
  "stream": true
}
```

### Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `message` | Object | The message to send to the agent |
| `message.role` | String | The role of the message sender (must be "user") |
| `message.content` | Array | Array of content blocks |
| `message.content[].type` | String | Type of content: "text", "file", or "image" |
| `message.content[].text` | String | Text content (required when type is "text") |
| `message.content[].file_id` | String | File ID (required when type is "file" or "image") |
| `message.content[].mime_type` | String | MIME type of the file (optional) |
| `stream` | Boolean | Whether to stream the response (default: true) |

### Response

When `stream` is `true`, the endpoint returns a stream of response chunks in plain text format.

### Error Codes

| Status Code | Description |
| ----------- | ----------- |
| 404 | Session not found |
| 400 | Invalid message format or empty content |
| 500 | Error processing the message |
| 501 | Non-streaming mode not supported |

### Example

```javascript
// JavaScript example using fetch
const response = await fetch('/api/v2/sessions/my-session-id/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: {
      role: 'user',
      content: [{ type: 'text', text: 'What is the capital of France?' }]
    },
    stream: true
  })
});

// Handle streaming response
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(new TextDecoder().decode(value));
}
```

## Cancel Interaction

```http
DELETE /api/v2/sessions/{session_id}/chat
```

Cancels an ongoing interaction in the specified session.

### Request

No request body required.

### Response

```json
{
  "status": "success",
  "message": "Cancellation signal sent for session: my-session-id"
}
```

### Error Codes

| Status Code | Description |
| ----------- | ----------- |
| 404 | Session not found |
| 500 | Failed to cancel interaction |

### Example

```javascript
// JavaScript example using fetch
const response = await fetch('/api/v2/sessions/my-session-id/chat', {
  method: 'DELETE'
});

const result = await response.json();
console.log(result.status); // "success" or "error"
```

## Notes

- The chat API supports text content and file attachments.
- Streaming responses use plain text format with each chunk ending in a newline.
- Only messages with the role "user" are accepted.
- Messages must contain at least one text content block.