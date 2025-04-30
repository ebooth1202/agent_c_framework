# API Overview

## Introduction

The Agent C React UI communicates with a backend API to handle user authentication, chat functionality, tool integration, file management, and more. This document provides an overview of the API structure and major endpoints.

## API Configuration

API configuration is defined in `src/config/config.js`, which specifies:

- Base URL for API requests
- Endpoint paths for different features
- Authentication settings
- Timeout configurations

## API Service Layer

The Agent C React UI implements a dedicated API service layer to separate API calls from state management and UI components. This service layer is organized into specialized service modules:

```
src/services/
  ├── api.js           # Base API utilities and common functions
  ├── chat-api.js       # Chat and message related endpoints
  ├── index.js          # Re-exports for service modules
  ├── model-api.js      # Model configuration endpoints
  ├── persona-api.js    # Persona management endpoints
  ├── session-api.js    # Session management endpoints
  └── tools-api.js      # Tool management endpoints
```

See [Service Layer](./service-layer.md) for detailed implementation guidelines.

## Major API Endpoints

The Agent C API uses a mixture of REST-style and RPC-style endpoints. For complete details on all endpoints, see [API Endpoints Reference](./api-endpoints.md).

### Chat Endpoints

- `POST /chat` - Send messages and receive AI responses
- `GET /messages/{sessionId}` - Retrieve message history for a session

### Session Endpoints

- `POST /initialize` - Create a new chat session
- `GET /session/{sessionId}` - Get a specific chat session
- `POST /update_session` - Update session settings

### Tool Endpoints

- `GET /tools` - Retrieve available tools
- `GET /get_agent_tools/{sessionId}` - Get tools for a specific session
- `POST /update_tools` - Update enabled tools for a session

### Model Endpoints

- `GET /models` - Retrieve available models

### Persona Endpoints

- `GET /personas` - Retrieve available personas
- `POST /update_persona` - Update session persona

### File Endpoints

- `POST /upload_file` - Upload files for use in chat
- `GET /file/{fileId}` - Retrieve file information

## Request Format

Most API requests follow a standard JSON format:

```json
{
  "key": "value",
  // Additional request parameters
}
```

## Response Format

API responses typically follow this structure:

```json
{
  "data": {}, // Response data
  "error": null, // Error information if applicable
  "status": "success" // Status indicator
}
```

## Error Handling

When an error occurs, the API returns:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  },
  "status": "error"
}
```

## API Versioning

The current API version is specified in the request URL path (e.g., `/api/v1/endpoint`) or through headers.

## Rate Limiting

The API implements rate limiting to prevent abuse. Requests exceeding limits receive a 429 status code.

## See Also

- [Authentication](./authentication.md) - Details on authentication flow
- [Data Fetching](./data-fetching.md) - Best practices for API data fetching
- [Error Handling](./error-handling.md) - Detailed error handling strategies