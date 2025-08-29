/**
 * Configuration types and defaults for the Realtime Client
 */

import type { AuthManager } from '../auth';

/**
 * Connection state enum representing the WebSocket connection lifecycle
 */
export enum ConnectionState {
  /** Not connected to the server */
  DISCONNECTED = 'DISCONNECTED',
  /** Attempting to establish connection */
  CONNECTING = 'CONNECTING',
  /** Successfully connected to the server */
  CONNECTED = 'CONNECTED',
  /** Connection lost, attempting to reconnect */
  RECONNECTING = 'RECONNECTING'
}

/**
 * Configuration for reconnection behavior
 */
export interface ReconnectionConfig {
  /** Whether to automatically reconnect on disconnect */
  enabled: boolean;
  /** Initial delay before first reconnection attempt (ms) */
  initialDelay: number;
  /** Maximum delay between reconnection attempts (ms) */
  maxDelay: number;
  /** Multiplier for exponential backoff */
  backoffMultiplier: number;
  /** Maximum number of reconnection attempts (0 = unlimited) */
  maxAttempts: number;
  /** Jitter factor to randomize delays (0-1) */
  jitterFactor: number;
}

/**
 * Configuration for the Realtime Client
 */
export interface RealtimeClientConfig {
  /** WebSocket API URL (e.g., wss://api.example.com/rt/ws) */
  apiUrl: string;
  
  /** JWT authentication token (optional if using AuthManager) */
  authToken?: string;
  
  /** Optional AuthManager instance for automatic token management */
  authManager?: AuthManager;
  
  /** Optional session ID to resume */
  sessionId?: string;
  
  /** Enable automatic reconnection on disconnect */
  autoReconnect?: boolean;
  
  /** Detailed reconnection configuration */
  reconnection?: Partial<ReconnectionConfig>;
  
  /** WebSocket connection timeout (ms) */
  connectionTimeout?: number;
  
  /** Ping interval to keep connection alive (ms) */
  pingInterval?: number;
  
  /** Pong timeout - close connection if no pong received (ms) */
  pongTimeout?: number;
  
  /** Maximum size for incoming messages (bytes) */
  maxMessageSize?: number;
  
  /** Enable debug logging */
  debug?: boolean;
  
  /** Custom headers for WebSocket connection */
  headers?: Record<string, string>;
  
  /** WebSocket protocols to use */
  protocols?: string[];
  
  /** Binary type for WebSocket ('blob' or 'arraybuffer') */
  binaryType?: 'blob' | 'arraybuffer';
  
  /** Enable turn management (default: true) */
  enableTurnManager?: boolean;
}

/**
 * Default reconnection configuration
 */
export const defaultReconnectionConfig: ReconnectionConfig = {
  enabled: true,
  initialDelay: 1000,      // 1 second
  maxDelay: 30000,         // 30 seconds
  backoffMultiplier: 1.5,  // 1.5x increase each attempt
  maxAttempts: 0,          // Unlimited attempts
  jitterFactor: 0.3        // 30% jitter
};

/**
 * Default client configuration
 */
export const defaultConfig: Partial<RealtimeClientConfig> = {
  autoReconnect: true,
  reconnection: defaultReconnectionConfig,
  connectionTimeout: 10000,  // 10 seconds
  pingInterval: 30000,       // 30 seconds
  pongTimeout: 10000,        // 10 seconds
  maxMessageSize: 10 * 1024 * 1024, // 10MB
  debug: false,
  binaryType: 'arraybuffer',
  enableTurnManager: true     // Enable turn management by default
};

/**
 * Merge user config with defaults
 */
export function mergeConfig(
  userConfig: RealtimeClientConfig
): Required<Omit<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'>> & 
  Pick<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'> {
  
  const config = {
    ...defaultConfig,
    ...userConfig
  } as RealtimeClientConfig;

  // Merge reconnection config - ensure it's always defined
  config.reconnection = {
    ...defaultReconnectionConfig,
    ...(userConfig.reconnection || {})
  };

  // Ensure required fields are present
  if (!config.apiUrl) {
    throw new Error('apiUrl is required in RealtimeClientConfig');
  }
  
  // Either authToken or authManager must be provided
  if (!config.authToken && !config.authManager) {
    throw new Error('Either authToken or authManager is required in RealtimeClientConfig');
  }

  return config as Required<Omit<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'>> & 
    Pick<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'>;
}