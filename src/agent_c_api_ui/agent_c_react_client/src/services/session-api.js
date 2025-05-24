/**
 * Session API Service
 * 
 * Handles all API requests related to session management, including:
 * - Creating and managing sessions
 * - Session authentication
 * - Session state synchronization
 * - Agent configuration and tool management
 * 
 * Updated for v2 API endpoints with backward compatibility
 */

import api from './api';

/**
 * Initialize a session with model and parameters (v1 compatibility)
 * @param {Object} config - Session configuration with model, parameters, persona, etc.
 * @returns {Promise<Object>} Session data including ui_session_id
 * @deprecated Use createSession instead for v2 API
 */
export async function initialize(config = {}) {
  try {
    // Map v1 parameters to v2 format
    const v2Config = {
      model_id: config.model_name || config.model_id,
      persona_id: config.persona_name || config.persona_id || 'default',
      temperature: config.temperature,
      name: config.name || 'Session',
      ...config
    };
    
    // Remove v1-specific fields
    delete v2Config.model_name;
    delete v2Config.persona_name;
    
    const response = await api.post('/sessions', v2Config);
    const extracted = api.extractResponseData(response);
    
    // Return in v1 format for backward compatibility
    return {
      ui_session_id: extracted.data.id,
      ...extracted.data
    };
  } catch (error) {
    throw api.processApiError(error, 'Failed to initialize session');
  }
}

/**
 * Create a new session (v2 API)
 * @param {Object} config - Initial session configuration
 * @param {string} config.model_id - Model identifier
 * @param {string} config.persona_id - Persona identifier
 * @param {number} config.temperature - Temperature setting
 * @param {string} config.name - Session name
 * @returns {Promise<Object>} Session data
 */
export async function createSession(config = {}) {
  try {
    const response = await api.post('/sessions', config);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to create session');
  }
}

/**
 * Get an existing session by ID (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session data
 */
export async function getSession(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session');
  }
}

/**
 * Verify if a session exists and is valid (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Object with valid boolean and session data
 */
export async function verifySession(sessionId) {
  try {
    const sessionData = await getSession(sessionId);
    return {
      valid: true,
      session: sessionData
    };
  } catch (error) {
    // Check for 404 in multiple places where it might be
    const is404 = error.statusCode === 404 || 
                  error.originalError?.statusCode === 404 ||
                  (error.isProcessed && error.message.includes('not found'));
    
    if (is404) {
      return { valid: false };
    }
    throw error.isProcessed ? error : api.processApiError(error, 'Failed to verify session');
  }
}

/**
 * List all sessions with pagination (v2 API)
 * @param {Object} params - Query parameters
 * @param {number} params.limit - Maximum number of sessions to return
 * @param {number} params.offset - Number of sessions to skip
 * @returns {Promise<Object>} Paginated session list
 */
export async function listSessions(params = {}) {
  try {
    const response = await api.get('/sessions', { params });
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to list sessions');
  }
}

/**
 * Update session configuration (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {Object} config - Updated session configuration
 * @returns {Promise<Object>} Updated session data
 */
export async function updateSession(sessionId, config) {
  try {
    const response = await api.patch(`/sessions/${sessionId}`, config);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update session');
  }
}

/**
 * Delete a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<boolean>} True if deletion was successful
 */
export async function deleteSession(sessionId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}`);
    // v2 API returns 204 No Content on successful deletion
    return response.status === 204 || response.status === undefined;
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete session');
  }
}

/**
 * Delete all sessions (v1 compatibility)
 * @returns {Promise<Object>} Object with deleted count
 */
export async function deleteAllSessions() {
  try {
    // v2 API doesn't have a bulk delete, so we list and delete each
    const sessionList = await listSessions({ limit: 100 });
    let deletedCount = 0;
    
    for (const session of sessionList.items || []) {
      try {
        const success = await deleteSession(session.id);
        if (success) deletedCount++;
      } catch (error) {
        console.warn(`Failed to delete session ${session.id}:`, error);
      }
    }
    
    return { deleted_count: deletedCount };
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete all sessions');
  }
}

/**
 * Get agent configuration for a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Agent configuration
 */
export async function getAgentConfig(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/agent`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve agent configuration');
  }
}

