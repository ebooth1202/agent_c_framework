/**
 * Tools API Service
 * 
 * Handles all API requests related to tools, including:
 * - Retrieving available tools
 * - Tool execution and management
 * - Tool configurations
 */

import api from './api';

/**
 * Get list of available tools
 * @returns {Promise<Array>} List of tools
 */
export async function getTools() {
  try {
    return await api.get('/tools');
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve available tools');
  }
}

/**
 * Get detailed information about a specific tool
 * @param {string} toolId - Tool identifier
 * @returns {Promise<Object>} Tool details
 */
export async function getToolDetails(toolId) {
  try {
    return await api.get(`/tools/${toolId}`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve tool details');
  }
}

/**
 * Execute a tool directly (not through the assistant)
 * @param {string} toolId - Tool identifier
 * @param {Object} parameters - Tool parameters
 * @returns {Promise<Object>} Tool execution result
 */
export async function executeTool(toolId, parameters = {}) {
  try {
    return await api.post(`/tools/${toolId}/execute`, parameters);
  } catch (error) {
    throw api.processApiError(error, 'Failed to execute tool');
  }
}

/**
 * Get tool configurations for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Tool configurations
 */
export async function getSessionTools(sessionId) {
  try {
    return await api.get(`/session/${sessionId}/tools`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session tools');
  }
}

/**
 * Update tool configurations for a session
 * @param {string} sessionId - Session identifier
 * @param {Array} tools - Updated tool configurations
 * @returns {Promise<Object>} Updated tool configurations
 */
export async function updateSessionTools(sessionId, tools) {
  try {
    return await api.put(`/session/${sessionId}/tools`, { tools });
  } catch (error) {
    throw api.processApiError(error, 'Failed to update session tools');
  }
}

/**
 * Get categories of available tools
 * @returns {Promise<Array>} Tool categories
 */
export async function getToolCategories() {
  try {
    return await api.get('/tools/categories');
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve tool categories');
  }
}

export default {
  getTools,
  getToolDetails,
  executeTool,
  getSessionTools,
  updateSessionTools,
  getToolCategories,
};