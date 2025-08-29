/**
 * React Context for Agent C Realtime SDK
 * Provides access to the RealtimeClient instance throughout the React component tree
 */

import { createContext, useContext } from 'react';
import type { RealtimeClient } from '@agentc/realtime-core';

/**
 * Context value containing the RealtimeClient instance and related utilities
 */
export interface AgentCContextValue {
  /** The RealtimeClient instance */
  client: RealtimeClient | null;
  /** Whether the client is currently initializing */
  isInitializing: boolean;
  /** Any error that occurred during initialization */
  error: Error | null;
}

/**
 * React Context for providing RealtimeClient throughout the app
 */
export const AgentCContext = createContext<AgentCContextValue | undefined>(undefined);

/**
 * Custom hook to access the RealtimeClient from context
 * @throws Error if used outside of AgentCProvider
 */
export function useRealtimeClient(): RealtimeClient {
  const context = useContext(AgentCContext);
  
  if (!context) {
    throw new Error(
      'useRealtimeClient must be used within an AgentCProvider. ' +
      'Please wrap your application with <AgentCProvider> at the root level.'
    );
  }
  
  if (context.error) {
    throw context.error;
  }
  
  if (context.isInitializing) {
    throw new Error(
      'RealtimeClient is still initializing. Please wait for initialization to complete.'
    );
  }
  
  if (!context.client) {
    throw new Error(
      'RealtimeClient is not available. This may indicate a configuration error.'
    );
  }
  
  return context.client;
}

/**
 * Custom hook to access the full context value
 * Useful for checking initialization state or errors
 */
export function useAgentCContext(): AgentCContextValue {
  const context = useContext(AgentCContext);
  
  if (!context) {
    throw new Error(
      'useAgentCContext must be used within an AgentCProvider. ' +
      'Please wrap your application with <AgentCProvider> at the root level.'
    );
  }
  
  return context;
}

/**
 * Custom hook to safely access the RealtimeClient or null
 * Does not throw if client is not available
 */
export function useRealtimeClientSafe(): RealtimeClient | null {
  const context = useContext(AgentCContext);
  
  if (!context) {
    return null;
  }
  
  return context.client;
}