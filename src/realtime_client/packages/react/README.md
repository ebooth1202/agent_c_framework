# @agentc/realtime-react

React integration for the Agent C Realtime SDK. Provides hooks, providers, and utilities for building voice and chat interfaces with AI agents.

## Installation

```bash
npm install @agentc/realtime-react @agentc/realtime-core
```

## Quick Start

```tsx
import { AgentCProvider, useChat, useAudio, useInitializationStatus } from '@agentc/realtime-react';
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';

function App() {
  const [client, setClient] = useState<RealtimeClient | null>(null);
  
  const handleLogin = async (credentials) => {
    const authManager = new AuthManager();
    await authManager.login(credentials);
    
    const newClient = new RealtimeClient({
      apiUrl: authManager.getWebSocketUrl(),
      authManager
    });
    
    setClient(newClient);
    await newClient.connect();
  };
  
  if (!client) {
    return <LoginForm onLogin={handleLogin} />;
  }
  
  return (
    <AgentCProvider client={client}>
      <ChatInterface />
    </AgentCProvider>
  );
}

function ChatInterface() {
  const { isInitialized } = useInitializationStatus();
  const { messages, sendMessage } = useChat();
  const { startRecording, stopRecording, isRecording } = useAudio();
  
  if (!isInitialized) {
    return <div>Initializing...</div>;
  }
  
  return (
    <div>
      {/* Message display */}
      {messages.map(msg => (
        <div key={msg.id}>{msg.role}: {msg.content}</div>
      ))}
      
      {/* Input controls */}
      <button onClick={() => isRecording ? stopRecording() : startRecording()}>
        {isRecording ? '🔴 Stop' : '🎤 Start'}
      </button>
      
      <input onKeyPress={(e) => {
        if (e.key === 'Enter') {
          sendMessage(e.target.value);
          e.target.value = '';
        }
      }} />
    </div>
  );
}
```

## Core Concepts

### Provider-Based Architecture

All hooks require the `AgentCProvider` at the root of your component tree:

```tsx
<AgentCProvider client={realtimeClient}>
  {/* All child components can use hooks */}
</AgentCProvider>
```

### Event-Driven Data Flow

After connection, the SDK automatically receives initialization events with all configuration data:

1. `chat_user_data` - User profile
2. `voice_list` - Available voices
3. `agent_list` - Available agents
4. `avatar_list` - Available avatars
5. `tool_catalog` - Available tools
6. `chat_session_changed` - Current session

Access this data using the `useAgentCData()` hook.

## Available Hooks

### Data Access Hooks

#### `useAgentCData()`
Access all configuration data from initialization events.

```tsx
const { user, voices, agents, avatars, tools } = useAgentCData();
```

#### `useInitializationStatus()`
Track SDK initialization state.

```tsx
const { isInitialized, isConnecting, error } = useInitializationStatus();
```

#### `useUserData()`
Dedicated hook for user profile access.

```tsx
const { user, isLoading, error } = useUserData();
```

### Connection Hooks

#### `useConnection()`
Manage WebSocket connection.

```tsx
const { isConnected, connectionStats, reconnect } = useConnection();
```

#### `useRealtimeClient()`
Direct access to the RealtimeClient instance.

```tsx
const client = useRealtimeClient();
```

### Chat Hooks

#### `useChat()`
Complete chat functionality.

```tsx
const { messages, sendMessage, clearMessages, isAgentTyping } = useChat();
```

#### `useChatSession()`
Manage chat sessions.

```tsx
const { currentSession, sessions, createSession, switchSession } = useChatSession();
```

### Audio Hooks

#### `useAudio()`
Audio recording and playback control.

```tsx
const { 
  isRecording, 
  startRecording, 
  stopRecording,
  isMuted,
  toggleMute,
  audioLevel
} = useAudio();
```

#### `useTurnState()`
Monitor conversation turn management.

```tsx
const { turnState, isUserTurn, isAgentTurn } = useTurnState();
```

### Voice & Agent Hooks

#### `useVoiceModel()`
Voice model selection.

```tsx
const { voiceModel, setVoiceModel, availableVoices } = useVoiceModel();
```

#### `useAgent()`
Agent selection and management.

```tsx
const { currentAgent, availableAgents, selectAgent } = useAgent();
```

