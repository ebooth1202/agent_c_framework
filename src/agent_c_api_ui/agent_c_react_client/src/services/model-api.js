/**
 * Model API Service
 * 
 * Handles all API requests related to models, including:
 * - Retrieving available models
 * - Getting model parameters and configurations
 * - Updating model settings
 * 
 * NOTE: This service now uses v2 API through adapter functions while
 * maintaining v1 API signatures for backward compatibility.
 */

import {
  getModels as getModelsAdapter,
  getModelDetails as getModelDetailsAdapter,
  getModelParameters as getModelParametersAdapter,
  setSessionModel as setSessionModelAdapter,
  updateModelParameters as updateModelParametersAdapter,
  getDefaultParameters as getDefaultParametersAdapter
} from './v1-api-adapters';

/**
 * Get list of available models
 * @returns {Promise<Array>} List of models
 */
export async function getModels() {
  try {
    console.log('[model-api] getModels() - using v2 adapter');
    return await getModelsAdapter();
  } catch (error) {
    console.error('[model-api] getModels() failed:', error);
    throw error;
  }
}

/**
 * Get detailed information about a specific model
 * @param {string} modelId - Model identifier
 * @returns {Promise<Object>} Model details
 */
export async function getModelDetails(modelId) {
  try {
    console.log('[model-api] getModelDetails() - using v2 adapter for model:', modelId);
    return await getModelDetailsAdapter(modelId);
  } catch (error) {
    console.error('[model-api] getModelDetails() failed for model:', modelId, error);
    throw error;
  }
}

/**
 * Get parameter configurations for a model
 * @param {string} modelId - Model identifier
 * @returns {Promise<Object>} Model parameters
 */
export async function getModelParameters(modelId) {
  try {
    console.log('[model-api] getModelParameters() - using v2 adapter for model:', modelId);
    return await getModelParametersAdapter(modelId);
  } catch (error) {
    console.error('[model-api] getModelParameters() failed for model:', modelId, error);
    throw error;
  }
}

/**
 * Set the model for an existing session
 * @param {string} sessionId - Session identifier
 * @param {string} modelId - Model identifier
 * @param {Object} parameters - Optional model parameters to set
 * @returns {Promise<Object>} Updated session
 */
export async function setSessionModel(sessionId, modelId, parameters = {}) {
  try {
    console.log('[model-api] setSessionModel() - using v2 adapter for session:', sessionId, 'model:', modelId);
    return await setSessionModelAdapter(sessionId, modelId, parameters);
  } catch (error) {
    console.error('[model-api] setSessionModel() failed for session:', sessionId, 'model:', modelId, error);
    throw error;
  }
}

/**
 * Update model parameters for a session
 * @param {string} sessionId - Session identifier
 * @param {Object} parameters - Model parameters to update
 * @returns {Promise<Object>} Updated parameters
 */
export async function updateModelParameters(sessionId, parameters) {
  try {
    console.log('[model-api] updateModelParameters() - using v2 adapter for session:', sessionId);
    return await updateModelParametersAdapter(sessionId, parameters);
  } catch (error) {
    console.error('[model-api] updateModelParameters() failed for session:', sessionId, error);
    throw error;
  }
}

/**
 * Get default parameters for a model
 * @param {string} modelId - Model identifier
 * @returns {Promise<Object>} Default parameters
 */
export async function getDefaultParameters(modelId) {
  try {
    console.log('[model-api] getDefaultParameters() - using v2 adapter for model:', modelId);
    return await getDefaultParametersAdapter(modelId);
  } catch (error) {
    console.error('[model-api] getDefaultParameters() failed for model:', modelId, error);
    throw error;
  }
}

export default {
  getModels,
  getModelDetails,
  getModelParameters,
  setSessionModel,
  updateModelParameters,
  getDefaultParameters,
};