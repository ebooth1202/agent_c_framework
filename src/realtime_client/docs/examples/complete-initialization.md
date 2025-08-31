# Complete SDK Initialization Guide - The FULL Picture

This guide shows you the **complete picture** of how to work with the Agent C login response payload and properly initialize the SDK. Most documentation skips over the details - this guide shows you **everything** that's available and how to use it all.

## What's REALLY in the Login Response

When you authenticate with Agent C (either directly in development or through your backend in production), you receive a comprehensive payload with **everything** needed to initialize the SDK. Here's what you're actually getting:

```typescript
// This is the COMPLETE login response structure
interface CompleteLoginResponse {
  // Authentication tokens
  agent_c_token: string;        // JWT for WebSocket authentication
  heygen_token: string;         // HeyGen access token for avatar creation
  
  // UI session for reconnection
  ui_session_id: string;        // Three-word slug like "tiger-castle-moon"
  
  // Complete user information
  user: {
    user_id: string;
    user_name: string;
    email: string | null;
    first_name: string | null;
    last_name: string | null;
    is_active: boolean;
    roles: string[];           // User's roles in the system
    groups: string[];          // User's group memberships
    created_at: string | null;
    last_login: string | null;
  };
  
  // Available agents for this user
  agents: Array<{
    name: string;              // Display name
    key: string;               // Unique identifier for API calls
    agent_description: string | null;
    category: string[];        // Agent categories/tags
  }>;
  
  // HeyGen avatars available
  avatars: Array<{
    avatar_id: string;         // HeyGen avatar ID
    created_at: number;        // Unix timestamp
    default_voice: string;     // Default voice for this avatar
    is_public: boolean;
    normal_preview: string;    // Preview image URL
    pose_name: string;
    status: string;
  }>;
  
  // Available toolsets with schemas
  toolsets: Array<{
    name: string;
    description: string;
    schemas: {
      [toolName: string]: {
        type: "function";
        function: {
          name: string;
          description: string;
          parameters: {
            type: "object";
            properties: Record<string, any>;
            required: string[];
          };
        };
      };
    };
  }>;
  
  // TTS voices with formats
  voices: Array<{
    voice_id: string;          // Unique identifier
    vendor: string;            // Provider (openai, heygen, system)
    description: string;       // Human-readable description
    output_format: string;     // Audio format (pcm16, none, special)
  }>;
}
```

### Important: WebSocket URL is NOT in the Response!

**Critical Detail**: The WebSocket URL is **NOT** included in the login response. You must construct it yourself:

```typescript
// The response does NOT include websocket_url
// You must build it from your API URL configuration
const wsUrl = `wss://${API_HOST}/rt/ws`;
```

## Complete Initialization Example - Using EVERYTHING

Here's how to properly initialize the SDK using **all** the data from the login response:

```typescript
import { 
  AuthManager, 
  RealtimeClient,
  VoiceManager,
  AvatarManager,
  SessionManager
} from '@agentc/realtime-core';

class CompleteSDKInitializer {
  private authManager: AuthManager;
  private client: RealtimeClient;
  private loginPayload: CompleteLoginResponse;
  
