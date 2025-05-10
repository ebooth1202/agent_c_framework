/**
 * Debug API Service
 * 
 * Handles all API requests related to debugging, including:
 * - Session debugging information
 * - Agent state inspection
 */

import api, { extractResponseData } from './api_v2';

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