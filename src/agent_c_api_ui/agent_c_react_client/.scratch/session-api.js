/**
 * Session API Service
 * 
 * Handles all API requests related to session management, including:
 * - Creating and managing sessions
 * - Session authentication
 * - Session state synchronization
 */

import api, { extractResponseData } from './api_v2';

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
 * Verify if a session exists and is valid
 * @param {string} sessionId - Session identifier
 * @returns {Promise<boolean>} Whether the session is valid
 */
export async function verifySession(sessionId) {
  try {
    await getSession(sessionId);
    return true;
  } catch (error) {
    if (error.statusCode === 404) {
      return false;
    }
    throw error;
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
    return extractResponseData(response).data.tools || [];
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

/**
 * Set the model for a session
 * @param {string} sessionId - Session identifier
 * @param {string} modelId - Model identifier
 * @param {Object} parameters - Optional model parameters to set
 * @returns {Promise<Object>} Updated agent configuration
 */
export async function setSessionModel(sessionId, modelId, parameters = {}) {
  try {
    return await updateAgentConfig(sessionId, {
      model_id: modelId,
      ...parameters
    });
  } catch (error) {
    throw api.processApiError(error, 'Failed to set session model');
  }
}

/**
 * Set the persona for a session
 * @param {string} sessionId - Session identifier
 * @param {string} personaId - Persona identifier
 * @returns {Promise<Object>} Updated agent configuration
 */
export async function setSessionPersona(sessionId, personaId) {
  try {
    return await updateAgentConfig(sessionId, {
      persona_id: personaId
    });
  } catch (error) {
    throw api.processApiError(error, 'Failed to set session persona');
  }
}

/**
 * Update model parameters for a session
 * @param {string} sessionId - Session identifier
 * @param {Object} parameters - Model parameters to update
 * @returns {Promise<Object>} Updated agent configuration
 */
export async function updateModelParameters(sessionId, parameters) {
  try {
    return await updateAgentConfig(sessionId, parameters);
  } catch (error) {
    throw api.processApiError(error, 'Failed to update model parameters');
  }
}

export default {
  createSession,
  getSession,
  verifySession,
  listSessions,
  updateSession,
  deleteSession,
  getAgentConfig,
  updateAgentConfig,
  getSessionTools,
  updateSessionTools,
  setSessionModel,
  setSessionPersona,
  updateModelParameters,
};