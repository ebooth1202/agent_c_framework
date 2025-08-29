# AuthManager API Reference

The `AuthManager` class handles authentication with the Agent C platform, manages JWT tokens, and provides access to configuration like available voices and avatars.

## Import

```typescript
import { AuthManager } from '@agentc/realtime-core';
```

## Constructor

```typescript
constructor(config: AuthConfig)
```

Creates a new AuthManager instance.

### Parameters

- `config` (AuthConfig) - Configuration object

### Configuration Options

```typescript
interface AuthConfig {
  apiUrl: string;           // Base API URL (e.g., 'https://api.agentc.ai')
  tokenRefreshBuffer?: number; // Minutes before expiry to refresh (default: 5)
  enableAutoRefresh?: boolean; // Auto-refresh tokens (default: true)
  debug?: boolean;          // Enable debug logging (default: false)
}
```

### Example

```typescript
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai',
  tokenRefreshBuffer: 5,
  enableAutoRefresh: true,
  debug: true
});
```

## Authentication Methods

### login()

Authenticates with the Agent C platform using an API key.

```typescript
async login(apiKey: string): Promise<LoginResponse>
```

**Parameters:**
- `apiKey` (string) - Your Agent C API key

**Returns:** Promise resolving to LoginResponse

```typescript
interface LoginResponse {
  agentc_token: string;     // JWT for WebSocket connection
  heygen_token?: string;    // HeyGen access token (if available)
  ui_session_id: string;    // UI session identifier
  voices: Voice[];          // Available TTS voices
  avatars?: Avatar[];       // Available avatars (if configured)
  expires_at: number;       // Token expiration timestamp
}

interface Voice {
  voice_id: string;         // Voice identifier (e.g., 'nova', 'echo')
  name: string;             // Display name
  vendor: string;           // Provider (e.g., 'openai')
  description?: string;     // Voice description
  output_format?: string;   // Audio format (e.g., 'pcm16')
}

interface Avatar {
  avatar_id: string;        // Avatar identifier
  name: string;             // Display name
  preview_url?: string;     // Preview image URL
}
```

**Example:**
```typescript
try {
  const response = await authManager.login('sk-abc123...');
  console.log('Authenticated! Token:', response.agentc_token);
  console.log('Available voices:', response.voices);
} catch (error) {
  console.error('Login failed:', error);
}
```

### refreshTokens()

Manually refreshes the authentication tokens.

```typescript
async refreshTokens(): Promise<TokenPair>
```

**Returns:** Promise resolving to new token pair

```typescript
interface TokenPair {
  agentCToken: string;
  heygenToken?: string;
  expiresAt: number;
}
```

**Note:** Usually called automatically before token expiry

**Example:**
```typescript
try {
  const tokens = await authManager.refreshTokens();
  console.log('Tokens refreshed, expires at:', new Date(tokens.expiresAt));
} catch (error) {
  console.error('Token refresh failed:', error);
}
```

### logout()

Clears stored tokens and stops auto-refresh.

```typescript
logout(): void
```

**Example:**
```typescript
authManager.logout();
console.log('Logged out');
```

## Token Management

### getTokens()

Gets the current token pair.

```typescript
getTokens(): TokenPair | null
```

**Returns:** Current tokens or null if not authenticated

**Example:**
```typescript
const tokens = authManager.getTokens();
if (tokens) {
  console.log('Agent C Token:', tokens.agentCToken);
  console.log('Expires:', new Date(tokens.expiresAt));
} else {
  console.log('Not authenticated');
}
```

### getAgentCToken()

Gets just the Agent C JWT token.

```typescript
getAgentCToken(): string | null
```

**Returns:** JWT token or null

**Example:**
```typescript
const token = authManager.getAgentCToken();
if (token) {
  // Use token for API calls
}
```

### getHeyGenToken()

Gets the HeyGen access token for avatar sessions.

```typescript
getHeyGenToken(): string | null
```

**Returns:** HeyGen token or null

**Example:**
```typescript
const heygenToken = authManager.getHeyGenToken();
if (heygenToken) {
  // Use for HeyGen avatar creation
}
```

### isAuthenticated()

Checks if currently authenticated with valid tokens.

```typescript
isAuthenticated(): boolean
```

**Returns:** `true` if authenticated with non-expired tokens

**Example:**
```typescript
if (authManager.isAuthenticated()) {
  // Proceed with authenticated operations
} else {
  // Need to login
  await authManager.login(apiKey);
}
```

### getTokenExpiry()

Gets the token expiration time.

```typescript
getTokenExpiry(): Date | null
```