  /**
   * Initialize the SDK with the COMPLETE login payload
   * This shows how to use ALL the data, not just the token
   */
  async initializeWithFullPayload(loginResponse: CompleteLoginResponse) {
    // Store the complete payload for later use
    this.loginPayload = loginResponse;
    
    // 1. Initialize AuthManager with configuration
    this.authManager = new AuthManager({
      apiUrl: 'https://api.agentc.example.com',  // Your API base URL
      autoRefresh: true,
      refreshBufferMs: 5 * 60 * 1000,  // Refresh 5 minutes before expiry
    });
    
    // 2. Store ALL the authentication data in AuthManager
    // The AuthManager stores the complete login response internally
    // This is done automatically by login(), but here's what happens:
    this.authManager['loginData'] = loginResponse;  // Internal storage
    
    // Parse JWT to get expiry
    const expiresAt = this.parseJWTExpiry(loginResponse.agent_c_token);
    
    // Set tokens with expiry
    await this.authManager.setTokens({
      agentCToken: loginResponse.agent_c_token,
      heygenToken: loginResponse.heygen_token,
      expiresAt: expiresAt
    });
    
    // Update AuthManager state with user info
    this.authManager['state'].user = loginResponse.user;
    this.authManager['state'].uiSessionId = loginResponse.ui_session_id;
    
    // 3. Construct the WebSocket URL (NOT in response!)
    const wsUrl = this.buildWebSocketUrl();
    
    // 4. Create RealtimeClient with AuthManager
    this.client = new RealtimeClient({
      apiUrl: wsUrl,
      authManager: this.authManager,
      sessionId: loginResponse.ui_session_id,  // Use for reconnection
      autoReconnect: true,
      enableTurnManager: true,
      enableAudio: true,
      audioConfig: {
        enableInput: true,
        enableOutput: true,
        respectTurnState: true,
        sampleRate: 16000,  // Match voice format requirements
      },
      debug: true  // See what's happening
    });
    
    // 5. Access ALL the resources through AuthManager
    this.demonstrateDataAccess();
    
    // 6. Initialize subsystems with the available data
    await this.initializeSubsystems();
    
    // 7. Connect to the WebSocket
    await this.client.connect();
    
    console.log('SDK fully initialized with ALL available data!');
  }
  
  /**
   * Build the WebSocket URL - NOT provided in response!
   */
  private buildWebSocketUrl(): string {
    // You must construct this yourself from your API configuration
    const apiHost = 'api.agentc.example.com';
    const wsProtocol = 'wss';  // Always use secure WebSocket
    
    // Build the base URL
    const wsUrl = `${wsProtocol}://${apiHost}/rt/ws`;
    
    // Token is added as query parameter by the client
    // Session ID is also added if available
    return wsUrl;
  }
  
  /**
   * Parse JWT to extract expiry time
   */
  private parseJWTExpiry(token: string): number {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }
    
    const payload = JSON.parse(
      atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
    );
    
