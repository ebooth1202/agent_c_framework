# Chat API

## Overview

The Chat API enables real-time communication with AI agents within sessions. It provides endpoints for sending messages with multimodal content (text, images, files) and receiving streaming responses as the agent generates content, makes tool calls, and completes tasks.

This API supports Server-Sent Events (SSE) for streaming responses, allowing clients to display incremental updates as the agent thinks and responds to user messages. It also provides methods for managing interactions, such as cancellation.

## Key Features

- **Multimodal messaging**: Send text, images, and files in a single message
- **Real-time streaming**: Receive incremental responses as they're generated
- **Tool interaction visibility**: See when and how agents use tools
- **Thinking process transparency**: View the agent's reasoning process
- **Interaction management**: Cancel ongoing interactions if needed

## Send a Chat Message

```http
POST /api/v2/sessions/{session_id}/chat
```

Sends a message to the agent and receives a streaming response. This endpoint allows for interactive, real-time communication with an AI agent.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session to interact with |

### Request Body

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

### Request Parameters

| Name | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `message` | Object | Yes | The message to send to the agent |
| `message.role` | String | Yes | The role of the message sender (must be "user") |
| `message.content` | Array | Yes | Array of content blocks that make up the message |
| `message.content[].type` | String | Yes | Type of content: "text", "file", or "image" |
| `message.content[].text` | String | Yes* | Text content (*required when type is "text") |
| `message.content[].file_id` | String | Yes* | File ID (*required when type is "file" or "image") |
| `message.content[].mime_type` | String | No | MIME type of the file (optional, detected automatically if not provided) |
| `stream` | Boolean | No | Whether to stream the response (default: true) |

### Response Format

When `stream` is `true` (the default), the endpoint returns a Server-Sent Events (SSE) stream with `Content-Type: text/event-stream`. The stream consists of JSON-encoded events, each on a separate line, representing the agent's response as it's generated.

### Event Types

The streaming response includes various event types that represent different aspects of the agent's response:

| Event Type | Description | Example Fields |
| ---------- | ----------- | -------------- |
| `text_delta` | Incremental text content from the assistant | `{"type": "text_delta", "content": "Hello"}` |
| `tool_call` | Complete tool invocation by the assistant | `{"type": "tool_call", "name": "calculator", "arguments": {...}}` |
| `tool_call_delta` | Incremental updates to tool calls | `{"type": "tool_call_delta", "name": "calc"}` |
| `thought_delta` | Incremental thinking process updates | `{"type": "thought_delta", "content": "First, I need to..."}` |
| `completion` | Final completion status | `{"type": "completion", "id": "comp_123", "status": "complete"}` |

### Example Event Sequence

```
{"type":"text_delta","content":"Hello, I'm Agent C."}
{"type":"text_delta","content":" How can I help you with your Python question?"}
{"type":"thought_delta","content":"The user is asking about Python. I should be ready to provide code examples or explanations."}
{"type":"completion","id":"comp_abc123","status":"complete"}
```

### Multimodal Message Example

Example request with both text and an image:

```json
{
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "What's wrong with this Python code?"
      },
      {
        "type": "image",
        "file_id": "file_abc123"
      }
    ]
  },
  "stream": true
}
```

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 400 | BAD_REQUEST | Invalid message format, empty content, or other validation errors |
| 404 | NOT_FOUND | Specified session doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Server error processing the message |
| 501 | NOT_IMPLEMENTED | Non-streaming mode is requested but not yet supported |

### Client Integration Examples

#### JavaScript (Browser)

```javascript
// Using the Fetch API with a stream processor
async function sendChatMessage(sessionId, message) {
  try {
    const response = await fetch(`/api/v2/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        message: {
          role: 'user',
          content: [{ type: 'text', text: message }]
        },
        stream: true
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Unknown error');
    }
    
    // Process the streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    // Display area for the response
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // Add new chunks to the buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep the last (potentially incomplete) line
      
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const event = JSON.parse(line);
          
          switch (event.type) {
            case 'text_delta':
              // Append text to the response area
              responseDiv.innerHTML += event.content;
              break;
              
            case 'thought_delta':
              // Show thinking in a different style
              const thoughtDiv = document.createElement('div');
              thoughtDiv.className = 'thought';
              thoughtDiv.textContent = event.content;
              responseDiv.appendChild(thoughtDiv);
              break;
              
            case 'tool_call':
              // Display tool usage
              const toolDiv = document.createElement('div');
              toolDiv.className = 'tool-call';
              toolDiv.innerHTML = `<strong>Using tool:</strong> ${event.name}`;
              responseDiv.appendChild(toolDiv);
              break;
              
            case 'completion':
              // Mark the response as complete
              const completeDiv = document.createElement('div');
              completeDiv.className = 'completion-status';
              completeDiv.textContent = 'Response complete';
              responseDiv.appendChild(completeDiv);
              break;
              
            default:
              console.log('Other event:', event);
          }
        } catch (e) {
          console.error('Error parsing event:', line, e);
        }
      }
    }
  } catch (error) {
    console.error('Chat error:', error);
    alert(`Error: ${error.message}`);
  }
}
```

#### Python

```python
import json
import requests

