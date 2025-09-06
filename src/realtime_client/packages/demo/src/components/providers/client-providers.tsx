"use client"

import React from 'react';
import { AgentCProvider } from '@agentc/realtime-react';
import { getToken } from '@/lib/auth';

interface ClientProvidersProps {
  children: React.ReactNode;
}

export default function ClientProviders({ children }: ClientProvidersProps) {
  const [authToken, setAuthToken] = React.useState<string | null>(null);
  
  React.useEffect(() => {
    // Get the auth token from cookies
    const token = getToken();
    console.log('🔐 Auth token for AgentC Provider:', token ? 'Found' : 'Not found');
    setAuthToken(token);
  }, []);
  
  // Don't render AgentCProvider until we have a token
  if (!authToken) {
    console.log('⏳ Waiting for auth token...');
    return <>{children}</>;
  }
  
  console.log('🚀 Initializing AgentCProvider with auth token');
  
  return (
    <AgentCProvider config={{
      websocketUrl: 'ws://localhost:8000/api/rt/ws',
      authToken: authToken,
      enableAudio: true,
      debug: true
    }}>
      {children}
    </AgentCProvider>
  );
}