#### `useAvatar()`
Avatar session management.

```tsx
const { isAvatarEnabled, avatarSession, startAvatarSession } = useAvatar();
```

### Utility Hooks

#### `useEventListener()`
Subscribe to specific SDK events.

```tsx
useEventListener('text:delta', (event) => {
  console.log('Streaming text:', event.delta);
});
```

#### `useConnectionStats()`
Monitor connection statistics.

```tsx
const { latency, bandwidth, uptime } = useConnectionStats();
```

## Components

### AgentCProvider

The root provider that enables all hooks.

```tsx
interface AgentCProviderProps {
  client: RealtimeClient | null;
  children: React.ReactNode;
  fallback?: React.ReactNode; // Shown while initializing
}
```

Example with fallback:

```tsx
<AgentCProvider 
  client={client}
  fallback={<LoadingScreen />}
>
  <App />
</AgentCProvider>
```

## Best Practices

### 1. Always Check Initialization

```tsx
function SafeComponent() {
  const { isInitialized } = useInitializationStatus();
  const { user } = useAgentCData();
  
  if (!isInitialized) {
    return <LoadingSpinner />;
  }
  
  // Safe to use data
  return <div>Welcome {user?.display_name}</div>;
}
```

### 2. Handle Connection States

```tsx
function RobustComponent() {
  const { isInitialized, error } = useInitializationStatus();
  const { isConnected } = useConnection();
  
  if (error) return <ErrorBoundary error={error} />;
  if (!isConnected) return <Reconnecting />;
  if (!isInitialized) return <Initializing />;
  
  return <MainContent />;
}
```

### 3. Use Optional Chaining

```tsx
function DefensiveComponent() {
  const { user, voices } = useAgentCData();
  
  return (
    <div>
      <h1>{user?.display_name || 'Guest'}</h1>
      <p>{voices?.length || 0} voices available</p>
    </div>
  );
}
```

### 4. Clean Up Effects

```tsx
function EffectComponent() {
  const client = useRealtimeClient();
  
  useEffect(() => {
    if (!client) return;
    
    const handler = (event) => console.log(event);
    client.on('custom:event', handler);
    
    return () => {
      client.off('custom:event', handler);
    };
  }, [client]);
}
```

## TypeScript Support

All hooks and components are fully typed:

```tsx
import type {
  AgentCData,
  InitializationStatus,
  AudioState,
  ChatMessage,
  Voice,
  Agent,
  UserProfile
} from '@agentc/realtime-react';

// Hooks return typed data
const { user }: { user: UserProfile | null } = useUserData();
const { messages }: { messages: ChatMessage[] } = useChat();
```

## Migration from v1

If upgrading from v1, key changes include:

1. **Simplified login** - Login only returns tokens
2. **Automatic events** - Configuration arrives via events
3. **New hooks** - Use `useAgentCData()` instead of manual state
4. **No storage needed** - SDK manages all data internally

See the [Migration Guide](../../docs/guides/authentication-migration.md) for details.

## Examples

### Complete Chat Application

```tsx
import React from 'react';
import {
  AgentCProvider,
  useInitializationStatus,
  useAgentCData,
  useChat,
  useAudio,
  useVoiceModel
} from '@agentc/realtime-react';

function ChatApp({ client }) {
  return (
    <AgentCProvider client={client}>
      <ChatUI />
    </AgentCProvider>
  );
}

function ChatUI() {
  const { isInitialized } = useInitializationStatus();
  const { user, voices } = useAgentCData();
  const { messages, sendMessage, isAgentTyping } = useChat();
  const { isRecording, startRecording, stopRecording } = useAudio();
  const { voiceModel, setVoiceModel } = useVoiceModel();
  
  if (!isInitialized) {
    return <div>Loading...</div>;
  }
  
  return (
    <div className="chat-app">
      <header>
        <h1>Chat with AI</h1>
        <span>Welcome, {user?.display_name}</span>
      </header>
      
      <div className="voice-selector">
        <select value={voiceModel} onChange={(e) => setVoiceModel(e.target.value)}>
          <option value="none">Text Only</option>
          {voices.map(v => (
            <option key={v.voice_id} value={v.voice_id}>{v.name}</option>
          ))}
        </select>
      </div>
      
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
        {isAgentTyping && <div className="typing">AI is typing...</div>}
      </div>
      
      <div className="controls">
        <button 
          onClick={() => isRecording ? stopRecording() : startRecording()}
          className={isRecording ? 'recording' : ''}
        >
          {isRecording ? '🔴 Stop Recording' : '🎤 Start Recording'}
        </button>
        
        <input
          type="text"
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === 'Enter' && e.target.value) {
              sendMessage(e.target.value);
              e.target.value = '';
            }
          }}
        />
      </div>
    </div>
  );
}
```

