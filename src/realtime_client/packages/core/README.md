# @agentc/realtime-core

Core SDK for Agent C Realtime platform. Provides WebSocket-based real-time communication with AI agents, supporting both voice and text interactions.

## Features

- 🎙️ **Real-time Voice Streaming** - High-performance audio with WebRTC
- 💬 **Streaming Text Chat** - Real-time text with typing indicators
- 🔄 **Binary Protocol** - 33% bandwidth savings for audio
- 🎯 **Turn Management** - Sophisticated conversation flow control
- 🔌 **Event-Driven Architecture** - Comprehensive event system
- 🎭 **Avatar Support** - HeyGen avatar integration
- 🔐 **Flexible Authentication** - Development and production patterns
- ♻️ **Automatic Reconnection** - Resilient connection management

## Installation

```bash
npm install @agentc/realtime-core
```

### Audio Worklet Setup

For voice features, deploy the audio worklet to your public directory:

```bash
cp node_modules/@agentc/realtime-core/dist/worklets/audio-processor.worklet.js public/worklets/
```

## Quick Start

```typescript
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

// Create auth manager
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai'
});

// Authenticate (development mode)
await authManager.login({
  username: 'your-username',
  password: 'your-password'
});

// Create and connect client
const client = new RealtimeClient({
  apiUrl: authManager.getWebSocketUrl(),
  authManager: authManager,
  audioConfig: {
    enableAudio: true,
    enableVAD: true
  }
});

await client.connect();

// Listen for initialization events (automatic)
client.on('chat_user_data', (event) => {
  console.log('User:', event.user);
});

client.on('initialization:complete', () => {
  console.log('Ready to chat!');
});

// Send messages
await client.sendText('Hello!');

// Start voice conversation
await client.startAudioStream();
```

## Core Concepts

### Authentication

The SDK supports two authentication patterns:

#### Development Mode
Direct login with ChatUser credentials:

```typescript
const authManager = new AuthManager();
await authManager.login({
  username: 'dev-user',
  password: 'dev-password'
});
```

#### Production Mode
Token-based authentication from your backend:

```typescript
// Your backend provides tokens
const tokens = await yourBackend.getAgentCTokens();

// Initialize with tokens (no credentials)
await authManager.initializeFromPayload({
  agent_c_token: tokens.jwt_token,
  websocket_url: tokens.websocket_url,
  heygen_token: tokens.heygen_token,
  expires_at: tokens.expires_at
});
```

### Event-Driven Architecture

After connection, the SDK automatically receives 6 initialization events:

```typescript
// These events are sent automatically
client.on('chat_user_data', (e) => { /* User profile */ });
client.on('voice_list', (e) => { /* Available voices */ });
client.on('agent_list', (e) => { /* Available agents */ });
client.on('avatar_list', (e) => { /* Available avatars */ });
client.on('tool_catalog', (e) => { /* Available tools */ });
client.on('chat_session_changed', (e) => { /* Current session */ });

// Fired when all initialization is complete
client.on('initialization:complete', () => {
  // Ready for interaction
});
```

### Binary Audio Protocol

The SDK uses an efficient binary protocol for audio:

- **Format**: PCM16 at 24000Hz
- **Transport**: Raw ArrayBuffer over WebSocket
- **Processing**: Off-thread via AudioWorklet
- **Compression**: 33% bandwidth savings vs JSON

```typescript
// Audio is automatically handled
client.on('audio:output', (audioData: ArrayBuffer) => {
  // Binary audio frames are automatically played
  console.log('Audio frame size:', audioData.byteLength);
});
```

## API Reference

### RealtimeClient

Main client for WebSocket communication.

```typescript
class RealtimeClient {
  constructor(config: RealtimeConfig);
  
  // Connection
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;
  
  // Messaging
  sendText(text: string): Promise<void>;
  
  // Audio
  startAudioStream(): Promise<void>;
  stopAudioStream(): Promise<void>;
  
  // Events
  on(event: string, handler: Function): void;
  off(event: string, handler: Function): void;
  emit(event: string, data?: any): void;
  
  // Session
  createSession(name?: string): Promise<ChatSession>;
  switchSession(sessionId: string): Promise<void>;
  
  // Voice
  setVoiceModel(voiceId: string): Promise<void>;
  getVoiceModel(): string;
}
```

### AuthManager

Handles authentication and token management.

