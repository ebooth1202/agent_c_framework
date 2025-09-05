/**
 * useAgentCData - React hook for accessing all WebSocket initialization data
 * 
 * This hook provides access to all configuration data received from the
 * 6 initialization events after WebSocket connection is established:
 * - chat_user_data (user profile)
 * - avatar_list (available avatars)
 * - voice_list (available voices)
 * - agent_list (available agents)
 * - tool_catalog (available toolsets)
 * - chat_session_changed (current session)
 */

import { useEffect, useState, useCallback } from 'react';
import { useRealtimeClientSafe } from '../providers/AgentCContext';
import type { User, Agent, AgentConfiguration, Voice, Avatar, Toolset } from '@agentc/realtime-core';

/**
 * All configuration data from WebSocket initialization
 */
export interface AgentCData {
  /** Current user data */
  user: User | null;
  
  /** Available voices for text-to-speech */
  voices: Voice[];
  
  /** Available AI agents */
  agents: Agent[];
  
  /** Current agent configuration from active session */
  currentAgentConfig: AgentConfiguration | null;
  
  /** Available HeyGen avatars */
  avatars: Avatar[];
  
  /** Available tool sets */
  toolsets: Toolset[];
}

/**
 * Return type for the useAgentCData hook
 */
export interface UseAgentCDataReturn {
  /** All configuration data */
  data: AgentCData;
  
  /** Whether initialization is still loading */
  isLoading: boolean;
  
  /** Whether initialization has completed */
  isInitialized: boolean;
  
  /** Error if initialization failed */
  error: string | null;
  
  /** Refresh the data from client */
  refresh: () => void;
}

/**
 * React hook for accessing all WebSocket initialization data
 * 
 * This hook waits for all 6 initialization events to complete before
 * marking as initialized. The data will update automatically as events
 * are received from the server.
 * 
 * @example
 * ```tsx
 * function ConfigurationDisplay() {
 *   const { data, isLoading, isInitialized } = useAgentCData();
 *   
 *   if (isLoading) return <div>Loading configuration...</div>;
 *   if (!isInitialized) return <div>Waiting for initialization...</div>;
 *   
 *   return (
 *     <div>
 *       <h2>Welcome {data.user?.user_name}</h2>
 *       <p>Available agents: {data.agents.length}</p>
 *       <p>Available voices: {data.voices.length}</p>
 *       <p>Available avatars: {data.avatars.length}</p>
 *       <p>Available toolsets: {data.toolsets.length}</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useAgentCData(): UseAgentCDataReturn {
  const client = useRealtimeClientSafe();
  
  // Initialize with empty data
  const [data, setData] = useState<AgentCData>({
    user: null,
    voices: [],
    agents: [],
    currentAgentConfig: null,
    avatars: [],
    toolsets: []
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Update all data from client
  const updateData = useCallback(() => {
    if (!client) {
      setData({
        user: null,
        voices: [],
        agents: [],
        currentAgentConfig: null,
        avatars: [],
        toolsets: []
      });
      setIsLoading(false);
      setIsInitialized(false);
      setError('Client not available');
      return;
    }
    
    try {
      // Get all data from client
      const newData: AgentCData = {
        user: client.getUserData(),
        voices: client.getVoicesList(),
        agents: client.getAgentsList(),
        currentAgentConfig: client.getCurrentAgentConfig(),
        avatars: client.getAvailableAvatars(),
        toolsets: client.getToolsets()
      };
      
      setData(newData);
      setError(null);
      
      // Check if fully initialized
      const initialized = client.isFullyInitialized();
      setIsInitialized(initialized);
      
      // If connected but not initialized, we're still loading
      if (client.isConnected() && !initialized) {
        setIsLoading(true);
      } else {
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Failed to get Agent C data:', err);
      setError(err instanceof Error ? err.message : 'Failed to get data');
      setIsLoading(false);
    }
  }, [client]);
  
  // Subscribe to initialization events
  useEffect(() => {
    if (!client) {
      setIsLoading(false);
      return;
    }
    
    // Initial update
    updateData();
    
    // Handle individual data events
    const handleUserData = (event: any) => {
      if (event.user) {
        setData(prev => ({ ...prev, user: event.user }));
      }
    };
    
    const handleAvatarList = (event: any) => {
      if (event.avatars) {
        setData(prev => ({ ...prev, avatars: event.avatars }));
      }
    };
    
    const handleVoiceList = (event: any) => {
      if (event.voices) {
        setData(prev => ({ ...prev, voices: event.voices }));
      }
    };
    
    const handleAgentList = (event: any) => {
      if (event.agents) {
        setData(prev => ({ ...prev, agents: event.agents }));
      }
    };
    
    const handleToolCatalog = (event: any) => {
      if (event.toolsets) {
        setData(prev => ({ ...prev, toolsets: event.toolsets }));
      }
    };
    
    // Handle session changes which include agent configuration
    const handleSessionChanged = (event: any) => {
      if (event.chat_session?.agent_config) {
        setData(prev => ({ ...prev, currentAgentConfig: event.chat_session.agent_config }));
      }
    };
    
    // Handle agent configuration changes
    const handleAgentConfigChanged = (event: any) => {
      if (event.agent_config) {
        setData(prev => ({ ...prev, currentAgentConfig: event.agent_config }));
      }
    };
    
    // Handle initialization complete event
    const handleInitialized = () => {
      // When initialization completes, do a final update
      updateData();
      setIsInitialized(true);
      setIsLoading(false);
    };
    
    // Handle connection events
    const handleConnect = () => {
      // When connected, initialization will start
      setIsLoading(true);
      setError(null);
    };
    
    const handleDisconnect = () => {
      // Keep existing data on disconnect but mark as not loading
      setIsLoading(false);
    };
    
    const handleError = (event: any) => {
      const errorMessage = event?.error?.message || event?.message || 'An error occurred';
      setError(errorMessage);
      setIsLoading(false);
    };
    
    // Subscribe to all events
    client.on('chat_user_data', handleUserData);
    client.on('avatar_list', handleAvatarList);
    client.on('voice_list', handleVoiceList);
    client.on('agent_list', handleAgentList);
    client.on('tool_catalog', handleToolCatalog);
    client.on('chat_session_changed', handleSessionChanged);
    client.on('agent_configuration_changed', handleAgentConfigChanged);
    client.on('initialized' as any, handleInitialized);
    client.on('connected', handleConnect);
    client.on('disconnected', handleDisconnect);
    client.on('error', handleError);
    
    return () => {
      client.off('chat_user_data', handleUserData);
      client.off('avatar_list', handleAvatarList);
      client.off('voice_list', handleVoiceList);
      client.off('agent_list', handleAgentList);
      client.off('tool_catalog', handleToolCatalog);
      client.off('chat_session_changed', handleSessionChanged);
      client.off('agent_configuration_changed', handleAgentConfigChanged);
      client.off('initialized' as any, handleInitialized);
      client.off('connected', handleConnect);
      client.off('disconnected', handleDisconnect);
      client.off('error', handleError);
    };
  }, [client, updateData]);
  
  return {
    data,
    isLoading,
    isInitialized,
    error,
    refresh: updateData
  };
}

// Re-export types for convenience
export type { User, Agent, AgentConfiguration, Voice, Avatar, Toolset };