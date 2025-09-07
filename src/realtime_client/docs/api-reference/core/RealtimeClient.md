# RealtimeClient API Reference

The `RealtimeClient` class is the main entry point for the Agent C Realtime SDK. It manages WebSocket connections, handles events, coordinates subsystems, and provides methods for interacting with the Agent C platform.

## Import

```typescript
import { RealtimeClient } from '@agentc/realtime-core';
```

## Constructor

```typescript
constructor(config: RealtimeClientConfig)
```

Creates a new RealtimeClient instance.

### Parameters

- `config` (RealtimeClientConfig) - Configuration object for the client

### Configuration Options

```typescript
interface RealtimeClientConfig {
  // Required
  apiUrl: string;                    // WebSocket URL from login response or provided
  
  // Authentication (one required)
  authToken?: string;                // JWT token for authentication
  authManager?: AuthManager;         // AuthManager instance for token management
  
  // Optional
  sessionId?: string;                // UI session ID for reconnection
  enableAudio?: boolean;             // Enable audio subsystem (default: false)
  audioConfig?: AudioConfig;         // Audio configuration
  enableTurnManager?: boolean;       // Enable turn management (default: true)
  autoReconnect?: boolean;           // Enable automatic reconnection (default: true)
  reconnection?: ReconnectionConfig; // Reconnection settings
  debug?: boolean;                   // Enable debug logging (default: false)
  connectionTimeout?: number;        // Connection timeout in ms (default: 10000)
  pingInterval?: number;             // WebSocket ping interval in ms (default: 30000)
  pongTimeout?: number;              // Pong timeout in ms (default: 5000)
  protocols?: string[];              // WebSocket subprotocols
  headers?: Record<string, string>;  // Additional headers
}

interface AudioConfig {
  enableInput?: boolean;             // Enable microphone input (default: true)
  enableOutput?: boolean;            // Enable audio output (default: true)
  sampleRate?: number;               // Audio sample rate (default: 16000)
  chunkDuration?: number;            // Chunk duration in ms (default: 100)
  respectTurnState?: boolean;        // Respect turn management (default: true)
  initialVolume?: number;            // Initial volume 0-1 (default: 1.0)
}

interface ReconnectionConfig {
  maxAttempts?: number;              // Max reconnection attempts (default: 5)
  initialDelay?: number;             // Initial delay in ms (default: 1000)
  maxDelay?: number;                 // Max delay in ms (default: 30000)
  backoffMultiplier?: number;        // Backoff multiplier (default: 1.5)
}
```

### Example

```typescript
// Using AuthManager (recommended)
const authManager = new AuthManager({ 
  apiUrl: 'https://localhost:8000' 
});
const loginResponse = await authManager.login({ 
  username: 'your-username',
  password: 'your-password' 
});

const client = new RealtimeClient({
  apiUrl: loginResponse.wsUrl, // WebSocket URL from login response
  authManager,
  enableAudio: true,
  audioConfig: {
    enableInput: true,
    enableOutput: true,
    respectTurnState: true
  },
  debug: true
});

// Or with JWT token directly
const client = new RealtimeClient({
  apiUrl: wsUrl, // WebSocket URL from login or environment
  authToken: jwtToken, // JWT token from login
  enableAudio: true,
  debug: true
});
```

## Connection Methods

### connect()

Establishes a WebSocket connection to the Agent C server.

```typescript
async connect(): Promise<void>
```

**Returns:** Promise that resolves when connected

**Throws:** Error if connection fails or times out

**Example:**
```typescript
try {
  await client.connect();
  console.log('Connected!');
} catch (error) {
  console.error('Connection failed:', error);
}
```

### disconnect()

Closes the WebSocket connection.

```typescript
disconnect(): void
```

**Example:**
```typescript
client.disconnect();
```

### isConnected()

Checks if the client is currently connected.

```typescript
isConnected(): boolean
```

**Returns:** `true` if connected, `false` otherwise

**Example:**
```typescript
if (client.isConnected()) {
  client.sendText('Hello!');
}
```

