# Agent C API v2 Documentation

## Overview

The Agent C API v2 provides a clean, RESTful interface for interacting with Agent C. It's organized around resource types with consistent HTTP methods and status codes. This documentation provides details on endpoint usage, request/response formats, authentication, and sample code.

### API Design Principles

1. **RESTful Resource Orientation** - Resources are identified by URLs and manipulated using standard HTTP methods
2. **Consistent Response Formats** - Standardized success and error responses
3. **Versioned Interface** - Clear API versioning with `/api/v{version}` prefix
4. **Comprehensive Documentation** - Complete OpenAPI/Swagger specifications
5. **Async/Streaming Support** - Real-time event delivery for chat interactions

## Base URL

All API URLs referenced in the documentation are relative to the base URL:  

```
https://your-agent-c-instance.com/api/v2/
```

## Authentication

The Agent C API uses JWT (JSON Web Tokens) for authentication. All endpoints except configuration resources require authentication.

### Authentication Flow

1. Obtain a JWT token by authenticating with your credentials
2. Include the JWT token in the `Authorization` header of subsequent requests:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Example Authentication Request

```python
import requests

auth_response = requests.post(
    "https://your-agent-c-instance.com/api/auth/login",
    json={"username": "your_username", "password": "your_password"}
)

token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Use headers in subsequent requests
response = requests.get(
    "https://your-agent-c-instance.com/api/v2/sessions",
    headers=headers
)
```

## Standard Response Format

Most endpoints return responses in a standardized format:  

```json
{
  "data": {}, // The response data (object or array)
  "meta": {   // Optional metadata about the response
    "pagination": {
      "total": 42,
      "page": 1,
      "size": 10
    }
  },
  "errors": [] // Present only if there are non-fatal errors
}
```

## Error Handling

The API uses HTTP status codes to indicate the success or failure of requests:

- `200 OK` - The request succeeded
- `201 Created` - A resource was successfully created
- `204 No Content` - The request succeeded with no response body
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `409 Conflict` - Request conflicts with current state
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

Error responses have a standardized format:  

```json
{
  "detail": {
    "error": "Brief error description",
    "error_code": "ERROR_CODE",
    "message": "Human-readable error message",
    "params": {} // Optional parameters related to the error
  }
}
```

## API Resources

### Configuration Resources

- `/config/models` - Available LLM models
- `/config/personas` - Available personas
- `/config/tools` - Available tools
- `/config/system` - Combined system configuration

### Session Resources

- `/sessions` - Chat session management
- `/sessions/{session_id}` - Individual session operations
- `/sessions/{session_id}/agent` - Agent configuration
- `/sessions/{session_id}/tools` - Session tools management
- `/sessions/{session_id}/chat` - Chat messaging
- `/sessions/{session_id}/files` - File management

### History Resources

- `/history` - Session history listing
- `/history/{session_id}` - Session history management
- `/history/{session_id}/events` - Event access
- `/history/{session_id}/stream` - Event streaming
- `/history/{session_id}/replay` - Replay controls

### Debug Resources

- `/debug/sessions/{session_id}` - Session debugging
- `/debug/agent/{session_id}` - Agent state debugging

## API Versioning

The Agent C API uses path-based versioning with the format `/api/v{version}/`. Currently supported versions:

- `/api/v1/` - Legacy API (deprecated)
- `/api/v2/` - Current API version
- `/api/latest/` - Always points to latest version

Example version-specific request:  

```http
GET https://your-agent-c-instance.com/api/v2/sessions
```

Example latest version request:  

```http
GET https://your-agent-c-instance.com/api/latest/sessions
```

## Pagination

List endpoints support pagination using the following query parameters:

- `page`: Page number (1-based indexing)
- `size`: Number of items per page

Paginated responses include metadata:  

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "total": 42,   // Total number of items
      "pages": 5,    // Total number of pages
      "page": 1,     // Current page
      "size": 10,    // Items per page
      "has_next": true,    // Whether there's a next page
      "has_previous": false  // Whether there's a previous page
    }
  }
}
```

## Sample Usage Patterns

### Creating a Session and Sending Messages

```python
import requests

# Create a new session
session_response = requests.post(
    "https://your-agent-c-instance.com/api/v2/sessions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "name": "My Test Session",
        "model": "gpt-4",
        "persona": "assistant"
    }
)

session_id = session_response.json()["data"]["id"]

# Send a message
message_response = requests.post(
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "message": "Hello, can you help me with some Python code?",
        "stream": True  # Enable streaming response
    }
)

# Process streaming response...
```

## Implementation Status

- [x] Configuration Resources
- [x] Session Management
  - [x] Session CRUD operations
  - [x] Agent configuration
  - [x] Chat messaging
  - [x] File management
- [x] History Resources
  - [x] History management
  - [x] Event access
  - [x] Replay control
- [x] Debug Resources

## Detailed Documentation

See the following resources for detailed information about specific API endpoints:

- [Configuration API](/docs/api_v2/config.md) - Models, personas, tools, and system settings
- [Sessions API](/docs/api_v2/agent.md) - Session management and agent configuration
- [Chat API](/docs/api_v2/chat.md) - Chat interactions and message handling
- [History API](/docs/api_v2/history.md) - Accessing and managing interaction history

## Migration from v1

See the [migration guide](/docs/api_migration.md) for details on transitioning from v1 to v2 API.