**Returns:** Expiration date or null if not authenticated

**Example:**
```typescript
const expiry = authManager.getTokenExpiry();
if (expiry) {
  console.log('Token expires at:', expiry);
  const remaining = expiry.getTime() - Date.now();
  console.log('Minutes remaining:', Math.floor(remaining / 60000));
}
```

## Configuration Access

### getVoices()

Gets the list of available TTS voices.

```typescript
getVoices(): Voice[]
```

**Returns:** Array of available voices

**Example:**
```typescript
const voices = authManager.getVoices();
voices.forEach(voice => {
  console.log(`${voice.name} (${voice.voice_id}): ${voice.description}`);
});

// Find specific voice
const nova = voices.find(v => v.voice_id === 'nova');
```

### getAvatars()

Gets the list of available avatars.

```typescript
getAvatars(): Avatar[]
```

**Returns:** Array of available avatars

**Example:**
```typescript
const avatars = authManager.getAvatars();
avatars.forEach(avatar => {
  console.log(`${avatar.name}: ${avatar.avatar_id}`);
  if (avatar.preview_url) {
    console.log('Preview:', avatar.preview_url);
  }
});
```

### getUiSessionId()

Gets the UI session identifier.

```typescript
getUiSessionId(): string | null
```

**Returns:** UI session ID or null

**Example:**
```typescript
const sessionId = authManager.getUiSessionId();
console.log('UI Session:', sessionId);
```

### getLoginResponse()

Gets the complete login response data.

```typescript
getLoginResponse(): LoginResponse | null
```

**Returns:** Full login response or null

**Example:**
```typescript
const loginData = authManager.getLoginResponse();
if (loginData) {
  console.log('Full login data:', loginData);
}
```

## Auto-Refresh Configuration

### setAutoRefresh()

Enables or disables automatic token refresh.

```typescript
setAutoRefresh(enabled: boolean): void
```

**Parameters:**
- `enabled` (boolean) - Whether to enable auto-refresh

**Example:**
```typescript
// Disable auto-refresh
authManager.setAutoRefresh(false);

// Re-enable auto-refresh
authManager.setAutoRefresh(true);
```

### setTokenRefreshBuffer()

Sets how many minutes before expiry to refresh tokens.

```typescript
setTokenRefreshBuffer(minutes: number): void
```

**Parameters:**
- `minutes` (number) - Minutes before expiry to refresh

**Example:**
```typescript
// Refresh tokens 10 minutes before expiry
authManager.setTokenRefreshBuffer(10);
```

### stopAutoRefresh()

Stops the automatic token refresh timer.

```typescript
stopAutoRefresh(): void
```

**Example:**
```typescript
authManager.stopAutoRefresh();
```

## Event Handling

AuthManager extends EventEmitter and emits events for token lifecycle:

### Events

- `auth:login` - Successful login
- `auth:logout` - Logout occurred
- `auth:tokens-refreshed` - Tokens refreshed
- `auth:token-expired` - Token expired
- `auth:error` - Authentication error

### on()

Subscribe to authentication events.

```typescript
on(event: string, handler: Function): void
```

**Example:**
```typescript
authManager.on('auth:login', (response: LoginResponse) => {
  console.log('Logged in successfully');
  console.log('Available voices:', response.voices.length);
});

authManager.on('auth:tokens-refreshed', (tokens: TokenPair) => {
  console.log('Tokens refreshed, new expiry:', new Date(tokens.expiresAt));
});

authManager.on('auth:token-expired', () => {
  console.log('Token expired, need to re-authenticate');
});

authManager.on('auth:error', (error: Error) => {
  console.error('Auth error:', error.message);
});
```

### off()

Unsubscribe from events.

```typescript
off(event: string, handler: Function): void
```

### once()

Subscribe to an event for a single occurrence.

```typescript
once(event: string, handler: Function): void
```

## Complete Example

