/**
 * React Provider Component for Agent C Realtime SDK
 * Manages the lifecycle of the RealtimeClient instance
 */

import React, { useEffect, useState, useRef, useMemo } from 'react';
import { 
  RealtimeClient, 
  RealtimeClientConfig,
  AuthManager
} from '@agentc/realtime-core';
import { AgentCContext, AgentCContextValue } from './AgentCContext';

/**
 * Configuration props for the AgentCProvider
 */
export interface AgentCProviderProps {
  /** Child components that will have access to the RealtimeClient */
  children: React.ReactNode;
  
  /** WebSocket API URL (e.g., wss://api.example.com/rt/ws) */
  apiUrl?: string;
  
  /** JWT authentication token */
  authToken?: string;
  
  /** Optional AuthManager instance for automatic token management */
  authManager?: AuthManager;
  
  /** Complete configuration object (overrides individual props) */
  config?: RealtimeClientConfig;
  
  /** Whether to automatically connect on mount (default: false) */
  autoConnect?: boolean;
  
  /** Callback when client is successfully initialized */
  onInitialized?: (client: RealtimeClient) => void;
  
  /** Callback when initialization fails */
  onError?: (error: Error) => void;
  
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Provider component that creates and manages a singleton RealtimeClient instance
 */
export function AgentCProvider({
  children,
  apiUrl,
  authToken,
  authManager,
  config,
  autoConnect = false,
  onInitialized,
  onError,
  debug = false
}: AgentCProviderProps): React.ReactElement {
  const [client, setClient] = useState<RealtimeClient | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Use ref to track if we've already initialized to prevent double initialization in StrictMode
  const initializationRef = useRef(false);
  const clientRef = useRef<RealtimeClient | null>(null);
  
  // Build configuration from props or use provided config
  const clientConfig = useMemo((): RealtimeClientConfig | null => {
    // If full config is provided, use it directly
    if (config) {
      return config;
    }
    
    // Build config from individual props
    if (!apiUrl) {
      // Try to get from environment variable
      const envApiUrl = process.env.REACT_APP_AGENTC_API_URL || 
                        process.env.NEXT_PUBLIC_AGENTC_API_URL;
      
      if (!envApiUrl) {
        console.error('AgentCProvider: apiUrl is required. Provide it as a prop or set REACT_APP_AGENTC_API_URL environment variable.');
        return null;
      }
      
      return {
        apiUrl: envApiUrl,
        authToken,
        authManager,
        debug,
        autoReconnect: true,
        enableAudio: false // Audio requires explicit opt-in
      };
    }
    
    return {
      apiUrl,
      authToken,
      authManager,
      debug,
      autoReconnect: true,
      enableAudio: false // Audio requires explicit opt-in
    };
  }, [apiUrl, authToken, authManager, config, debug]);
  
  // Initialize the client
  useEffect(() => {
    // Prevent double initialization in React StrictMode
    if (initializationRef.current) {
      return;
    }
    
    if (!clientConfig) {
      const error = new Error('Invalid configuration: Missing required parameters');
      setError(error);
      setIsInitializing(false);
      onError?.(error);
      return;
    }
    
    initializationRef.current = true;
    
    try {
      if (debug) {
        console.log('AgentCProvider: Initializing RealtimeClient with config:', {
          ...clientConfig,
          authToken: clientConfig.authToken ? '[REDACTED]' : undefined
        });
      }
      
      const newClient = new RealtimeClient(clientConfig);
      clientRef.current = newClient;
      
      // Set up connection state listener for debugging
      if (debug) {
        newClient.on('connected', () => {
          console.log('AgentCProvider: Client connected');
        });
        
        newClient.on('disconnected', ({ code, reason }) => {
          console.log('AgentCProvider: Client disconnected', { code, reason });
        });
        
        newClient.on('error', (error) => {
          console.error('AgentCProvider: Client error', error);
        });
      }
      
      setClient(newClient);
      setIsInitializing(false);
      setError(null);
      
      onInitialized?.(newClient);
      
      // Auto-connect if requested
      if (autoConnect) {
        newClient.connect().catch((err) => {
          console.error('AgentCProvider: Auto-connect failed', err);
          const connectError = new Error(`Failed to auto-connect: ${err.message}`);
          setError(connectError);
          onError?.(connectError);
        });
      }
    } catch (err) {
      const initError = err instanceof Error ? err : new Error('Failed to initialize RealtimeClient');
      console.error('AgentCProvider: Initialization failed', initError);
      setError(initError);
      setIsInitializing(false);
      onError?.(initError);
      initializationRef.current = false;
    }
    
    // Cleanup function
    return () => {
      if (clientRef.current) {
        if (debug) {
          console.log('AgentCProvider: Cleaning up RealtimeClient');
        }
        
        // Disconnect if connected
        if (clientRef.current.isConnected()) {
          clientRef.current.disconnect();
        }
        
        // Destroy the client to clean up all resources
        clientRef.current.destroy();
        clientRef.current = null;
      }
      
      // Reset initialization flag for potential re-mount
      initializationRef.current = false;
    };
  }, [clientConfig, autoConnect, onInitialized, onError, debug]);
  
  // Update auth token if it changes
  useEffect(() => {
    if (client && authToken && !authManager) {
      // Only update token if not using AuthManager (which handles its own tokens)
      client.setAuthToken(authToken);
      
      if (debug) {
        console.log('AgentCProvider: Auth token updated');
      }
    }
  }, [client, authToken, authManager, debug]);
  
  // Update auth manager if it changes
  useEffect(() => {
    if (client && authManager) {
      client.setAuthManager(authManager);
      
      if (debug) {
        console.log('AgentCProvider: AuthManager updated');
      }
    }
  }, [client, authManager, debug]);
  
  // Context value
  const contextValue = useMemo<AgentCContextValue>(() => ({
    client,
    isInitializing,
    error
  }), [client, isInitializing, error]);
  
  return (
    <AgentCContext.Provider value={contextValue}>
      {children}
    </AgentCContext.Provider>
  );
}

/**
 * HOC to wrap a component with AgentCProvider
 * Useful for quick setup in examples or tests
 */
export function withAgentCProvider<P extends object>(
  Component: React.ComponentType<P>,
  providerProps: Omit<AgentCProviderProps, 'children'>
): React.ComponentType<P> {
  return function WrappedComponent(props: P) {
    return (
      <AgentCProvider {...providerProps}>
        <Component {...props} />
      </AgentCProvider>
    );
  };
}