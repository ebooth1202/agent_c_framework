/**
 * Persona API Service
 * 
 * Handles all API requests related to personas, including:
 * - Retrieving available personas
 * - Getting persona details
 * - Managing persona settings for sessions
 */

import api from './api';

/**
 * Get list of available personas
 * @returns {Promise<Array>} List of personas
 */
export async function getPersonas() {
  try {
    return await api.get('/personas');
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve available personas');
  }
}

/**
 * Get detailed information about a specific persona
 * @param {string} personaId - Persona identifier
 * @returns {Promise<Object>} Persona details
 */
export async function getPersonaDetails(personaId) {
  try {
    return await api.get(`/personas/${personaId}`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve persona details');
  }
}

/**
 * Set the persona for an existing session
 * @param {string} sessionId - Session identifier
 * @param {string} personaId - Persona identifier
 * @returns {Promise<Object>} Updated session
 */
export async function setSessionPersona(sessionId, personaId) {
  try {
    return await api.put(`/session/${sessionId}/persona`, {
      persona_id: personaId
    });
  } catch (error) {
    throw api.processApiError(error, 'Failed to set session persona');
  }
}

/**
 * Get the current persona for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Current persona
 */
export async function getSessionPersona(sessionId) {
  try {
    return await api.get(`/session/${sessionId}/persona`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve session persona');
  }
}

/**
 * Get persona categories
 * @returns {Promise<Array>} Persona categories
 */
export async function getPersonaCategories() {
  try {
    return await api.get('/personas/categories');
  } catch (error) {
    throw api.processApiError(error, 'Failed to retrieve persona categories');
  }
}

export default {
  getPersonas,
  getPersonaDetails,
  setSessionPersona,
  getSessionPersona,
  getPersonaCategories,
};