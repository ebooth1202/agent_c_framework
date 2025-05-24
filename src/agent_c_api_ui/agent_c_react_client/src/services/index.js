/**
 * API Services Index
 * 
 * This file exports all API services for easy import throughout the application.
 * 
 * The services are organized into logical groups:
 * - Core API utilities and base functionality
 * - Session management and configuration
 * - Chat and messaging functionality
 * - Configuration and system information
 * - History and replay functionality
 * 
 * All services support both v2 API endpoints and v1 backward compatibility.
 */

// Import all service modules
import apiService from './api';
import sessionService from './session-api';
import modelService from './model-api';
import toolsService from './tools-api';
import personaService from './persona-api';
import chatService from './chat-api';
import configService from './config-api';
import historyService from './history-api';

// =============================================================================
// SERVICE EXPORTS - Organized by functional groups
// =============================================================================

// Export individual services for direct access
export const api = apiService;
export const session = sessionService;
export const model = modelService;
export const tools = toolsService;
export const persona = personaService;
export const chat = chatService;
export const config = configService;
export const history = historyService;

// =============================================================================
// CORE API UTILITIES
// =============================================================================

export {
  // Core API utilities and configuration
  processApiError,
  showErrorToast,
  API_CONFIG,
  extractResponseData,
} from './api';

// =============================================================================
// SESSION MANAGEMENT (v2 API with v1 compatibility)
// =============================================================================

export {
  // v2 Session Management
  initialize,
  createSession,
  getSession,
  verifySession,
  listSessions,
  updateSession,
  deleteSession,
  deleteAllSessions,
  
  // v2 Agent Configuration
  getAgentConfig,
  updateAgentConfig,
  
  // v2 Session Tools
  getSessionTools,
  updateSessionTools,
  
  // v2 Messaging
  sendMessage,
  getMessages,
  stopGeneration,
  
  // v1 Compatibility Methods
  updateSettings,    // Maps to updateAgentConfig
  updateTools,       // Maps to updateSessionTools
  getAgentTools,     // Maps to getSessionTools
} from './session-api';

// =============================================================================
// CHAT AND MESSAGING (v2 API with v1 compatibility)
// =============================================================================

export {
  // v2 Chat Methods
  sendStreamingMessage,
  
  // v2 File Management
  uploadFile,
  downloadFile,
  getFileMetadata,
  listFiles,
  deleteFile,
  
  // v2 Chat History
  getChatHistory,
  streamChatHistory,
  
  // v1 Compatibility Methods
  sendChatMessage,      // Maps to sendStreamingMessage
  uploadAttachment,     // Maps to uploadFile
  downloadAttachment,   // Maps to downloadFile
  
  // Shared Methods
  cancelChat,
} from './chat-api';

// =============================================================================
// CONFIGURATION AND SYSTEM (v2 API)
// =============================================================================

export {
  // System Configuration
  getSystemConfig,
  
  // Model Information
  getModels,
  getModelDetails,
  getModelParameters,
  
  // Persona Information
  getPersonas,
  getPersonaDetails,
  
  // Tool Information
  getTools,
  getToolDetails,
} from './config-api';

// =============================================================================
// HISTORY AND REPLAY (v2 API)
// =============================================================================

export {
  // History Management
  listHistories,
  getHistoryDetails,
  deleteHistory,
  
  // Event Management
  getEvents,
  streamEvents,
  
  // Replay Control
  getReplayStatus,
  controlReplay,
} from './history-api';

// =============================================================================
// LEGACY v1 SERVICE EXPORTS (for backward compatibility)
// =============================================================================

// Model API (v1 compatibility)
export {
  getModels as getModelsLegacy,
  getModelDetails as getModelDetailsLegacy,
  getModelParameters as getModelParametersLegacy,
  setSessionModel,
  updateModelParameters,
  getDefaultParameters,
} from './model-api';

// Tools API (v1 compatibility)
export {
  getTools as getToolsLegacy,
  getToolDetails as getToolDetailsLegacy,
  executeTool,
  getSessionTools as getSessionToolsLegacy,
  updateSessionTools as updateSessionToolsLegacy,
  getToolCategories,
} from './tools-api';

// Persona API (v1 compatibility)
export {
  getPersonas as getPersonasLegacy,
  getPersonaDetails as getPersonaDetailsLegacy,
  setSessionPersona,
  getSessionPersona,
  getPersonaCategories,
} from './persona-api';

// =============================================================================
// DEFAULT EXPORT - All services combined
// =============================================================================

export default {
  // Core services
  api: apiService,
  session: sessionService,
  chat: chatService,
  config: configService,
  history: historyService,
  
  // Legacy services (for backward compatibility)
  model: modelService,
  tools: toolsService,
  persona: personaService,
};