### getConnectionState()

Gets the current connection state.

```typescript
getConnectionState(): ConnectionState
```

**Returns:** Current ConnectionState enum value

```typescript
enum ConnectionState {
  DISCONNECTED = 0,
  CONNECTING = 1,
  CONNECTED = 2,
  RECONNECTING = 3
}
```

**Example:**
```typescript
const state = client.getConnectionState();
if (state === ConnectionState.CONNECTED) {
  // Ready to send messages
}
```

## Message Methods

### sendText()

Sends a text message to the agent.

```typescript
sendText(text: string, fileIds?: string[]): void
```

**Parameters:**
- `text` (string) - The text message to send
- `fileIds` (string[], optional) - Array of file IDs to attach

**Throws:** Error if not connected

**Example:**
```typescript
client.sendText('What is the weather today?');

// With file attachments
client.sendText('Analyze this document', ['file123', 'file456']);
```

### sendBinaryFrame()

Sends raw binary data (audio) to the server.

```typescript
sendBinaryFrame(data: ArrayBuffer | ArrayBufferView): void
```

**Parameters:**
- `data` - Binary audio data (PCM16 format)

**Throws:** Error if not connected or binary not supported

**Example:**
```typescript
const audioData = new Int16Array(1600); // 100ms of 16kHz audio
client.sendBinaryFrame(audioData.buffer);
```

### sendEvent()

Sends a raw event to the server. This is an advanced method that allows sending any valid ClientEventMap event directly.

```typescript
sendEvent<K extends keyof ClientEventMap>(event: ClientEventMap[K]): void
```

**Parameters:**
- `event` - A valid event object from the ClientEventMap type

**Throws:** Error if not connected to the server

**Note:** This is a public API method as of version 0.1.0. Most use cases should use the higher-level methods like `sendText()`, `setAgent()`, etc. Use this method when you need direct control over the event structure or for advanced integrations.

**Example:**
```typescript
// Send a custom event
client.sendEvent({ type: 'ping' });

// Send a text input event (equivalent to sendText)
client.sendEvent({ 
  type: 'text_input', 
  text: 'Hello',
  file_ids: ['file123'] 
});

// Send a session management event
client.sendEvent({ 
  type: 'resume_chat_session', 
  session_id: 'session-123' 
});

// TypeScript ensures type safety
client.sendEvent<'set_agent'>({ 
  type: 'set_agent', 
  agent_key: 'support-agent' 
});
```

## Agent Management

### getAgents()

Requests the list of available agents.

```typescript
getAgents(): void
```

**Emits:** `agents_list` event with available agents

**Example:**
```typescript
client.getAgents();
client.on('agents_list', (event) => {
  console.log('Available agents:', event.agents);
});
```

### setAgent()

Sets the active agent for the session.

```typescript
setAgent(agentKey: string): void
```

**Parameters:**
- `agentKey` (string) - The agent identifier

**Example:**
```typescript
client.setAgent('customer-service-agent');
```

## Voice Management

### setAgentVoice()

Changes the agent's text-to-speech voice.

```typescript
setAgentVoice(voiceId: string): void
```

**Parameters:**
- `voiceId` (string) - Voice identifier (e.g., 'nova', 'echo', 'none', 'avatar')

**Example:**
```typescript
client.setAgentVoice('nova');

// Disable audio output
client.setAgentVoice('none');

// Use avatar voice (HeyGen)
client.setAgentVoice('avatar');
```

### getVoiceManager()

Gets the VoiceManager instance.

```typescript
getVoiceManager(): VoiceManager | null
```

**Returns:** VoiceManager instance or null if not initialized

**Example:**
```typescript
const voiceManager = client.getVoiceManager();
const currentVoice = voiceManager?.getCurrentVoice();
```

## Session Management

### newChatSession()

Creates a new chat session.

```typescript
newChatSession(agentKey?: string): void
```

**Parameters:**
- `agentKey` (string, optional) - Agent to use for the new session

**Emits:** `chat_session_changed` event with new session details

