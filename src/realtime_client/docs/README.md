# Agent C Realtime SDK Documentation

Welcome to the Agent C Realtime SDK documentation. This SDK provides a powerful, type-safe TypeScript/JavaScript library for building real-time voice and text applications with AI agents, including optional HeyGen avatar support.

## 📦 Packages

The SDK is organized into two main packages:

- **[@agentc/realtime-core](#core-sdk)** - Framework-agnostic TypeScript library with all core functionality
- **[@agentc/realtime-react](#react-bindings)** - React hooks and components for easy integration

## 🚀 Quick Start

```typescript
// Vanilla JavaScript/TypeScript
import { RealtimeClient, AuthManager } from '@agentc/realtime-core';

// Initialize with authentication
const authManager = new AuthManager({
  apiUrl: 'https://localhost:8000'  // Or your Agent C server URL
});

// Login with ChatUser credentials
await authManager.login({ 
  username: 'your-username', 
  password: 'your-password' 
});

// Create and connect client using the WebSocket URL from login
const client = new RealtimeClient({
  apiUrl: authManager.getWebSocketUrl(),  // URL from login response
  authManager,
  enableAudio: true
});

await client.connect();

// Send a message
client.sendText('Hello, Agent!');

// Listen for responses
client.on('text_delta', (event) => {
  console.log(event.content);
});
```

```tsx
// React Application
import { AgentCProvider, useRealtimeClient, useChat } from '@agentc/realtime-react';

function App() {
  return (
    <AgentCProvider config={{ 
      apiUrl: 'https://localhost:8000',  // Your Agent C server URL
      credentials: {
        username: 'your-username',
        password: 'your-password'
      }
    }}>
      <ChatComponent />
    </AgentCProvider>
  );
}

function ChatComponent() {
  const { sendMessage } = useChat();
  
  const handleSend = () => {
    sendMessage('Hello, Agent!');
  };
  
  return <button onClick={handleSend}>Send Message</button>;
}
```

## 📚 Documentation Structure

### Getting Started
- **[Getting Started Guide](./getting-started.md)** - Installation, setup, and your first connection
- **[Architecture Overview](./architecture.md)** - Understanding the SDK design and data flow

### API Reference

#### Core SDK
- **[RealtimeClient](./api-reference/core/RealtimeClient.md)** - Main client class for WebSocket connections
- **[AuthManager](./api-reference/core/AuthManager.md)** - Authentication and token management
- **[TurnManager](./api-reference/core/TurnManager.md)** - Conversation turn control
- **[VoiceManager](./api-reference/core/VoiceManager.md)** - Voice model management
- **[SessionManager](./api-reference/core/SessionManager.md)** - Chat session handling
- **[AvatarManager](./api-reference/core/AvatarManager.md)** - HeyGen avatar integration
- **[AudioInput](./api-reference/core/AudioInput.md)** - Microphone capture and streaming
- **[AudioOutput](./api-reference/core/AudioOutput.md)** - TTS playback

#### React Bindings
- **[AgentCProvider](./api-reference/react/AgentCProvider.md)** - React context provider
- **[React Hooks](./api-reference/react/hooks.md)** - All available React hooks
- **[React Examples](./api-reference/react/examples.md)** - Complete React usage examples

### Guides
- **[Authentication Guide](./guides/authentication.md)** - ChatUser login and JWT token management
- **[Audio Streaming Guide](./guides/audio-streaming.md)** - Binary audio streaming setup
- **[Turn Management Guide](./guides/turn-management.md)** - Understanding conversation flow
- **[Voice Models Guide](./guides/voice-models.md)** - Working with different TTS voices
- **[Avatar Integration Guide](./guides/avatar-integration.md)** - Setting up HeyGen avatars

## 🌟 Key Features

### 🎯 Production-Ready
- **Binary WebSocket streaming** for 33% bandwidth reduction
- **Automatic reconnection** with exponential backoff
- **Token refresh** before expiry
- **Type-safe events** with TypeScript generics

### 🎤 Advanced Audio
- **Web Audio API** with AudioWorklet for optimal performance
- **Turn-aware streaming** prevents talk-over conflicts
- **Multiple voice models** including OpenAI TTS
- **Binary PCM16** transmission without base64 overhead

### 🤖 Avatar Support
- **HeyGen integration** for virtual avatars
- **Automatic voice switching** in avatar mode
- **Session coordination** with Agent C backend

### 📱 Multi-Platform
- **Browser support** for modern web applications
- **Node.js support** for server-side applications
- **React bindings** for React applications
- **Framework agnostic** core library

## 💻 Requirements

- **Node.js** 16.0 or later
- **TypeScript** 4.5 or later (for TypeScript projects)
- **Modern browser** with Web Audio API support (Chrome 66+, Firefox 76+, Safari 14.1+)
- **React** 18.0 or later (for React bindings only)

## 📦 Installation

### NPM
```bash
npm install @agentc/realtime-core
# For React applications
npm install @agentc/realtime-react
```

### Yarn
```bash
yarn add @agentc/realtime-core
# For React applications
yarn add @agentc/realtime-react
```

### PNPM
```bash
pnpm add @agentc/realtime-core
# For React applications
pnpm add @agentc/realtime-react
```

## 🔧 Configuration

The SDK can be configured through environment variables or directly in code:

```typescript
// Environment variables
AGENTC_API_URL=https://localhost:8000  # Your Agent C server URL
AGENTC_USERNAME=your-username
AGENTC_PASSWORD=your-password

// Direct configuration
const authManager = new AuthManager({
  apiUrl: process.env.AGENTC_API_URL || 'https://localhost:8000'
});

// Login to get JWT token and WebSocket URL
await authManager.login({
  username: process.env.AGENTC_USERNAME,
  password: process.env.AGENTC_PASSWORD
});

const client = new RealtimeClient({
  apiUrl: authManager.getWebSocketUrl(),  // WebSocket URL from login
  authManager,  // Handles JWT token automatically
  enableAudio: true,
  audioConfig: {
    enableInput: true,
    enableOutput: true,
    sampleRate: 16000,
    respectTurnState: true
  },
  reconnection: {
    maxAttempts: 5,
    initialDelay: 1000,
    maxDelay: 30000
  }
});
```

## 🧪 Examples

Check out our example applications:

- **[Basic Chat](../examples/basic-chat)** - Simple text chat with an agent
- **[Voice Assistant](../examples/voice-assistant)** - Voice-enabled AI assistant
- **[Avatar Demo](../examples/avatar-demo)** - HeyGen avatar integration
- **[React App](../examples/react-app)** - Complete React application

## 🛠️ Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/agentc-ai/realtime-sdk.git
cd realtime-sdk

# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run tests
pnpm test

# Start development mode
pnpm dev
```

### Package Structure

```
packages/
├── core/               # Core SDK package
│   ├── src/
│   │   ├── client/    # WebSocket client
│   │   ├── auth/      # Authentication
│   │   ├── audio/     # Audio system
│   │   ├── session/   # Session management
│   │   ├── voice/     # Voice management
│   │   ├── avatar/    # Avatar integration
│   │   └── events/    # Event types
│   └── dist/          # Built files
└── react/             # React bindings
    ├── src/
    │   ├── providers/ # Context providers
    │   ├── hooks/     # React hooks
    │   └── components/# UI components
    └── dist/          # Built files
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## 📄 License

This SDK is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

## 🆘 Support

- **Documentation**: You are here!
- **GitHub Issues**: Report bugs or request features
- **Discord**: Join our community
- **Email**: Contact support

## 🔗 Related Resources

- [Agent C Platform Documentation](https://localhost:8000/docs)
- [API Reference](https://localhost:8000/api/docs)
- [HeyGen Documentation](https://docs.heygen.com)
- [Web Audio API Reference](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

Built with ❤️ by the Agent C team