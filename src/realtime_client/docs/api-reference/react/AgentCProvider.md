# AgentCProvider API Reference

The `AgentCProvider` component provides the Agent C Realtime SDK context to React applications, managing client lifecycle and configuration.

## Import

```typescript
import { AgentCProvider } from '@agentc/realtime-react';
```

## Overview

AgentCProvider is a React context provider that creates and manages a RealtimeClient instance, making it available to child components through React hooks.

## Props

```typescript
interface AgentCProviderProps {
  config: AgentCConfig;
  children: React.ReactNode;
  onError?: (error: Error) => void;
  autoConnect?: boolean;
  debug?: boolean;
}
```

### Configuration

```typescript
interface AgentCConfig {
  // Required
  apiUrl: string;           // WebSocket URL
  
  // Authentication (one required)
  apiKey?: string;          // API key for authentication
  authToken?: string;       // JWT token (if already authenticated)
  
  // Optional
  authApiUrl?: string;      // Auth API URL (defaults to apiUrl base)
  enableAudio?: boolean;    // Enable audio features (default: false)
  audioConfig?: AudioConfig; // Audio configuration
  reconnection?: ReconnectionConfig; // Reconnection settings
  enableTurnManager?: boolean; // Turn management (default: true)
}

interface AudioConfig {
  enableInput?: boolean;    // Enable microphone (default: true)
  enableOutput?: boolean;   // Enable TTS (default: true)
  sampleRate?: number;      // Sample rate (default: 16000)
  respectTurnState?: boolean; // Respect turns (default: true)
  initialVolume?: number;   // Initial volume 0-1 (default: 1)
}

interface ReconnectionConfig {
  maxAttempts?: number;     // Max reconnection attempts (default: 5)
  initialDelay?: number;    // Initial delay in ms (default: 1000)
  maxDelay?: number;        // Max delay in ms (default: 30000)
}
```

## Basic Usage

```tsx
import { AgentCProvider } from '@agentc/realtime-react';

function App() {
  return (
    <AgentCProvider 
      config={{
        apiUrl: 'wss://api.agentc.ai/rt/ws',
        apiKey: 'your-api-key',
        enableAudio: true
      }}
      autoConnect={true}
      debug={true}
    >
      <YourComponents />
    </AgentCProvider>
  );
}
```

## Props Details

### config (required)

The configuration object for the RealtimeClient.

**Example:**
```tsx
<AgentCProvider 
  config={{
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    apiKey: process.env.REACT_APP_AGENTC_KEY,
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
    }
  }}
>
```

### children (required)

React components that will have access to the Agent C context.

### onError (optional)

Error handler callback for client errors.

**Example:**
```tsx
<AgentCProvider 
  config={config}
  onError={(error) => {
    console.error('Agent C Error:', error);
    showErrorNotification(error.message);
  }}
>
```

### autoConnect (optional)

Whether to automatically connect when the provider mounts.

**Default:** `false`

**Example:**
```tsx
<AgentCProvider 
  config={config}
  autoConnect={true}  // Connect immediately
>
```

### debug (optional)

Enable debug logging.

**Default:** `false`

**Example:**
```tsx
<AgentCProvider 
  config={config}
  debug={process.env.NODE_ENV === 'development'}
>
```

## Context Value

The provider makes the following context available:

```typescript
interface AgentCContextValue {
  client: RealtimeClient | null;
  isInitialized: boolean;
  error: Error | null;
}
```

## Environment Variables

The provider can read configuration from environment variables:

```bash
# .env
REACT_APP_AGENTC_API_URL=wss://api.agentc.ai/rt/ws
REACT_APP_AGENTC_API_KEY=your-api-key
REACT_APP_AGENTC_DEBUG=true
```

```tsx
// Will use env vars as defaults
<AgentCProvider 
  config={{
    apiUrl: process.env.REACT_APP_AGENTC_API_URL!,
    apiKey: process.env.REACT_APP_AGENTC_API_KEY!
  }}
  debug={process.env.REACT_APP_AGENTC_DEBUG === 'true'}
>
```

