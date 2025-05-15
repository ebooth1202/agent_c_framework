/**
 * Chat API Service
 * 
 * Handles all API requests related to chat functionality, including:
 * - Message streaming
 * - Chat history management
 * - Message attachments
 */

import api, { extractResponseData } from './api_v2';

/**
 * Send a chat message with streaming support
 * @param {string} sessionId - Session identifier
 * @param {string|Array} messageContent - Message content to send (string or content array)
 * @param {boolean} stream - Whether to stream the response
 * @param {Function} onChunk - Callback for each streamed chunk
 * @returns {Promise<Object|Array>} Complete response after streaming finishes
 */
export async function sendChatMessage(sessionId, messageContent, stream = true, onChunk = null) {
  // Build message in v2 format
  const message = {
    message: {
      role: 'user',
      content: Array.isArray(messageContent) ? messageContent : [{ type: 'text', text: messageContent }]
    },
    stream
  };

  // If not streaming, use regular POST
  if (!stream) {
    try {
      const response = await api.post(`/sessions/${sessionId}/chat`, message);
      return extractResponseData(response).data;
    } catch (error) {
      throw api.processApiError(error, 'Failed to send message');
    }
  }

  // Handle streaming response
  const url = `${api.API_CONFIG.baseUrl}/sessions/${sessionId}/chat`;
  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
    credentials: api.API_CONFIG.credentials,
  };

  try {
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      throw api.processApiError(
        response, 
        `Message streaming failed with status ${response.status}`
      );
    }
    
    if (!response.body) {
      throw api.processApiError(
        new Error('ReadableStream not supported in this browser'),
        'Streaming not supported in your browser'
      );
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const events = [];
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk
      const chunk = decoder.decode(value, { stream: true });
      
      // Process each line (in case multiple events arrived in one chunk)
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        try {
          // Parse JSON
          const data = JSON.parse(line);
          
          // Add to events array
          events.push(data);
          
          // Call the chunk handler callback
          if (onChunk && typeof onChunk === 'function') {
            onChunk(data);
          }
        } catch (e) {
          console.warn('Error parsing streaming chunk:', e, line);
        }
      }
    }
    
    return events;
  } catch (error) {
    throw api.processApiError(error, 'Message streaming failed');
  }
}

/**
 * Cancel the current chat generation
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Cancellation result
 */
export async function cancelChatGeneration(sessionId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}/chat`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to cancel chat generation');
  }
}

/**
 * Upload a file to be used in chat
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File details including file_id
 */
export async function uploadFile(sessionId, file) {
  try {
    const response = await api.uploadFile(
      `/sessions/${sessionId}/files`, 
      file,
      'file'
    );
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to upload file');
  }
}

/**
 * List files attached to a session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Array>} List of files
 */
export async function listFiles(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to list files');
  }
}

/**
 * Get file metadata
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Object>} File metadata
 */
export async function getFileMetadata(sessionId, fileId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files/${fileId}`);
    return extractResponseData(response).data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get file metadata');
  }
}

/**
 * Download a file
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Blob>} File content
 */
export async function downloadFile(sessionId, fileId) {
  try {
    return await api.downloadFile(`/sessions/${sessionId}/files/${fileId}/content`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to download file');
  }
}

/**
 * Delete a file
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<boolean>} Success status
 */
export async function deleteFile(sessionId, fileId) {
  try {
    await api.delete(`/sessions/${sessionId}/files/${fileId}`);
    return true;
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete file');
  }
}

export default {
  sendChatMessage,
  cancelChatGeneration,
  uploadFile,
  listFiles,
  getFileMetadata,
  downloadFile,
  deleteFile,
};