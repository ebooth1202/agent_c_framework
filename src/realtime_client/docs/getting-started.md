# Getting Started with Agent C Realtime SDK

This guide will help you get up and running with the Agent C Realtime SDK in minutes. We'll cover installation, basic setup, and creating your first real-time connection.

## Prerequisites

Before you begin, ensure you have:

- **Node.js** version 16.0 or later
- **An Agent C API key** (get one at [agentc.ai](https://agentc.ai))
- **A modern web browser** (Chrome 66+, Firefox 76+, or Safari 14.1+)
- **Basic knowledge** of JavaScript/TypeScript

For React applications, you'll also need:
- **React** version 18.0 or later

## Installation

Choose your package manager and install the appropriate packages:

### Core SDK (Vanilla JavaScript/TypeScript)

```bash
# NPM
npm install @agentc/realtime-core

# Yarn
yarn add @agentc/realtime-core

# PNPM
pnpm add @agentc/realtime-core
```

### React Bindings (For React Applications)

```bash
# NPM
npm install @agentc/realtime-core @agentc/realtime-react

# Yarn
yarn add @agentc/realtime-core @agentc/realtime-react

# PNPM
pnpm add @agentc/realtime-core @agentc/realtime-react
```

## Basic Setup

### Option 1: Vanilla JavaScript/TypeScript

Create a simple HTML file with the SDK:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Agent C Realtime Demo</title>
</head>
<body>
    <div id="app">
        <button id="connect">Connect</button>
        <button id="send" disabled>Send Message</button>
        <div id="messages"></div>
    </div>
    
    <script type="module">
        import { RealtimeClient, AuthManager } from '@agentc/realtime-core';
        
        // Initialize authentication
        const authManager = new AuthManager({
            apiUrl: 'https://api.agentc.ai'
        });
        
        // Login with your API key
        await authManager.login('your-api-key');
        
        // Create the client
        const client = new RealtimeClient({
            apiUrl: 'wss://api.agentc.ai/rt/ws',
            authManager,
            debug: true // Enable debug logging
        });
        
        // Handle connection
        document.getElementById('connect').onclick = async () => {
            await client.connect();
            document.getElementById('send').disabled = false;
        };
        
        // Send a message
        document.getElementById('send').onclick = () => {
            client.sendText('Hello, Agent!');
        };
        
        // Listen for responses
        client.on('text_delta', (event) => {
            const messages = document.getElementById('messages');
            messages.innerHTML += event.content;
        });
        
        // Handle connection events
        client.on('connected', () => {
            console.log('Connected to Agent C!');
        });
        
        client.on('disconnected', ({ reason }) => {
            console.log('Disconnected:', reason);
        });
    </script>
</body>
</html>
```

### Option 2: Node.js Application

```typescript
import { RealtimeClient, AuthManager } from '@agentc/realtime-core';

async function main() {
    // Initialize authentication
    const authManager = new AuthManager({
        apiUrl: 'https://api.agentc.ai'
    });
    
    // Login with API key
    await authManager.login(process.env.AGENTC_API_KEY!);
    
    // Create and configure client
    const client = new RealtimeClient({
        apiUrl: 'wss://api.agentc.ai/rt/ws',
        authManager,
        enableAudio: false, // Audio not supported in Node.js
        debug: true
    });
    
    // Set up event handlers
    client.on('connected', () => {
        console.log('Connected to Agent C!');
        
        // Send initial message
        client.sendText('Hello from Node.js!');
    });
    
    client.on('text_delta', (event) => {
        process.stdout.write(event.content);
    });
    
    client.on('completion', (event) => {
        if (!event.running) {
            console.log('\n[Response complete]');
        }
    });
    
    client.on('error', (error) => {
        console.error('Error:', error.message);
    });
    
    // Connect to the service
    await client.connect();
    
    // Keep the process running
    process.stdin.resume();
}

main().catch(console.error);
```

### Option 3: React Application

```tsx
// App.tsx
import React from 'react';
import { AgentCProvider } from '@agentc/realtime-react';
import ChatInterface from './ChatInterface';

function App() {
    return (
        <AgentCProvider 
            config={{
                apiUrl: 'wss://api.agentc.ai/rt/ws',
                apiKey: process.env.REACT_APP_AGENTC_API_KEY,
                enableAudio: true,
                debug: true
            }}
        >
            <ChatInterface />
        </AgentCProvider>
    );
}

export default App;
```

```tsx
// ChatInterface.tsx
import React, { useState } from 'react';
import { 
    useRealtimeClient, 
    useConnection, 
    useChat 
} from '@agentc/realtime-react';

function ChatInterface() {
    const { connect, disconnect, isConnected } = useConnection();
    const { messages, sendMessage } = useChat();
    const [input, setInput] = useState('');
    
    const handleConnect = async () => {
        try {
            await connect();
        } catch (error) {
            console.error('Connection failed:', error);
        }
    };
    
    const handleSend = () => {
        if (input.trim() && isConnected) {
            sendMessage(input);
            setInput('');
        }
    };
    
    return (
        <div>
            <button onClick={isConnected ? disconnect : handleConnect}>
                {isConnected ? 'Disconnect' : 'Connect'}
            </button>
            
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={msg.role}>
                        {msg.content}
                    </div>
                ))}
            </div>
            
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                disabled={!isConnected}
            />
            <button onClick={handleSend} disabled={!isConnected}>
                Send
            </button>
        </div>
    );
}

