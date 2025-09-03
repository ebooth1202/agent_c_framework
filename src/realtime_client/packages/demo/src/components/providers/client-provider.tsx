'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import type { RealtimeClientConfig } from '@agentc/realtime-core';
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
 * Configures and wraps AgentCProvider with auth tokens
 */
export function ClientProvider({ 
  children, 
  apiUrl,
  enableAudio = true,
  enableTurnManagement = true,
  respectTurnState = true
}: ClientProviderProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, getAuthToken, loginResponse } = useAuth();
  const [configReady, setConfigReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Create client configuration
  const clientConfig = useMemo<RealtimeClientConfig | null>(() => {
    const token = getAuthToken();
    
    if (!token) {
      return null;
    }

    const baseUrl = apiUrl || process.env.NEXT_PUBLIC_AGENTC_API_URL || 'wss://agent-c-prod.censius.ai';
    
    return {
      apiUrl: baseUrl,
      authToken: token,
      enableAudio,
      autoReconnect: true,
      
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
    loginResponse,
    apiUrl,
    enableAudio
  ]);

  // Mark config as ready when we have a valid config
  useEffect(() => {
    if (clientConfig && !authLoading) {
      setConfigReady(true);
    }
  }, [clientConfig, authLoading]);

  // Show loading state
  if (authLoading || !configReady) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-36" />
        </div>
        <p className="text-sm text-muted-foreground">
          {authLoading ? 'Checking authentication...' : 'Preparing chat client...'}
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

  // Render with AgentCProvider which will handle client creation and connection
  return (
    <AgentCProvider 
      config={clientConfig}
      autoConnect={true}
      debug={true}
    >
      {children}
    </AgentCProvider>
  );
}