```typescript
class AuthManager {
  constructor(config?: AuthConfig);
  
  // Development mode - direct login
  login(credentials: LoginCredentials): Promise<LoginResponse>;
  
  // Production mode - token initialization
  initializeFromPayload(payload: TokenPayload): Promise<void>;
  
  // Token management
  getToken(): string | null;
  getWebSocketUrl(): string;
  isAuthenticated(): boolean;
  
  // Events
  on('token-expiring', handler: Function): void;
  on('token-refreshed', handler: Function): void;
}
```

### Event System

Comprehensive event types for all interactions:

```typescript
// Connection events
client.on('connected', (event: ConnectedEvent) => {});
client.on('disconnected', (event: DisconnectedEvent) => {});
client.on('error', (event: ErrorEvent) => {});

// Message events
client.on('text:delta', (event: TextDeltaEvent) => {});
client.on('text:complete', (event: TextCompleteEvent) => {});
client.on('typing:start', (event: TypingStartEvent) => {});

// Audio events
client.on('audio:output', (data: ArrayBuffer) => {});
client.on('audio:start', (event: AudioStartEvent) => {});
client.on('audio:stop', (event: AudioStopEvent) => {});

// Turn management
client.on('user_turn_start', (event: UserTurnStartEvent) => {});
client.on('agent_turn_start', (event: AgentTurnStartEvent) => {});
```

## Configuration

### RealtimeConfig

```typescript
interface RealtimeConfig {
  apiUrl: string;              // WebSocket URL
  authManager: AuthManager;    // Auth manager instance
  
  audioConfig?: {
    enableAudio?: boolean;      // Enable audio features
    enableVAD?: boolean;        // Voice Activity Detection
    vadThreshold?: number;      // VAD sensitivity (0-1)
    sampleRate?: number;        // Audio sample rate
    echoCancellation?: boolean; // Echo cancellation
    noiseSuppression?: boolean; // Noise suppression
  };
  
  connectionConfig?: {
    autoReconnect?: boolean;    // Auto-reconnect on disconnect
    maxReconnectAttempts?: number;
    reconnectDelay?: number;    // Base delay in ms
    heartbeatInterval?: number; // Keepalive interval
  };
  
  debug?: boolean;              // Enable debug logging
}
```

### AuthConfig

```typescript
interface AuthConfig {
  apiUrl?: string;              // API base URL
  tokenRefreshBuffer?: number;  // Seconds before expiry to refresh
  storage?: 'memory' | 'session'; // Token storage location
}
```

## Audio System

### Audio Processing Pipeline

```
Microphone → getUserMedia → AudioContext → AudioWorklet → PCM16 → WebSocket → Server
                                               ↓
                                         (Resampling)
                                          24000Hz
```

### AudioWorklet Setup

The audio worklet handles off-thread processing:

1. Place worklet in public directory
2. SDK automatically loads from `/worklets/audio-processor.worklet.js`
3. Handles Float32 to PCM16 conversion
4. Automatic resampling to 24000Hz

### Turn Management

Prevents users and agents from talking over each other:

```typescript
// Listen for turn events
client.on('user_turn_start', () => {
  // User can speak
  enableMicrophone();
});

client.on('user_turn_end', () => {
  // User should stop
  disableMicrophone();
});

client.on('agent_turn_start', () => {
  // Agent is speaking
  showSpeakingIndicator();
});
```

## Advanced Usage

### Custom Event Handlers

```typescript
// Create event aggregator
class MessageAggregator {
  private chunks: Map<string, string[]> = new Map();
  
  constructor(client: RealtimeClient) {
    client.on('text:delta', this.handleDelta.bind(this));
    client.on('text:complete', this.handleComplete.bind(this));
  }
  
  private handleDelta(event: TextDeltaEvent) {
    if (!this.chunks.has(event.messageId)) {
      this.chunks.set(event.messageId, []);
    }
    this.chunks.get(event.messageId)!.push(event.delta);
  }
  
  private handleComplete(event: TextCompleteEvent) {
    const chunks = this.chunks.get(event.messageId);
    console.log('Full message:', chunks?.join(''));
    this.chunks.delete(event.messageId);
  }
}
```

### Session Management

```typescript
// Create new session
const session = await client.createSession('Customer Support');

// List sessions
const sessions = await client.getSessions();

// Switch session
await client.switchSession(session.id);

// Session events
client.on('session:created', (event) => {
  console.log('New session:', event.session);
});

client.on('session:switched', (event) => {
  console.log('Switched to:', event.session);
});
```

### Voice Model Management

```typescript
// Get available voices
client.on('voice_list', (event) => {
  const voices = event.voices;
  // [{ voice_id: 'nova', name: 'Nova', language: 'en-US' }, ...]
});

// Set voice model
await client.setVoiceModel('nova');

// Special modes
await client.setVoiceModel('none');   // Text-only mode
await client.setVoiceModel('avatar'); // Avatar handles audio
```

