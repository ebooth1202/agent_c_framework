/**
 * React Provider Component for Agent C Realtime SDK
 * Manages the lifecycle of the RealtimeClient instance
 */

import React, { useEffect, useState, useRef, useMemo } from 'react';
import { 
  RealtimeClient, 
  RealtimeClientConfig,
  AuthManager,
  ChatUserDataEvent,
  AgentListEvent,
  AvatarListEvent,
  VoiceListEvent,
  ToolCatalogEvent,
  ChatSessionChangedEvent,
  ErrorEvent
} from '@agentc/realtime-core';
import { AgentCContext, AgentCContextValue, InitializationState } from './AgentCContext';

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
  
  /** Callback when all initialization events have been received */
  onInitializationComplete?: (data: InitializationState) => void;
  
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
  onInitializationComplete,
  onError,
  debug = false
}: AgentCProviderProps): React.ReactElement {
  const [client, setClient] = useState<RealtimeClient | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Initialization state tracking
  const [initialization, setInitialization] = useState<InitializationState>({
    isInitialized: false,
    receivedEvents: new Set<string>(),
    user: null,
    agents: [],
    avatars: [],
    voices: [],
    tools: [],
    currentSession: null
  });
  
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
        console.warn('AgentCProvider: Initializing RealtimeClient with config:', {
          ...clientConfig,
          authToken: clientConfig.authToken ? '[REDACTED]' : undefined
        });
      }
      
      const newClient = new RealtimeClient(clientConfig);
      clientRef.current = newClient;
      
      // Set up initialization event listeners
      const requiredInitEvents = new Set([
        'chat_user_data',
        'avatar_list',
        'voice_list',
        'agent_list',
        'tool_catalog',
        'chat_session_changed'
      ]);
      
      const updateInitialization = (eventType: string, data: any) => {
        setInitialization(prev => {
          const newState = { ...prev };
          const newReceivedEvents = new Set(prev.receivedEvents);
          newReceivedEvents.add(eventType);
          
          // Update specific data based on event type
          switch (eventType) {
            case 'chat_user_data':
              newState.user = data.user;
              break;
            case 'agent_list':
              newState.agents = data.agents;
              break;
            case 'avatar_list':
              newState.avatars = data.avatars;
              break;
            case 'voice_list':
              newState.voices = data.voices;
              break;
            case 'tool_catalog':
              newState.tools = data.tools;
              break;
            case 'chat_session_changed':
              newState.currentSession = data.chat_session;
              break;
          }
          
          newState.receivedEvents = newReceivedEvents;
          
          // Check if all required events have been received
          const allReceived = Array.from(requiredInitEvents).every(
            event => newReceivedEvents.has(event)
          );
          newState.isInitialized = allReceived;
          
          if (allReceived && !prev.isInitialized) {
            if (debug) {
              console.warn('AgentCProvider: All initialization events received');
            }
            // Invoke callback when initialization is complete
            if (onInitializationComplete) {
              onInitializationComplete(newState);
            }
          }
          
          return newState;
        });
      };
      
      // Listen for initialization events
      newClient.on('chat_user_data', (data: ChatUserDataEvent) => {
        if (debug) console.warn('AgentCProvider: Received chat_user_data event');
        updateInitialization('chat_user_data', data);
      });
      
      newClient.on('agent_list', (data: AgentListEvent) => {
        if (debug) console.warn('AgentCProvider: Received agent_list event');
        updateInitialization('agent_list', data);
      });
      
      newClient.on('avatar_list', (data: AvatarListEvent) => {
        if (debug) console.warn('AgentCProvider: Received avatar_list event');
        updateInitialization('avatar_list', data);
      });
      
      newClient.on('voice_list', (data: VoiceListEvent) => {
        if (debug) console.warn('AgentCProvider: Received voice_list event');
        updateInitialization('voice_list', data);
      });
      
      newClient.on('tool_catalog', (data: ToolCatalogEvent) => {
        if (debug) console.warn('AgentCProvider: Received tool_catalog event');
        updateInitialization('tool_catalog', data);
      });
      
      newClient.on('chat_session_changed', (data: ChatSessionChangedEvent) => {
        if (debug) console.warn('AgentCProvider: Received chat_session_changed event');
        updateInitialization('chat_session_changed', data);
      });
      
      // Set up connection state listener for debugging
      if (debug) {
        newClient.on('connected', () => {
          console.warn('AgentCProvider: Client connected');
        });
        
        newClient.on('disconnected', ({ code, reason }: { code: number; reason: string }) => {
          console.warn('AgentCProvider: Client disconnected', { code, reason });
        });
        
        newClient.on('error', (error: ErrorEvent) => {
          console.error('AgentCProvider: Client error', error);
        });
      }
      
      setClient(newClient);
      setIsInitializing(false);
      setError(null);
      
      onInitialized?.(newClient);
      
      // Auto-connect if requested
      if (autoConnect) {
        newClient.connect().catch((err: Error) => {
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
          // console.log('AgentCProvider: Cleaning up RealtimeClient');
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
  }, [clientConfig, autoConnect, onInitialized, onInitializationComplete, onError, debug]);
  
  // Update auth token if it changes
  useEffect(() => {
    if (client && authToken && !authManager) {
      // Only update token if not using AuthManager (which handles its own tokens)
      client.setAuthToken(authToken);
      
      if (debug) {
        // console.log('AgentCProvider: Auth token updated');
      }
    }
  }, [client, authToken, authManager, debug]);
  
  // Update auth manager if it changes
  useEffect(() => {
    if (client && authManager) {
      client.setAuthManager(authManager);
      
      if (debug) {
        // console.log('AgentCProvider: AuthManager updated');
      }
    }
  }, [client, authManager, debug]);
  
  // Context value
  const contextValue = useMemo<AgentCContextValue>(() => ({
    client,
    isInitializing,
    error,
    initialization
  }), [client, isInitializing, error, initialization]);
  
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