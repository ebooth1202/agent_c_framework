/**
 * Test Utilities Export
 * Central export for all test utilities, mocks, and factories
 */

// WebSocket Mocks
export {
  MockWebSocket,
  mockWebSocketConstructor,
  WebSocketMock,
  createMockWebSocket,
  setupWebSocketMock
} from './mocks/mock-websocket';

// Audio Mocks
export {
  MockAudioContext,
  MockAudioBuffer,
  MockMediaStream,
  MockMediaStreamTrack,
  MockMediaRecorder,
  mockGetUserMedia,
  setupAudioMocks
} from './mocks/audio-mocks';

// Test Helpers
export {
  sleep,
  waitFor,
  nextTick,
  createMockAgentCEvent,
  createMockAudioBuffer,
  createDeferred,
  MockTimers,
  spyOnConsole,
  createMockEventEmitter
} from './utils/test-helpers';

// Realtime Test Utils
export {
  defaultTestConfig,
  createMockRealtimeClient,
  waitForSocketConnection,
  simulateTurnSequence,
  TestResponseBuilder,
  createMockSessionManager,
  createMockTurnManager,
  createMockAuthManager,
  RealtimeTestHarness
} from './utils/realtime-test-utils';

// Message Factories
export {
  ChatMessageFactory,
  SystemEventFactory,
  ErrorResponseFactory,
  TurnEventFactory,
  ToolCallFactory,
  ToolResponseFactory,
  AudioEventFactory,
  ConnectionEventFactory
} from './factories/message-factory';

// Re-export message factory types
export type {
  ChatMessage,
  SystemEvent,
  ErrorResponse,
  TurnEvent,
  ToolCall,
  ToolResponse,
  AudioEvent,
  ConnectionEvent
} from './factories/message-factory';

// MSW utilities
export {
  DELAYS,
  STATUS,
  successResponse,
  errorResponse,
  networkErrorHandler,
  timeoutHandler,
  paginatedResponse,
  authenticatedHandler,
  createCRUDHandlers,
  RequestTracker,
  createFileHandlers,
  createHandlersFromConfig
} from './utils/msw-utils';

// MSW handlers and server
export { handlers, authHandlers, sessionHandlers, userHandlers, errorHandlers, scenarioHandlers } from './mocks/handlers';
export { server, serverLifecycle, useHandlers, replaceAllHandlers, waitForRequest, expectRequest } from './mocks/server';