/**
 * Update agent configuration for a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {Object} config - Agent configuration updates
 * @param {string} config.persona_id - Persona identifier
 * @param {number} config.temperature - Temperature setting
 * @param {Object} config.parameters - Additional parameters
 * @returns {Promise<Object>} Updated agent configuration
 */
export async function updateAgentConfig(sessionId, config) {
  try {
    const response = await api.patch(`/sessions/${sessionId}/agent`, config);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update agent configuration');
  }
}

/**
 * Update agent settings (v1 compatibility)
 * @param {Object} params - Update parameters
 * @param {string} params.ui_session_id - Session identifier
 * @param {string} params.persona_name - Persona name (mapped to persona_id)
 * @param {number} params.temperature - Temperature setting
 * @returns {Promise<Object>} Updated configuration
 */
export async function updateSettings(params) {
  try {
    const { ui_session_id, persona_name, ...config } = params;
    
    // Map v1 parameters to v2 format
    if (persona_name) {
      config.persona_id = persona_name;
    }
    
    return await updateAgentConfig(ui_session_id, config);
  } catch (error) {
    throw api.processApiError(error, 'Failed to update settings');
  }
}

/**
 * Get tools for a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session tools configuration
 */
export async function getSessionTools(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/tools`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session tools');
  }
}

/**
 * Update tools for a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {Array} tools - Array of tool identifiers
 * @returns {Promise<boolean>} True if update was successful
 */
export async function updateSessionTools(sessionId, tools) {
  try {
    const response = await api.put(`/sessions/${sessionId}/tools`, tools);
    // v2 API returns 204 No Content on successful update
    return response.status === 204 || response.status === undefined;
  } catch (error) {
    throw api.processApiError(error, 'Failed to update session tools');
  }
}

/**
 * Update tools (v1 compatibility)
 * @param {Object} params - Update parameters
 * @param {string} params.ui_session_id - Session identifier
 * @param {Array} params.tools - Array of tool identifiers
 * @returns {Promise<Object>} Update result
 */
export async function updateTools(params) {
  try {
    const { ui_session_id, tools } = params;
    const success = await updateSessionTools(ui_session_id, tools);
    return { success, tools };
  } catch (error) {
    throw api.processApiError(error, 'Failed to update tools');
  }
}

/**
 * Get agent tools (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Object with initialized_tools array
 */
export async function getAgentTools(sessionId) {
  try {
    const toolsData = await getSessionTools(sessionId);
    return {
      initialized_tools: toolsData.tools || []
    };
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve agent tools');
  }
}

/**
 * Send a message to the session (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {Object} message - Message to send (includes content, files, etc.)
 * @returns {Promise<Object>} Message response
 */
export async function sendMessage(sessionId, message) {
  try {
    const response = await api.post(`/sessions/${sessionId}/chat`, message);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to send message');
  }
}

/**
 * Get message history for a session (via history API)
 * @param {string} sessionId - Session identifier
 * @param {Object} params - Query parameters (limit, offset, etc.)
 * @returns {Promise<Array>} Message history
 */
export async function getMessages(sessionId, params = {}) {
  try {
    const response = await api.get(`/history/${sessionId}/events`, { params });
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve messages');
  }
}

/**
 * Cancel/stop the current chat generation (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Cancellation result
 */
export async function cancelChat(sessionId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}/chat`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to cancel chat');
  }
}

/**
 * Stop the current session generation/stream (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Result
 */
export async function stopGeneration(sessionId) {
  try {
    return await cancelChat(sessionId);
  } catch (error) {
    throw api.processApiError(error, 'Failed to stop generation');
  }
}

export default {
  // v2 API methods
  createSession,
  getSession,
  updateSession,
  deleteSession,
  listSessions,
  verifySession,
  deleteAllSessions,
  getAgentConfig,
  updateAgentConfig,
  getSessionTools,
  updateSessionTools,
  sendMessage,
  getMessages,
  cancelChat,
  
  // v1 compatibility methods
  initialize,
  updateSettings,
  updateTools,
  getAgentTools,
  stopGeneration,
};