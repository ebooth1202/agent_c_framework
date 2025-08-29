# Agent C Authentication Guide

This guide covers authentication with the Agent C Realtime API using the ChatUser system, including login flows, token management, and how to build application-specific user systems on top of Agent C's platform authentication.

## Overview: The ChatUser Concept

Agent C uses a **ChatUser** authentication system that represents platform-level users, not application end-users. This is a critical distinction:

- **ChatUsers** are Agent C platform accounts with credentials (username/password)
- **ChatUsers** have access to agents, voices, avatars, and toolsets
- **Applications** can implement their own user system while sharing ChatUsers
- **NO API KEYS** - Agent C uses username/password authentication exclusively

### Authentication Architecture

```
Application End-User (optional, your implementation)
           │
           ▼
    Your Application
           │
           ▼
ChatUser Credentials (username/password)
           │
           ▼
Agent C Login Endpoint (/rt/login)
           │
           ▼
    JWT Token + Config
           │
           ▼
   WebSocket Connection
```

## Getting Started

### Development Setup

Agent C runs locally on port 8000 during development:

```typescript
// Development configuration
const AUTH_CONFIG = {
  apiUrl: 'https://localhost:8000',  // HTTPS required for Agent C
  loginEndpoint: '/rt/login',
  refreshEndpoint: '/rt/refresh_token'
};
```

### Basic Login Flow

```typescript
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

// Create auth manager pointing to local Agent C
const authManager = new AuthManager({
  apiUrl: 'https://localhost:8000'
});

// Login with ChatUser credentials (NOT API keys!)
const loginResponse = await authManager.login({
  username: 'your_chatuser_username',
  password: 'your_chatuser_password'
});

// The login response contains everything needed
console.log('JWT Token:', loginResponse.agent_c_token);
console.log('WebSocket URL:', loginResponse.websocket_url);
console.log('Available Agents:', loginResponse.agents);
console.log('Available Voices:', loginResponse.voices);
```

## Complete Login Implementation

### 1. The Login Request

```typescript
interface LoginRequest {
  username: string;
  password: string;
}

async function loginToChatUser(credentials: LoginRequest) {
  const response = await fetch('https://localhost:8000/rt/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials)
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`);
  }

  return response.json();
}
```

### 2. Understanding the Login Response

The login response contains comprehensive configuration data:

```typescript
interface LoginResponse {
  // Authentication tokens
  agent_c_token: string;        // JWT for Agent C API
  heygen_token?: string;        // Token for HeyGen avatar sessions
  
  // Dynamic WebSocket URL (use this, not hardcoded URLs!)
  websocket_url: string;        // e.g., "wss://localhost:8000/rt/ws"
  
  // User information
  user: {
    id: string;
    username: string;
    name: string;
    email?: string;
  };
  
  // Available resources
  agents: Agent[];              // Agents this ChatUser can access
  voices: Voice[];              // TTS voices available
  avatars?: Avatar[];           // HeyGen avatars if configured
  toolsets: Toolset[];          // Available tool configurations
  
  // Session info
  ui_session_id: string;        // Unique session identifier
  expires_at: number;           // Token expiry timestamp
}
```

### 3. Using the Login Response

```typescript
class AgentCAuthManager {
  private loginData: LoginResponse | null = null;
  private websocketUrl: string | null = null;
  
  async authenticate(username: string, password: string): Promise<void> {
    // Login to Agent C
    const response = await fetch('https://localhost:8000/rt/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) {
      throw new Error('Authentication failed');
    }
    
    this.loginData = await response.json();
    
    // IMPORTANT: Use the dynamic WebSocket URL from the response
    this.websocketUrl = this.loginData.websocket_url;
    
    // Schedule token refresh
    this.scheduleTokenRefresh();
  }
  
  getWebSocketUrl(): string {
    if (!this.websocketUrl) {
      throw new Error('Not authenticated');
    }
    return this.websocketUrl;
  }
  
  getToken(): string {
    if (!this.loginData) {
      throw new Error('Not authenticated');
    }
    return this.loginData.agent_c_token;
  }
  
  getAvailableAgents(): Agent[] {
    return this.loginData?.agents || [];
  }
  