```typescript
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

async function setupAuthentication() {
  // Create auth manager
  const authManager = new AuthManager({
    apiUrl: 'https://api.agentc.ai',
    tokenRefreshBuffer: 5,
    enableAutoRefresh: true,
    debug: true
  });
  
  // Subscribe to events
  authManager.on('auth:login', (response) => {
    console.log('✅ Authenticated successfully');
    console.log(`📢 ${response.voices.length} voices available`);
    if (response.avatars) {
      console.log(`🎭 ${response.avatars.length} avatars available`);
    }
  });
  
  authManager.on('auth:tokens-refreshed', (tokens) => {
    console.log('🔄 Tokens refreshed automatically');
    const remaining = tokens.expiresAt - Date.now();
    console.log(`⏰ Next refresh in ${Math.floor(remaining / 60000)} minutes`);
  });
  
  authManager.on('auth:token-expired', () => {
    console.log('⚠️ Token expired - re-authenticating...');
    // Re-authenticate
    authManager.login(process.env.AGENTC_API_KEY!);
  });
  
  authManager.on('auth:error', (error) => {
    console.error('❌ Authentication error:', error.message);
  });
  
  // Perform login
  try {
    const response = await authManager.login(process.env.AGENTC_API_KEY!);
    
    // Display available resources
    console.log('\nAvailable Voices:');
    response.voices.forEach(voice => {
      console.log(`  - ${voice.name} (${voice.voice_id})`);
      console.log(`    Vendor: ${voice.vendor}`);
      console.log(`    Format: ${voice.output_format || 'default'}`);
    });
    
    if (response.avatars && response.avatars.length > 0) {
      console.log('\nAvailable Avatars:');
      response.avatars.forEach(avatar => {
        console.log(`  - ${avatar.name} (${avatar.avatar_id})`);
      });
    }
    
    // Check authentication status
    console.log('\nAuthentication Status:');
    console.log('Authenticated:', authManager.isAuthenticated());
    console.log('Token expires:', authManager.getTokenExpiry());
    console.log('UI Session:', authManager.getUiSessionId());
    
    // Create realtime client with auth manager
    const client = new RealtimeClient({
      apiUrl: 'wss://api.agentc.ai/rt/ws',
      authManager,  // Pass auth manager to client
      enableAudio: true
    });
    
    // Connect using managed authentication
    await client.connect();
    console.log('✅ Connected to realtime API');
    
    // The client will automatically use tokens from auth manager
    // and reconnect when tokens are refreshed
    
    return { authManager, client };
    
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}

// Usage
setupAuthentication()
  .then(({ client }) => {
    // Use the authenticated client
    client.sendText('Hello!');
  })
  .catch(console.error);
```

## Token Refresh Lifecycle

The AuthManager automatically handles token refresh:

```typescript
// Token refresh timeline example
// Assuming token expires in 60 minutes and buffer is 5 minutes

Time 0:    Login successful, token expires at Time 60
Time 55:   Auto-refresh triggered (5 minutes before expiry)
Time 55:   New token obtained, expires at Time 115
Time 110:  Auto-refresh triggered again
Time 110:  New token obtained, expires at Time 170
...continues until logout or error
```

## Error Handling

The AuthManager can throw or emit errors for:

1. **Network Errors**
   - Connection failures
   - Timeout errors

2. **Authentication Errors**
   - Invalid API key
   - Expired tokens
   - Permission denied

3. **Configuration Errors**
   - Invalid API URL
   - Missing required config

Example error handling:

```typescript
// Handle login errors
try {
  await authManager.login(apiKey);
} catch (error) {
  if (error.response?.status === 401) {
    console.error('Invalid API key');
  } else if (error.code === 'ECONNREFUSED') {
    console.error('Cannot connect to API');
  } else {
    console.error('Login failed:', error.message);
  }
}

// Handle refresh errors
authManager.on('auth:error', (error) => {
  if (error.message.includes('refresh')) {
    console.error('Token refresh failed, need to re-login');
    // Attempt re-login
    authManager.login(apiKey);
  }
});
```

## Best Practices

1. **Always check authentication before operations:**
```typescript
if (!authManager.isAuthenticated()) {
  await authManager.login(apiKey);
}
```

2. **Store API keys securely:**
```typescript
// Use environment variables
const apiKey = process.env.AGENTC_API_KEY;

// Never hardcode keys
// BAD: authManager.login('sk-abc123...')
// GOOD: authManager.login(apiKey)
```

3. **Handle token expiration gracefully:**
```typescript
authManager.on('auth:token-expired', async () => {
  try {
    await authManager.login(apiKey);
    // Reconnect client if needed
  } catch (error) {
    // Handle re-auth failure
  }
});
```

4. **Use with RealtimeClient for automatic token management:**
```typescript
const client = new RealtimeClient({
  authManager,  // Pass manager, not token
  // Client will use fresh tokens automatically
});
```

5. **Clean up on application exit:**
```typescript
process.on('SIGINT', () => {
  authManager.logout();
  authManager.stopAutoRefresh();
  process.exit(0);
});
```

## TypeScript Types

```typescript
import {
  AuthManager,
  AuthConfig,
  LoginResponse,
  TokenPair,
  Voice,
  Avatar
} from '@agentc/realtime-core';
```

All methods and events are fully typed for TypeScript applications.