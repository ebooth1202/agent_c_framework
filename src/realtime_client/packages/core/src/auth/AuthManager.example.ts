/**
 * Example usage of AuthManager.initializeFromPayload
 * 
 * This demonstrates how production apps can initialize the SDK
 * with a complete login payload from their backend.
 */

import { AuthManager } from './AuthManager';
import { LoginResponse } from '../events/types/CommonTypes';

// Example 1: Traditional login flow (existing functionality)
async function traditionalLogin() {
  const authManager = new AuthManager({
    apiUrl: 'https://api.example.com',
    autoRefresh: true,
  });

  // Login with credentials
  await authManager.login({
    username: 'user@example.com',
    password: 'password123',
  });

  // Access resources
  // const agents = authManager.getAgents();
  // const voices = authManager.getVoices();
  // const token = authManager.getAgentCToken();
}

// Example 2: Initialize from backend payload (NEW METHOD)
async function initializeFromBackend() {
  const authManager = new AuthManager({
    apiUrl: 'https://api.example.com',
    autoRefresh: true,
  });

  // Your backend provides the complete login payload
  // This might come from your own authentication service
  const payloadFromBackend: LoginResponse = {
    agent_c_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    heygen_token: 'hg_token_123...',
    user: {
      user_id: 'user123',
      user_name: 'user@example.com',
      email: 'user@example.com',
      first_name: 'John',
      last_name: 'Doe',
      is_active: true,
      roles: ['user'],
      groups: [],
      created_at: '2024-01-01T00:00:00Z',
      last_login: '2024-01-01T00:00:00Z',
    },
    agents: [
      {
        key: 'agent1',
        name: 'Assistant',
        agent_description: 'AI Assistant',
        category: ['assistant'],
      },
    ],
    avatars: [
      {
        avatar_id: 'avatar1',
        created_at: 1704067200,
        default_voice: 'en-US-1',
        is_public: false,
        normal_preview: 'https://example.com/avatar.jpg',
        pose_name: 'default',
        status: 'active',
      },
    ],
    voices: [
      {
        voice_id: 'voice1',
        vendor: 'openai',
        description: 'Alloy voice',
        output_format: 'pcm16',
      },
    ],
    toolsets: [
      {
        name: 'Default Tools',
        description: 'Standard toolset',
        schemas: {},
      },
    ],
    ui_session_id: 'session_abc123',
  };

  // WebSocket URL (might also come from your backend)
  const wsUrl = 'wss://api.example.com/rt/ws';

  // Initialize with the complete payload
  await authManager.initializeFromPayload(payloadFromBackend, wsUrl);

  // Now you can access all resources immediately
  const agents = authManager.getAgents();
  const voices = authManager.getVoices();
  // const avatars = authManager.getAvatars();
  // const toolsets = authManager.getToolsets();
  // const token = authManager.getAgentCToken();
  // const heygenToken = authManager.getHeygenToken();
  const user = authManager.getUser();
  // const sessionId = authManager.getUiSessionId();

  // AuthManager is fully initialized and ready to use
  console.log('Authenticated user:', user?.user_name);
  console.log('Available agents:', agents.length);
  console.log('Available voices:', voices.length);
  
  // The auth tokens will auto-refresh if autoRefresh is enabled
  // The authManager will emit the same events as if you had logged in normally
}

// Example 3: Using with RealtimeClient
async function useWithRealtimeClient() {
  const authManager = new AuthManager({
    apiUrl: 'https://api.example.com',
    autoRefresh: true,
  });

  // Get payload from your backend
  const payload = await fetch('/api/agent-c-auth')
    .then(r => r.json());
    
  const wsUrl = 'wss://api.example.com/rt/ws';

  // Initialize AuthManager
  await authManager.initializeFromPayload(payload, wsUrl);

  // Now create RealtimeClient with the initialized AuthManager
  // (RealtimeClient implementation would use authManager.getAgentCToken())
  // const client = new RealtimeClient({
  //   wsUrl,
  //   authManager,
  // });
}

export { traditionalLogin, initializeFromBackend, useWithRealtimeClient };