**Example:**
```typescript
client.newChatSession();

// With specific agent
client.newChatSession('sales-agent');
```

### resumeChatSession()

Resumes an existing chat session.

```typescript
resumeChatSession(sessionId: string): void
```

**Parameters:**
- `sessionId` (string) - Session ID to resume

**Example:**
```typescript
client.resumeChatSession('session-123-456');
```

### setChatSessionName()

Sets a name for the current chat session.

```typescript
setChatSessionName(sessionName: string): void
```

**Parameters:**
- `sessionName` (string) - Name for the session

**Example:**
```typescript
client.setChatSessionName('Product inquiry - John Doe');
```

### setSessionMetadata()

Sets metadata for the current session.

```typescript
setSessionMetadata(meta: Record<string, any>): void
```

**Parameters:**
- `meta` (object) - Metadata object

**Example:**
```typescript
client.setSessionMetadata({
  userId: 'user123',
  topic: 'technical-support',
  priority: 'high'
});
```

### getSessionManager()

Gets the SessionManager instance.

```typescript
getSessionManager(): SessionManager | null
```

**Returns:** SessionManager instance or null

**Example:**
```typescript
const sessionManager = client.getSessionManager();
const currentSession = sessionManager?.getCurrentSession();
```

## Audio Control

### startAudioRecording()

Starts recording from the microphone.

```typescript
async startAudioRecording(): Promise<void>
```

**Returns:** Promise that resolves when recording starts

**Throws:** Error if audio not enabled or permission denied

**Example:**
```typescript
try {
  await client.startAudioRecording();
  console.log('Recording started');
} catch (error) {
  if (error.name === 'NotAllowedError') {
    console.error('Microphone permission denied');
  }
}
```

### stopAudioRecording()

Stops microphone recording.

```typescript
stopAudioRecording(): void
```

**Example:**
```typescript
client.stopAudioRecording();
```

### startAudioStreaming()

Starts streaming audio to the server.

```typescript
startAudioStreaming(): void
```

**Throws:** Error if not connected or audio not initialized

**Example:**
```typescript
await client.startAudioRecording();
client.startAudioStreaming();
```

### stopAudioStreaming()

Stops streaming audio to the server.

```typescript
stopAudioStreaming(): void
```

**Example:**
```typescript
client.stopAudioStreaming();
```

### setAudioVolume()

Sets the audio playback volume.

```typescript
setAudioVolume(volume: number): void
```

**Parameters:**
- `volume` (number) - Volume level between 0 and 1

**Throws:** Error if volume out of range

**Example:**
```typescript
client.setAudioVolume(0.8); // 80% volume
```

### getAudioStatus()

Gets the current audio system status.

```typescript
getAudioStatus(): AudioStatus
```

**Returns:** AudioStatus object

```typescript
interface AudioStatus {
  // Input status
  isRecording: boolean;
  isStreaming: boolean;
  hasPermission: boolean;
  currentLevel: number;      // Current audio level (0-1)
  
  // Output status
  isPlaying: boolean;
  bufferSize: number;
  volume: number;
  
  // System status
  isAudioEnabled: boolean;
  isInputEnabled: boolean;
  isOutputEnabled: boolean;
}
```

**Example:**
```typescript
const status = client.getAudioStatus();
console.log('Recording:', status.isRecording);
console.log('Audio level:', status.currentLevel);
```

## Avatar Management

### setAvatarSession()

Notifies the server that a HeyGen avatar session is active.

```typescript
setAvatarSession(sessionId: string, avatarId: string): void
```

**Parameters:**
- `sessionId` (string) - HeyGen session ID
- `avatarId` (string) - Avatar ID used

**Example:**
```typescript
// After HeyGen STREAM_READY event
client.setAvatarSession('heygen-session-123', 'avatar-456');
```

### clearAvatarSession()

Clears the current avatar session.

```typescript
clearAvatarSession(): void
```

**Example:**
```typescript
client.clearAvatarSession();
```

### getAvatarManager()

Gets the AvatarManager instance.

```typescript
getAvatarManager(): AvatarManager | null
```