  getAvailableVoices(): Voice[] {
    return this.loginData?.voices || [];
  }
}
```

## Token Management

### Automatic Token Refresh

JWT tokens expire and need to be refreshed. The refresh endpoint uses the existing token:

```typescript
class TokenManager {
  private token: string;
  private expiresAt: number;
  private refreshTimer?: NodeJS.Timeout;
  
  constructor(initialToken: string, expiresAt: number) {
    this.token = initialToken;
    this.expiresAt = expiresAt;
    this.scheduleRefresh();
  }
  
  private scheduleRefresh(): void {
    // Clear any existing timer
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }
    
    // Calculate when to refresh (5 minutes before expiry)
    const now = Date.now();
    const expiryTime = this.expiresAt * 1000; // Convert to milliseconds
    const refreshTime = expiryTime - (5 * 60 * 1000); // 5 minutes before
    const delay = refreshTime - now;
    
    if (delay > 0) {
      this.refreshTimer = setTimeout(() => {
        this.refreshToken();
      }, delay);
    } else {
      // Token expired or about to expire, refresh immediately
      this.refreshToken();
    }
  }
  
  private async refreshToken(): Promise<void> {
    try {
      const response = await fetch('https://localhost:8000/rt/refresh_token', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      
      const data = await response.json();
      this.token = data.agent_c_token;
      this.expiresAt = data.expires_at;
      
      // Schedule next refresh
      this.scheduleRefresh();
      
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Emit event for re-authentication
      this.emit('token-refresh-failed');
    }
  }
  
  getToken(): string {
    return this.token;
  }
  
  isExpired(): boolean {
    return Date.now() >= this.expiresAt * 1000;
  }
}
```

## Implementing Application-Level Users

While Agent C uses ChatUsers for platform authentication, your application can implement its own user system on top:

### Strategy 1: Shared ChatUser with App Users

Multiple application users share a single ChatUser account:

```typescript
class ApplicationAuthService {
  private chatUserAuth: AgentCAuthManager;
  private appUsers: Map<string, AppUser> = new Map();
  
  constructor() {
    // Single shared ChatUser for all app users
    this.chatUserAuth = new AgentCAuthManager();
  }
  
  async initializePlatform(): Promise<void> {
    // Authenticate with shared ChatUser credentials
    // These could be stored in environment variables
    await this.chatUserAuth.authenticate(
      process.env.SHARED_CHATUSER_USERNAME!,
      process.env.SHARED_CHATUSER_PASSWORD!
    );
  }
  
  async loginAppUser(email: string, password: string): Promise<AppUser> {
    // Authenticate against YOUR user database
    const user = await this.validateAppUser(email, password);
    
    if (!user) {
      throw new Error('Invalid credentials');
    }
    
    // App user is authenticated, they'll use the shared ChatUser connection
    this.appUsers.set(user.id, user);
    
    return {
      ...user,
      // Provide the shared Agent C connection details
      agentCToken: this.chatUserAuth.getToken(),
      websocketUrl: this.chatUserAuth.getWebSocketUrl()
    };
  }
  
  private async validateAppUser(email: string, password: string): Promise<AppUser | null> {
    // Your application's user authentication logic
    // This could be against your own database, OAuth, etc.
    return yourDatabaseQuery(email, password);
  }
}
```

### Strategy 2: ChatUser Per Application User

Each application user has their own ChatUser account:

```typescript
class DedicatedUserAuthService {
  private userSessions: Map<string, ChatUserSession> = new Map();
  
  async loginUser(appUserId: string, appUserPassword: string): Promise<UserSession> {
    // First authenticate the app user
    const appUser = await this.authenticateAppUser(appUserId, appUserPassword);
    
    // Map app user to their ChatUser credentials
    const chatUserCreds = await this.getChatUserCredentials(appUser.id);
    
    // Login to Agent C with user-specific ChatUser
    const authManager = new AgentCAuthManager();
    await authManager.authenticate(
      chatUserCreds.username,
      chatUserCreds.password
    );
    
    // Store session
    const session = {
      appUser,
      authManager,
      token: authManager.getToken(),
      websocketUrl: authManager.getWebSocketUrl()
    };
    
    this.userSessions.set(appUser.id, session);
    return session;
  }
  
