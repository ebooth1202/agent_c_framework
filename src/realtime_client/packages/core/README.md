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

## 📚 Documentation

For comprehensive documentation, API reference, and advanced usage:

- **[Complete API Reference](../../docs/api-reference/core/)** - Full documentation for all classes and methods
- **[RealtimeClient Guide](../../docs/api-reference/core/RealtimeClient.md)** - Main client API and configuration
- **[Authentication Guide](../../docs/api-reference/core/AuthManager.md)** - Authentication patterns and token management
- **[Event System Reference](../../docs/api-reference/core/EventSystem.md)** - Complete event types and handlers
- **[Audio System](../../docs/api-reference/core/AudioInput.md)** - Audio input, output, and processing
- **[Turn Management](../../docs/api-reference/core/TurnManager.md)** - Conversation flow control
- **[Session Management](../../docs/api-reference/core/SessionManager.md)** - Chat session handling
- **[TypeScript Types](../../docs/api-reference/core/Types.md)** - Full type definitions

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

## Key APIs

### RealtimeClient

The main client for WebSocket communication. [See full documentation →](../../docs/api-reference/core/RealtimeClient.md)

```typescript
const client = new RealtimeClient({
  apiUrl: string,
  authManager: AuthManager,
  audioConfig?: AudioConfig,
  connectionConfig?: ConnectionConfig
});

// Core methods
await client.connect();
await client.sendText('Hello!');
await client.startAudioStream();
```

### AuthManager

Handles authentication and token lifecycle. [See full documentation →](../../docs/api-reference/core/AuthManager.md)

```typescript
const authManager = new AuthManager({ apiUrl });

// Development mode
await authManager.login({ username, password });

// Production mode
await authManager.initializeFromPayload(tokenPayload);
```

### Event System

Comprehensive typed events for all interactions. [See full event reference →](../../docs/api-reference/core/events.md)

```typescript
// Message streaming
client.on('text:delta', (event) => { /* partial text */ });
client.on('text:complete', (event) => { /* full message */ });

// Audio streaming
client.on('audio:output', (data: ArrayBuffer) => { /* audio data */ });

// Turn management
client.on('user_turn_start', () => { /* user can speak */ });
client.on('agent_turn_start', () => { /* agent speaking */ });
```

## Configuration

For detailed configuration options, see the [Client Configuration Guide](../../docs/api-reference/core/ClientConfig.md).

### Basic Configuration

```typescript
const client = new RealtimeClient({
  apiUrl: 'wss://api.agentc.ai/realtime',
  authManager: authManager,
  audioConfig: {
    enableAudio: true,
    enableVAD: true
  },
  connectionConfig: {
    autoReconnect: true
  }
});
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

## Advanced Topics

For advanced usage patterns and detailed guides:

- **[Message Handlers](../../docs/api-reference/core/AdvancedMessageHandlers.md)** - Custom message aggregation and processing
- **[Session Management](../../docs/api-reference/core/SessionManager.md)** - Multi-session handling and persistence
- **[Voice Management](../../docs/api-reference/core/VoiceManager.md)** - Voice model selection and configuration
- **[Reconnection Strategies](../../docs/api-reference/core/ReconnectionManager.md)** - Connection resilience and recovery
- **[Avatar Integration](../../docs/api-reference/core/AvatarManager.md)** - HeyGen avatar session management
- **[Event Stream Processing](../../docs/api-reference/core/EventStreamProcessor.md)** - Advanced event handling patterns

## TypeScript Support

Full TypeScript support with comprehensive type definitions. [See complete type reference →](../../docs/api-reference/core/Types.md)

```typescript
import type {
  RealtimeClient,
  RealtimeConfig,
  AuthManager,
  ChatMessage,
  ChatSession,
  // ... and many more
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

## Example Usage

For more examples and patterns, check the [examples directory](./examples) or see the comprehensive documentation.

### Voice-Enabled Chat

```typescript
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

// Setup authentication
const authManager = new AuthManager({ apiUrl: 'https://api.agentc.ai' });
await authManager.login({ username, password });

// Create client with voice support
const client = new RealtimeClient({
  apiUrl: authManager.getWebSocketUrl(),
  authManager,
  audioConfig: {
    enableAudio: true,
    enableVAD: true
  }
});

// Connect and wait for initialization
await client.connect();
await new Promise(resolve => {
  client.on('initialization:complete', resolve);
});

// Handle messages
client.on('text:complete', (event) => {
  console.log(`${event.role}: ${event.text}`);
});

// Start voice conversation
await client.startAudioStream();
```

## Contributing

See [Contributing Guide](../../CONTRIBUTING.md) for development setup and guidelines.

## License

MIT

## Resources

- **[📚 Full Documentation](../../docs/api-reference/core/)** - Complete API reference and guides
- **[🎯 Quick Start Guide](../../docs/api-reference/core/index.md)** - Get up and running quickly
- **[💡 Examples](./examples)** - Sample implementations and patterns
- **[🧪 Testing Guide](../../docs/testing_standards_and_architecture.md)** - Testing approaches and standards
- **[🔧 API Implementation Guide](../../docs/../api/docs/realtime_api_implementation_guide.md)** - Server API specification