**Returns:** AvatarManager instance or null

### getAvailableAvatars()

Gets the list of available avatars.

```typescript
getAvailableAvatars(): Avatar[]
```

**Returns:** Array of available avatars

**Example:**
```typescript
const avatars = client.getAvailableAvatars();
avatars.forEach(avatar => {
  console.log(avatar.name, avatar.avatar_id);
});
```

### getHeyGenAccessToken()

Gets the HeyGen access token for creating avatar sessions.

```typescript
getHeyGenAccessToken(): string | null
```

**Returns:** HeyGen access token or null

**Example:**
```typescript
const token = client.getHeyGenAccessToken();
if (token) {
  // Use token to create HeyGen session
}
```

## Event Handling

### on()

Subscribes to an event.

```typescript
on<K extends keyof RealtimeEventMap>(
  event: K, 
  handler: (data: RealtimeEventMap[K]) => void
): void
```

**Parameters:**
- `event` - Event name
- `handler` - Event handler function

**Example:**
```typescript
client.on('text_delta', (event) => {
  console.log('Received:', event.content);
});

client.on('connected', () => {
  console.log('Connected to server');
});

client.on('error', (error) => {
  console.error('Error:', error.message);
});
```

### off()

Unsubscribes from an event.

```typescript
off<K extends keyof RealtimeEventMap>(
  event: K, 
  handler: (data: RealtimeEventMap[K]) => void
): void
```

**Example:**
```typescript
const handler = (event) => console.log(event);
client.on('text_delta', handler);
// Later...
client.off('text_delta', handler);
```

### once()

Subscribes to an event for a single occurrence.

```typescript
once<K extends keyof RealtimeEventMap>(
  event: K, 
  handler: (data: RealtimeEventMap[K]) => void
): void
```

**Example:**
```typescript
client.once('connected', () => {
  console.log('First connection established');
});
```

## Available Events

### Connection Events
- `connected` - Connection established
- `disconnected` - Connection closed
- `reconnecting` - Attempting to reconnect
- `reconnected` - Successfully reconnected

### Message Events
- `text_delta` - Streaming text chunk
- `completion` - Response completion status
- `error` - Error occurred

### Audio Events
- `audio:output` - Binary audio data received
- `audio:input:start` - Recording started
- `audio:input:stop` - Recording stopped
- `audio:level` - Audio level update

### Turn Events
- `user_turn_start` - User's turn to speak
- `user_turn_end` - Agent's turn to respond
- `turn_state_changed` - Turn state changed

### Session Events
- `chat_session_changed` - Active session changed
- `chat_session_name_changed` - Session renamed
- `session_metadata_changed` - Metadata updated

### Voice Events
- `agent_voice_changed` - Agent voice changed
- `voices_list` - Available voices received

### Avatar Events
- `avatar_session_set` - Avatar session established
- `avatars_list` - Available avatars received

## Utility Methods

### setAuthManager()

Sets or updates the AuthManager instance.

```typescript
setAuthManager(authManager: AuthManager): void
```

**Parameters:**
- `authManager` - AuthManager instance

**Example:**
```typescript
const authManager = new AuthManager({ apiUrl: 'https://localhost:8000' });
await authManager.login({ 
  username: 'your-username',
  password: 'your-password' 
});
client.setAuthManager(authManager);
```

### setAuthToken()

Updates the authentication token.

```typescript
setAuthToken(token: string): void
```

**Parameters:**
- `token` (string) - JWT authentication token

**Note:** Causes reconnection if currently connected

**Example:**
```typescript
client.setAuthToken('new-jwt-token');
```

### setSessionId()

Updates the UI session ID.

```typescript
setSessionId(sessionId: string | null): void
```

**Parameters:**
- `sessionId` - Session ID or null

**Note:** Causes reconnection if currently connected

### getTurnManager()

Gets the TurnManager instance.

```typescript
getTurnManager(): TurnManager | null
```

**Returns:** TurnManager instance or null

### getAuthManager()

Gets the AuthManager instance.

