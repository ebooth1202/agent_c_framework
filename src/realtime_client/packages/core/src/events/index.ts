/**
 * Public exports for the Agent C Realtime SDK event system
 * This module provides all event-related types and utilities
 */

// Export common types
export * from './types/CommonTypes';

// Export client event types
export * from './types/ClientEvents';

// Export server event types  
export * from './types/ServerEvents';

// Export EventEmitter
export { EventEmitter, EventListener } from './EventEmitter';

// Export EventRegistry and type maps
export {
  EventRegistry,
  ClientEventMap,
  ServerEventMap,
  RealtimeEventMap,
  EventType,
  ClientEventType,
  ServerEventType,
  EventData
} from './EventRegistry';