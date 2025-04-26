# Authentication

## Overview

The Agent C React UI uses token-based authentication to secure API requests. This document explains the authentication flow, token management, and security best practices.

## Authentication Flow

1. **User Login**:
   - User provides credentials via the login form
   - Client sends credentials to the `/auth/login` endpoint
   - Server validates credentials and returns an access token and refresh token

2. **Token Storage**:
   - Access token is stored in memory (not in localStorage for security)
   - Refresh token may be stored in an HTTP-only cookie
   - Session information is managed through the SessionContext provider

3. **Authenticated Requests**:
   - Access token is included in the Authorization header of API requests
   - Format: `Authorization: Bearer {access_token}`

4. **Token Refresh**:
   - When the access token expires, the client uses the refresh token to obtain a new access token
   - Refresh is handled automatically by the authentication interceptor

5. **Logout**:
   - Client calls the `/auth/logout` endpoint
   - Tokens are invalidated on the server
   - Client clears local token storage and context state

## Implementation in SessionContext

The `SessionContext` in `src/contexts/SessionContext.jsx` manages authentication state:

```jsx
// Key authentication-related state
const [isAuthenticated, setIsAuthenticated] = useState(false);
const [user, setUser] = useState(null);
const [accessToken, setAccessToken] = useState(null);

// Authentication methods
const login = async (credentials) => { /* implementation */ };
const logout = async () => { /* implementation */ };
const refreshToken = async () => { /* implementation */ };
```

## Secure API Request Pattern

Requests to authenticated endpoints follow this pattern:

```jsx
const makeAuthenticatedRequest = async (endpoint, options = {}) => {
  if (!accessToken) {
    throw new Error('No access token available');
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  };
  
  try {
    const response = await fetch(`${config.apiBaseUrl}${endpoint}`, {
      ...options,
      headers
    });
    
    // Handle 401 Unauthorized (expired token)
    if (response.status === 401) {
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry the original request with new token
        return makeAuthenticatedRequest(endpoint, options);
      } else {
        // Refresh failed, redirect to login
        setIsAuthenticated(false);
        return null;
      }
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};
```

## Security Best Practices

1. **Token Storage**:
   - Never store access tokens in localStorage or sessionStorage
   - Use in-memory storage or HTTP-only cookies for refresh tokens

2. **Token Expiration**:
   - Use short-lived access tokens (15-60 minutes)
   - Implement proper token refresh mechanism

3. **HTTPS**:
   - Always use HTTPS for all API communication

4. **CSRF Protection**:
   - Include CSRF tokens in requests when using cookie-based authentication

5. **Error Handling**:
   - Don't expose detailed authentication errors to users
   - Log authentication failures on the server

## Handling Authentication Errors

Common authentication errors include:

- **401 Unauthorized**: Token is invalid or expired
- **403 Forbidden**: User doesn't have permission for the requested resource
- **500 Internal Server Error**: Server-side authentication error

These should be handled gracefully in the UI:

```jsx
switch (error.status) {
  case 401:
    // Redirect to login page
    navigate('/login', { state: { from: location } });
    break;
  case 403:
    // Show permission denied message
    setErrorMessage('You don't have permission to access this resource');
    break;
  default:
    // Show generic error message
    setErrorMessage('An error occurred. Please try again later.');
}
```

## See Also

- [API Overview](./api-overview.md) - General API information
- [Data Fetching](./data-fetching.md) - Best practices for API data fetching
- [Error Handling](./error-handling.md) - Detailed error handling strategies