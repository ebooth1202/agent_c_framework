# Improved API Service Layer Design

## Overview

The improved API service layer will be designed to work with the new v2 RESTful API. The service layer will maintain the same basic structure of our current implementation but with updated endpoints, parameter handling, and response processing to match the v2 API specifications.

## Key Design Principles

1. **Maintain Service Structure**: Keep the logical separation of concerns with individual service modules.
2. **Version Agnostic Interfaces**: Design the consumer-facing methods to be as version-agnostic as possible, allowing for future API version changes with minimal impact.
3. **Consistent Response Handling**: Standardize how we handle the new consistent response format from the v2 API.
4. **Error Handling**: Enhance error handling to work with the standard error format of the v2 API.
5. **Pagination Support**: Add standardized pagination handling for list endpoints.

## Base API Service

### api.js Changes

- Update `API_CONFIG.baseUrl` to use the v2 endpoint ('/api/v2')
- Enhance `processApiError` to extract the v2 standard error format
- Add a `extractResponseData` utility to handle the standard `{ data, meta, errors }` format
- Add support for pagination in GET requests

```javascript
// Example extractResponseData utility
export function extractResponseData(response) {
  // Handle v2 API standard response format
  if (response && response.data !== undefined) {
    return {
      data: response.data,
      meta: response.meta || {},
      errors: response.errors || []
    };
  }
  
  // Return the response itself for endpoints that don't follow the standard format
  return { data: response, meta: {}, errors: [] };
}
```

## Config API Service (New)

Add a new `config-api.js` service for the new v2 configuration resources:

```javascript
/**
 * Config API Service
 * 
 * Handles all API requests related to system configuration, including:
 * - Models, personas, and tools configuration
 * - Combined system configuration
 */

import api, { extractResponseData } from './api';

/**
 * Get all available models
 * @returns {Promise<Array>} List of models
 */
export async function getModels() {
  try {
    const response = await api.get('/config/models');
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve available models');
  }
}

/**
 * Get all available personas
 * @returns {Promise<Array>} List of personas
 */
export async function getPersonas() {
  try {
    const response = await api.get('/config/personas');
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve available personas');
  }
}

/**
 * Get all available tools
 * @returns {Promise<Array>} List of tools
 */
export async function getTools() {
  try {
    const response = await api.get('/config/tools');
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve available tools');
  }
}

/**
 * Get combined system configuration (models, personas, tools)
 * @returns {Promise<Object>} System configuration
 */
export async function getSystemConfig() {
  try {
    const response = await api.get('/config/system');
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve system configuration');
  }
}

export default {
  getModels,
  getPersonas,
  getTools,
  getSystemConfig,
};
```

## Session API Service

Update the session-api.js to use the v2 endpoints and parameter formats:

```javascript
/**
 * Session API Service
 * 
 * Handles all API requests related to session management, including:
 * - Creating and managing sessions
 * - Session authentication
 * - Session state synchronization
 */

import api, { extractResponseData } from './api';

/**
 * Create a new session
 * @param {Object} config - Session configuration with model_id, persona_id, etc.
 * @returns {Promise<Object>} Session data including session_id
 */
export async function createSession(config = {}) {
  try {
    const response = await api.post('/sessions', config);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to create session');
  }
}

/**
 * Get an existing session by ID
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session data
 */
export async function getSession(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session');
  }
}

/**
 * List all sessions
 * @param {Object} options - Pagination options (limit, offset)
 * @returns {Promise<Object>} List of sessions with pagination metadata
 */
export async function listSessions(options = { limit: 10, offset: 0 }) {
  try {
    const response = await api.get('/sessions', { params: options });
    return extractResponseData(response);
  } catch (error) {
    throw api.processApiError(error, 'Failed to list sessions');
  }
}

/**
 * Update session properties
 * @param {string} sessionId - Session identifier
 * @param {Object} updates - Properties to update (name, metadata, etc.)
 * @returns {Promise<Object>} Updated session data
 */
export async function updateSession(sessionId, updates = {}) {
  try {
    const response = await api.patch(`/sessions/${sessionId}`, updates);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update session');
  }
}

/**
 * Delete a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<boolean>} Success status
 */
export async function deleteSession(sessionId) {
  try {
    await api.delete(`/sessions/${sessionId}`);
    return true;
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete session');
  }
}

/**
 * Get agent configuration for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Agent configuration
 */
export async function getAgentConfig(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/agent`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve agent configuration');
  }
}