    // Convert seconds to milliseconds
    return payload.exp * 1000;
  }
  
  /**
   * Demonstrate accessing ALL the data from the login response
   */
  private demonstrateDataAccess() {
    // Access user information
    const user = this.authManager.getUser();
    console.log('User:', {
      id: user?.user_id,
      name: user?.user_name,
      email: user?.email,
      roles: user?.roles,
      groups: user?.groups,
      lastLogin: user?.last_login
    });
    
    // Access available agents
    const agents = this.authManager.getAgents();
    console.log('Available Agents:', agents.map(a => ({
      name: a.name,
      key: a.key,
      description: a.agent_description,
      categories: a.category
    })));
    
    // Access available avatars
    const avatars = this.authManager.getAvatars();
    console.log('Available Avatars:', avatars.map(a => ({
      id: a.avatar_id,
      preview: a.normal_preview,
      defaultVoice: a.default_voice,
      status: a.status
    })));
    
    // Access available voices
    const voices = this.authManager.getVoices();
    console.log('Available Voices:', voices.map(v => ({
      id: v.voice_id,
      vendor: v.vendor,
      description: v.description,
      format: v.output_format
    })));
    
    // Access available toolsets
    const toolsets = this.authManager.getToolsets();
    console.log('Available Toolsets:', toolsets.map(t => ({
      name: t.name,
      description: t.description,
      tools: Object.keys(t.schemas)
    })));
    
    // Access tokens
    console.log('Tokens:', {
      agentCToken: this.authManager.getAgentCToken() ? 'Present' : 'Missing',
      heygenToken: this.authManager.getHeygenToken() ? 'Present' : 'Missing',
      uiSessionId: this.authManager.getUiSessionId()
    });
  }
  
  /**
   * Initialize all subsystems with the available data
   */
  private async initializeSubsystems() {
    // VoiceManager is automatically initialized by RealtimeClient
    // when AuthManager has voices, but here's how to access it:
    const voiceManager = this.client.getVoiceManager();
    if (voiceManager) {
      // Set default voice if available
      const voices = this.authManager.getVoices();
      const defaultVoice = voices.find(v => v.voice_id === 'nova');
      if (defaultVoice) {
        voiceManager.setCurrentVoice(defaultVoice.voice_id, 'client');
      }
      
      console.log('Voice Manager initialized with', voices.length, 'voices');
    }
    
    // AvatarManager is also auto-initialized
    const avatarManager = this.client.getAvatarManager();
    if (avatarManager) {
      const avatars = this.authManager.getAvatars();
      console.log('Avatar Manager initialized with', avatars.length, 'avatars');
    }
    
    // SessionManager for chat history
    const sessionManager = this.client.getSessionManager();
    if (sessionManager) {
      console.log('Session Manager ready for chat history management');
    }
    
    // TurnManager for conversation flow
    const turnManager = this.client.getTurnManager();
    if (turnManager) {
      console.log('Turn Manager ready for conversation control');
    }
  }
  
  /**
   * Use agents from the login response
   */
  async selectAndUseAgent() {
    const agents = this.authManager.getAgents();
    
    if (agents.length === 0) {
      console.error('No agents available for this user');
      return;
    }
    
    // Find a specific agent or use the first one
    const defaultAgent = agents.find(a => a.key === 'default_realtime') || agents[0];
    
    console.log('Selecting agent:', defaultAgent.name);
    
    // Set the agent on the connection
    this.client.setAgent(defaultAgent.key);
    
    // Create a new chat session with this agent
    this.client.newChatSession(defaultAgent.key);
  }
  
  /**
   * Use voices from the login response
   */
  async selectAndUseVoice() {
    const voices = this.authManager.getVoices();
    
    // Find specific voice types
    const textOnlyVoice = voices.find(v => v.voice_id === 'none');
    const avatarVoice = voices.find(v => v.voice_id === 'avatar');
    const ttsVoices = voices.filter(v => 
      v.voice_id !== 'none' && v.voice_id !== 'avatar'
    );
    
    console.log('Available voice modes:', {
      textOnly: !!textOnlyVoice,
      avatar: !!avatarVoice,
      ttsCount: ttsVoices.length
    });
    
    // Select a TTS voice
    const selectedVoice = ttsVoices.find(v => v.voice_id === 'nova') || ttsVoices[0];
    if (selectedVoice) {
      console.log('Setting voice:', selectedVoice.description);
      this.client.setAgentVoice(selectedVoice.voice_id);
      
      // Check the audio format for this voice
      console.log('Audio format:', selectedVoice.output_format);
      if (selectedVoice.output_format === 'pcm16') {
        console.log('Voice uses PCM16 format at 16kHz');
      }
    }
  }
  
  /**
   * Use avatars from the login response
   */
  async createAvatarSession() {
    const avatars = this.authManager.getAvatars();
    const heygenToken = this.authManager.getHeygenToken();
    
    if (avatars.length === 0 || !heygenToken) {
      console.error('No avatars available or missing HeyGen token');
      return;
    }
    
    const selectedAvatar = avatars[0];
    console.log('Creating avatar session with:', selectedAvatar.avatar_id);
    
    // This would integrate with HeyGen SDK
    // When avatar session is ready, notify Agent C:
    const avatarSessionId = 'heygen-session-uuid';
    this.client.setAvatarSession(avatarSessionId, selectedAvatar.avatar_id);
  }
  
  /**
   * Use toolsets information
   */
  displayAvailableTools() {
    const toolsets = this.authManager.getToolsets();
    
    console.log('Available Tools:');
    toolsets.forEach(toolset => {
      console.log(`\nToolset: ${toolset.name}`);
      console.log(`Description: ${toolset.description}`);
      
      Object.entries(toolset.schemas).forEach(([toolName, schema]) => {
        console.log(`  - ${toolName}: ${schema.function.description}`);
        
        // Display parameters
        const params = schema.function.parameters.properties;
        Object.entries(params).forEach(([paramName, paramDef]: [string, any]) => {
          const required = schema.function.parameters.required.includes(paramName);
          console.log(`    * ${paramName} (${paramDef.type}${required ? ', required' : ''}): ${paramDef.description}`);
        });
      });
    });
  }
}

