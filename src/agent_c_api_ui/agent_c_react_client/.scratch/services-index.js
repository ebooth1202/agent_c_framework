/**
 * API Services Index
 * 
 * This file exports all API services for easy import throughout the application.
 */

import apiService from './api_v2';
import configService from './config-api';
import sessionService from './session-api';
import chatService from './chat-api';
import historyService from './history-api';
import debugService from './debug-api';

// Export individual services
export const api = apiService;
export const config = configService;
export const session = sessionService;
export const chat = chatService;
export const history = historyService;
export const debug = debugService;

// Export individual functions from each service
export {
  // Core API utilities
  processApiError,
  showErrorToast,
  API_CONFIG,
  extractResponseData,
} from './api_v2';

// Export all service methods from config-api
export {
  getModels,
  getPersonas,
  getTools,
  getSystemConfig,
  getModelDetails,
  getPersonaDetails,
  getToolDetails,
  getModelParameters,
} from './config-api';

// Export all service methods from session-api
export {
  createSession,
  getSession,
  verifySession,
  listSessions,
  updateSession,
  deleteSession,
  getAgentConfig,
  updateAgentConfig,
  getSessionTools,
  updateSessionTools,
  setSessionModel,
  setSessionPersona,
  updateModelParameters,
} from './session-api';

// Export all service methods from chat-api
export {
  sendChatMessage,
  cancelChatGeneration,
  uploadFile,
  listFiles,
  getFileMetadata,
  downloadFile,
  deleteFile,
} from './chat-api';

// Export all service methods from history-api
export {
  listHistories,
  getHistoryDetails,
  getEvents,
  streamEvents,
  getReplayStatus,
  controlReplay,
} from './history-api';

// Export all service methods from debug-api
export {
  getSessionDebugInfo,
  getAgentDebugInfo,
} from './debug-api';

// Default export combining all services
export default {
  api: apiService,
  config: configService,
  session: sessionService,
  chat: chatService,
  history: historyService,
  debug: debugService,
};