export default ChatInterface;
```

## First Connection

Let's establish your first connection and send a message:

```typescript
import { RealtimeClient, AuthManager } from '@agentc/realtime-core';

async function quickStart() {
    // Step 1: Authenticate
    const authManager = new AuthManager({
        apiUrl: 'https://api.agentc.ai'
    });
    
    const loginResponse = await authManager.login('your-api-key');
    console.log('Logged in! Available voices:', loginResponse.voices);
    
    // Step 2: Create client
    const client = new RealtimeClient({
        apiUrl: 'wss://api.agentc.ai/rt/ws',
        authManager,
        enableAudio: true,
        audioConfig: {
            enableInput: true,
            enableOutput: true,
            sampleRate: 16000
        }
    });
    
    // Step 3: Set up event handlers
    client.on('connected', () => {
        console.log('✅ Connected!');
    });
    
    client.on('text_delta', (event) => {
        // Streaming text response
        process.stdout.write(event.content);
    });
    
    client.on('audio:output', (audioData) => {
        // Binary audio data received
        console.log('Received audio chunk:', audioData.byteLength, 'bytes');
    });
    
    client.on('error', (error) => {
        console.error('❌ Error:', error.message);
    });
    
    // Step 4: Connect
    await client.connect();
    
    // Step 5: Send your first message
    client.sendText('Hello! Can you introduce yourself?');
    
    // Optional: Start audio streaming
    if (client.getAudioStatus().isAudioEnabled) {
        await client.startAudioRecording();
        client.startAudioStreaming();
    }
}

quickStart().catch(console.error);
```

## Environment Configuration

For production applications, use environment variables:

### .env file
```bash
# Agent C Configuration
AGENTC_API_URL=wss://api.agentc.ai/rt/ws
AGENTC_API_KEY=your-api-key-here
AGENTC_DEBUG=true

# Optional: HeyGen Configuration for Avatars
HEYGEN_API_KEY=your-heygen-key
```

### Loading configuration
```typescript
import { RealtimeClient, AuthManager } from '@agentc/realtime-core';
import dotenv from 'dotenv';

dotenv.config();

const authManager = new AuthManager({
    apiUrl: process.env.AGENTC_API_URL!
});

await authManager.login(process.env.AGENTC_API_KEY!);

const client = new RealtimeClient({
    apiUrl: process.env.AGENTC_API_URL!,
    authManager,
    debug: process.env.AGENTC_DEBUG === 'true'
});
```

## Adding Audio Support

To enable voice interactions:

```typescript
const client = new RealtimeClient({
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    authManager,
    enableAudio: true,
    audioConfig: {
        enableInput: true,    // Enable microphone
        enableOutput: true,   // Enable TTS playback
        sampleRate: 16000,    // Audio sample rate
        respectTurnState: true, // Prevent talk-over
        initialVolume: 0.8    // Initial volume (0-1)
    }
});

// Request microphone permission and start recording
await client.startAudioRecording();

// Start streaming audio to server
client.startAudioStreaming();

