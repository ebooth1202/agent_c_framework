# API Service Layer

## Introduction

The Agent C React UI implements a dedicated API service layer to separate API calls from state management and UI components. This approach provides several benefits:

- **Separation of concerns**: API logic is isolated from UI components
- **Consistent error handling**: Centralized error handling for all API requests
- **Testability**: Services can be easily mocked for testing
- **Reusability**: API methods can be reused across multiple components
- **Maintainability**: Easier to update API endpoints or request formats in one place

## Service Layer Architecture

The service layer is organized into specialized service modules:

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

## Base API Service

The `api.js` module provides base functionality for all service modules, including:

- API configuration
- Request interceptors
- Response handling
- Error processing
- Authentication header management

### Example Implementation

```javascript
// src/services/api.js
import { API_CONFIG } from '../config/config';

// Create base API request with proper headers and error handling
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.baseUrl}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      // Handle error responses
      const errorData = await response.json().catch(() => ({}));
      throw {
        status: response.status,
        statusText: response.statusText,
        data: errorData,
      };
    }
    
    // For successful responses, handle both JSON and non-JSON responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    // Log and rethrow error for handling in service or component
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
};

// Authenticated API request with token
export const authenticatedRequest = async (endpoint, options = {}, token) => {
  if (!token) {
    throw new Error('Authentication token required for this request');
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };
  
  return apiRequest(endpoint, { ...options, headers });
};
```

## Specialized Service Modules

Each specialized service module follows the same pattern:

1. Import base API utilities
2. Define endpoint-specific functions 
3. Export service methods

### Example: Tools API Service

```javascript
// src/services/tools-api.js
import { apiRequest } from './api';

// Get all available tools
export const getTools = async () => {
  return apiRequest('/tools');
};

// Get tools for a specific session
export const getSessionTools = async (sessionId) => {
  return apiRequest(`/get_agent_tools/${sessionId}`);
};

// Update tools for a session
export const updateSessionTools = async (ui_session_id, toolsList) => {
  return apiRequest('/update_tools', {
    method: 'POST',
    body: JSON.stringify({
      ui_session_id,
      tools: toolsList
    })
  });
};
```

## Important API Implementation Details

### Mixed API Styles

The Agent C API uses a combination of REST-style and RPC-style endpoints:

- **REST-style examples**: `/tools`, `/models`, `/sessions`
- **RPC-style examples**: `/get_agent_tools/${sessionId}`, `/update_tools`

It's important to verify the exact endpoint URL, HTTP method, and parameter format for each API call by checking the backend implementation.

### Response Formats

API responses may have inconsistent formats depending on the endpoint:

1. Direct data objects: `{ property1: value1, property2: value2 }`
2. Wrapped responses: `{ data: { ... }, status: "success" }`
3. Array responses: `[item1, item2, ...]`

Service methods should normalize these different formats as needed.

## Using the Service Layer in Components

Components should import and use service methods rather than making fetch calls directly:

```jsx
import { useEffect, useState } from 'react';
import { getTools, getSessionTools } from '../services/tools-api';

function ToolSelector({ sessionId }) {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTools = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Use the service method
        const toolsData = await getSessionTools(sessionId);
        setTools(toolsData);
      } catch (err) {
        setError('Failed to load tools');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadTools();
  }, [sessionId]);

  // Component rendering
}
```

## Best Practices

1. **Consistent Error Handling**: All service methods should use the same error handling pattern.

2. **Typing with JSDoc or TypeScript**: Document expected parameters and return types.

3. **Parameter Validation**: Validate required parameters before making requests.

4. **Response Normalization**: Handle and normalize different response formats.

5. **Logging**: Include appropriate logging for debugging and monitoring.

6. **Mocking for Tests**: Design services to be easily mockable for component testing.

7. **Documentation**: Keep API endpoint documentation up-to-date to match actual implementation.

## API Reference Documentation

To avoid mismatches between the service layer implementation and the actual API, maintain an up-to-date API reference document listing:

- Endpoint URLs
- HTTP methods
- Required parameters
- Response formats
- Error codes and messages
- Authentication requirements

This documentation should be verified against the actual backend implementation.

## See Also

- [API Overview](./api-overview.md) - General API information
- [Authentication](./authentication.md) - Authentication flow details
- [Error Handling](./error-handling.md) - Detailed error handling strategies