/**
 * Update agent configuration
 * @param {string} sessionId - Session identifier
 * @param {Object} config - Updated configuration (temperature, persona_id, etc.)
 * @returns {Promise<Object>} Updated agent configuration
 */
export async function updateAgentConfig(sessionId, config = {}) {
  try {
    const response = await api.patch(`/sessions/${sessionId}/agent`, config);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update agent configuration');
  }
}

/**
 * Get tool configurations for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Array>} Tool configurations
 */
export async function getSessionTools(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/tools`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session tools');
  }
}

/**
 * Update tool configurations for a session
 * @param {string} sessionId - Session identifier
 * @param {Array} tools - Updated tool configurations
 * @returns {Promise<boolean>} Success status
 */
export async function updateSessionTools(sessionId, tools = []) {
  try {
    await api.put(`/sessions/${sessionId}/tools`, tools);
    return true;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update session tools');
  }
}

export default {
  createSession,
  getSession,
  listSessions,
  updateSession,
  deleteSession,
  getAgentConfig,
  updateAgentConfig,
  getSessionTools,
  updateSessionTools,
};
```

## Chat API Service

Update chat-api.js to work with the v2 chat endpoints:

```javascript
/**
 * Chat API Service
 * 
 * Handles all API requests related to chat functionality, including:
 * - Message streaming
 * - Chat history management
 * - Message attachments
 */

import api, { extractResponseData } from './api';

/**
 * Send a chat message with streaming support
 * @param {string} sessionId - Session identifier
 * @param {Object} messageContent - Message content to send
 * @param {boolean} stream - Whether to stream the response
 * @param {Function} onChunk - Callback for each streamed chunk
 * @returns {Promise<Object>} Complete response after streaming finishes
 */
export async function sendChatMessage(sessionId, messageContent, stream = true, onChunk = null) {
  // Build message in v2 format
  const message = {
    message: {
      role: 'user',
      content: Array.isArray(messageContent) ? messageContent : [{ type: 'text', text: messageContent }]
    },
    stream
  };

  // If not streaming, use regular POST
  if (!stream) {
    try {
      const response = await api.post(`/sessions/${sessionId}/chat`, message);
      return extractResponseData(response).data;
    } catch (error) {
      throw api.processApiError(error, 'Failed to send message');
    }
  }

  // Handle streaming response
  const url = `${api.API_CONFIG.baseUrl}/sessions/${sessionId}/chat`;
  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
    credentials: api.API_CONFIG.credentials,
  };

  try {
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      throw api.processApiError(
        response, 
        `Message streaming failed with status ${response.status}`
      );
    }
    
    if (!response.body) {
      throw api.processApiError(
        new Error('ReadableStream not supported in this browser'),
        'Streaming not supported in your browser'
      );
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const events = [];
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk
      const chunk = decoder.decode(value, { stream: true });
      
      // Process each line (in case multiple events arrived in one chunk)
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        try {
          // Parse JSON
          const data = JSON.parse(line);
          
          // Add to events array
          events.push(data);
          
          // Call the chunk handler callback
          if (onChunk && typeof onChunk === 'function') {
            onChunk(data);
          }
        } catch (e) {
          console.warn('Error parsing streaming chunk:', e, line);
        }
      }
    }
    
    return events;
  } catch (error) {
    throw api.processApiError(error, 'Message streaming failed');
  }
}

/**
 * Cancel the current chat generation
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Cancellation result
 */
export async function cancelChatGeneration(sessionId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}/chat`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to cancel chat generation');
  }
}

