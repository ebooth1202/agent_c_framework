/**
 * History API Service
 * 
 * Handles all API requests related to session history, including:
 * - Listing session histories
 * - Event retrieval and replay
 */

import api, { extractResponseData } from './api_v2';

/**
 * List available session histories
 * @param {Object} options - Pagination options (limit, offset, sort_by, sort_order)
 * @returns {Promise<Object>} List of histories with pagination metadata
 */
export async function listHistories(options = {}) {
  try {
    const response = await api.get('/history', { params: options });
    return extractResponseData(response);
  } catch (error) {
    throw api.processApiError(error, 'Failed to list histories');
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
 * Get events for a session history
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Event retrieval options (event_types, start_time, end_time, limit)
 * @returns {Promise<Array>} List of events
 */
export async function getEvents(sessionId, options = {}) {
  try {
    const response = await api.get(`/history/${sessionId}/events`, { params: options });
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get events');
  }
}

/**
 * Stream events for a session history
 * @param {string} sessionId - Session identifier
 * @param {Object} options - Streaming options (event_types, real_time, speed_factor)
 * @param {Function} onEvent - Callback for each event
 * @returns {Promise<void>}
 */
export async function streamEvents(sessionId, options = {}, onEvent) {
  const url = `${api.API_CONFIG.baseUrl}/history/${sessionId}/stream`;
  const params = new URLSearchParams(options).toString();
  const fullUrl = `${url}?${params}`;
  
  try {
    const response = await fetch(fullUrl, {
      method: 'GET',
      credentials: api.API_CONFIG.credentials,
      headers: api.API_CONFIG.headers,
    });
    
    if (!response.ok) {
      throw api.processApiError(
        response, 
        `Event streaming failed with status ${response.status}`
      );
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process each line in the buffer
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer
      
      for (const line of lines) {
        if (line.trim() && line.startsWith('data: ')) {
          try {
            // Parse SSE data
            const eventData = JSON.parse(line.slice(6));
            
            // Call the event handler
            if (onEvent && typeof onEvent === 'function') {
              onEvent(eventData);
            }
          } catch (e) {
            console.warn('Error parsing event stream data:', e, line);
          }
        }
      }
    }
  } catch (error) {
    throw api.processApiError(error, 'Event streaming failed');
  }
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
 * @param {string} action - Control action (start, pause, resume, stop, seek)
 * @param {number|null} position - Position for seek actions
 * @param {number} speed - Playback speed factor
 * @returns {Promise<Object>} Updated replay status
 */
export async function controlReplay(sessionId, action, position = null, speed = 1.0) {
  try {
    const payload = { action, speed };
    if (position !== null) {
      payload.position = position;
    }
    
    const response = await api.post(`/history/${sessionId}/replay`, payload);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to control replay');
  }
}

export default {
  listHistories,
  getHistoryDetails,
  getEvents,
  streamEvents,
  getReplayStatus,
  controlReplay,
};