# API Error Handling

## Introduction

This document outlines best practices for handling API errors in the Agent C React UI. Proper error handling improves user experience by providing clear feedback and enables developers to debug issues effectively.

## Error Response Format

The Agent C API typically returns error responses in this format:

```json
{
  "error": {
    "message": "Human-readable error description",
    "code": "ERROR_CODE"
  }
}
```

Or sometimes with this alternate format:

```json
{
  "data": null,
  "error": {
    "message": "Human-readable error description",
    "code": "ERROR_CODE"
  },
  "status": "error"
}
```

## Common HTTP Error Codes

- `400 Bad Request` - Invalid parameters or malformed request
- `401 Unauthorized` - Authentication required or invalid credentials
- `403 Forbidden` - Insufficient permissions for the requested operation
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Request conflicts with current state
- `422 Unprocessable Entity` - Request validation failure
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Service temporarily unavailable

## Error Handling in the Service Layer

All API service modules should implement consistent error handling:

```javascript
// src/services/api.js
export const apiRequest = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}${endpoint}`, options);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      // Construct a standardized error object
      const error = {
        status: response.status,
        statusText: response.statusText,
        message: errorData.error?.message || 'An unknown error occurred',
        code: errorData.error?.code || 'UNKNOWN_ERROR',
        data: errorData
      };
      
      // Log the error for debugging
      console.error(`API Error (${endpoint}):`, error);
      
      throw error;
    }
    
    // Process successful response
    return response.json();
  } catch (error) {
    // Handle network errors or JSON parsing errors
    if (!error.status) {
      console.error(`Network Error (${endpoint}):`, error);
      throw {
        status: 0,
        statusText: 'Network Error',
        message: 'Unable to connect to the server',
        code: 'NETWORK_ERROR',
        originalError: error
      };
    }
    
    throw error;
  }
};
```

## Component-Level Error Handling

### Using try-catch with Async/Await

```jsx
const handleSubmit = async (formData) => {
  setLoading(true);
  setError(null);
  
  try {
    const result = await submitForm(formData);
    setSuccess(true);
  } catch (error) {
    // Handle specific error types
    if (error.status === 401) {
      setError('Your session has expired. Please log in again.');
      // Redirect to login
    } else if (error.status === 400) {
      setError(error.message || 'Invalid form data. Please check your inputs.');
    } else {
      setError('An unexpected error occurred. Please try again later.');
    }
    
    // Log for debugging
    console.error('Form submission error:', error);
  } finally {
    setLoading(false);
  }
};
```

### Using Error Boundaries for React Components

```jsx
// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Component error:', error, errorInfo);
    // Optionally send to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## Centralized Error State Management

For consistent error handling across the application, consider implementing a central error context:

```jsx
// src/contexts/ErrorContext.jsx
import React, { createContext, useContext, useState } from 'react';

const ErrorContext = createContext(null);

export const ErrorProvider = ({ children }) => {
  const [errors, setErrors] = useState([]);

  const addError = (error) => {
    const id = Date.now();
    setErrors(prev => [...prev, { id, ...error }]);
    
    // Auto-dismiss non-critical errors after 5 seconds
    if (!error.critical) {
      setTimeout(() => {
        dismissError(id);
      }, 5000);
    }
  };

  const dismissError = (id) => {
    setErrors(prev => prev.filter(error => error.id !== id));
  };

  const clearAllErrors = () => {
    setErrors([]);
  };

  return (
    <ErrorContext.Provider value={{ errors, addError, dismissError, clearAllErrors }}>
      {children}
    </ErrorContext.Provider>
  );
};

export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};
```

## User-Friendly Error Messages

Translate technical error codes into user-friendly messages:

```javascript
const getUserFriendlyMessage = (error) => {
  // Handle common error codes
  switch (error.code) {
    case 'INVALID_CREDENTIALS':
      return 'The username or password you entered is incorrect.';
    case 'SESSION_EXPIRED':
      return 'Your session has expired. Please log in again.';
    case 'RATE_LIMIT_EXCEEDED':
      return 'You've reached the request limit. Please try again later.';
    case 'NETWORK_ERROR':
      return 'Unable to connect to the server. Please check your internet connection.';
    default:
      // For unknown errors, provide a generic message
      return 'An unexpected error occurred. Please try again later.';
  }
};
```

## Error Monitoring and Reporting

Consider implementing a system to collect and report errors to a monitoring service:

```javascript
const reportError = (error, context = {}) => {
  // Add additional context
  const errorWithContext = {
    ...error,
    url: window.location.href,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    ...context
  };
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error report:', errorWithContext);
  }
  
  // Send to error reporting service in production
  // errorReportingService.captureError(errorWithContext);
};
```

## Best Practices

1. **Be Specific**: Provide specific error messages that help users understand what went wrong.

2. **Suggest Solutions**: When possible, suggest how to fix the problem (e.g., "Try a different username" or "Check your internet connection").

3. **Graceful Degradation**: Design components to work in a degraded state when non-critical features fail.

4. **Avoid Technical Details**: Hide technical error details from users unless they are developers.

5. **Logging**: Log detailed error information for debugging without exposing it to users.

6. **Recovery Options**: Provide clear recovery paths like retry buttons or alternative actions.

7. **Consistent UI**: Use consistent error message styling and positioning throughout the app.

## Common Error Scenarios

### Authentication Errors

- Handle expired tokens by automatically refreshing or redirecting to login
- Provide clear feedback for invalid credentials
- Detect and handle account lockouts

### Network Errors

- Implement retry mechanisms with exponential backoff
- Cache critical data for offline access
- Display offline indicators

### Form Validation Errors

- Display field-specific error messages next to the relevant inputs
- Aggregate and display API validation errors from the server
- Support both client-side and server-side validation

### Resource Not Found

- Provide helpful navigation options when resources don't exist
- Check for common causes (typos in IDs, deleted resources)

## See Also

- [API Overview](./api-overview.md) - General API information
- [Service Layer](./service-layer.md) - API service layer implementation
- [API Endpoints Reference](./api-endpoints.md) - Comprehensive endpoint documentation