# Authentication Guide

This guide covers authentication with the Agent C Realtime API, including API keys, JWT tokens, token refresh, and security best practices.

## Overview

The Agent C Realtime SDK uses a two-step authentication process:

1. **API Key Authentication** - Exchange your API key for JWT tokens
2. **JWT Token Usage** - Use JWT tokens for WebSocket connections

## Authentication Flow

```
API Key
   │
   ▼
Login Endpoint (/auth/login)
   │
   ▼
JWT Tokens (Agent C + HeyGen)
   │
   ▼
WebSocket Connection
   │
   ▼
Auto-refresh before expiry
```

## Getting Started

### 1. Obtain a HeyGen Access Token

Get your HeyGen Access Token from the Agent C dashboard:

1. Log into [Agent C Platform](https://agentc.ai)
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy and store securely

### 2. Basic Authentication

```typescript
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

// Create auth manager
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai'
});

// Login with API key
const loginResponse = await authManager.login('sk-your-api-key');

// Create client with auth manager
const client = new RealtimeClient({
  apiUrl: 'wss://api.agentc.ai/rt/ws',
  authManager
});

// Connect (uses JWT from auth manager)
await client.connect();
```

## Authentication Methods

### Method 1: Using AuthManager (Recommended)

The AuthManager handles token lifecycle automatically:

```typescript
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai',
  tokenRefreshBuffer: 5,    // Refresh 5 minutes before expiry
  enableAutoRefresh: true   // Auto-refresh tokens
});

// Login once
await authManager.login(process.env.AGENTC_API_KEY);

// Tokens are managed automatically
const client = new RealtimeClient({
  apiUrl: 'wss://api.agentc.ai/rt/ws',
  authManager  // Pass manager, not token
});
```

### Method 2: Direct Token Usage

If you already have a JWT token:

```typescript
const client = new RealtimeClient({
  apiUrl: 'wss://api.agentc.ai/rt/ws',
  authToken: 'eyJhbGciOiJIUzI1NiIs...'  // Your JWT token
});

await client.connect();
```

### Method 3: React with AgentCProvider

For React applications:

```tsx
<AgentCProvider 
  config={{
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    apiKey: process.env.REACT_APP_AGENTC_KEY  // Provider handles auth
  }}
>
  <App />
</AgentCProvider>
```

## Token Management

### Understanding Token Lifecycle

```typescript
// Login response structure
interface LoginResponse {
  agentc_token: string;      // JWT for Agent C API
  heygen_token?: string;     // Token for HeyGen avatars
  ui_session_id: string;     // Session identifier
  expires_at: number;        // Unix timestamp
  voices: Voice[];           // Available TTS voices
  avatars?: Avatar[];        // Available avatars
}
```

### Token Expiration

Tokens typically expire after 1 hour:

```typescript
// Check if token is expired
const isExpired = authManager.getTokenExpiry() < new Date();

// Get time until expiry
const expiry = authManager.getTokenExpiry();
const minutesRemaining = (expiry - Date.now()) / 60000;
```

### Automatic Token Refresh

The AuthManager refreshes tokens automatically:

```typescript
authManager.on('auth:tokens-refreshed', (tokens) => {
  console.log('Tokens refreshed, expires:', new Date(tokens.expiresAt));
});

authManager.on('auth:token-expired', () => {
  console.log('Token expired, re-authenticating...');
  authManager.login(apiKey);
});
```

### Manual Token Refresh

```typescript
// Manually refresh tokens
const newTokens = await authManager.refreshTokens();

// Update client with new token
client.setAuthToken(newTokens.agentCToken);
```

## Environment Configuration

### Development Setup

```bash
# .env.development
AGENTC_API_URL=http://localhost:8080
AGENTC_WS_URL=ws://localhost:8080/rt/ws
AGENTC_API_KEY=sk-dev-...
AGENTC_DEBUG=true
```

### Production Setup

```bash
# .env.production
AGENTC_API_URL=https://api.agentc.ai
AGENTC_WS_URL=wss://api.agentc.ai/rt/ws
AGENTC_API_KEY=sk-prod-...
AGENTC_DEBUG=false
```

### Loading Environment Variables

```typescript
import dotenv from 'dotenv';

// Load environment-specific config
dotenv.config({ 
  path: process.env.NODE_ENV === 'production' 
    ? '.env.production' 
    : '.env.development' 
});

const authManager = new AuthManager({
  apiUrl: process.env.AGENTC_API_URL!
});

await authManager.login(process.env.AGENTC_API_KEY!);
```

## Security Best Practices

### 1. Never Expose API Keys

```typescript
// ❌ BAD - Never hardcode keys
const apiKey = 'sk-abc123...';

// ✅ GOOD - Use environment variables
const apiKey = process.env.AGENTC_API_KEY;

// ✅ GOOD - Use secure key management
const apiKey = await secretManager.getSecret('agentc-api-key');
```

### 2. Secure Storage

```typescript
// Browser - Use secure storage abstraction
class SecureStorage {
  private encrypt(data: string): string {
    // Implement encryption
    return encrypted;
  }
  
  private decrypt(data: string): string {
    // Implement decryption
    return decrypted;
  }
  
  setToken(token: string): void {
    const encrypted = this.encrypt(token);
    sessionStorage.setItem('auth_token', encrypted);
  }
  
  getToken(): string | null {
    const encrypted = sessionStorage.getItem('auth_token');
    return encrypted ? this.decrypt(encrypted) : null;
  }
}
```

### 3. Token Rotation

```typescript
// Implement token rotation
class TokenRotation {
  private rotationInterval = 30 * 60 * 1000; // 30 minutes
  
  startRotation(authManager: AuthManager): void {
    setInterval(async () => {
      try {
        await authManager.refreshTokens();
        console.log('Tokens rotated successfully');
      } catch (error) {
        console.error('Token rotation failed:', error);
      }
    }, this.rotationInterval);
  }
}
```

### 4. HTTPS Only

```typescript
// Ensure HTTPS in production
if (process.env.NODE_ENV === 'production' && !window.location.protocol.includes('https')) {
  throw new Error('HTTPS is required in production');
}
```

### 5. API Key Restrictions

Configure API key restrictions in Agent C dashboard:

- **IP Whitelist**: Restrict to specific IPs
- **Domain Whitelist**: Restrict to your domains
- **Rate Limiting**: Set appropriate limits
- **Scope Limitations**: Limit key permissions

## Handling Authentication Errors

### Common Error Scenarios

```typescript
try {
  await authManager.login(apiKey);
} catch (error) {
  if (error.response?.status === 401) {
    // Invalid API key
    console.error('Invalid API key');
  } else if (error.response?.status === 403) {
    // Key doesn't have required permissions
    console.error('Insufficient permissions');
  } else if (error.response?.status === 429) {
    // Rate limited
    console.error('Rate limited, retry after:', error.response.headers['retry-after']);
  } else if (error.code === 'ECONNREFUSED') {
    // Cannot connect to auth server
    console.error('Cannot connect to authentication server');
  } else {
    // Unknown error
    console.error('Authentication failed:', error.message);
  }
}
```

### Retry Logic

```typescript
class AuthRetry {
  async loginWithRetry(
    authManager: AuthManager, 
    apiKey: string, 
    maxRetries = 3
  ): Promise<LoginResponse> {
    let lastError: Error;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await authManager.login(apiKey);
      } catch (error) {
        lastError = error;
        
        // Don't retry on auth errors
        if (error.response?.status === 401 || error.response?.status === 403) {
          throw error;
        }
        
        // Exponential backoff
        const delay = Math.pow(2, i) * 1000;
        console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }
}
```

## Multi-Tenant Authentication

For applications serving multiple tenants:

```typescript
class MultiTenantAuth {
  private authManagers = new Map<string, AuthManager>();
  
  async authenticateTenant(tenantId: string, apiKey: string): Promise<AuthManager> {
    // Create tenant-specific auth manager
    const authManager = new AuthManager({
      apiUrl: `https://${tenantId}.api.agentc.ai`
    });
    
    await authManager.login(apiKey);
    this.authManagers.set(tenantId, authManager);
    
    return authManager;
  }
  
  getAuthManager(tenantId: string): AuthManager | undefined {
    return this.authManagers.get(tenantId);
  }
  
  async refreshAllTenants(): Promise<void> {
    const promises = Array.from(this.authManagers.values()).map(
      manager => manager.refreshTokens()
    );
    
    await Promise.all(promises);
  }
}
```

## OAuth Integration (Future)

Planned OAuth support:

```typescript
// Future OAuth flow
const oauth = new AgentCOAuth({
  clientId: 'your-client-id',
  redirectUri: 'https://yourapp.com/callback',
  scopes: ['realtime', 'avatars']
});

