/**
 * History API Service
 * 
 * Handles all API requests related to session history, including:
 * - Listing session histories
 * - Retrieving session history details
 * - Event retrieval and streaming
 * - Replay control
 */

import api, { extractResponseData } from './api';

/**
 * List available session histories
 * @param {Object} options - Pagination and sorting options
 * @param {number} [options.limit=50] - Maximum number of histories to return (1-100)
 * @param {number} [options.offset=0] - Number of histories to skip for pagination
 * @param {string} [options.sort_by='start_time'] - Field to sort by
 * @param {string} [options.sort_order='desc'] - Sort order ('asc' or 'desc')
 * @returns {Promise<Object>} List of histories with pagination metadata
 */
export async function listHistories(options = {}) {
  try {
    const response = await api.get('/history', { params: options });
    const { data, meta } = extractResponseData(response);
    return { histories: data.items, pagination: meta.pagination };
  } catch (error) {
    throw api.processApiError(error, 'Failed to list session histories');
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
 * Delete a session history
 * @param {string} sessionId - Session identifier
 * @returns {Promise<boolean>} True if successfully deleted
 */
export async function deleteHistory(sessionId) {
  try {
    const response = await api.delete(`/history/${sessionId}`);
    // For 204 No Content responses, response may not have all properties
    if (response && response.status === 204) {
      return true;
    }
    // For regular success responses with content
    return extractResponseData(response).data?.status === 'success';
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete history');
  }
}

/**
 * Get events for a session history
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Event retrieval options
 * @param {Array<string>} [options.event_types] - Filter by event types
 * @param {string} [options.start_time] - Filter events after this timestamp (ISO-8601)
 * @param {string} [options.end_time] - Filter events before this timestamp (ISO-8601)
 * @param {number} [options.limit=100] - Maximum number of events to return
 * @returns {Promise<Array>} List of events
 */
export async function getEvents(sessionId, options = {}) {
  try {
    const response = await api.get(`/history/${sessionId}/events`, { params: options });
    const result = extractResponseData(response);
    return { 
      events: result.data, 
      pagination: result.meta?.pagination
    };
  } catch (error) {
    throw api.processApiError(error, 'Failed to get session events');
  }
}

/**
 * Stream events for a session history using Server-Sent Events
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Streaming options
 * @param {Array<string>} [options.event_types] - Filter by event types
 * @param {boolean} [options.real_time=false] - When true, replays events with original timing
 * @param {number} [options.speed_factor=1.0] - Speed multiplier for real-time replay
 * @param {Function} onEvent - Callback for each event
 * @param {Function} [onError] - Callback for errors
 * @returns {EventSource} EventSource instance that must be closed when done
 */
export function streamEvents(sessionId, options = {}, onEvent, onError) {
  const baseUrl = api.API_CONFIG.baseUrl;
  const params = new URLSearchParams();
  
  // Add options to query parameters
  Object.entries(options).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else {
        params.append(key, value);
      }
    }
  });
  
  const url = `${baseUrl}/history/${sessionId}/stream?${params.toString()}`;
  
  // Create EventSource for SSE
  const eventSource = new EventSource(url, { withCredentials: true });
  
  // Set up event handlers
  eventSource.onmessage = (event) => {
    try {
      const eventData = JSON.parse(event.data);
      if (onEvent && typeof onEvent === 'function') {
        onEvent(eventData);
      }
    } catch (error) {
      console.error('Error parsing event stream data:', error, event.data);
      if (onError && typeof onError === 'function') {
        onError(error);
      }
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('Event stream error:', error);
    if (onError && typeof onError === 'function') {
      onError(error);
    }
  };
  
  // Return the EventSource so caller can close it when done
  return eventSource;
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
 * @param {string} action - Control action ('play', 'pause', 'seek')
 * @param {Object} options - Control options
 * @param {string} [options.position] - Timestamp position for seek actions
 * @param {number} [options.speed=1.0] - Playback speed factor
 * @returns {Promise<boolean>} True if control action was successful
 */
export async function controlReplay(sessionId, action, options = {}) {
  try {
    const payload = {
      action,
      ...options
    };
    
    const response = await api.post(`/history/${sessionId}/replay`, payload);
    return extractResponseData(response).data === true;
  } catch (error) {
    throw api.processApiError(error, `Failed to ${action} replay`);
  }
}

export default {
  listHistories,
  getHistoryDetails,
  deleteHistory,
  getEvents,
  streamEvents,
  getReplayStatus,
  controlReplay,
};