/**
 * Upload a file to be used in chat
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File details including file_id
 */
export async function uploadFile(sessionId, file) {
  try {
    const response = await api.uploadFile(
      `/sessions/${sessionId}/files`, 
      file,
      'file'
    );
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to upload file');
  }
}

/**
 * List files attached to a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Array>} List of files
 */
export async function listFiles(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to list files');
  }
}

/**
 * Get file metadata
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Object>} File metadata
 */
export async function getFileMetadata(sessionId, fileId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files/${fileId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get file metadata');
  }
}

/**
 * Download a file
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Blob>} File content
 */
export async function downloadFile(sessionId, fileId) {
  try {
    return await api.downloadFile(`/sessions/${sessionId}/files/${fileId}/content`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to download file');
  }
}

/**
 * Delete a file
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<boolean>} Success status
 */
export async function deleteFile(sessionId, fileId) {
  try {
    await api.delete(`/sessions/${sessionId}/files/${fileId}`);
    return true;
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete file');
  }
}

export default {
  sendChatMessage,
  cancelChatGeneration,
  uploadFile,
  listFiles,
  getFileMetadata,
  downloadFile,
  deleteFile,
};
```

## History API Service

Add a new history-api.js service for the v2 history endpoints:

```javascript
/**
 * History API Service
 * 
 * Handles all API requests related to session history, including:
 * - Listing session histories
 * - Event retrieval and replay
 */

import api, { extractResponseData } from './api';

/**
 * List available session histories
 * @param {Object} options - Pagination options (limit, offset, sort_by, sort_order)
 * @returns {Promise<Object>} List of histories with pagination metadata
 */
export async function listHistories(options = {}) {
  try {
    const response = await api.get('/history', { params: options });
    return extractResponseData(response);
  } catch (error) {
    throw api.processApiError(error, 'Failed to list histories');
  }
}

/**
 * Get detailed information about a session history
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} History details
 */
export async function getHistoryDetails(sessionId) {
  try {
    const response = await api.get(`/history/${sessionId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get history details');
  }
}

/**
 * Get events for a session history
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Event retrieval options (event_types, start_time, end_time, limit)
 * @returns {Promise<Array>} List of events
 */
export async function getEvents(sessionId, options = {}) {
  try {
    const response = await api.get(`/history/${sessionId}/events`, { params: options });
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get events');
  }
}

/**
 * Stream events for a session history
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Streaming options (event_types, real_time, speed_factor)
 * @param {Function} onEvent - Callback for each event
 * @returns {Promise<void>}
 */
export async function streamEvents(sessionId, options = {}, onEvent) {
  const url = `${api.API_CONFIG.baseUrl}/history/${sessionId}/stream`;
  const params = new URLSearchParams(options).toString();
  const fullUrl = `${url}?${params}`;
  
  try {
    const response = await fetch(fullUrl, {
      method: 'GET',
      credentials: api.API_CONFIG.credentials,
      headers: api.API_CONFIG.headers,
    });
    
    if (!response.ok) {
      throw api.processApiError(
        response, 
        `Event streaming failed with status ${response.status}`
      );
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process each line in the buffer
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer
      
      for (const line of lines) {
        if (line.trim() && line.startsWith('data: ')) {
          try {
            // Parse SSE data
            const eventData = JSON.parse(line.slice(6));
            
            // Call the event handler
            if (onEvent && typeof onEvent === 'function') {
              onEvent(eventData);
            }
          } catch (e) {
            console.warn('Error parsing event stream data:', e, line);
          }
        }
      }
    }
  } catch (error) {
    throw api.processApiError(error, 'Event streaming failed');
  }
}

/**
 * Get replay status for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Replay status
 */
export async function getReplayStatus(sessionId) {
  try {
    const response = await api.get(`/history/${sessionId}/replay`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get replay status');
  }
}

/**
 * Control session replay
 * @param {string} sessionId - Session identifier
 * @param {string} action - Control action (start, pause, resume, stop, seek)
 * @param {number|null} position - Position for seek actions
 * @param {number} speed - Playback speed factor
 * @returns {Promise<Object>} Updated replay status
 */
export async function controlReplay(sessionId, action, position = null, speed = 1.0) {
  try {
    const payload = { action, speed };
    if (position !== null) {
      payload.position = position;
    }
    
    const response = await api.post(`/history/${sessionId}/replay`, payload);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to control replay');
  }
}

export default {
  listHistories,
  getHistoryDetails,
  getEvents,
  streamEvents,
  getReplayStatus,
  controlReplay,
};
```

## Debug API Service

Add a new debug-api.js service for the v2 debug endpoints:

```javascript
/**
 * Debug API Service
 * 
 * Handles all API requests related to debugging, including:
 * - Session debugging information
 * - Agent state inspection
 */

import api, { extractResponseData } from './api';

/**
 * Get detailed debug information about a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session debug information
 */
export async function getSessionDebugInfo(sessionId) {
  try {
    const response = await api.get(`/debug/sessions/${sessionId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get session debug information');
  }
}

/**
 * Get detailed debug information about an agent
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Agent debug information
 */
export async function getAgentDebugInfo(sessionId) {
  try {
    const response = await api.get(`/debug/agent/${sessionId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get agent debug information');
  }
}

export default {
  getSessionDebugInfo,
  getAgentDebugInfo,
};
```

## Updated index.js

Update index.js to export all the services:

```javascript
/**
 * API Services Index
 * 
 * This file exports all API services for easy import throughout the application.
 */

import apiService from './api';
import configService from './config-api';
import sessionService from './session-api';
import chatService from './chat-api';
import historyService from './history-api';
import debugService from './debug-api';

// Export individual services
export const api = apiService;
export const config = configService;
export const session = sessionService;
export const chat = chatService;
export const history = historyService;
export const debug = debugService;

// Export individual functions from each service
export {
  // Core API utilities
  processApiError,
  showErrorToast,
  API_CONFIG,
  extractResponseData,
} from './api';

// Export all service methods from config-api
export {
  getModels,
  getPersonas,
  getTools,
  getSystemConfig,
} from './config-api';

// Export all service methods from session-api
export {
  createSession,
  getSession,
  listSessions,
  updateSession,
  deleteSession,
  getAgentConfig,
  updateAgentConfig,
  getSessionTools,
  updateSessionTools,
} from './session-api';

// Export all service methods from chat-api
export {
  sendChatMessage,
  cancelChatGeneration,
  uploadFile,
  listFiles,
  getFileMetadata,
  downloadFile,
  deleteFile,
} from './chat-api';

// Export all service methods from history-api
export {
  listHistories,
  getHistoryDetails,
  getEvents,
  streamEvents,
  getReplayStatus,
  controlReplay,
} from './history-api';

// Export all service methods from debug-api
export {
  getSessionDebugInfo,
  getAgentDebugInfo,
} from './debug-api';

// Default export combining all services
export default {
  api: apiService,
  config: configService,
  session: sessionService,
  chat: chatService,
  history: historyService,
  debug: debugService,
};
```

## Migration Approach

To implement this design, we'll use the Adapter Pattern approach:

1. **Create Core v2 Services**:
   - Implement the v2 API services in a separate directory
   - Add thorough unit testing

2. **Implement Adapter Layer**:
   - Create v1-compatible adapters that use v2 services internally
   - Maintain the same interface as the v1 API

3. **Replace v1 Services with Adapters**:
   - Update the original service files to use the adapters
   - No changes needed to components at this stage

4. **Component Migration**:
   - Gradually update components to use v2 services directly
   - Remove adapter usage as components are migrated

This approach allows for a smooth transition with minimal disruption to the application while still enabling a clear path to complete migration.