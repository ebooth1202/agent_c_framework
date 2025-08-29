/**
 * useConnection - React hook for connection management
 * Provides interface for monitoring and controlling WebSocket connection
 */

import { useEffect, useState, useCallback } from 'react';
import { ConnectionState } from '@agentc/realtime-core';
import { useRealtimeClientSafe, useAgentCContext } from '../providers/AgentCContext';

/**
 * Connection statistics
 */
export interface ConnectionStats {
  /** Number of connection attempts */
  connectionAttempts: number;
  
  /** Number of successful connections */
  successfulConnections: number;
  
  /** Number of failed connections */
  failedConnections: number;
  
  /** Last connection time */
  lastConnectedAt: Date | null;
  
  /** Last disconnection time */
  lastDisconnectedAt: Date | null;
  
  /** Current session duration in milliseconds */
  sessionDuration: number;
}

/**
 * Return type for the useConnection hook
 */
export interface UseConnectionReturn {
  /** Current connection state */
  connectionState: ConnectionState;
  
  /** Whether currently connected */
  isConnected: boolean;
  
  /** Whether currently connecting */
  isConnecting: boolean;
  
  /** Whether connection is closed */
  isDisconnected: boolean;
  
  /** Whether client is initializing */
  isInitializing: boolean;
  
  /** Connect to the server */
  connect: () => Promise<void>;
  
  /** Disconnect from the server */
  disconnect: () => void;
  
  /** Reconnect to the server */
  reconnect: () => Promise<void>;
  
  /** Connection error if any */
  error: Error | null;
  
  /** Connection statistics */
  stats: ConnectionStats;
  
  /** Whether auto-reconnect is enabled */
  autoReconnectEnabled: boolean;
  
  /** Current reconnect attempt number */
  reconnectAttempt: number;
  
  /** Maximum reconnect attempts */
  maxReconnectAttempts: number;
}

/**
 * React hook for connection management
 * Provides interface for monitoring and controlling WebSocket connection
 */
export function useConnection(): UseConnectionReturn {
  const client = useRealtimeClientSafe();
  const { isInitializing, error: contextError } = useAgentCContext();
  
  // State
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [error, setError] = useState<Error | null>(contextError);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [stats, setStats] = useState<ConnectionStats>({
    connectionAttempts: 0,
    successfulConnections: 0,
    failedConnections: 0,
    lastConnectedAt: null,
    lastDisconnectedAt: null,
    sessionDuration: 0
  });
  
  // Session duration tracking
  const [sessionStartTime, setSessionStartTime] = useState<number | null>(null);
  
  // Update connection state from client
  const updateConnectionState = useCallback(() => {
    if (!client) {
      setConnectionState(ConnectionState.DISCONNECTED);
      return;
    }
    
    const state = client.getConnectionState();
    setConnectionState(state);
  }, [client]);
  
  // Connect
  const connect = useCallback(async (): Promise<void> => {
    if (!client) {
      throw new Error('Client not available');
    }
    
    if (client.isConnected()) {
      console.warn('Already connected');
      return;
    }
    
    setError(null);
    setStats(prev => ({
      ...prev,
      connectionAttempts: prev.connectionAttempts + 1
    }));
    
    try {
      await client.connect();
      
      setStats(prev => ({
        ...prev,
        successfulConnections: prev.successfulConnections + 1,
        lastConnectedAt: new Date()
      }));
      
      setSessionStartTime(Date.now());
      setReconnectAttempt(0);
    } catch (err) {
      const connectionError = err instanceof Error ? err : new Error('Connection failed');
      setError(connectionError);
      
      setStats(prev => ({
        ...prev,
        failedConnections: prev.failedConnections + 1
      }));
      
      throw connectionError;
    }
  }, [client]);
  
  // Disconnect
  const disconnect = useCallback(() => {
    if (!client) {
      console.warn('Client not available');
      return;
    }
    
    client.disconnect();
    
    setStats(prev => ({
      ...prev,
      lastDisconnectedAt: new Date()
    }));
    
    setSessionStartTime(null);
  }, [client]);
  
  // Reconnect
  const reconnect = useCallback(async (): Promise<void> => {
    if (!client) {
      throw new Error('Client not available');
    }
    
    // Disconnect first if connected
    if (client.isConnected()) {
      client.disconnect();
    }
    
    // Wait a moment before reconnecting
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Connect again
    await connect();
  }, [client, connect]);
  
  // Subscribe to connection events
  useEffect(() => {
    if (!client) return;
    
    // Initial state update
    updateConnectionState();
    
    // Handle connection events
    const handleConnected = () => {
      setConnectionState(ConnectionState.CONNECTED);
      setError(null);
      setSessionStartTime(Date.now());
      
      setStats(prev => ({
        ...prev,
        lastConnectedAt: new Date()
      }));
    };
    
    const handleDisconnected = ({ code, reason }: { code: number; reason: string }) => {
      setConnectionState(ConnectionState.DISCONNECTED);
      setSessionStartTime(null);
      
      setStats(prev => ({
        ...prev,
        lastDisconnectedAt: new Date()
      }));
      
      // Set error if it was an unexpected disconnection
      if (code !== 1000) { // 1000 is normal closure
        setError(new Error(`Disconnected: ${reason} (code: ${code})`));
      }
    };
    
    const handleReconnecting = ({ attempt }: { attempt: number }) => {
      setConnectionState(ConnectionState.RECONNECTING);
      setReconnectAttempt(attempt);
    };
    
    const handleError = (error: any) => {
      const err = error instanceof Error ? error : new Error(error.message || 'Unknown error');
      setError(err);
      
      setStats(prev => ({
        ...prev,
        failedConnections: prev.failedConnections + 1
      }));
    };
    
    // Subscribe to events
    client.on('connected', handleConnected);
    client.on('disconnected', handleDisconnected);
    client.on('reconnecting', handleReconnecting);
    client.on('error', handleError);
    
    return () => {
      client.off('connected', handleConnected);
      client.off('disconnected', handleDisconnected);
      client.off('reconnecting', handleReconnecting);
      client.off('error', handleError);
    };
  }, [client, updateConnectionState]);
  
  // Update session duration
  useEffect(() => {
    if (!sessionStartTime) {
      return;
    }
    
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        sessionDuration: Date.now() - sessionStartTime
      }));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [sessionStartTime]);
  
  // Get configuration values - client doesn't expose getConfig, use defaults
  const autoReconnectEnabled = true; // Default from mergeConfig
  const maxReconnectAttempts = 5; // Default from ReconnectionConfig
  
  // Computed states
  const isConnected = connectionState === ConnectionState.CONNECTED;
  const isConnecting = connectionState === ConnectionState.CONNECTING;
  const isDisconnected = connectionState === ConnectionState.DISCONNECTED;
  
  return {
    connectionState,
    isConnected,
    isConnecting,
    isDisconnected,
    isInitializing,
    connect,
    disconnect,
    reconnect,
    error,
    stats,
    autoReconnectEnabled,
    reconnectAttempt,
    maxReconnectAttempts
  };
}