# Detailed Plan for Phase 1: API Service Layer Implementation

After reviewing the current code, documentation, and refactoring goals, I've developed a detailed plan for implementing the API Service Layer as part of Phase 1 of the SessionContext refactoring.

## Phase 1 Overview

**Goal**: Separate API calls from state management to create a clean service layer that will provide the foundation for further context splitting.

**Benefits**:
- Improved separation of concerns
- Consistent error handling
- Easier testing through mocking
- Better organization of API-related code
- Cleaner SessionContext with less responsibility

## Implementation Plan

### Step 1: Create Base API Service Structure

Create a new `/src/services` directory with the following files:

1. **`api.js` - Core API Service**
   - Implement a fetch wrapper with consistent error handling
   - Handle API URL configuration
   - Provide common request/response processing
   - Implement request timeout and retry logic

2. **`session-api.js` - Session Service**
   - Initialize and verify sessions
   - Update session settings
   - Debug session state

3. **`model-api.js` - Model Service**
   - Fetch available models
   - Handle model configuration

4. **`tools-api.js` - Tool Service**
   - Fetch available tools
   - Get active tools for a session
   - Update tool selection

5. **`persona-api.js` - Persona Service**
   - Fetch available personas

6. **`index.js` - Service Entry Point**
   - Export all services for easy importing

### Step 2: Implement Core API Service

In `api.js`, implement the core functionality:

```javascript
// api.js
import { API_URL } from '@/config/config';

class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const DEFAULT_TIMEOUT = 30000; // 30 seconds

async function handleResponse(response, endpoint) {
  const contentType = response.headers.get("content-type");
  
  if (!response.ok) {
    let errorText;
    try {
      errorText = await response.text();
    } catch (e) {
      errorText = 'Could not read error response';
    }
    throw new ApiError(
      `${endpoint} failed: ${response.status} - ${errorText}`,
      response.status,
      errorText
    );
  }

  if (!contentType?.includes('application/json')) {
    throw new ApiError(
      `${endpoint} returned non-JSON content-type: ${contentType}`,
      response.status
    );
  }

  try {
    const text = await response.text();
    return JSON.parse(text);
  } catch (e) {
    throw new ApiError(
      `Invalid JSON from ${endpoint}: ${e.message}`,
      response.status
    );
  }
}

async function fetchWithTimeout(url, options, timeout = DEFAULT_TIMEOUT) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new ApiError(`Request timeout after ${timeout}ms`, 408);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function apiGet(endpoint, params = {}) {
  const url = new URL(`${API_URL}${endpoint}`);
  Object.keys(params).forEach(key => 
    url.searchParams.append(key, params[key])
  );
  
  const response = await fetchWithTimeout(url.toString(), {
    method: 'GET',
    headers: {
      'Accept': 'application/json'
    }
  });
  
  return handleResponse(response, endpoint);
}

export async function apiPost(endpoint, data = {}) {
  const response = await fetchWithTimeout(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return handleResponse(response, endpoint);
}

export async function apiDelete(endpoint) {
  const response = await fetchWithTimeout(`${API_URL}${endpoint}`, {
    method: 'DELETE',
    headers: {
      'Accept': 'application/json'
    }
  });
  
  return handleResponse(response, endpoint);
}

export async function apiUpload(endpoint, formData) {
  const response = await fetchWithTimeout(`${API_URL}${endpoint}`, {
    method: 'POST',
    body: formData
  });
  
  return handleResponse(response, endpoint);
}

export { ApiError };
```

### Step 3: Implement Session Service

In `session-api.js`, implement the session-related API calls:

```javascript
// session-api.js
import { apiGet, apiPost, apiDelete } from './api';

export async function initializeSession(sessionParams) {
  return apiPost('/initialize', sessionParams);
}

export async function verifySession(sessionId) {
  return apiGet(`/verify_session/${sessionId}`);
}

export async function updateSessionSettings(sessionId, settings) {
  return apiPost('/update_settings', {
    ui_session_id: sessionId,
    ...settings
  });
}

export async function deleteAllSessions() {
  return apiDelete('/sessions');
}

export async function getAgentConfig(sessionId) {
  return apiGet(`/get_agent_config/${sessionId}`);
}

export async function debugAgentState(sessionId) {
  return apiGet(`/debug_agent_state/${sessionId}`);
}

export async function debugChatSession(sessionId) {
  return apiGet(`/chat_session_debug/${sessionId}`);
}
```

### Step 4: Implement Model Service

In `model-api.js`, implement the model-related API calls:

