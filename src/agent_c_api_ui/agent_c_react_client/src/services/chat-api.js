/**
 * Chat API Service
 * 
 * Handles all API requests related to chat functionality, including:
 * - Message streaming
 * - Chat history management
 * - Message attachments
 */

import api from './api';

/**
 * Send a chat message with streaming support
 * @param {string} sessionId - Session identifier
 * @param {Object} message - Message object to send
 * @param {Function} onChunk - Callback for each streamed chunk
 * @returns {Promise<Object>} Complete response after streaming finishes
 */
export async function sendStreamingMessage(sessionId, message, onChunk) {
  const url = `${api.API_CONFIG.baseUrl}/session/${sessionId}/stream`;
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
    let accumulatedResponse = {};
    
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
          // Check for data: prefix used in server-sent events
          const jsonStr = line.startsWith('data: ') 
            ? line.slice(6) 
            : line;
          
          // Parse JSON
          const data = JSON.parse(jsonStr);
          
          // Update accumulated response with latest data
          accumulatedResponse = { ...accumulatedResponse, ...data };
          
          // Call the chunk handler callback
          if (onChunk && typeof onChunk === 'function') {
            onChunk(data);
          }
        } catch (e) {
          console.warn('Error parsing streaming chunk:', e, line);
        }
      }
    }
    
    return accumulatedResponse;
  } catch (error) {
    throw api.processApiError(error, 'Message streaming failed');
  }
}

/**
 * Upload a file attachment to be used in chat
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File reference to use in messages
 */
export async function uploadAttachment(sessionId, file) {
  try {
    return await api.uploadFile(
      `/session/${sessionId}/attachments`, 
      file,
      'file',
      { filename: file.name }
    );
  } catch (error) {
    throw api.processApiError(error, 'Failed to upload attachment');
  }
}

/**
 * Download a file attachment
 * @param {string} sessionId - Session identifier
 * @param {string} attachmentId - Attachment identifier
 * @returns {Promise<Blob>} File data
 */
export async function downloadAttachment(sessionId, attachmentId) {
  try {
    return await api.downloadFile(`/session/${sessionId}/attachments/${attachmentId}`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to download attachment');
  }
}

/**
 * Delete a message from chat history
 * @param {string} sessionId - Session identifier
 * @param {string} messageId - Message identifier
 * @returns {Promise<Object>} Result
 */
export async function deleteMessage(sessionId, messageId) {
  try {
    return await api.delete(`/session/${sessionId}/messages/${messageId}`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete message');
  }
}

/**
 * Edit a previous user message
 * @param {string} sessionId - Session identifier
 * @param {string} messageId - Message identifier
 * @param {Object} updatedMessage - Updated message content
 * @returns {Promise<Object>} Updated message
 */
export async function editMessage(sessionId, messageId, updatedMessage) {
  try {
    return await api.put(`/session/${sessionId}/messages/${messageId}`, updatedMessage);
  } catch (error) {
    throw api.processApiError(error, 'Failed to edit message');
  }
}

/**
 * Regenerate an assistant response
 * @param {string} sessionId - Session identifier
 * @param {string} messageId - Message identifier to regenerate from
 * @returns {Promise<Object>} New response
 */
export async function regenerateResponse(sessionId, messageId) {
  try {
    return await api.post(`/session/${sessionId}/regenerate`, { message_id: messageId });
  } catch (error) {
    throw api.processApiError(error, 'Failed to regenerate response');
  }
}

export default {
  sendStreamingMessage,
  uploadAttachment,
  downloadAttachment,
  deleteMessage,
  editMessage,
  regenerateResponse,
};