  private async getChatUserCredentials(appUserId: string): Promise<ChatUserCredentials> {
    // Your logic to map app users to ChatUsers
    // This could be 1:1 mapping stored in your database
    return {
      username: `chatuser_${appUserId}`,
      password: await this.getChatUserPassword(appUserId)
    };
  }
}
```

### Strategy 3: Multi-Tenant with Pooled ChatUsers

For multi-tenant applications with ChatUser pooling:

```typescript
class MultiTenantAuthService {
  private tenantPools: Map<string, ChatUserPool> = new Map();
  
  async authenticateTenant(tenantId: string, userCredentials: any): Promise<TenantSession> {
    // Get or create pool for tenant
    let pool = this.tenantPools.get(tenantId);
    if (!pool) {
      pool = await this.createTenantPool(tenantId);
      this.tenantPools.set(tenantId, pool);
    }
    
    // Authenticate the tenant's user
    const user = await this.authenticateTenantUser(tenantId, userCredentials);
    
    // Assign a ChatUser from the pool
    const chatUserSession = await pool.assignChatUser(user.id);
    
    return {
      tenant: tenantId,
      user,
      agentCToken: chatUserSession.token,
      websocketUrl: chatUserSession.websocketUrl,
      agents: chatUserSession.agents,
      voices: chatUserSession.voices
    };
  }
  
  private async createTenantPool(tenantId: string): Promise<ChatUserPool> {
    // Create a pool of ChatUsers for this tenant
    const poolSize = this.getPoolSizeForTenant(tenantId);
    const pool = new ChatUserPool();
    
    for (let i = 0; i < poolSize; i++) {
      const creds = await this.getTenantChatUserCreds(tenantId, i);
      await pool.addChatUser(creds.username, creds.password);
    }
    
    return pool;
  }
}

class ChatUserPool {
  private availableUsers: ChatUserSession[] = [];
  private assignedUsers: Map<string, ChatUserSession> = new Map();
  
  async addChatUser(username: string, password: string): Promise<void> {
    const auth = new AgentCAuthManager();
    await auth.authenticate(username, password);
    
    this.availableUsers.push({
      auth,
      token: auth.getToken(),
      websocketUrl: auth.getWebSocketUrl(),
      inUse: false
    });
  }
  
  async assignChatUser(appUserId: string): Promise<ChatUserSession> {
    // Find available ChatUser or wait for one
    const session = this.availableUsers.find(u => !u.inUse);
    if (!session) {
      throw new Error('No available ChatUsers in pool');
    }
    
    session.inUse = true;
    this.assignedUsers.set(appUserId, session);
    return session;
  }
  
  releaseChatUser(appUserId: string): void {
    const session = this.assignedUsers.get(appUserId);
    if (session) {
      session.inUse = false;
      this.assignedUsers.delete(appUserId);
    }
  }
}
```

## Complete Client Integration

### Creating a Realtime Client with Authentication

```typescript
import { RealtimeClient } from '@agentc/realtime-core';

class AgentCClient {
  private client?: RealtimeClient;
  private authManager: AgentCAuthManager;
  
  constructor() {
    this.authManager = new AgentCAuthManager();
  }
  
  async connect(username: string, password: string): Promise<void> {
    // Step 1: Authenticate with Agent C
    await this.authManager.authenticate(username, password);
    
    // Step 2: Create client with dynamic WebSocket URL from login
    this.client = new RealtimeClient({
      apiUrl: this.authManager.getWebSocketUrl(), // Use URL from login response!
      authManager: this.authManager,  // Pass the auth manager instance
      autoReconnect: true
    });
    
    // Step 3: Set up event handlers
    this.client.on('connection_established', () => {
      console.log('Connected to Agent C');
    });
    
    this.client.on('text_delta', (event) => {
      console.log('Received text:', event.content);
    });
    
    // Step 4: Connect
    await this.client.connect();
  }
  