```javascript
// model-api.js
import { apiGet } from './api';

export async function getAvailableModels() {
  return apiGet('/models');
}

// Helper function to extract default parameters from a model
export function getDefaultModelParameters(model) {
  if (!model || !model.parameters) return {};
  
  const params = {};
  
  // Extract basic parameters
  if (model.parameters.temperature) {
    params.temperature = model.parameters.temperature.default;
  }
  
  // Extract reasoning-related parameters
  if (model.parameters.reasoning_effort) {
    params.reasoning_effort = model.parameters.reasoning_effort.default;
  }
  
  // Extract Claude-specific parameters
  if (model.parameters.extended_thinking) {
    const extendedThinking = model.parameters.extended_thinking.enabled === true;
    params.extended_thinking = extendedThinking;
    
    if (extendedThinking && model.parameters.extended_thinking.budget_tokens) {
      params.budget_tokens = model.parameters.extended_thinking.budget_tokens.default;
    } else {
      params.budget_tokens = 0;
    }
  }
  
  return params;
}
```

### Step 5: Implement Tool Service

In `tools-api.js`, implement the tool-related API calls:

```javascript
// tools-api.js
import { apiGet, apiPost } from './api';

export async function getAvailableTools() {
  return apiGet('/tools');
}

export async function getAgentTools(sessionId) {
  return apiGet(`/get_agent_tools/${sessionId}`);
}

export async function updateTools(sessionId, tools) {
  return apiPost('/update_tools', {
    ui_session_id: sessionId,
    tools: tools
  });
}
```

### Step 6: Implement Persona Service

In `persona-api.js`, implement the persona-related API calls:

```javascript
// persona-api.js
import { apiGet } from './api';

export async function getAvailablePersonas() {
  return apiGet('/personas');
}
```

### Step 7: Create Service Index

Create an index file to export all services:

```javascript
// index.js
export * from './api';
export * as sessionService from './session-api';
export * as modelService from './model-api';
export * as toolsService from './tools-api';
export * as personaService from './persona-api';
```

### Step 8: Update SessionContext to Use Service Layer

Refactor SessionContext to use the new service layer:

1. Replace direct fetch calls with service calls
2. Update error handling to use ApiError class
3. Maintain the same context API for backwards compatibility
4. Make sure all API interactions go through the service layer

### Step 9: Implement Chat Service

If time permits, implement chat-related API calls in a separate service:

```javascript
// chat-api.js
import { API_URL } from '@/config/config';
import { ApiError } from './api';

export async function sendChatMessage(sessionId, message, fileIds = []) {
  const formData = new FormData();
  formData.append('ui_session_id', sessionId);
  formData.append('message', message);
  
  if (fileIds && fileIds.length > 0) {
    formData.append('file_ids', JSON.stringify(fileIds));
  }
  
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new ApiError(
      `Chat request failed: ${response.status}`,
      response.status
    );
  }
  
  return response; // Return the raw response for streaming
}

export async function cancelChatInteraction(sessionId) {
  const formData = new FormData();
  formData.append('ui_session_id', sessionId);
  
  const response = await fetch(`${API_URL}/cancel`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new ApiError(
      `Cancel request failed: ${response.status}`,
      response.status
    );
  }
  
  return response.json();
}
```

### Step 10: Testing Plan

1. **Unit Tests**:
   - Test each API service function with mock responses
   - Verify error handling and response processing
   - Check parameter handling and URL construction

2. **Integration Tests**:
   - Verify SessionContext still functions with the new service layer
   - Test all user interactions that trigger API calls

3. **Manual Testing**:
   - Check all primary flows in the application
   - Verify error states show appropriate messages
   - Check network requests to ensure they're using the service layer

### Step 11: Documentation Updates

1. Create README.md in the services directory explaining:
   - Service architecture
   - How to use the services
   - Error handling patterns
   - How to extend with new services

2. Update existing component documentation to reference the new service layer where applicable

## Implementation Sequence

1. Create the directory structure and placeholder files
2. Implement the core `api.js` service
3. Implement individual API services one at a time:
   - Start with `model-api.js` and `persona-api.js` (used during initialization)
   - Move to `session-api.js` (core functionality)
   - Finish with `tools-api.js` (used after session initialization)
4. Update SessionContext to use one service at a time, testing after each update
5. Run complete integration tests
6. Document the new service layer

## Risk Assessment and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing functionality | High | Medium | Implement one service at a time with thorough testing |
| Performance degradation | Medium | Low | Monitor API response times, implement timeouts and caching |
| Error handling edge cases | Medium | Medium | Create comprehensive error handling patterns, add monitoring |
| Increased complexity | Low | Low | Create clear documentation, follow consistent patterns |
| Initialization race conditions | High | Medium | Maintain careful sequencing of API calls during initialization |

## Success Criteria

1. All API calls are routed through the service layer
2. Error handling is consistent across all API calls
3. SessionContext maintains the same public API
4. No regressions in existing functionality
5. Code is more maintainable and testable

## Next Steps After Phase 1

After completing Phase 1, we'll be ready to proceed to Phase 2, which involves creating the Core SessionContext with proper separation of concerns. The API service layer will make this easier by removing API-related complexity from the context.