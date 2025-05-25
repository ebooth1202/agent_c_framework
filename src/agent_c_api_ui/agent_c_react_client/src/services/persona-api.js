/**
 * Persona API Service
 * 
 * Handles all API requests related to personas, including:
 * - Retrieving available personas
 * - Getting persona details
 * - Managing persona settings for sessions
 * 
 * NOTE: This service now uses v2 API through adapter functions while
 * maintaining v1 API signatures for backward compatibility.
 */

import {
  getPersonas as getPersonasAdapter,
  getPersonaDetails as getPersonaDetailsAdapter,
  setSessionPersona as setSessionPersonaAdapter,
  getSessionPersona as getSessionPersonaAdapter,
  getPersonaCategories as getPersonaCategoriesAdapter
} from './v1-api-adapters';

/**
 * Get list of available personas
 * @returns {Promise<Array>} List of personas
 */
export async function getPersonas() {
  try {
    console.log('[persona-api] getPersonas() - using v2 adapter');
    return await getPersonasAdapter();
  } catch (error) {
    console.error('[persona-api] getPersonas() failed:', error);
    throw error;
  }
}

/**
 * Get detailed information about a specific persona
 * @param {string} personaId - Persona identifier
 * @returns {Promise<Object>} Persona details
 */
export async function getPersonaDetails(personaId) {
  try {
    console.log('[persona-api] getPersonaDetails() - using v2 adapter for persona:', personaId);
    return await getPersonaDetailsAdapter(personaId);
  } catch (error) {
    console.error('[persona-api] getPersonaDetails() failed for persona:', personaId, error);
    throw error;
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
    console.log('[persona-api] setSessionPersona() - using v2 adapter for session:', sessionId, 'persona:', personaId);
    return await setSessionPersonaAdapter(sessionId, personaId);
  } catch (error) {
    console.error('[persona-api] setSessionPersona() failed for session:', sessionId, 'persona:', personaId, error);
    throw error;
  }
}

/**
 * Get the current persona for a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Current persona
 */
export async function getSessionPersona(sessionId) {
  try {
    console.log('[persona-api] getSessionPersona() - using v2 adapter for session:', sessionId);
    return await getSessionPersonaAdapter(sessionId);
  } catch (error) {
    console.error('[persona-api] getSessionPersona() failed for session:', sessionId, error);
    throw error;
  }
}

/**
 * Get persona categories
 * @returns {Promise<Array>} Persona categories
 */
export async function getPersonaCategories() {
  try {
    console.log('[persona-api] getPersonaCategories() - using v2 adapter');
    return await getPersonaCategoriesAdapter();
  } catch (error) {
    console.error('[persona-api] getPersonaCategories() failed:', error);
    throw error;
  }
}

export default {
  getPersonas,
  getPersonaDetails,
  setSessionPersona,
  getSessionPersona,
  getPersonaCategories,
};