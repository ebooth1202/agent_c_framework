# Phase 1: API Service Layer Implementation Plan

## Overview

This document details the implementation plan for Phase 1 of the SessionContext refactoring: creating a dedicated API service layer to separate API calls from state management.

## Objectives

1. Extract all API calls from the SessionContext into dedicated service modules
2. Implement consistent error handling and request formatting
3. Make the SessionContext consume the API services
4. Ensure backward compatibility with existing components

## Implementation Steps

### Step 1: Create Base API Service

1. Create `src/services/api.js` with:
   - Base API URL configuration
   - Fetch wrapper with standardized error handling
   - Request/response interceptors
   - Authentication handling (if needed)

```javascript
// src/services/api.js
import { API_URL } from '@/config/config';

/**
 * Base API service with error handling and request formatting
 */
class ApiService {
  constructor(baseUrl = API_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic request method with standardized error handling
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        // Try to get error details
        let errorText;
        try {
          errorText = await response.text();
        } catch (e) {
          errorText = 'Could not read error response';
        }
        throw new Error(`${endpoint} failed: ${response.status} - ${errorText}`);
      }

      const contentType = response.headers.get('content-type');
      
      // Return raw response for non-JSON responses (like files)
      if (!contentType?.includes('application/json')) {
        return response;
      }

      // Parse JSON response
      const text = await response.text();
      try {
        return JSON.parse(text);
      } catch (e) {
        console.error(`Failed to parse JSON from ${endpoint}:`, text);
        throw new Error(`Invalid JSON from ${endpoint}: ${e.message}`);
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request with JSON body
   */
  async post(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * POST request with FormData body
   */
  async postForm(endpoint, formData, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      headers: {}, // Let the browser set the correct Content-Type with boundary
      body: formData,
    });
  }
}

export const apiService = new ApiService();
export default apiService;
```

### Step 2: Create Session API Service

1. Create `src/services/session-api.js` with methods for session management:
   - `initializeSession`
   - `updateSettings`
   - `cancelStream`
   - `getAgentConfig`

```javascript
// src/services/session-api.js
import apiService from './api';

/**
 * Session API service for managing sessions and settings
 */
export const sessionApi = {
  /**
   * Initialize a new session or update an existing one
   */
  async initializeSession(data) {
    return apiService.post('/initialize', data);
  },

  /**
   * Update session settings
   */
  async updateSettings(data) {
    return apiService.post('/update_settings', data);
  },

  /**
   * Cancel ongoing stream
   */
  async cancelStream(sessionId) {
    const formData = new FormData();
    formData.append('ui_session_id', sessionId);
    return apiService.postForm('/cancel', formData);
  },

  /**
   * Get agent configuration
   */
  async getAgentConfig(sessionId) {
    return apiService.get(`/get_agent_config/${sessionId}`);
  },
};

export default sessionApi;
```

### Step 3: Create Model API Service

1. Create `src/services/model-api.js` with methods for model management:
   - `getModels`
   - `getPersonas`

```javascript
// src/services/model-api.js
import apiService from './api';

/**
 * Model API service for managing models and personas
 */
export const modelApi = {
  /**
   * Get available models
   */
  async getModels() {
    return apiService.get('/models');
  },

  /**
   * Get available personas
   */
  async getPersonas() {
    return apiService.get('/personas');
  },
};

export default modelApi;
```

### Step 4: Create Tools API Service

1. Create `src/services/tools-api.js` with methods for tool management:
   - `getTools`
   - `getAgentTools`
   - `updateTools`

```javascript
// src/services/tools-api.js
import apiService from './api';

/**
 * Tools API service for managing tools
 */
export const toolsApi = {
  /**
   * Get available tools
   */
  async getTools() {
    return apiService.get('/tools');
  },

  /**
   * Get tools equipped for a specific agent
   */
  async getAgentTools(sessionId) {
    return apiService.get(`/get_agent_tools/${sessionId}`);
  },

  /**
   * Update tools for a session
   */
  async updateTools(sessionId, tools) {
    return apiService.post('/update_tools', {
      ui_session_id: sessionId,
      tools: tools
    });
  },
};

export default toolsApi;
```

