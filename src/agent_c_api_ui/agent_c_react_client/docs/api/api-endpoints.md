# API Endpoints Reference

## Introduction

This document provides a definitive reference for all API endpoints used by the Agent C React UI. It includes detailed information about each endpoint's URL, HTTP method, request parameters, and response format.

## API Base URL

The base URL for all API endpoints is configured in `src/config/config.js` as `API_CONFIG.baseUrl` which typically resolves to:

```
http://localhost:8000/api/v1
```

## Authentication Endpoints

### Login
- **Endpoint**: `/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns a session token
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "token": "string",
    "user": {
      "id": "string",
      "name": "string",
      "email": "string"
    }
  }
  ```

### Logout
- **Endpoint**: `/logout`
- **Method**: `POST`
- **Description**: Invalidates the user's session token
- **Authentication**: Required
- **Response**: Status 200 OK

## Session Endpoints

### Initialize Session
- **Endpoint**: `/initialize`
- **Method**: `POST`
- **Description**: Creates a new chat session with specified parameters
- **Request Body**:
  ```json
  {
    "model_name": "string",
    "backend": "string",
    "persona_name": "string",
    "temperature": number
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "string",
    "model": {
      "id": "string",
      "name": "string"
    }
  }
  ```

### Get Session
- **Endpoint**: `/session/{sessionId}`
- **Method**: `GET`
- **Description**: Retrieves details of a specific session
- **Response**:
  ```json
  {
    "session_id": "string",
    "created_at": "datetime",
    "model": {
      "id": "string",
      "name": "string"
    },
    "messages": [
      /* message objects */
    ]
  }
  ```

### Update Session Settings
- **Endpoint**: `/update_session`
- **Method**: `POST`
- **Description**: Updates the settings for an existing session
- **Request Body**:
  ```json
  {
    "ui_session_id": "string",
    "model_name": "string",
    "temperature": number
  }
  ```
- **Response**: Status 200 OK

## Chat Message Endpoints

### Send Message
- **Endpoint**: `/chat`
- **Method**: `POST`
- **Description**: Sends a user message and receives an AI response
- **Request Body**:
  ```json
  {
    "ui_session_id": "string",
    "message": "string",
    "files": [{ "file_id": "string" }],
    "stream": boolean
  }
  ```
- **Response** (non-streaming):
  ```json
  {
    "response": "string",
    "message_id": "string"
  }
  ```
- **Response** (streaming): Server-sent events with JSON chunks

### Get Messages History
- **Endpoint**: `/messages/{sessionId}`
- **Method**: `GET`
- **Description**: Retrieves message history for a specific session
- **Response**:
  ```json
  [
    {
      "id": "string",
      "role": "user|assistant|system",
      "content": "string",
      "timestamp": "datetime"
    }
  ]
  ```

## Model Endpoints

### Get Available Models
- **Endpoint**: `/models`
- **Method**: `GET`
- **Description**: Retrieves the list of available models
- **Response**:
  ```json
  [
    {
      "id": "string",
      "label": "string",
      "description": "string",
      "model_type": "string",
      "backend": "string",
      "supports_tools": boolean,
      "tool_choice": "string",
      "default_params": {
        "temperature": number,
        "max_tokens": number
      }
    }
  ]
  ```

## Tools Endpoints

### Get Available Tools
- **Endpoint**: `/tools`
- **Method**: `GET`
- **Description**: Retrieves all available tools
- **Response**:
  ```json
  {
    "essential_tools": [
      {
        "name": "string",
        "description": "string",
        "category": "string"
      }
    ],
    "groups": {
      "group_name": [
        {
          "name": "string",
          "description": "string",
          "category": "string"
        }
      ]
    },
    "categories": ["string"]
  }
  ```

### Get Session Tools
- **Endpoint**: `/get_agent_tools/{sessionId}`
- **Method**: `GET`
- **Description**: Retrieves tools enabled for a specific session
- **Response**:
  ```json
  [
    "tool_name1",
    "tool_name2"
  ]
  ```

### Update Session Tools
- **Endpoint**: `/update_tools`
- **Method**: `POST`
- **Description**: Updates the enabled tools for a session
- **Request Body**:
  ```json
  {
    "ui_session_id": "string",
    "tools": ["string"]
  }
  ```
- **Response**: Status 200 OK

## Persona Endpoints

### Get Available Personas
- **Endpoint**: `/personas`
- **Method**: `GET`
- **Description**: Retrieves all available agent personas
- **Response**:
  ```json
  [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "icon": "string"
    }
  ]
  ```

### Update Session Persona
- **Endpoint**: `/update_persona`
- **Method**: `POST`
- **Description**: Updates the persona for a session
- **Request Body**:
  ```json
  {
    "ui_session_id": "string", 
    "persona_id": "string"
  }
  ```
- **Response**: Status 200 OK

## File Endpoints

### Upload File
- **Endpoint**: `/upload_file`
- **Method**: `POST`
- **Description**: Uploads a file for use in chat
- **Request Body**: Form data with `file` field
- **Response**:
  ```json
  {
    "file_id": "string",
    "filename": "string",
    "size": number,
    "mime_type": "string"
  }
  ```

### Get File
- **Endpoint**: `/file/{fileId}`
- **Method**: `GET`
- **Description**: Retrieves file information
- **Response**: File content with appropriate Content-Type header

## Important Implementation Notes

### Endpoint Style Inconsistency

The Agent C API uses a mixture of REST-style and RPC-style endpoints:

- REST endpoints use resource names and HTTP methods (e.g., `GET /models`)
- RPC endpoints use verb-based naming (e.g., `POST /update_tools`)

When implementing API services, pay careful attention to:

1. The exact endpoint URL format
2. The correct HTTP method (GET, POST, etc.)
3. The expected parameter format (URL params vs. JSON body)

### Query Parameter vs. Request Body

Some endpoints may accept parameters in different formats:

- As URL query parameters: `/endpoint?param1=value1&param2=value2`
- As JSON in the request body: `{ "param1": "value1", "param2": "value2" }`

Consult the backend implementation if documentation is unclear.

### Response Format Variations

API responses may use different formats:

1. Direct data objects: `{ "key": "value" }`
2. Wrapped responses: `{ "data": {...}, "status": "success" }`
3. Array responses: `[item1, item2, ...]`

Service methods should handle these variations consistently.

## Error Handling

Most API endpoints will return error responses in this format:

```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

Common HTTP status codes:

- `400` - Bad Request (client error, invalid parameters)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server-side issue)

## See Also

- [API Overview](./api-overview.md) - General API information
- [Service Layer](./service-layer.md) - API service layer implementation
- [Authentication](./authentication.md) - Authentication flow details