// Example usage
async function main() {
  const initializer = new CompleteSDKInitializer();
  
  // In production, this comes from YOUR backend
  // In development, from direct Agent C login
  const loginResponse = await getLoginResponse();
  
  // Initialize with EVERYTHING
  await initializer.initializeWithFullPayload(loginResponse);
  
  // Now use all the capabilities
  await initializer.selectAndUseAgent();
  await initializer.selectAndUseVoice();
  initializer.displayAvailableTools();
}
```

## Production Pattern - Backend Provides Everything

In production, your backend fetches the login payload and passes it to the frontend:

### Backend - Fetching and Providing the Complete Payload

```typescript
// backend/services/agentc-auth.ts
export class AgentCAuthService {
  /**
   * Get complete Agent C configuration for a user
   * This runs on YOUR backend, not in the browser
   */
  async getCompleteAgentCPayload(userId: string): Promise<any> {
    // Your backend authenticates with Agent C
    const response = await fetch('https://api.agentc.example.com/rt/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        // These credentials NEVER leave your backend
        username: process.env.AGENTC_USERNAME,
        password: process.env.AGENTC_PASSWORD
      })
    });
    
    const loginData: CompleteLoginResponse = await response.json();
    
    // Add the WebSocket URL since it's not in the response
    const enhancedPayload = {
      ...loginData,
      websocket_url: `wss://${process.env.AGENTC_HOST}/rt/ws`,
      
      // Add any additional configuration
      api_host: process.env.AGENTC_HOST,
      api_protocol: 'https',
      
      // Add user context
      app_user: {
        id: userId,
        // ... other app user data
      }
    };
    
    return enhancedPayload;
  }
}

// backend/routes/auth.ts
app.post('/api/auth/initialize-agentc', authenticate, async (req, res) => {
  const userId = req.user.id;
  
  const agentCService = new AgentCAuthService();
  const payload = await agentCService.getCompleteAgentCPayload(userId);
  
  // Send EVERYTHING to the frontend
  res.json({
    agent_c: payload,
    // Include your app's data too
    app_config: {
      features: ['voice', 'avatar', 'chat'],
      theme: 'dark'
    }
  });
});
```

### Frontend - Using the Complete Payload

```typescript
// frontend/src/services/AgentCService.ts
export class AgentCProductionInitializer {
  private authManager: AuthManager;
  private client: RealtimeClient;
  