### Step 5: Create Chat API Service

1. Create `src/services/chat-api.js` with methods for chat interactions:
   - `sendMessage`
   - `uploadFile`
   - `getFiles`

```javascript
// src/services/chat-api.js
import apiService from './api';

/**
 * Chat API service for message and file operations
 */
export const chatApi = {
  /**
   * Send a message to the chat
   */
  async sendMessage(sessionId, message, options = {}) {
    const formData = new FormData();
    formData.append('ui_session_id', sessionId);
    formData.append('message', message);
    
    // Add optional parameters
    if (options.customPrompt) {
      formData.append('custom_prompt', options.customPrompt);
    }
    
    if (options.fileIds && options.fileIds.length > 0) {
      formData.append('file_ids', JSON.stringify(options.fileIds));
    }
    
    if (options.temperature !== undefined) {
      formData.append('temperature', options.temperature);
    }
    
    if (options.reasoningEffort !== undefined) {
      formData.append('reasoning_effort', options.reasoningEffort);
    }
    
    if (options.modelName) {
      formData.append('llm_model', options.modelName);
    }
    
    // Return the raw response so the caller can process the stream
    const response = await fetch(`${apiService.baseUrl}/chat`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.status}`);
    }
    
    return response;
  },

  /**
   * Upload a file
   */
  async uploadFile(sessionId, file) {
    const formData = new FormData();
    formData.append('ui_session_id', sessionId);
    formData.append('file', file);
    
    return apiService.postForm('/upload_file', formData);
  },

  /**
   * Get files for a session
   */
  async getFiles(sessionId) {
    return apiService.get(`/files/${sessionId}`);
  },
};

export default chatApi;
```

### Step 6: Update SessionContext to Use API Services

1. Import the API services in `SessionContext.jsx`
2. Replace direct fetch calls with API service calls
3. Update error handling to use the standardized approach

Example updates for some of the key methods:

```javascript
// In SessionContext.jsx
import sessionApi from '@/services/session-api';
import modelApi from '@/services/model-api';
import toolsApi from '@/services/tools-api';

// Replace fetchInitialData
const fetchInitialData = async () => {
  try {
    console.log('Starting fetchInitialData with API_URL:', API_URL);
    if (!API_URL) {
      throw new Error('API_URL is undefined. Please check your environment variables.');
    }
    setIsLoading(true);
    setIsInitialized(false);

    // Parallel fetching using API services
    const [personasData, toolsData, modelsData] = await Promise.all([
      modelApi.getPersonas(),
      toolsApi.getTools(),
      modelApi.getModels()
    ]);

    // Store data returned from backend into their data structures.
    setPersonas(personasData);
    setAvailableTools(toolsData);
    setModelConfigs(modelsData.models);

    // Rest of the method remains the same
    // ...
  } catch (err) {
    console.error('Error fetching initial data:', err);
    setError(`Failed to load initial data: ${err.message}`);
  } finally {
    setIsLoading(false);
  }
};

// Replace initializeSession
const initializeSession = async (forceNew = false, initialModel = null, modelConfigsData = null) => {
  setIsReady(false);
  try {
    // First part of the method unchanged
    // ...
    
    const jsonData = {
      model_name: currentModel.id,
      backend: currentModel.backend,
      persona_name: persona || 'default'
    };

    // Rest of preparatory logic
    // ...
    
    // Use the session API service
    const data = await sessionApi.initializeSession(jsonData);
    
    if (data.ui_session_id) {
      localStorage.setItem("ui_session_id", data.ui_session_id);
      setSessionId(data.ui_session_id);
      setIsReady(true);
      setError(null);

      // Update modelName state to reflect the current model
      setModelName(currentModel.id);
      setSelectedModel(currentModel);
    } else {
      throw new Error("No ui_session_id in response");
    }
  } catch (err) {
    console.error("Session initialization failed:", err);
    setIsReady(false);
    setError(`Session initialization failed: ${err.message}`);
  }
};