  async selectAgent(agentId: string): Promise<void> {
    // Use agents from login response
    const availableAgents = this.authManager.getAvailableAgents();
    const agent = availableAgents.find(a => a.id === agentId);
    
    if (!agent) {
      throw new Error(`Agent ${agentId} not available for this ChatUser`);
    }
    
    // Send agent selection event
    await this.client?.sendEvent({
      type: 'set_agent',
      agent_id: agentId
    });
  }
  
  async selectVoice(voiceId: string): Promise<void> {
    // Use voices from login response
    const availableVoices = this.authManager.getAvailableVoices();
    const voice = availableVoices.find(v => v.voice_id === voiceId);
    
    if (!voice) {
      throw new Error(`Voice ${voiceId} not available`);
    }
    
    await this.client?.sendEvent({
      type: 'set_voice',
      voice_id: voiceId
    });
  }
}
```

## Environment Configuration

### Development Environment

```bash
# .env.development
AGENTC_API_URL=https://localhost:8000
AGENTC_CHATUSER_USERNAME=dev_user
AGENTC_CHATUSER_PASSWORD=dev_password
AGENTC_DEBUG=true
```

### Production Environment

```bash
# .env.production
AGENTC_API_URL=https://agentc-api.yourdomain.com
AGENTC_CHATUSER_USERNAME=prod_user
AGENTC_CHATUSER_PASSWORD=prod_secure_password
AGENTC_DEBUG=false
```

### Using Environment Variables

```typescript
import dotenv from 'dotenv';

// Load environment configuration
dotenv.config({
  path: process.env.NODE_ENV === 'production' 
    ? '.env.production' 
    : '.env.development'
});

// Create auth manager with environment config
const authManager = new AgentCAuthManager();

// Login with environment credentials
await authManager.authenticate(
  process.env.AGENTC_CHATUSER_USERNAME!,
  process.env.AGENTC_CHATUSER_PASSWORD!
);
```

## Error Handling

### Authentication Errors

```typescript
async function handleLogin(username: string, password: string) {
  try {
    const response = await fetch('https://localhost:8000/rt/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) {
      switch (response.status) {
        case 401:
          throw new Error('Invalid username or password');
        case 403:
          throw new Error('Account locked or insufficient permissions');
        case 429:
          const retryAfter = response.headers.get('Retry-After');
          throw new Error(`Rate limited. Retry after ${retryAfter} seconds`);
        case 500:
          throw new Error('Server error. Please try again later');
        default:
          throw new Error(`Login failed: ${response.statusText}`);
      }
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Cannot connect to Agent C server. Check if it\'s running on localhost:8000');
    }
    throw error;
  }
}
```

### Token Refresh Errors

```typescript
class ResilientTokenManager {
  private retryCount = 0;
  private maxRetries = 3;
  