### Voice-Only Interface

```tsx
function VoiceInterface() {
  const { isInitialized } = useInitializationStatus();
  const { isRecording, startRecording, stopRecording, audioLevel } = useAudio();
  const { turnState, isUserTurn, isAgentTurn } = useTurnState();
  const { messages } = useChat();
  
  if (!isInitialized) return <div>Initializing...</div>;
  
  return (
    <div className="voice-interface">
      <div className="status">
        {isUserTurn && <span>🎤 Your turn to speak</span>}
        {isAgentTurn && <span>🤖 AI is speaking</span>}
        {turnState === 'processing' && <span>⏳ Processing...</span>}
      </div>
      
      <button
        onClick={() => isRecording ? stopRecording() : startRecording()}
        disabled={!isUserTurn && !isRecording}
        className={`voice-button ${isRecording ? 'active' : ''}`}
      >
        <span className="icon">{isRecording ? '🔴' : '🎤'}</span>
        <div className="audio-level" style={{ height: `${audioLevel * 100}%` }} />
      </button>
      
      <div className="transcript">
        {messages.slice(-5).map(msg => (
          <p key={msg.id} className={msg.role}>
            {msg.content}
          </p>
        ))}
      </div>
    </div>
  );
}
```

### Session Management

```tsx
function SessionManager() {
  const { sessions, currentSession, createSession, switchSession } = useChatSession();
  const [isCreating, setIsCreating] = useState(false);
  
  const handleCreate = async () => {
    setIsCreating(true);
    const name = prompt('Session name:');
    if (name) {
      await createSession(name);
    }
    setIsCreating(false);
  };
  
  return (
    <div className="session-manager">
      <button onClick={handleCreate} disabled={isCreating}>
        + New Session
      </button>
      
      <div className="session-list">
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session ${session.id === currentSession?.id ? 'active' : ''}`}
            onClick={() => switchSession(session.id)}
          >
            <span className="name">{session.name || 'Untitled'}</span>
            <span className="date">{new Date(session.created_at).toLocaleDateString()}</span>
            <span className="count">{session.message_count} messages</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Error Handling

```tsx
function ErrorBoundaryExample() {
  const { error: initError } = useInitializationStatus();
  const { error: userError } = useUserData();
  const { isConnected, reconnect } = useConnection();
  
  const error = initError || userError;
  
  if (error) {
    return (
      <div className="error-container">
        <h2>Connection Error</h2>
        <p>{error.message}</p>
        <button onClick={reconnect}>Retry</button>
      </div>
    );
  }
  
  if (!isConnected) {
    return (
      <div className="reconnecting">
        <div className="spinner" />
        <p>Reconnecting...</p>
      </div>
    );
  }
  
  return <MainApp />;
}
```

## Testing

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { AgentCProvider } from '@agentc/realtime-react';
import { MockRealtimeClient } from './mocks';

describe('Chat Component', () => {
  it('should wait for initialization', async () => {
    const mockClient = new MockRealtimeClient();
    
    render(
      <AgentCProvider client={mockClient}>
        <ChatInterface />
      </AgentCProvider>
    );
    
    // Should show loading initially
    expect(screen.getByText(/initializing/i)).toBeInTheDocument();
    
    // Simulate initialization complete
    mockClient.emit('initialization:complete');
    
    // Should show chat interface
    await waitFor(() => {
      expect(screen.getByText(/chat/i)).toBeInTheDocument();
    });
  });
});
```

## API Reference

For detailed API documentation, see:
- [Hooks API Reference](../../docs/api-reference/react/hooks.md)
- [Provider API Reference](../../docs/api-reference/react/provider.md)
- [TypeScript Types](../../docs/api-reference/react/types.md)

## License

MIT