  /**
   * Initialize with the complete payload from YOUR backend
   * This is the production pattern - no direct Agent C auth
   */
  async initializeFromBackend() {
    // 1. Get the complete payload from YOUR backend
    const response = await fetch('/api/auth/initialize-agentc', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('app_token')}`
      }
    });
    
    const data = await response.json();
    const agentCPayload = data.agent_c;
    
    // 2. Create AuthManager with proper configuration
    this.authManager = new AuthManager({
      apiUrl: `https://${agentCPayload.api_host}`,
      autoRefresh: true,
      onTokensRefreshed: async (tokens) => {
        // Refresh through YOUR backend
        await this.refreshThroughBackend();
      }
    });
    
    // 3. Initialize AuthManager with ALL the data
    // Note: There's no initializeFromPayload method currently,
    // so we need to use the internal storage approach:
    
    // Store the complete login data
    this.authManager['loginData'] = agentCPayload;
    
    // Parse and set tokens
    const expiresAt = this.parseJWTExpiry(agentCPayload.agent_c_token);
    await this.authManager.setTokens({
      agentCToken: agentCPayload.agent_c_token,
      heygenToken: agentCPayload.heygen_token,
      expiresAt: expiresAt
    });
    
    // Update state with user and session info
    this.authManager['state'].user = agentCPayload.user;
    this.authManager['state'].uiSessionId = agentCPayload.ui_session_id;
    
    // 4. Create RealtimeClient with all features
    this.client = new RealtimeClient({
      apiUrl: agentCPayload.websocket_url,
      authManager: this.authManager,
      sessionId: agentCPayload.ui_session_id,
      autoReconnect: true,
      enableTurnManager: true,
      enableAudio: true,
      audioConfig: {
        enableInput: true,
        enableOutput: true,
        respectTurnState: true
      }
    });
    
    // 5. Connect with all subsystems initialized
    await this.client.connect();
    
    // 6. Now everything is available
    this.logAvailableResources();
  }
  
  /**
   * Log all available resources to show what we have
   */
  private logAvailableResources() {
    console.group('Agent C Resources Initialized');
    
    console.log('User:', this.authManager.getUser());
    console.log('Agents:', this.authManager.getAgents());
    console.log('Voices:', this.authManager.getVoices());
    console.log('Avatars:', this.authManager.getAvatars());
    console.log('Toolsets:', this.authManager.getToolsets());
    console.log('UI Session:', this.authManager.getUiSessionId());
    
    console.log('Subsystems:', {
      voiceManager: !!this.client.getVoiceManager(),
      avatarManager: !!this.client.getAvatarManager(),
      sessionManager: !!this.client.getSessionManager(),
      turnManager: !!this.client.getTurnManager()
    });
    
    console.groupEnd();
  }
  
  private parseJWTExpiry(token: string): number {
    const payload = JSON.parse(
      atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))
    );
    return payload.exp * 1000;
  }
  
  private async refreshThroughBackend() {
    const response = await fetch('/api/auth/refresh-agentc', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('app_token')}`
      }
    });
    
    const data = await response.json();
    
    // Update tokens in AuthManager
    await this.authManager.setTokens({
      agentCToken: data.agent_c_token,
      heygenToken: data.heygen_token,
      expiresAt: this.parseJWTExpiry(data.agent_c_token)
    });
  }
}
```

## Development Pattern - Direct Login

For development only, you can use direct login and still access everything:

```typescript
// development/dev-initializer.ts
export class DevelopmentInitializer {
  private authManager: AuthManager;
  private client: RealtimeClient;
  
  /**
   * Development only - direct login to Agent C
   * Shows how login() method populates everything
   */
  async initializeForDevelopment() {
    console.warn('⚠️ Using direct login - DEVELOPMENT ONLY!');
    
    // 1. Create AuthManager
    this.authManager = new AuthManager({
      apiUrl: 'https://localhost:8000',  // Local dev server
      autoRefresh: true
    });
    
    // 2. Direct login - this populates EVERYTHING
    const loginResponse = await this.authManager.login({
      username: process.env.DEV_USERNAME!,
      password: process.env.DEV_PASSWORD!
    });
    
    // The login() method automatically:
    // - Stores the complete response in loginData
    // - Parses and stores tokens with expiry
    // - Updates user and uiSessionId in state
    // - Schedules token refresh
    
    // 3. Create client - WebSocket URL must be constructed
    const wsUrl = 'wss://localhost:8000/rt/ws';
    
    this.client = new RealtimeClient({
      apiUrl: wsUrl,
      authManager: this.authManager,
      sessionId: loginResponse.ui_session_id,
      autoReconnect: true,
      enableTurnManager: true,
      enableAudio: true,
      audioConfig: {
        enableInput: true,
        enableOutput: true
      },
      debug: true  // See everything in development
    });
    
    // 4. Everything is now available through AuthManager
    console.log('Development initialization complete');
    console.log('Available resources:', {
      agents: this.authManager.getAgents().length,
      voices: this.authManager.getVoices().length,
      avatars: this.authManager.getAvatars().length,
      toolsets: this.authManager.getToolsets().length
    });
    
    // 5. Connect
    await this.client.connect();
  }
}
```

## Proposed SDK Enhancement - initializeFromPayload Method

The SDK should have a proper `initializeFromPayload` method to make this cleaner:

```typescript
// Proposed addition to AuthManager
export class AuthManager {
  /**
   * Initialize from a complete login payload (production pattern)
   * This should be added to the SDK for cleaner initialization
   */
  async initializeFromPayload(payload: CompleteLoginResponse & { websocket_url?: string }) {
    // Store the complete payload
    this.loginData = payload;
    
    // Parse JWT expiry
    const expiresAt = this.parseJWTExpiry(payload.agent_c_token);
    
    // Create and store token pair
    const tokens: TokenPair = {
      agentCToken: payload.agent_c_token,
      heygenToken: payload.heygen_token,
      expiresAt
    };
    
    await this.storage.setTokens(tokens);
    
    // Update state
    this.updateState({
      isAuthenticated: true,
      tokens,
      user: payload.user,
      uiSessionId: payload.ui_session_id,
      isAuthenticating: false,
    });
    
    // Schedule refresh if enabled
    if (this.config.autoRefresh) {
      this.scheduleTokenRefresh(tokens);
    }
    
    // Emit login event for subsystems
    this.emit('auth:login', payload);
    
    return payload;
  }
}
```

## Common Mistakes and How to Avoid Them

### Mistake 1: Only Using the Token

```typescript
// ❌ WRONG - Missing all the other data
const client = new RealtimeClient({
  apiUrl: 'wss://api.example.com/rt/ws',
  authToken: loginResponse.agent_c_token  // Just the token
});

// ✅ CORRECT - Use AuthManager with complete data
const authManager = new AuthManager({...});
// Store complete login response
authManager['loginData'] = loginResponse;
await authManager.setTokens({...});

const client = new RealtimeClient({
  apiUrl: wsUrl,
  authManager: authManager  // Has access to everything
});
```

### Mistake 2: Expecting WebSocket URL in Response

```typescript
// ❌ WRONG - There's no websocket_url in the response
const wsUrl = loginResponse.websocket_url;  // undefined!

// ✅ CORRECT - Build it yourself
const wsUrl = `wss://${API_HOST}/rt/ws`;
```

### Mistake 3: Not Using Available Resources

```typescript
// ❌ WRONG - Hardcoding when data is available
client.setAgent('default_agent');  // What if user doesn't have access?

// ✅ CORRECT - Use what's available
const agents = authManager.getAgents();
const defaultAgent = agents.find(a => a.key === 'default_agent') || agents[0];
if (defaultAgent) {
  client.setAgent(defaultAgent.key);
}
```

### Mistake 4: Ignoring Voice Formats

```typescript
// ❌ WRONG - Assuming all voices use same format
audioConfig: {
  sampleRate: 24000  // What if voice uses 16000?
}

// ✅ CORRECT - Check voice format
const voices = authManager.getVoices();
const selectedVoice = voices.find(v => v.voice_id === 'nova');
if (selectedVoice?.output_format === 'pcm16') {
  // PCM16 uses 16kHz
  audioConfig.sampleRate = 16000;
}
```

## Testing Your Implementation

Here's how to verify you're using everything correctly:

```typescript
function verifyCompleteInitialization(authManager: AuthManager, client: RealtimeClient) {
  const checks = {
    hasTokens: !!authManager.getAgentCToken(),
    hasHeyGenToken: !!authManager.getHeygenToken(),
    hasUser: !!authManager.getUser(),
    hasUISession: !!authManager.getUiSessionId(),
    hasAgents: authManager.getAgents().length > 0,
    hasVoices: authManager.getVoices().length > 0,
    hasAvatars: authManager.getAvatars().length > 0,
    hasToolsets: authManager.getToolsets().length > 0,
    
    // Subsystems initialized
    hasVoiceManager: !!client.getVoiceManager(),
    hasAvatarManager: !!client.getAvatarManager(),
    hasSessionManager: !!client.getSessionManager(),
    hasTurnManager: !!client.getTurnManager(),
    
    // Voice manager has voices
    voiceManagerInitialized: client.getVoiceManager()?.getAvailableVoices().length > 0
  };
  
  const failed = Object.entries(checks)
    .filter(([_, value]) => !value)
    .map(([key]) => key);
  
  if (failed.length > 0) {
    console.error('Initialization incomplete:', failed);
    return false;
  }
  
  console.log('✅ Complete initialization verified!');
  return true;
}
```

## Summary

The Agent C login response contains **much more** than just authentication tokens. It provides:

1. **Authentication tokens** (JWT and HeyGen)
2. **User information** with roles and groups
3. **Available agents** the user can access
4. **HeyGen avatars** for video streaming
5. **Voice models** with format specifications
6. **Toolsets** with complete schemas
7. **UI session ID** for reconnection

The WebSocket URL is **NOT** included and must be constructed from your API configuration.

To properly use the SDK:

1. **Store the complete login response** in AuthManager
2. **Parse the JWT** to get token expiry
3. **Build the WebSocket URL** yourself
4. **Initialize with AuthManager** not just a token
5. **Access all resources** through AuthManager methods
6. **Use available data** instead of hardcoding

In production, your backend fetches this data and provides it to the frontend. In development, you can use direct login but should transition to the production pattern before deployment.

The SDK automatically initializes subsystems (VoiceManager, AvatarManager, etc.) when the AuthManager has the necessary data, giving you a fully-featured real-time communication client with voice, avatar, and chat capabilities.