class StreamProcessor:
    def __init__(self):
        self.buffer = ""
        self.complete = False
        
    def process_chunk(self, chunk):
        # Add chunk to buffer
        self.buffer += chunk.decode('utf-8')
        
        # Process complete lines
        lines = self.buffer.split('\n')
        self.buffer = lines.pop()  # Keep the last (potentially incomplete) line
        
        for line in lines:
            if not line.strip():
                continue
                
            try:
                event = json.loads(line)
                
                if event['type'] == 'text_delta':
                    print(event['content'], end='')
                elif event['type'] == 'thought_delta':
                    print(f"[Thinking: {event['content']}]", end='')
                elif event['type'] == 'tool_call':
                    print(f"\n[Using tool: {event['name']}]\n")
                elif event['type'] == 'completion':
                    self.complete = True
                    print("\n[Response complete]\n")
            except json.JSONDecodeError:
                print(f"Error parsing event: {line}\n")


def send_chat_message(session_id, message_text):
    # Prepare the request
    request_data = {
        "message": {
            "role": "user",
            "content": [{
                "type": "text",
                "text": message_text
            }]
        },
        "stream": True
    }
    
    # Send the request
    response = requests.post(
        f"https://api.example.com/api/v2/sessions/{session_id}/chat",
        json=request_data,
        stream=True,
        headers={"Accept": "text/event-stream"}
    )
    
    # Check for errors
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    # Process the streaming response
    processor = StreamProcessor()
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            processor.process_chunk(chunk)
            if processor.complete:
                break

# Example usage
send_chat_message("550e8400-e29b-41d4-a716-446655440000", "What's the capital of France?")
```

## Cancel Interaction

```http
DELETE /api/v2/sessions/{session_id}/chat
```

Cancels an ongoing interaction in the specified session. This is useful when you need to interrupt a long-running interaction, such as when the user wants to ask a different question or when the agent is stuck in a loop.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session containing the interaction to cancel |

### Request

No request body required.

### Response

```json
{
  "status": "success",
  "message": "Cancellation signal sent for session: 550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Failed to cancel the interaction |

### Example Usage

#### JavaScript

```javascript
async function cancelInteraction(sessionId) {
  try {
    const response = await fetch(`/api/v2/sessions/${sessionId}/chat`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    const result = await response.json();
    
    if (response.ok) {
      console.log(`Cancellation ${result.status}: ${result.message}`);
      return true;
    } else {
      console.error(`Error: ${result.detail || 'Unknown error'}`);
      return false;
    }
  } catch (error) {
    console.error('Cancellation error:', error);
    return false;
  }
}
```

#### Python

```python
import requests

def cancel_interaction(session_id):
    response = requests.delete(
        f"https://api.example.com/api/v2/sessions/{session_id}/chat"
    )
    
    result = response.json()
    
    if response.status_code == 200:
        print(f"Cancellation {result['status']}: {result['message']}")
        return True
    else:
        print(f"Error: {result.get('detail', 'Unknown error')}")
        return False
```

## Implementation Notes

### Multimodal Content Support

The chat API supports several content types in a single message:

- **Text**: Basic text content (required for user messages)
- **Images**: Images can be included using file IDs from previously uploaded files
- **Files**: Documents and other files can be attached using file IDs

### Streaming Response Format

- Each event in the stream is a JSON object on a separate line
- Each line ends with a newline character (`\n`)
- Clients should buffer incoming data and process complete JSON objects
- Partial JSON objects may be split across chunks, requiring buffering

### Message Requirements

- Only messages with the role "user" are currently accepted
- Messages must contain at least one text content block
- File references (images, documents) must have been previously uploaded

### Cancellation Behavior

- Cancellation is best-effort; there's no guarantee the agent will stop immediately
- The agent will attempt to halt processing as soon as possible
- Any partial response already sent will not be reversed