// Initiate OAuth flow
const authUrl = oauth.getAuthorizationUrl();
window.location.href = authUrl;

// Handle callback
const tokens = await oauth.handleCallback(callbackUrl);
```

## Session Management

### UI Session Persistence

```typescript
// Save session for reconnection
const sessionId = authManager.getUiSessionId();
localStorage.setItem('ui_session_id', sessionId);

// Restore session on page reload
const savedSessionId = localStorage.getItem('ui_session_id');
if (savedSessionId) {
  const client = new RealtimeClient({
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    authManager,
    sessionId: savedSessionId  // Reconnect to same session
  });
}
```

### Session Validation

```typescript
// Validate session is still active
async function validateSession(sessionId: string): Promise<boolean> {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/validate`, {
      headers: {
        'Authorization': `Bearer ${authManager.getAgentCToken()}`
      }
    });
    
    return response.ok;
  } catch {
    return false;
  }
}
```

## Testing Authentication

### Mock Authentication for Tests

```typescript
// Mock auth manager for testing
class MockAuthManager extends AuthManager {
  async login(apiKey: string): Promise<LoginResponse> {
    return {
      agentc_token: 'mock-jwt-token',
      heygen_token: 'mock-heygen-token',
      ui_session_id: 'mock-session-id',
      expires_at: Date.now() + 3600000,
      voices: [
        { voice_id: 'nova', name: 'Nova', vendor: 'openai' }
      ]
    };
  }
  
  async refreshTokens(): Promise<TokenPair> {
    return {
      agentCToken: 'refreshed-mock-token',
      heygenToken: 'refreshed-heygen-token',
      expiresAt: Date.now() + 3600000
    };
  }
}

// Use in tests
const mockAuth = new MockAuthManager({ apiUrl: 'http://test' });
const client = new RealtimeClient({ 
  apiUrl: 'ws://test',
  authManager: mockAuth 
});
```

## Troubleshooting

### Common Issues

**"Invalid API key" error:**
- Verify key is correct and active
- Check for extra whitespace
- Ensure using correct environment

**"Token expired" during connection:**
- Enable auto-refresh in AuthManager
- Check tokenRefreshBuffer setting
- Verify system time is correct

**"Cannot connect to auth server":**
- Check network connectivity
- Verify API URL is correct
- Check firewall/proxy settings

**"Rate limited" errors:**
- Implement exponential backoff
- Cache tokens appropriately
- Check API key rate limits

### Debug Logging

Enable debug logging for troubleshooting:

```typescript
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai',
  debug: true  // Enable debug logging
});

// Monitor auth events
authManager.on('auth:login', (response) => {
  console.log('Login successful:', response);
});

authManager.on('auth:error', (error) => {
  console.error('Auth error:', error);
});
```

## Best Practices Summary

1. **Use AuthManager** for automatic token management
2. **Store keys securely** in environment variables
3. **Implement retry logic** for network failures
4. **Monitor token expiry** and refresh proactively
5. **Use HTTPS** in production
6. **Restrict API keys** by IP/domain
7. **Rotate tokens** regularly
8. **Handle errors** gracefully
9. **Log auth events** for debugging
10. **Test auth flows** thoroughly