// Replace updateAgentSettings
const updateAgentSettings = async (updateType, values) => {
  if (!sessionId || !isReady) return;
  try {
    switch (updateType) {
      case 'MODEL_CHANGE': {
        // Logic for model change
        // ...
        
        // Initialize new session with the custom prompt
        await initializeSession(false, modelWithPersona);
        setSettingsVersion(v => v + 1);
        const updatedModelConfig = {
          modelName: values.modelName,
          modelParameters: newParameters
        };
        saveConfigToStorage(updatedModelConfig);
        break;
      }
      case 'SETTINGS_UPDATE': {
        const updatedPersona = values.persona_name || persona;
        const updatedPrompt = values.customPrompt || customPrompt;
        setPersona(updatedPersona);
        setCustomPrompt(updatedPrompt);

        const jsonData = {
          ui_session_id: sessionId,
          model_name: modelName,
          backend: selectedModel?.backend,
          persona_name: updatedPersona,
          custom_prompt: updatedPrompt
        };

        console.log('json data being sent for settings update:', jsonData);

        await sessionApi.updateSettings(jsonData);
        setSettingsVersion(v => v + 1);
        const updatedSettingsConfig = {
          persona: updatedPersona,
          customPrompt: updatedPrompt
        };
        saveConfigToStorage(updatedSettingsConfig);
        break;
      }
      case 'PARAMETER_UPDATE': {
        // Logic for parameter updates
        // ...
        
        // Use session API for the update
        await sessionApi.updateSettings(jsonData);
        setSettingsVersion(v => v + 1);
        const updatedParamConfig = {
          modelParameters: updatedParameters
        };
        saveConfigToStorage(updatedParamConfig);
        break;
      }
      default:
        break;
    }
  } catch (err) {
    setError(`Failed to update settings: ${err.message}`);
  }
};

// Replace fetchAgentTools
const fetchAgentTools = async () => {
  if (!sessionId || !isReady) return;
  try {
    const data = await toolsApi.getAgentTools(sessionId);
    if (data.status === 'success' && Array.isArray(data.initialized_tools)) {
      setActiveTools(data.initialized_tools.map(tool => tool.class_name));
    }
  } catch (err) {
    console.error('Error fetching agent tools:', err);
  }
};

// Replace handleEquipTools
const handleEquipTools = async (tools) => {
  try {
    await toolsApi.updateTools(sessionId, tools);
    await fetchAgentTools();
    setSettingsVersion(v => v + 1);
  } catch (err) {
    console.error("Failed to equip tools:", err);
    throw err;
  }
};
```

### Step 7: Testing and Verification

1. Test all API services independently
2. Test the updated SessionContext with the new API services
3. Verify that all existing functionality works as expected
4. Check error handling for various error scenarios
5. Test performance and ensure no regressions

## Expected Outcomes

1. All API calls are moved to dedicated service modules
2. SessionContext no longer contains direct API calls
3. Error handling is consistent across the application
4. Application functionality remains unchanged
5. Code is more modular and easier to maintain

## Risks and Mitigations

### Risks

1. **Breaking changes**: API service might handle responses differently
2. **Error handling**: Changes in error handling might affect UI behavior
3. **Timing issues**: Different promise resolution timing might affect state updates

### Mitigations

1. **Thorough testing**: Test each API service and integration point
2. **Incremental changes**: Update and test one API endpoint at a time
3. **Logging**: Add temporary logging to track API calls and responses

## Success Criteria

1. All API calls are made through the new service layer
2. No direct fetch calls remain in SessionContext
3. All existing functionality works without regression
4. Code is more modular and maintainable
5. Error handling is improved and consistent