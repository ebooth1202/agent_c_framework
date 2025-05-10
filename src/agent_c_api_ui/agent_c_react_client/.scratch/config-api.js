/**
 * Config API Service
 * 
 * Handles all API requests related to system configuration, including:
 * - Models, personas, and tools configuration
 * - Combined system configuration
 */

import api, { extractResponseData } from './api_v2';

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

/**
 * Get detailed information about a specific model
 * @param {string} modelId - Model identifier
 * @returns {Promise<Object>} Model details
 */
export async function getModelDetails(modelId) {
  try {
    const response = await api.get(`/config/models/${modelId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve model details');
  }
}

/**
 * Get detailed information about a specific persona
 * @param {string} personaId - Persona identifier
 * @returns {Promise<Object>} Persona details
 */
export async function getPersonaDetails(personaId) {
  try {
    const response = await api.get(`/config/personas/${personaId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve persona details');
  }
}

/**
 * Get detailed information about a specific tool
 * @param {string} toolId - Tool identifier
 * @returns {Promise<Object>} Tool details
 */
export async function getToolDetails(toolId) {
  try {
    const response = await api.get(`/config/tools/${toolId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve tool details');
  }
}

/**
 * Get parameter configurations for a model
 * @param {string} modelId - Model identifier
 * @returns {Promise<Object>} Model parameters
 */
export async function getModelParameters(modelId) {
  try {
    const response = await api.get(`/config/models/${modelId}/parameters`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve model parameters');
  }
}

export default {
  getModels,
  getPersonas,
  getTools,
  getSystemConfig,
  getModelDetails,
  getPersonaDetails,
  getToolDetails,
  getModelParameters,
};