## Authentication Methods

### Method 1: API Key

```tsx
<AgentCProvider 
  config={{
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    apiKey: 'sk-abc123...'  // Provider handles auth
  }}
>
```

### Method 2: Pre-authenticated Token

```tsx
<AgentCProvider 
  config={{
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    authToken: 'jwt-token-here'  // Already have token
  }}
>
```

### Method 3: Custom Auth Manager

```tsx
import { AuthManager } from '@agentc/realtime-core';

// Create auth manager separately
const authManager = new AuthManager({
  apiUrl: 'https://api.agentc.ai'
});

// Login before rendering
await authManager.login('api-key');

// Pass authenticated manager
<AgentCProvider 
  config={{
    apiUrl: 'wss://api.agentc.ai/rt/ws',
    authManager  // Use existing auth
  }}
>
```

## Complete Example

```tsx
import React, { useState } from 'react';
import { 
  AgentCProvider, 
  useConnection, 
  useChat 
} from '@agentc/realtime-react';

function App() {
  const [error, setError] = useState<Error | null>(null);
  
  const config = {
    apiUrl: process.env.REACT_APP_AGENTC_URL!,
    apiKey: process.env.REACT_APP_AGENTC_KEY!,
    enableAudio: true,
    audioConfig: {
      enableInput: true,
      enableOutput: true,
      respectTurnState: true,
      initialVolume: 0.8
    },
    reconnection: {
      maxAttempts: 5,
      initialDelay: 1000,
      maxDelay: 30000
    },
    enableTurnManager: true
  };
  
  return (
    <AgentCProvider 
      config={config}
      autoConnect={false}  // Manual connection
      debug={true}
      onError={(err) => {
        console.error('Agent C Error:', err);
        setError(err);
      }}
    >
      {error && (
        <div className="error-banner">
          Error: {error.message}
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      <ChatInterface />
    </AgentCProvider>
  );
}

function ChatInterface() {
  const { connect, disconnect, isConnected, connectionState } = useConnection();
  const { messages, sendMessage } = useChat();
  const [input, setInput] = useState('');
  
  const handleConnect = async () => {
    try {
      await connect();
      console.log('Connected successfully');
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
    <div className="chat-interface">
      <div className="connection-status">
        Status: {connectionState}
        <button onClick={isConnected ? disconnect : handleConnect}>
          {isConnected ? 'Disconnect' : 'Connect'}
        </button>
      </div>
      
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span className="role">{msg.role}:</span>
            <span className="content">{msg.content}</span>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          disabled={!isConnected}
        />
        <button onClick={handleSend} disabled={!isConnected}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
```

## Advanced Configuration

### Custom Client Configuration

```tsx
function CustomProvider({ children }) {
  const [client, setClient] = useState<RealtimeClient | null>(null);
  
  useEffect(() => {
    // Create custom client with advanced config
    const initClient = async () => {
      const authManager = new AuthManager({
        apiUrl: 'https://api.agentc.ai',
        tokenRefreshBuffer: 10,
        enableAutoRefresh: true
      });
      
      await authManager.login(process.env.REACT_APP_API_KEY!);
      
      const realtimeClient = new RealtimeClient({
        apiUrl: 'wss://api.agentc.ai/rt/ws',
        authManager,
        enableAudio: true,
        audioConfig: {
          enableInput: true,
          enableOutput: true,
          sampleRate: 16000,
          chunkDuration: 100,
          respectTurnState: true
        },
        enableTurnManager: true,
        debug: true,
        connectionTimeout: 10000,
        pingInterval: 30000,
        pongTimeout: 5000
      });
      
      setClient(realtimeClient);
    };
    
    initClient();
    
    return () => {
      client?.destroy();
    };
  }, []);
  
  if (!client) {
    return <div>Initializing...</div>;
  }
  
  return (
    <AgentCContext.Provider value={{ client, isInitialized: true, error: null }}>
      {children}
    </AgentCContext.Provider>
  );
}
```

### Multi-Environment Support