### Error Handling

```typescript
// Connection errors
client.on('error', (event: ErrorEvent) => {
  if (event.fatal) {
    // Fatal error - requires user intervention
    showErrorDialog(event.error);
  } else {
    // Non-fatal - will auto-retry
    console.warn('Temporary error:', event.error);
  }
});

// Reconnection handling
client.on('reconnecting', (event) => {
  showReconnectingUI(event.attempt, event.maxAttempts);
});

client.on('connected', () => {
  hideReconnectingUI();
  // Initialization events will follow
});
```

## TypeScript Support

Full TypeScript support with comprehensive types:

```typescript
import type {
  RealtimeClient,
  RealtimeConfig,
  AuthManager,
  LoginCredentials,
  LoginResponse,
  TokenPayload,
  ChatMessage,
  ChatSession,
  Voice,
  Agent,
  Avatar,
  Tool,
  UserProfile,
  ConnectionState,
  AudioState,
  TurnState,
  TextDeltaEvent,
  TextCompleteEvent,
  AudioOutputEvent,
  ChatUserDataEvent,
  VoiceListEvent,
  AgentListEvent
} from '@agentc/realtime-core';
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14.1+
- Edge 90+

Requirements:
- HTTPS (for microphone access)
- WebSocket support
- WebRTC support (for audio)
- AudioWorklet support

## Performance

### Metrics

- **WebSocket overhead**: < 5% CPU
- **Audio processing**: < 10% CPU (off-thread)
- **Memory usage**: ~50MB baseline
- **Latency**: < 100ms round-trip
- **Bandwidth**: ~4KB/s (audio), ~1KB/s (text)

### Optimization Tips

```typescript
// 1. Reuse client instance
const client = new RealtimeClient(config);
// Don't create multiple clients

// 2. Clean up when done
await client.disconnect();

// 3. Use event throttling for UI updates
import { throttle } from 'lodash';
const throttledUpdate = throttle(updateUI, 100);
client.on('audio:output', throttledUpdate);

// 4. Batch message updates
let messageBuffer = [];
setInterval(() => {
  if (messageBuffer.length > 0) {
    updateMessages(messageBuffer);
    messageBuffer = [];
  }
}, 100);
```

## Troubleshooting

### Common Issues

**WebSocket fails to connect**
- Verify HTTPS is enabled
- Check authentication credentials
- Ensure firewall allows WebSocket

**No audio input**
- Check microphone permissions
- Verify HTTPS (required for getUserMedia)
- Ensure audio worklet is deployed

**Audio is choppy**
- Check network bandwidth
- Verify CPU usage < 80%
- Try disabling video if using avatars

**User data is undefined**
- Wait for `initialization:complete` event
- Check authentication was successful
- Verify WebSocket is connected

## Examples

### Simple Chat Bot

```typescript
async function createChatBot() {
  const authManager = new AuthManager();
  await authManager.login({ username, password });
  
  const client = new RealtimeClient({
    apiUrl: authManager.getWebSocketUrl(),
    authManager
  });
  
  await client.connect();
  
  // Wait for initialization
  await new Promise(resolve => {
    client.on('initialization:complete', resolve);
  });
  
  // Chat bot logic
  client.on('text:complete', async (event) => {
    if (event.role === 'user') {
      console.log('User said:', event.text);
      
      // Bot responds
      if (event.text.toLowerCase().includes('help')) {
        await client.sendText('How can I assist you today?');
      }
    }
  });
  
  console.log('Chat bot ready!');
}
```

### Voice Assistant

```typescript
async function createVoiceAssistant() {
  const client = new RealtimeClient({
    apiUrl,
    authManager,
    audioConfig: {
      enableAudio: true,
      enableVAD: true,
      vadThreshold: 0.3
    }
  });
  
  await client.connect();
  
  // Voice interaction
  client.on('user_turn_start', () => {
    console.log('Listening...');
  });
  
  client.on('agent_turn_start', () => {
    console.log('Agent speaking...');
  });
  
  client.on('vad:speech_start', () => {
    console.log('User started speaking');
  });
  
  client.on('vad:speech_end', () => {
    console.log('User stopped speaking');
  });
  
  // Start listening
  await client.startAudioStream();
}
```

## Contributing

See [Contributing Guide](../../CONTRIBUTING.md) for development setup and guidelines.

## License

MIT

## Support

- [Documentation](../../docs)
- [API Reference](../../docs/api-reference/core)
- [Examples](./examples)
- [Issue Tracker](https://github.com/agentc/realtime-sdk/issues)