```typescript
getAuthManager(): AuthManager | null
```

**Returns:** AuthManager instance or null

### destroy()

Cleans up all resources and closes connections.

```typescript
destroy(): void
```

**Example:**
```typescript
// Clean up when done
client.destroy();
```

## Complete Example

```typescript
import { RealtimeClient, AuthManager, ConnectionState } from '@agentc/realtime-core';

async function main() {
  // Initialize authentication
  const authManager = new AuthManager({
    apiUrl: 'https://localhost:8000' // or process.env.API_URL
  });
  
  // Login with username and password
  const loginResponse = await authManager.login({
    username: 'your-username',
    password: 'your-password'
  });
  
  // Create client with WebSocket URL from login response
  const client = new RealtimeClient({
    apiUrl: loginResponse.wsUrl, // WebSocket URL from login
    authManager,
    enableAudio: true,
    audioConfig: {
      enableInput: true,
      enableOutput: true,
      respectTurnState: true,
      initialVolume: 0.8
    },
    reconnection: {
      maxAttempts: 5,
      initialDelay: 1000
    },
    debug: true
  });
  
  // Set up event handlers
  client.on('connected', () => {
    console.log('✅ Connected to Agent C');
  });
  
  client.on('text_delta', (event) => {
    process.stdout.write(event.content);
  });
  
  client.on('completion', (event) => {
    if (!event.running) {
      console.log('\n📝 Response complete');
    }
  });
  
  client.on('audio:output', (audioData) => {
    console.log('🔊 Audio chunk:', audioData.byteLength, 'bytes');
  });
  
  client.on('user_turn_start', () => {
    console.log('🎤 Your turn to speak');
  });
  
  client.on('error', (error) => {
    console.error('❌ Error:', error.message);
  });
  
  // Connect to the service
  await client.connect();
  
  // Check connection state
  if (client.getConnectionState() === ConnectionState.CONNECTED) {
    // Send a text message
    client.sendText('Hello! Please introduce yourself.');
    
    // Start audio if available
    const audioStatus = client.getAudioStatus();
    if (audioStatus.isAudioEnabled) {
      try {
        await client.startAudioRecording();
        client.startAudioStreaming();
        console.log('🎤 Audio streaming started');
      } catch (error) {
        console.error('Audio setup failed:', error);
      }
    }
    
    // Set voice preference
    client.setAgentVoice('nova');
    
    // Create a new session after 5 seconds
    setTimeout(() => {
      client.newChatSession();
      client.setChatSessionName('Demo Session');
    }, 5000);
  }
  
  // Clean up on exit
  process.on('SIGINT', () => {
    console.log('\nShutting down...');
    client.destroy();
    process.exit(0);
  });
}

main().catch(console.error);
```

## Error Handling

The RealtimeClient throws errors in these situations:

1. **Connection Errors**
   - Invalid API URL
   - Authentication failure
   - Connection timeout
   - Network errors

2. **Configuration Errors**
   - Missing required configuration
   - Invalid configuration values

3. **State Errors**
   - Attempting to send when not connected
   - Audio operations when audio not enabled

4. **Permission Errors**
   - Microphone permission denied
   - Browser doesn't support required APIs

Always wrap async operations in try-catch blocks and listen for error events:

```typescript
// Handle connection errors
try {
  await client.connect();
} catch (error) {
  if (error.message.includes('Authentication')) {
    // Handle auth error
  } else if (error.message.includes('timeout')) {
    // Handle timeout
  }
}

// Handle runtime errors
client.on('error', (error) => {
  console.error('Runtime error:', error);
  // Implement error recovery logic
});
```

## TypeScript Types

The RealtimeClient is fully typed. Key types include:

```typescript
import {
  RealtimeClient,
  RealtimeClientConfig,
  ConnectionState,
  AudioConfig,
  AudioStatus,
  RealtimeEventMap,
  TextDeltaEvent,
  CompletionEvent,
  // ... other event types
} from '@agentc/realtime-core';
```

All event handlers are type-safe, providing IntelliSense and compile-time checking.