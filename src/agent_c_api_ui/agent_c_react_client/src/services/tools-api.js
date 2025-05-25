/**
 * Tools API Service
 * 
 * Handles all API requests related to tools, including:
 * - Retrieving available tools
 * - Tool execution and management
 * - Tool configurations
 * 
 * NOTE: This service now uses v2 API through adapter functions while
 * maintaining v1 API signatures for backward compatibility.
 */

import {
  getTools as getToolsAdapter,
  getToolDetails as getToolDetailsAdapter,
  getSessionTools as getSessionToolsAdapter,
  updateSessionTools as updateSessionToolsAdapter,
  getToolCategories as getToolCategoriesAdapter,
  executeTool as executeToolAdapter
} from './v1-api-adapters';

/**
 * Get list of available tools
 * @returns {Promise<Array>} List of tools
 */
export async function getTools() {
  try {
    console.log('[tools-api] getTools() - using v2 adapter');
    return await getToolsAdapter();
  } catch (error) {
    console.error('[tools-api] getTools() failed:', error);
    throw error;
  }
}

/**
 * Get detailed information about a specific tool
 * @param {string} toolId - Tool identifier
 * @returns {Promise<Object>} Tool details
 */
export async function getToolDetails(toolId) {
  try {
    console.log('[tools-api] getToolDetails() - using v2 adapter for tool:', toolId);
    return await getToolDetailsAdapter(toolId);
  } catch (error) {
    console.error('[tools-api] getToolDetails() failed for tool:', toolId, error);
    throw error;
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
    console.log('[tools-api] executeTool() - using v2 adapter for tool:', toolId);
    return await executeToolAdapter(toolId, parameters);
  } catch (error) {
    console.error('[tools-api] executeTool() failed for tool:', toolId, error);
    throw error;
  }
}

/**
 * Get tool configurations for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Tool configurations
 */
export async function getSessionTools(sessionId) {
  try {
    console.log('[tools-api] getSessionTools() - using v2 adapter for session:', sessionId);
    return await getSessionToolsAdapter(sessionId);
  } catch (error) {
    console.error('[tools-api] getSessionTools() failed for session:', sessionId, error);
    throw error;
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
    console.log('[tools-api] updateSessionTools() - using v2 adapter for session:', sessionId);
    return await updateSessionToolsAdapter(sessionId, tools);
  } catch (error) {
    console.error('[tools-api] updateSessionTools() failed for session:', sessionId, error);
    throw error;
  }
}

/**
 * Get categories of available tools
 * @returns {Promise<Array>} Tool categories
 */
export async function getToolCategories() {
  try {
    console.log('[tools-api] getToolCategories() - using v2 adapter');
    return await getToolCategoriesAdapter();
  } catch (error) {
    console.error('[tools-api] getToolCategories() failed:', error);
    throw error;
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