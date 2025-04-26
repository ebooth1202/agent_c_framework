# API Overview

## Introduction

The Agent C React UI communicates with a backend API to handle user authentication, chat functionality, tool integration, file management, and more. This document provides an overview of the API structure and major endpoints.

## API Configuration

API configuration is defined in `src/config/config.js`, which specifies:

- Base URL for API requests
- Endpoint paths for different features
- Authentication settings
- Timeout configurations

## Major API Endpoints

### Chat Endpoints

- `POST /chat/completions` - Send messages and receive AI responses
- `GET /chat/sessions` - Retrieve user chat sessions
- `GET /chat/session/{id}` - Get a specific chat session
- `DELETE /chat/session/{id}` - Delete a chat session

### Tool Endpoints

- `GET /tools` - Retrieve available tools
- `POST /tools/{tool_id}/execute` - Execute a specific tool

### File Endpoints

- `POST /files/upload` - Upload files for use in chat
- `GET /files` - List uploaded files
- `DELETE /files/{file_id}` - Delete a file

### RAG Endpoints

- `POST /rag/collections` - Create a document collection
- `GET /rag/collections` - List document collections
- `POST /rag/search` - Search across document collections

### User Endpoints

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /user/profile` - Get user profile information

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