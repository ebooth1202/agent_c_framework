# Phase 2 Assessment: Creating Core SessionContext

## Current State

The API Service Layer (Phase 1) has been successfully completed:
- We have a comprehensive set of API services organized by domain
- The services follow consistent patterns with proper error handling
- The current SessionContext is already using these services
- We have detailed API documentation to guide our work

## Plan for Phase 2

Phase 2 requires extracting core session management into a dedicated context. Based on our API services and the current SessionContext implementation, here's my recommendation for proceeding:

### 1. Create a New Core SessionContext

The new SessionContext should be focused exclusively on core session management:

```jsx
// src/contexts/SessionContext.jsx (new version)
import React, { createContext, useState, useEffect } from 'react';
import { session as sessionService } from '../services';

export const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  // Core session state only
  const [sessionId, setSessionId] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState(null);

  // Core session functions
  const initializeSession = async (config) => {
    setIsReady(false);
    try {
      const data = await sessionService.initialize(config);
      if (data.ui_session_id) {
        localStorage.setItem("ui_session_id", data.ui_session_id);
        setSessionId(data.ui_session_id);
        setIsReady(true);
        setError(null);
        return data.ui_session_id;
      } else {
        throw new Error("No ui_session_id in response");
      }
    } catch (err) {
      setIsReady(false);
      setError(`Session initialization failed: ${err.message}`);
      throw err;
    }
  };

  const handleSessionsDeleted = () => {
    localStorage.removeItem("ui_session_id");
    setSessionId(null);
    setIsReady(false);
    setError(null);
  };

  // Check for existing session on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem("ui_session_id");
    if (savedSessionId) {
      setSessionId(savedSessionId);
      setIsReady(true);
    }
  }, []);

  return (
    <SessionContext.Provider
      value={{
        sessionId,
        isReady,
        isInitialized,
        setIsInitialized,
        error,
        setError,
        initializeSession,
        handleSessionsDeleted
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};
```

### 2. Create a Transitional Context (LegacySessionContext)

To maintain backward compatibility, we should:

1. Rename the current SessionContext to LegacySessionContext
2. Make LegacySessionContext use the new SessionContext internally
3. Gradually migrate components from LegacySessionContext to the new contexts

### 3. Implementation Steps for Phase 2

1. Create the new SessionContext with focused state and functionality
2. Rename the existing SessionContext to LegacySessionContext
3. Update LegacySessionContext to use the new SessionContext
4. Create a custom hook for accessing SessionContext
5. Update global context providers in App.jsx
6. Test the application to ensure all functionality works

### 4. Adjustments Needed Based on API Services

Now that we have clear API services, we can make some optimizations to our plan:

1. **Simplified initialization**: The session-api service provides clear methods for session creation and management, so we can simplify our initialization logic
2. **Better error handling**: We can leverage the consistent error handling in our API services
3. **Cleaner interfaces**: We can provide cleaner interfaces through our context by wrapping service methods

## Remaining Concerns

1. **Initialization Order**: We need to carefully manage the initialization order between contexts
2. **Session Validation**: We should consider adding session validation when using a saved sessionId
3. **Error Recovery**: We should implement better error recovery strategies

## Recommendation

We can proceed with Phase 2 as outlined above, with particular attention to:

1. Making the new SessionContext as focused as possible on session management only
2. Providing a clean migration path for components via the transitional LegacySessionContext
3. Taking advantage of our new API services for cleaner implementations
4. Adding proper error boundaries and recovery mechanisms