```tsx
const getConfig = () => {
  const env = process.env.REACT_APP_ENV || 'development';
  
  const configs = {
    development: {
      apiUrl: 'ws://localhost:8080/rt/ws',
      authApiUrl: 'http://localhost:8080',
      debug: true
    },
    staging: {
      apiUrl: 'wss://staging.agentc.ai/rt/ws',
      authApiUrl: 'https://staging.agentc.ai',
      debug: true
    },
    production: {
      apiUrl: 'wss://api.agentc.ai/rt/ws',
      authApiUrl: 'https://api.agentc.ai',
      debug: false
    }
  };
  
  return {
    ...configs[env],
    apiKey: process.env.REACT_APP_AGENTC_KEY!,
    enableAudio: true
  };
};

function App() {
  return (
    <AgentCProvider config={getConfig()}>
      <YourApp />
    </AgentCProvider>
  );
}
```

## Error Handling

```tsx
function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <AgentCProvider 
        config={config}
        onError={(error) => {
          // Log to error tracking service
          Sentry.captureException(error);
          
          // Show user-friendly message
          if (error.message.includes('Permission denied')) {
            showNotification('Please allow microphone access');
          } else if (error.message.includes('Network')) {
            showNotification('Connection lost. Retrying...');
          } else {
            showNotification('An error occurred');
          }
        }}
      >
        <App />
      </AgentCProvider>
    </ErrorBoundary>
  );
}

class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('React Error:', error, errorInfo);
  }
  
  render() {
    return this.props.children;
  }
}
```

## Best Practices

1. **Use environment variables for configuration:**
```tsx
<AgentCProvider 
  config={{
    apiUrl: process.env.REACT_APP_AGENTC_URL!,
    apiKey: process.env.REACT_APP_AGENTC_KEY!
  }}
>
```

2. **Handle errors appropriately:**
```tsx
<AgentCProvider 
  onError={(error) => {
    logError(error);
    showUserNotification(error);
  }}
>
```

3. **Lazy load audio features:**
```tsx
const [audioEnabled, setAudioEnabled] = useState(false);

<AgentCProvider 
  config={{
    ...baseConfig,
    enableAudio: audioEnabled
  }}
>
```

4. **Clean up on unmount:**
```tsx
useEffect(() => {
  return () => {
    // Provider handles cleanup automatically
    // But you can add additional cleanup here
  };
}, []);
```

5. **Use one provider per app:**
```tsx
// Good - single provider at root
<AgentCProvider config={config}>
  <Router>
    <App />
  </Router>
</AgentCProvider>

// Bad - multiple providers
<AgentCProvider config={config1}>
  <Component1 />
</AgentCProvider>
<AgentCProvider config={config2}>
  <Component2 />
</AgentCProvider>
```

## TypeScript Usage

```tsx
import { 
  AgentCProvider, 
  AgentCProviderProps,
  AgentCConfig 
} from '@agentc/realtime-react';

const config: AgentCConfig = {
  apiUrl: 'wss://api.agentc.ai/rt/ws',
  apiKey: 'your-key',
  enableAudio: true,
  audioConfig: {
    enableInput: true,
    enableOutput: true
  }
};

const App: React.FC = () => {
  const handleError = (error: Error): void => {
    console.error(error);
  };
  
  return (
    <AgentCProvider 
      config={config}
      onError={handleError}
      autoConnect={true}
      debug={false}
    >
      <YourComponents />
    </AgentCProvider>
  );
};
```

## Troubleshooting

### Provider not connecting

- Check API URL is correct
- Verify API key is valid
- Check network connectivity
- Look for errors in console

### Context is null in child components

- Ensure components are inside provider
- Check that provider is properly initialized
- Verify no errors during initialization

### Memory leaks

- Provider handles cleanup automatically
- Ensure custom hooks clean up subscriptions
- Check for circular references

## See Also

- [React Hooks](./hooks.md) - Available hooks for consuming the context
- [RealtimeClient](../core/RealtimeClient.md) - Core client documentation
- [Examples](./examples.md) - Complete React examples