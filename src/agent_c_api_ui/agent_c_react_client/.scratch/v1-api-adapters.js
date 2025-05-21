/**
 * v1 API Adapters
 * 
 * This file provides adapter functions to maintain backward compatibility
 * with the v1 API while transitioning to the v2 API. The adapters transform
 * parameters and responses to match the v1 API format expected by existing components.
 */

import * as v2Api from './services-index';

/**
 * Initialize a session with model and parameters (v1 compatibility)
 * @param {Object} config - Session configuration with model_name, persona_name, etc.
 * @returns {Promise<Object>} Session data in v1 format
 */
export async function initialize(config = {}) {
  try {
    // Convert v1 parameters to v2 format
    const v2Config = {
      model_id: config.model_name,
      persona_id: config.persona_name,
      temperature: config.temperature,
      name: config.session_name || 'New Session',
      // Map other parameters as needed
    };
    
    // Call v2 API
    const session = await v2Api.createSession(v2Config);
    
    // Return in v1 format
    return {
      ui_session_id: session.id,
      session_id: session.id,
      model_name: session.model_id,
      persona_name: session.persona_id,
      temperature: session.temperature,
      success: true
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Get available models (v1 compatibility)
 * @returns {Promise<Array>} List of models in v1 format
 */
export async function getModels() {
  try {
    const models = await v2Api.getModels();
    
    // Transform to v1 format
    return models.map(model => ({
      name: model.id,
      display_name: model.name,
      description: model.description,
      // Map other fields as needed
    }));
  } catch (error) {
    throw error;
  }
}

/**
 * Get available personas (v1 compatibility)
 * @returns {Promise<Array>} List of personas in v1 format
 */
export async function getPersonas() {
  try {
    const personas = await v2Api.getPersonas();
    
    // Transform to v1 format
    return personas.map(persona => ({
      name: persona.id,
      display_name: persona.name,
      description: persona.description,
      // Map other fields as needed
    }));
  } catch (error) {
    throw error;
  }
}

/**
 * Get available tools (v1 compatibility)
 * @returns {Promise<Array>} List of tools in v1 format
 */
export async function getTools() {
  try {
    const tools = await v2Api.getTools();
    
    // Transform to v1 format
    return tools.map(tool => ({
      name: tool.id,
      display_name: tool.name,
      description: tool.description,
      // Map other fields as needed
    }));
  } catch (error) {
    throw error;
  }
}

/**
 * Verify if a session exists (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Verification result in v1 format
 */
export async function verifySession(sessionId) {
  try {
    const isValid = await v2Api.verifySession(sessionId);
    
    // Return in v1 format
    return {
      valid: isValid,
      session_id: sessionId
    };
  } catch (error) {
    // v1 API returns false for invalid sessions, not an error
    return {
      valid: false,
      session_id: sessionId
    };
  }
}

/**
 * Update session settings (v1 compatibility)
 * @param {Object} config - Settings to update with ui_session_id, temperature, etc.
 * @returns {Promise<Object>} Update result in v1 format
 */
export async function updateSettings(config = {}) {
  try {
    const sessionId = config.ui_session_id;
    
    // Remove ui_session_id from config and map parameters
    const { ui_session_id, persona_name, model_name, ...otherParams } = config;
    
    const updateData = {
      ...otherParams
    };
    
    if (persona_name) {
      updateData.persona_id = persona_name;
    }
    
    if (model_name) {
      updateData.model_id = model_name;
    }
    
    // Call v2 API
    const result = await v2Api.updateAgentConfig(sessionId, updateData);
    
    // Return in v1 format
    return {
      success: true,
      ui_session_id: sessionId,
      updated_settings: result
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Get agent configuration (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Agent configuration in v1 format
 */
export async function getAgentConfig(sessionId) {
  try {
    const config = await v2Api.getAgentConfig(sessionId);
    
    // Return in v1 format
    return {
      config: {
        model_name: config.model_id,
        persona_name: config.persona_id,
        temperature: config.temperature,
        // Map other fields as needed
      },
      ui_session_id: sessionId
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Get agent tools (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Agent tools in v1 format
 */
export async function getAgentTools(sessionId) {
  try {
    const tools = await v2Api.getSessionTools(sessionId);
    
    // Return in v1 format
    return {
      initialized_tools: tools,
      ui_session_id: sessionId
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Update agent tools (v1 compatibility)
 * @param {Object} config - Tools update data with ui_session_id and tools array
 * @returns {Promise<Object>} Update result in v1 format
 */
export async function updateTools(config = {}) {
  try {
    const sessionId = config.ui_session_id;
    const tools = config.tools || [];
    
    // Call v2 API
    await v2Api.updateSessionTools(sessionId, tools);
    
    // Return in v1 format
    return {
      success: true,
      ui_session_id: sessionId,
      tools: tools
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Send a chat message (v1 compatibility)
 * This is a more complex adapter as it needs to handle both formats and streaming
 * @param {string} sessionId - Session identifier
 * @param {string} message - Message text
 * @param {Array} fileIds - Optional file IDs to include with the message
 * @param {Function} onChunk - Callback for streaming chunks
 * @returns {Promise<string>} Full response text
 */
export async function sendChatMessage(sessionId, message, fileIds = [], onChunk = null) {
  try {
    // Prepare content array with message and files
    const content = [];
    
    // Add text message
    content.push({ type: 'text', text: message });
    
    // Add file references if provided
    if (fileIds && fileIds.length > 0) {
      for (const fileId of fileIds) {
        content.push({ type: 'file', file_id: fileId });
      }
    }
    
    // Create an adapter for the streaming callback to convert v2 format to v1
    let fullText = '';
    const chunkAdapter = (chunk) => {
      // Process v2 event format
      if (chunk.type === 'text_delta') {
        const textPiece = chunk.content || '';
        fullText += textPiece;
        
        // Call the original callback with just the text as v1 API did
        if (onChunk) {
          onChunk(textPiece);
        }
      }
      // Handle other event types if needed (tool calls, etc.)
    };
    
    // Call v2 API with the adapter
    await v2Api.sendChatMessage(sessionId, content, true, chunkAdapter);
    
    // Return the full text for compatibility
    return fullText;
  } catch (error) {
    throw error;
  }
}

/**
 * Upload a file attachment (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {File} file - File to upload
 * @returns {Promise<Object>} File metadata in v1 format
 */
export async function uploadFile(sessionId, file) {
  try {
    const fileData = await v2Api.uploadFile(sessionId, file);
    
    // Return in v1 format
    return {
      id: fileData.file_id,
      name: fileData.name,
      mime_type: fileData.content_type,
      size: fileData.size,
      // Map other fields as needed
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Get session files (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Files in v1 format
 */
export async function getSessionFiles(sessionId) {
  try {
    const files = await v2Api.listFiles(sessionId);
    
    // Transform to v1 format
    const transformedFiles = files.map(file => ({
      id: file.file_id,
      name: file.name,
      mime_type: file.content_type,
      size: file.size,
      // Map other fields as needed
    }));
    
    // Return in v1 format
    return {
      files: transformedFiles,
      ui_session_id: sessionId
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Download a file (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Blob>} File content
 */
export async function downloadFile(sessionId, fileId) {
  try {
    return await v2Api.downloadFile(sessionId, fileId);
  } catch (error) {
    throw error;
  }
}

/**
 * Delete a file (v1 compatibility)
 * @param {string} sessionId - Session identifier
 * @param {string} fileId - File identifier
 * @returns {Promise<Object>} Result in v1 format
 */
export async function deleteFile(sessionId, fileId) {
  try {
    await v2Api.deleteFile(sessionId, fileId);
    
    // Return in v1 format
    return {
      success: true,
      message: 'File deleted successfully'
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Delete all sessions (v1 compatibility)
 * @returns {Promise<Object>} Result in v1 format
 */
export async function deleteAllSessions() {
  try {
    // Get all sessions
    const response = await v2Api.listSessions({ limit: 100 });
    const sessions = response.data;
    
    // Delete each session
    let deletedCount = 0;
    for (const session of sessions) {
      try {
        await v2Api.deleteSession(session.id);
        deletedCount++;
      } catch (e) {
        console.error(`Failed to delete session ${session.id}:`, e);
      }
    }
    
    // Return in v1 format
    return {
      success: true,
      deleted_count: deletedCount
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Cancel the current chat generation (v1 compatibility)
 * @param {Object} data - Cancel data with ui_session_id
 * @returns {Promise<Object>} Result in v1 format
 */
export async function cancelChat(data) {
  try {
    const sessionId = data.ui_session_id;
    await v2Api.cancelChatGeneration(sessionId);
    
    // Return in v1 format
    return {
      success: true,
      message: 'Generation cancelled'
    };
  } catch (error) {
    throw error;
  }
}

// Export all adapter functions
export default {
  initialize,
  getModels,
  getPersonas,
  getTools,
  verifySession,
  updateSettings,
  getAgentConfig,
  getAgentTools,
  updateTools,
  sendChatMessage,
  uploadFile,
  getSessionFiles,
  downloadFile,
  deleteFile,
  deleteAllSessions,
  cancelChat,
};