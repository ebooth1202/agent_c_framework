'use client';

import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { RealtimeClient, type RealtimeClientConfig } from '@agentc/realtime-core';
import { AgentCProvider } from '@agentc/realtime-react';
import { useAuth } from '@/contexts/auth-context';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';

/**
 * Client provider props
 */
export interface ClientProviderProps {
  children: React.ReactNode;
  apiUrl?: string;
  enableAudio?: boolean;
  enableTurnManagement?: boolean;
  respectTurnState?: boolean;
}

/**
 * Client provider component
 * Initializes the RealtimeClient with auth tokens and manages SDK lifecycle
 */
export function ClientProvider({ 
  children, 
  apiUrl,
  enableAudio = true,
  enableTurnManagement = true,
  respectTurnState = true
}: ClientProviderProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, getAuthToken, getUiSessionId, loginResponse } = useAuth();
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<RealtimeClient | null>(null);
  const initializationRef = useRef(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Create client configuration
  const clientConfig = useMemo<RealtimeClientConfig | null>(() => {
    const token = getAuthToken();
    const uiSessionId = getUiSessionId();
    
    if (!token || !uiSessionId) {
      return null;
    }

    const baseUrl = apiUrl || process.env.NEXT_PUBLIC_AGENTC_API_URL || 'wss://agent-c-prod.censius.ai';
    
    return {
      apiUrl: baseUrl,
      authToken: token,
      ui_session_id: uiSessionId,
      enableAudio,
      enableTurnManagement,
      respectTurnState,
      
      // Additional configuration from login response
      voices: loginResponse?.voices,
      avatars: loginResponse?.avatars,
      
      // Connection settings
      reconnection: {
        enabled: true,
        maxAttempts: 5,
        initialDelay: 1000,
        maxDelay: 30000,
        backoffMultiplier: 1.5
      },
      
      // Audio settings
      audioConfig: {
        sampleRate: 24000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    };
  }, [
    getAuthToken,
    getUiSessionId,
    loginResponse,
    apiUrl,
    enableAudio,
    enableTurnManagement,
    respectTurnState
  ]);

  // Initialize client
  useEffect(() => {
    // Skip if already initialized or no config
    if (initializationRef.current || !clientConfig) {
      return;
    }

    const initializeClient = async () => {
      try {
        setIsInitializing(true);
        setError(null);
        
        // Create and connect client
        const client = new RealtimeClient(clientConfig);
        clientRef.current = client;
        
        // Connect to the WebSocket
        await client.connect();
        
        initializationRef.current = true;
        setIsInitializing(false);
      } catch (err) {
        console.error('Failed to initialize RealtimeClient:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize client');
        setIsInitializing(false);
      }
    };

    initializeClient();

    // Cleanup on unmount
    return () => {
      if (clientRef.current) {
        if (clientRef.current.isConnected()) {
          clientRef.current.disconnect();
        }
        clientRef.current.destroy();
        clientRef.current = null;
      }
      initializationRef.current = false;
    };
  }, [clientConfig]);

  // Show loading state
  if (authLoading || isInitializing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-36" />
        </div>
        <p className="text-sm text-muted-foreground">
          {authLoading ? 'Checking authentication...' : 'Initializing chat client...'}
        </p>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>
            <strong>Connection Error:</strong> {error}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  // Don't render until client config is ready
  if (!clientConfig) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-sm text-muted-foreground">
          Waiting for authentication...
        </p>
      </div>
    );
  }

  // Render with AgentCProvider
  return (
    <AgentCProvider config={clientConfig}>
      {children}
    </AgentCProvider>
  );
}