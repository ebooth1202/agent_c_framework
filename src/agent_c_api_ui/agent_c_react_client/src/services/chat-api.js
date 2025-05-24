/**
 * Chat API Service
 * 
 * Handles all API requests related to chat functionality, including:
 * - Message streaming with v2 JSON events
 * - Chat history management
 * - File attachments and management
 * - Chat cancellation
 * 
 * Updated for v2 API endpoints with backward compatibility
 */

import api from './api';

/**
 * Send a chat message with streaming support (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {Object} message - Message object with structured content
 * @param {Function} onChunk - Callback for each streamed event
 * @returns {Promise<Object>} Complete response after streaming finishes
 */
export async function sendStreamingMessage(sessionId, message, onChunk) {
  const url = `${api.API_CONFIG.baseUrl}/sessions/${sessionId}/chat`;
  
  // Ensure message has proper v2 structure
  const v2Message = {
    message: {
      role: message.role || 'user',
      content: message.content || [{ type: 'text', text: message.text || message.message || '' }]
    },
    stream: true
  };
  
  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(v2Message),
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
    let accumulatedResponse = { text_content: '', events: [] };
    
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
          // Parse JSON event (v2 format)
          const event = JSON.parse(line);
          const eventType = event.type;
          
          // Store event in accumulated response
          accumulatedResponse.events.push(event);
          
          // Handle different event types
          if (eventType === 'text_delta') {
            const textPiece = event.content || '';
            accumulatedResponse.text_content += textPiece;
          } else if (eventType === 'completion') {
            accumulatedResponse.status = event.status;
            accumulatedResponse.complete = event.status === 'complete';
          }
          
          // Call the chunk handler callback with v2 event
          if (onChunk && typeof onChunk === 'function') {
            onChunk(event);
          }
        } catch (e) {
          console.warn('Error parsing streaming event:', e, line);
        }
      }
    }
    
    return accumulatedResponse;
  } catch (error) {
    throw api.processApiError(error, 'Message streaming failed');
  }
}

/**
 * Send a chat message with streaming support (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {string} message - Message text
 * @param {Array} fileIds - Array of file IDs to attach
 * @param {Function} onChunk - Callback for each streamed chunk
 * @returns {Promise<string>} Complete text response
 */
export async function sendChatMessage(sessionId, message, fileIds = null, onChunk = null) {
  try {
    // Convert v1 format to v2 format
    const content = [{ type: 'text', text: message }];
    
    // Add file references if provided
    if (fileIds && Array.isArray(fileIds)) {
      for (const fileId of fileIds) {
        content.push({ type: 'file', file_id: fileId });
      }
    }
    
    const v2Message = {
      role: 'user',
      content: content
    };
    
    // Convert v1 chunk callback to v2 event callback
    const v2OnChunk = onChunk ? (event) => {
      if (event.type === 'text_delta') {
        onChunk(event.content || '');
      }
    } : null;
    
    const response = await sendStreamingMessage(sessionId, v2Message, v2OnChunk);
    return response.text_content || '';
  } catch (error) {
    throw api.processApiError(error, 'Failed to send chat message');
  }
}

/**
 * Cancel the current chat interaction (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Cancellation result
 */
