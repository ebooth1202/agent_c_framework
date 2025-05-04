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

When `stream` is `true`, the endpoint returns a Server-Sent Events (SSE) stream of JSON-encoded events. Each event has a type and associated data.

Common event types include:

- `text_delta`: Text content updates from the assistant
- `tool_call`: Tool invocation events
- `tool_call_delta`: Incremental updates to tool calls
- `thought_delta`: Thinking process updates (when available)
- `completion`: Completion status information

Example event:

```json
{
  "type": "text_delta",
  "content": "Hello, I'm Agent C. How can I help you today?"
}
```

### Error Codes

| Status Code | Description |
| ----------- | ----------- |
| 404 | Session not found |
| 400 | Invalid message format or empty content |
| 500 | Error processing the message |
| 501 | Non-streaming mode not supported |

### Example

```javascript
// JavaScript example using fetch and EventSource for SSE
// Method 1: Using the Fetch API for manual event processing
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
let buffer = ''; // Buffer for incomplete JSON objects

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  // Convert the chunk to text and add to buffer
  buffer += new TextDecoder().decode(value);
  
  // Process complete JSON objects in the buffer
  const lines = buffer.split('\n');
  buffer = lines.pop(); // Keep the last incomplete line in the buffer
  
  for (const line of lines) {
    if (line.trim() === '') continue;
    try {
      const event = JSON.parse(line);
      // Handle different event types
      switch(event.type) {
        case 'text_delta':
          console.log('Assistant: ' + event.content);
          break;
        case 'tool_call':
          console.log('Tool call: ' + event.name);
          break;
        default:
          console.log('Event:', event);
      }
    } catch (e) {
      console.error('Invalid JSON:', line);
    }
  }
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