// Monitor audio levels
const status = client.getAudioStatus();
console.log('Audio level:', status.currentLevel);
console.log('Is recording:', status.isRecording);

// Stop audio when done
client.stopAudioStreaming();
client.stopAudioRecording();
```

## Handling Events

The SDK emits various events you can listen to:

```typescript
// Connection events
client.on('connected', () => console.log('Connected'));
client.on('disconnected', ({ code, reason }) => console.log('Disconnected:', reason));
client.on('reconnecting', ({ attempt }) => console.log('Reconnecting, attempt:', attempt));

// Message events
client.on('text_delta', (event) => console.log('Text chunk:', event.content));
client.on('completion', (event) => console.log('Complete:', !event.running));

// Audio events
client.on('audio:output', (audioData) => console.log('Audio received'));
client.on('audio:input:start', () => console.log('Recording started'));
client.on('audio:input:stop', () => console.log('Recording stopped'));

// Turn events
client.on('user_turn_start', () => console.log('Your turn to speak'));
client.on('user_turn_end', () => console.log('Agent is responding'));

// Voice events
client.on('agent_voice_changed', (event) => console.log('Voice changed to:', event.voice_id));

// Error events
client.on('error', (error) => console.error('Error:', error));
```

## Error Handling

Always implement proper error handling:

```typescript
try {
    await client.connect();
} catch (error) {
    if (error.message.includes('Authentication')) {
        console.error('Invalid API key');
    } else if (error.message.includes('timeout')) {
        console.error('Connection timeout - check your network');
    } else {
        console.error('Connection failed:', error);
    }
}

// Handle audio permission errors
try {
    await client.startAudioRecording();
} catch (error) {
    if (error.name === 'NotAllowedError') {
        console.error('Microphone permission denied');
    } else if (error.name === 'NotFoundError') {
        console.error('No microphone found');
    } else {
        console.error('Audio initialization failed:', error);
    }
}
```

## TypeScript Support

The SDK is written in TypeScript and provides full type definitions:

```typescript
import { 
    RealtimeClient, 
    AuthManager,
    ConnectionState,
    RealtimeEventMap,
    TextDeltaEvent,
    CompletionEvent 
} from '@agentc/realtime-core';

// All event handlers are type-safe
client.on('text_delta', (event: TextDeltaEvent) => {
    // TypeScript knows event.content is a string
    console.log(event.content);
});

// Configuration is fully typed
const config: RealtimeClientConfig = {
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    authManager,
    enableAudio: true,
    reconnection: {
        maxAttempts: 5,
        initialDelay: 1000
    }
};

// Check connection state with enum
if (client.getConnectionState() === ConnectionState.CONNECTED) {
    // Connected and ready
}
```

## Next Steps

Now that you have the basics working:

1. **Explore the API Reference** to learn about all available methods and options
2. **Read the Guides** for in-depth coverage of specific features:
   - [Authentication](./guides/authentication.md) - Advanced auth scenarios
   - [Audio Streaming](./guides/audio-streaming.md) - Voice interactions
   - [Turn Management](./guides/turn-management.md) - Conversation flow
   - [Voice Models](./guides/voice-models.md) - TTS options
   - [Avatar Integration](./guides/avatar-integration.md) - Virtual avatars

3. **Check out the Examples** for complete applications:
   - Basic chat application
   - Voice assistant
   - Avatar demo
   - React application

## Troubleshooting

### Common Issues

**Connection fails immediately**
- Check your API key is valid
- Verify the API URL is correct
- Ensure you're calling `authManager.login()` before connecting

**No audio output**
- Check browser supports Web Audio API
- Verify `enableOutput: true` in audio config
- Check system volume and browser permissions

**Microphone not working**
- Browser requires HTTPS for microphone access
- User must grant permission when prompted
- Check `enableInput: true` in audio config

**Messages not appearing**
- Ensure you're listening to the correct events
- Check the console for error messages
- Verify the connection is established

### Getting Help

If you encounter issues:

1. Check the [documentation](./README.md)
2. Search [GitHub issues](https://github.com/agentc-ai/realtime-sdk/issues)
3. Join our [Discord community](https://discord.gg/agentc)
4. Contact support at support@agentc.ai

---

Ready to build something amazing? Let's go! 🚀