export async function cancelChat(sessionId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}/chat`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to cancel chat');
  }
}

/**
 * Upload a file to be used in chat (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File reference to use in messages
 */
export async function uploadFile(sessionId, file) {
  try {
    const response = await api.uploadFile(
      `/sessions/${sessionId}/files`, 
      file,
      'file'
    );
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to upload file');
  }
}

/**
 * Upload a file attachment (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File reference with v1 format
 */
export async function uploadAttachment(sessionId, file) {
  try {
    const fileData = await uploadFile(sessionId, file);
    // Convert v2 response to v1 format
    return {
      id: fileData.file_id,
      filename: fileData.filename,
      mime_type: fileData.content_type,
      size: fileData.size,
      ...fileData
    };
  } catch (error) {
    throw api.processApiError(error, 'Failed to upload attachment');
  }
}

/**
 * Download a file (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Blob>} File data
 */
export async function downloadFile(sessionId, fileId) {
  try {
    return await api.downloadFile(`/sessions/${sessionId}/files/${fileId}/content`);
  } catch (error) {
    throw api.processApiError(error, 'Failed to download file');
  }
}

/**
 * Download a file attachment (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {string} attachmentId - Attachment identifier
 * @returns {Promise<Blob>} File data
 */
export async function downloadAttachment(sessionId, attachmentId) {
  try {
    return await downloadFile(sessionId, attachmentId);
  } catch (error) {
    throw api.processApiError(error, 'Failed to download attachment');
  }
}

/**
 * Get file metadata (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Object>} File metadata
 */
export async function getFileMetadata(sessionId, fileId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files/${fileId}`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get file metadata');
  }
}

/**
 * List files for a session (v2 API)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Array>} Array of file objects
 */
export async function listFiles(sessionId) {
  try {
    const response = await api.get(`/sessions/${sessionId}/files`);
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to list files');
  }
}

/**
 * Delete a file (v2 API)
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<boolean>} True if deletion was successful
 */
export async function deleteFile(sessionId, fileId) {
  try {
    const response = await api.delete(`/sessions/${sessionId}/files/${fileId}`);
    // v2 API returns 204 No Content on successful deletion
    return response.status === 204 || response.status === undefined;
  } catch (error) {
    throw api.processApiError(error, 'Failed to delete file');
  }
}

/**
 * Get chat messages/events for a session (via history API)
 * @param {string} sessionId - Session identifier
 * @param {Object} params - Query parameters (limit, offset, event_types)
 * @returns {Promise<Array>} Array of message events
 */
export async function getChatHistory(sessionId, params = {}) {
  try {
    const response = await api.get(`/history/${sessionId}/events`, { params });
    const extracted = api.extractResponseData(response);
    return extracted.data;
  } catch (error) {
    throw api.processApiError(error, 'Failed to get chat history');
  }
}

/**
 * Stream chat events for a session (via history API)
 * @param {string} sessionId - Session identifier
 * @param {Object} params - Stream parameters (event_types, real_time, speed_factor)
 * @param {Function} onEvent - Callback for each event
 * @returns {Promise<void>} Resolves when stream ends
 */
export async function streamChatHistory(sessionId, params = {}, onEvent) {
  const url = `${api.API_CONFIG.baseUrl}/history/${sessionId}/stream`;
  const queryParams = new URLSearchParams(params);
  const fullUrl = `${url}?${queryParams}`;
  
  const requestOptions = {
    method: 'GET',
    headers: {
      'Accept': 'text/event-stream',
    },
    credentials: api.API_CONFIG.credentials,
  };

  try {
    const response = await fetch(fullUrl, requestOptions);
    
    if (!response.ok) {
      throw api.processApiError(
        response, 
        `Event streaming failed with status ${response.status}`
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
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk
      const chunk = decoder.decode(value, { stream: true });
      
      // Process each line (Server-Sent Events format)
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.trim() && line.startsWith('data: ')) {
          try {
            const eventJson = line.slice(6); // Remove 'data: ' prefix
            const event = JSON.parse(eventJson);
            
            // Call the event handler callback
            if (onEvent && typeof onEvent === 'function') {
              onEvent(event);
            }
          } catch (e) {
            console.warn('Error parsing SSE event:', e, line);
          }
        }
      }
    }
  } catch (error) {
    throw api.processApiError(error, 'Event streaming failed');
  }
}

export default {
  // v2 API methods
  sendStreamingMessage,
  cancelChat,
  uploadFile,
  downloadFile,
  getFileMetadata,
  listFiles,
  deleteFile,
  getChatHistory,
  streamChatHistory,
  
  // v1 compatibility methods
  sendChatMessage,
  uploadAttachment,
  downloadAttachment,
};