  async refreshWithRetry(): Promise<void> {
    while (this.retryCount < this.maxRetries) {
      try {
        await this.refreshToken();
        this.retryCount = 0; // Reset on success
        return;
      } catch (error) {
        this.retryCount++;
        
        if (this.retryCount >= this.maxRetries) {
          // Max retries reached, need to re-authenticate
          console.error('Token refresh failed after retries. Re-authentication required.');
          this.emit('reauthentication-required');
          throw error;
        }
        
        // Exponential backoff
        const delay = Math.pow(2, this.retryCount) * 1000;
        console.log(`Refresh retry ${this.retryCount}/${this.maxRetries} in ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
}
```

## Security Best Practices

### 1. Secure Credential Storage

```typescript
// Never hardcode credentials
// ❌ BAD
const username = 'admin';
const password = 'password123';

// ✅ GOOD - Use environment variables
const username = process.env.CHATUSER_USERNAME;
const password = process.env.CHATUSER_PASSWORD;

// ✅ BETTER - Use secret management service
const credentials = await secretManager.getChatUserCredentials();
```

### 2. HTTPS for All Environments

Agent C requires HTTPS even for local development (for microphone access and security):

```typescript
// Development uses HTTPS (required for microphone and secure API)
if (process.env.NODE_ENV === 'development') {
  // Use HTTPS for localhost
  const apiUrl = 'https://localhost:8000';
  
  // Both development and production use HTTPS
  console.log('Development mode: Using HTTPS for local connections');
}
```

### 3. Token Security

```typescript
class SecureTokenStorage {
  private token?: string;
  
  setToken(token: string): void {
    // In-memory storage only, never localStorage for sensitive tokens
    this.token = token;
    
    // Optional: Use sessionStorage for browser (cleared on tab close)
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('agent_c_token', token);
    }
  }
  
  getToken(): string | null {
    return this.token || sessionStorage?.getItem('agent_c_token') || null;
  }
  
  clearToken(): void {
    this.token = undefined;
    sessionStorage?.removeItem('agent_c_token');
  }
}
```

## Testing Authentication

### Mock Authentication for Tests

```typescript
class MockAuthManager {
  async authenticate(username: string, password: string): Promise<LoginResponse> {
    // Mock successful authentication
    return {
      agent_c_token: 'mock-jwt-token',
      websocket_url: 'ws://localhost:8000/rt/ws',
      heygen_token: 'mock-heygen-token',
      user: {
        id: 'user-123',
        username: username,
        name: 'Test User'
      },
      agents: [
        { id: 'agent-1', name: 'Test Agent', model: 'gpt-4' }
      ],
      voices: [
        { voice_id: 'nova', name: 'Nova', vendor: 'openai' }
      ],
      avatars: [],
      toolsets: [],
      ui_session_id: 'session-123',
      expires_at: Date.now() / 1000 + 3600
    };
  }
}

// Use in tests
describe('Authentication', () => {
  it('should connect to Agent C', async () => {
    const mockAuth = new MockAuthManager();
    const client = new RealtimeClient({
      apiUrl: 'ws://localhost:8000/rt/ws',
      authManager: mockAuth
    });
    
    await mockAuth.authenticate('test', 'test');
    await client.connect();
    
    expect(client.isConnected()).toBe(true);
  });
});
```

## Troubleshooting

### Common Issues and Solutions

**"Cannot connect to localhost:8000"**
- Ensure Agent C server is running locally
- Verify using HTTPS (required) for localhost: https://localhost:8000
- Verify port 8000 is not blocked by firewall

**"Invalid username or password"**
- Verify ChatUser credentials are correct
- Check for trailing spaces in credentials
- Ensure you're using ChatUser credentials, not application user credentials

**"Token expired during connection"**
- Implement automatic token refresh
- Check system clock synchronization
- Reduce token refresh buffer time

**"WebSocket connection fails"**
- Use the `websocket_url` from login response
- Don't hardcode WebSocket URLs
- Check for proxy/firewall blocking WebSocket

**"No agents/voices available"**
- Check ChatUser permissions in Agent C
- Verify the ChatUser has been assigned resources
- Review login response for available resources

### Debug Logging

Enable detailed logging for troubleshooting:

```typescript
class DebugAuthManager extends AgentCAuthManager {
  async authenticate(username: string, password: string): Promise<void> {
    console.log(`[Auth] Attempting login for user: ${username}`);
    console.log(`[Auth] API URL: ${this.apiUrl}`);
    
    try {
      await super.authenticate(username, password);
      console.log('[Auth] Login successful');
      console.log('[Auth] Token expires at:', new Date(this.loginData.expires_at * 1000));
      console.log('[Auth] WebSocket URL:', this.websocketUrl);
      console.log('[Auth] Available agents:', this.loginData.agents.length);
      console.log('[Auth] Available voices:', this.loginData.voices.length);
    } catch (error) {
      console.error('[Auth] Login failed:', error);
      throw error;
    }
  }
}
```

## Summary

Key points about Agent C authentication:

1. **NO API KEYS** - Agent C uses username/password authentication only
2. **ChatUsers** are platform accounts, not your application's end users
3. **Login endpoint** returns JWT token and dynamic WebSocket URL
4. **Use the WebSocket URL** from login response, don't hardcode it
5. **Implement token refresh** to maintain long-running connections
6. **Applications can build** their own user systems on top of ChatUsers
7. **Development uses** https://localhost:8000 (HTTPS required)

Remember: ChatUsers are the foundation of Agent C authentication, but your application can implement any user model on top of this platform authentication layer.