# React Hooks API Reference

The Agent C Realtime React SDK provides a comprehensive set of hooks for building real-time applications.

## Authentication with Agent C

Agent C uses username/password authentication, not API keys. The authentication flow:

1. **REST API Login** - Authenticate with credentials at `https://localhost:8000/rt/login` (or your server URL)
2. **Receive Tokens** - Get JWT token and WebSocket URL from login response
3. **WebSocket Connection** - Connect to the WebSocket URL with the JWT token

### AgentCProvider Configuration

```typescript
// Development configuration
<AgentCProvider
  config={{
    // REST API endpoint for authentication
    restApiUrl: 'https://localhost:8000',
    // Optional: provide credentials for auto-connect
    credentials: {
      username: 'demo_user',
      password: 'demo_pass'
    },
    // WebSocket URL is obtained from login response
    autoConnect: false,
    enableAudio: true
  }}
>

// Production configuration with environment variables
<AgentCProvider
  config={{
    restApiUrl: process.env.REACT_APP_AGENTC_API_URL,
    credentials: {
      username: process.env.REACT_APP_AGENTC_USERNAME,
      password: process.env.REACT_APP_AGENTC_PASSWORD
    },
    autoConnect: true
  }}
>
```

## Available Hooks

- [`useRealtimeClient`](#userealtimeclient) - Direct client access
- [`useConnection`](#useconnection) - Connection management with authentication
- [`useChat`](#usechat) - Chat messaging
- [`useAudio`](#useaudio) - Audio control
- [`useTurnState`](#useturnstate) - Turn management
- [`useVoiceModel`](#usevoicemodel) - Voice selection
- [`useAvatar`](#useavatar) - Avatar integration

## Import

```typescript
import { 
  useRealtimeClient,
  useConnection,
  useChat,
  useAudio,
  useTurnState,
  useVoiceModel,
  useAvatar
} from '@agentc/realtime-react';
```

---

## useRealtimeClient

Direct access to the RealtimeClient instance. The client is automatically configured with authentication details from the AgentCProvider.

### Signature

```typescript
function useRealtimeClient(): RealtimeClient | null
```

### Returns

- `RealtimeClient | null` - The client instance or null if not initialized

### Important Notes

- The client instance is managed by the AgentCProvider
- WebSocket URL is automatically obtained from the authentication process
- JWT tokens are handled internally by the AuthManager
- Do not manually configure WebSocket URLs

### Example

```tsx
function CustomComponent() {
  const client = useRealtimeClient();
  const { isAuthenticated } = useConnection();
  
  useEffect(() => {
    if (!client || !isAuthenticated) return;
    
    const handler = (event) => {
      console.log('Custom event:', event);
    };
    
    client.on('custom_event', handler);
    
    return () => {
      client.off('custom_event', handler);
    };
  }, [client, isAuthenticated]);
  
  const sendCustomCommand = () => {
    if (!isAuthenticated) {
      console.error('Not authenticated');
      return;
    }
    client?.sendText('Custom command');
  };
  
  return (
    <button onClick={sendCustomCommand} disabled={!isAuthenticated}>
      Send Custom Command
    </button>
  );
}
```

---

## useConnection

Manages WebSocket connection state and control with Agent C authentication.

### Signature

```typescript
interface UseConnectionReturn {
  connect: (credentials?: { username: string; password: string }) => Promise<void>;
  disconnect: () => void;
  isConnected: boolean;
  isAuthenticated: boolean;
  connectionState: ConnectionState;
  error: Error | null;
  reconnectAttempt: number;
}

function useConnection(): UseConnectionReturn
```

### Returns

- `connect` - Async function to authenticate and establish connection
- `disconnect` - Function to close connection
- `isConnected` - Boolean WebSocket connection status
- `isAuthenticated` - Boolean authentication status
- `connectionState` - Current ConnectionState enum value
- `error` - Connection or authentication error if any
- `reconnectAttempt` - Current reconnection attempt number

### Authentication Flow

The connection process handles Agent C authentication:
1. Authenticates with username/password via REST API
2. Receives WebSocket URL from login response
3. Establishes WebSocket connection with JWT token

### Example

```tsx
function ConnectionManager() {
  const { 
    connect, 
    disconnect, 
    isConnected,
    isAuthenticated,
    connectionState, 
    error,
    reconnectAttempt 
  } = useConnection();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const handleConnect = async () => {
    try {
      // Authenticate and connect
      await connect({ username, password });
      console.log('Connected successfully');
    } catch (err) {
      console.error('Connection failed:', err);
    }
  };
  
  return (
    <div>
      <div>Status: {ConnectionState[connectionState]}</div>
      <div>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</div>
      {error && <div>Error: {error.message}</div>}
      {reconnectAttempt > 0 && <div>Reconnecting... Attempt {reconnectAttempt}</div>}
      
      {!isConnected ? (
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={handleConnect} disabled={!username || !password}>
            Connect
          </button>
        </div>
      ) : (
        <button onClick={disconnect}>Disconnect</button>
      )}
    </div>
  );
}
```

### With Environment Variables

```tsx
function AutoConnectionManager() {
  const { connect, isConnected } = useConnection();
  
  useEffect(() => {
    // Auto-connect using environment credentials
    if (!isConnected) {
      connect({
        username: process.env.REACT_APP_AGENTC_USERNAME || 'demo',
        password: process.env.REACT_APP_AGENTC_PASSWORD || 'demo'
      });
    }
  }, []);
  
  return <div>Connection status: {isConnected ? 'Connected' : 'Connecting...'}</div>;
}
```

---

## useChat

Manages chat messages and sessions.

### Signature

```typescript
interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

interface UseChatReturn {
  messages: Message[];
  sendMessage: (text: string, fileIds?: string[]) => void;
  streamingText: string;
  isStreaming: boolean;
  clearMessages: () => void;
  newSession: (agentKey?: string) => void;
  resumeSession: (sessionId: string) => void;
  setSessionName: (name: string) => void;
  currentSessionId: string | null;
  sessions: ChatSession[];
}

function useChat(): UseChatReturn
```

### Returns

- `messages` - Array of chat messages
- `sendMessage` - Function to send a message
- `streamingText` - Currently streaming text
- `isStreaming` - Whether text is streaming
- `clearMessages` - Clear current session messages
- `newSession` - Create new chat session
- `resumeSession` - Resume existing session
- `setSessionName` - Set session name
- `currentSessionId` - Current session ID
- `sessions` - All available sessions

### Example

```tsx
function ChatInterface() {
  const { 
    messages, 
    sendMessage, 
    streamingText, 
    isStreaming,
    clearMessages,
    newSession
  } = useChat();
  
  const [input, setInput] = useState('');
  
  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div>
      <button onClick={() => newSession()}>New Chat</button>
      <button onClick={clearMessages}>Clear</button>
      
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
        
        {isStreaming && (
          <div className="message assistant streaming">
            <strong>assistant:</strong> {streamingText}
          </div>
        )}
      </div>
      
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

---

## useAudio

Controls audio input and output.

### Signature

```typescript
interface UseAudioReturn {
  // Recording control
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  isRecording: boolean;
  
  // Streaming control
  startStreaming: () => void;
  stopStreaming: () => void;
  isStreaming: boolean;
  
  // Audio status
  hasPermission: boolean;
  audioLevel: number;
  isPlaying: boolean;
  
  // Volume control
  volume: number;
  setVolume: (volume: number) => void;
  
  // Error handling
  error: Error | null;
}

function useAudio(): UseAudioReturn
```

### Returns

Audio control functions and status information

### Example

```tsx
function AudioControls() {
  const {
    startRecording,
    stopRecording,
    isRecording,
    startStreaming,
    stopStreaming,
    isStreaming,
    hasPermission,
    audioLevel,
    volume,
    setVolume,
    error
  } = useAudio();
  
  const handleMicrophone = async () => {
    if (!isRecording) {
      try {
        await startRecording();
        startStreaming();
      } catch (err) {
        console.error('Microphone error:', err);
      }
    } else {
      stopStreaming();
      stopRecording();
    }
  };
  
  return (
    <div>
      {error && <div>Audio Error: {error.message}</div>}
      
      <button onClick={handleMicrophone}>
        {isRecording ? '🔴 Stop' : '🎤 Start'} Recording
      </button>
      
      <div>
        Audio Level: 
        <progress value={audioLevel} max={1} />
      </div>
      
      <div>
        Volume: 
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => setVolume(parseFloat(e.target.value))}
        />
        {Math.round(volume * 100)}%
      </div>
      
      <div>
        Status: {!hasPermission && 'No permission | '}
        {isRecording && 'Recording | '}
        {isStreaming && 'Streaming'}
      </div>
    </div>
  );
}
```

---

## useTurnState

Monitors and controls conversation turns.

### Signature

```typescript
interface UseTurnStateReturn {
  currentTurn: TurnState;
  isUserTurn: boolean;
  isAgentTurn: boolean;
  turnHistory: TurnHistoryEntry[];
  canTransmitAudio: boolean;
  turnDuration: number;
}

enum TurnState {
  USER_TURN = 'user_turn',
  AGENT_TURN = 'agent_turn',
  IDLE = 'idle'
}

interface TurnHistoryEntry {
  state: TurnState;
  timestamp: number;
  duration?: number;
}

function useTurnState(): UseTurnStateReturn
```

### Returns

Turn state information and history

### Example

```tsx
function TurnIndicator() {
  const { 
    currentTurn, 
    isUserTurn, 
    isAgentTurn,
    turnDuration 
  } = useTurnState();
  
  const getTurnDisplay = () => {
    if (isUserTurn) return '🎤 Your turn to speak';
    if (isAgentTurn) return '🤖 Agent is speaking';
    return '⏸️ Waiting...';
  };
  
  return (
    <div className="turn-indicator">
      <div>{getTurnDisplay()}</div>
      <div>Duration: {(turnDuration / 1000).toFixed(1)}s</div>
      
      <div className={`indicator ${currentTurn}`}>
        {currentTurn === TurnState.USER_TURN && '🟢'}
        {currentTurn === TurnState.AGENT_TURN && '🔴'}
        {currentTurn === TurnState.IDLE && '⚪'}
      </div>
    </div>
  );
}
```

---

## useVoiceModel

Manages TTS voice selection.

### Signature

```typescript
interface Voice {
  voice_id: string;
  name: string;
  vendor: string;
  description?: string;
  output_format?: string;
}

interface UseVoiceModelReturn {
  currentVoice: Voice | null;
  availableVoices: Voice[];
  setVoice: (voiceId: string) => void;
  isAvatarMode: boolean;
  isTextOnly: boolean;
}

function useVoiceModel(): UseVoiceModelReturn
```

### Returns

Voice management functions and state

### Example

```tsx
function VoiceSelector() {
  const { 
    currentVoice, 
    availableVoices, 
    setVoice,
    isAvatarMode,
    isTextOnly
  } = useVoiceModel();
  
  return (
    <div>
      <select 
        value={currentVoice?.voice_id || 'none'}
        onChange={(e) => setVoice(e.target.value)}
      >
        <option value="none">Text Only (No Audio)</option>
        {availableVoices.map(voice => (
          <option key={voice.voice_id} value={voice.voice_id}>
            {voice.name} - {voice.description}
          </option>
        ))}
        <option value="avatar">Avatar Mode</option>
      </select>
      
      <div>
        {isTextOnly && '📝 Text-only mode'}
        {isAvatarMode && '🎭 Avatar mode'}
        {!isTextOnly && !isAvatarMode && `🔊 Voice: ${currentVoice?.name}`}
      </div>
    </div>
  );
}
```

---

## useAvatar

Manages HeyGen avatar integration. HeyGen access tokens and available avatars are provided by Agent C during authentication.

### Signature

```typescript
interface Avatar {
  avatar_id: string;
  name: string;
  preview_url?: string;
  description?: string;
}

interface UseAvatarReturn {
  availableAvatars: Avatar[];
  currentAvatar: Avatar | null;
  isSessionActive: boolean;
  startAvatarSession: (avatarId: string) => Promise<void>;
  endAvatarSession: () => void;
  sessionId: string | null;
  error: Error | null;
  hasHeyGenAccess: boolean;
}

function useAvatar(): UseAvatarReturn
```

### Returns

Avatar management functions and state

### Authentication Note

HeyGen integration requires:
1. Valid Agent C authentication
2. HeyGen access token (provided in login response)
3. Available avatars list (provided in login response)

The SDK automatically handles HeyGen token management after Agent C authentication.

### Example

```tsx
function AvatarControls() {
  const {
    availableAvatars,
    currentAvatar,
    isSessionActive,
    startAvatarSession,
    endAvatarSession,
    error
  } = useAvatar();
  
  const [selectedAvatar, setSelectedAvatar] = useState('');
  
  const handleStartAvatar = async () => {
    if (selectedAvatar) {
      try {
        await startAvatarSession(selectedAvatar);
      } catch (err) {
        console.error('Avatar error:', err);
      }
    }
  };
  
  return (
    <div>
      {error && <div>Avatar Error: {error.message}</div>}
      
      {!isSessionActive ? (
        <div>
          <select 
            value={selectedAvatar}
            onChange={(e) => setSelectedAvatar(e.target.value)}
          >
            <option value="">Select an avatar</option>
            {availableAvatars.map(avatar => (
              <option key={avatar.avatar_id} value={avatar.avatar_id}>
                {avatar.name}
              </option>
            ))}
          </select>
          
          <button onClick={handleStartAvatar} disabled={!selectedAvatar}>
            Start Avatar
          </button>
        </div>
      ) : (
        <div>
          <div>Active: {currentAvatar?.name}</div>
          <button onClick={endAvatarSession}>Stop Avatar</button>
        </div>
      )}
    </div>
  );
}
```

---

## Complete Example

```tsx
import React, { useState } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat,
  useAudio,
  useTurnState,
  useVoiceModel
} from '@agentc/realtime-react';

function App() {
  return (
    <AgentCProvider 
      config={{
        // REST API endpoint for authentication
        restApiUrl: process.env.REACT_APP_AGENTC_API_URL || 'https://localhost:8000',
        // Optional: provide default credentials
        credentials: {
          username: process.env.REACT_APP_AGENTC_USERNAME,
          password: process.env.REACT_APP_AGENTC_PASSWORD
        },
        enableAudio: true,
        // WebSocket URL will be obtained from login response
        autoConnect: false
      }}
    >
      <CompleteInterface />
    </AgentCProvider>
  );
}

function CompleteInterface() {
  const { connect, disconnect, isConnected, isAuthenticated } = useConnection();
  const { messages, sendMessage, isStreaming, streamingText } = useChat();
  const { startRecording, stopRecording, isRecording, audioLevel } = useAudio();
  const { currentTurn, isUserTurn } = useTurnState();
  const { currentVoice, setVoice, availableVoices } = useVoiceModel();
  
  const [input, setInput] = useState('');
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [showLogin, setShowLogin] = useState(true);
  
  // Handle authentication and connection
  const handleConnect = async () => {
    try {
      await connect(credentials);
      setShowLogin(false);
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Failed to connect. Please check your credentials.');
    }
  };
  
  // Auto-start recording on user turn
  React.useEffect(() => {
    if (isUserTurn && !isRecording && isConnected) {
      startRecording().catch(console.error);
    } else if (!isUserTurn && isRecording) {
      stopRecording();
    }
  }, [isUserTurn, isRecording, isConnected]);
  
  // Show login form if not authenticated
  if (!isAuthenticated && showLogin) {
    return (
      <div className="login-form">
        <h2>Connect to Agent C</h2>
        <input
          type="text"
          placeholder="Username"
          value={credentials.username}
          onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        />
        <input
          type="password"
          placeholder="Password"
          value={credentials.password}
          onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        />
        <button 
          onClick={handleConnect}
          disabled={!credentials.username || !credentials.password}
        >
          Connect
        </button>
      </div>
    );
  }
  
  return (
    <div className="app">
      <header>
        <button onClick={disconnect}>
          Disconnect
        </button>
        
        <select 
          value={currentVoice?.voice_id || 'none'}
          onChange={(e) => setVoice(e.target.value)}
        >
          <option value="none">No Voice</option>
          {availableVoices.map(v => (
            <option key={v.voice_id} value={v.voice_id}>
              {v.name}
            </option>
          ))}
        </select>
        
        <div className="turn-indicator">
          {currentTurn}
        </div>
        
        <div className="audio-level">
          <progress value={audioLevel} max={1} />
        </div>
      </header>
      
      <main className="chat">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        
        {isStreaming && (
          <div className="message assistant streaming">
            {streamingText}
          </div>
        )}
      </main>
      
      <footer>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              sendMessage(input);
              setInput('');
            }
          }}
          disabled={!isConnected}
        />
        
        <button 
          onClick={() => {
            sendMessage(input);
            setInput('');
          }}
          disabled={!isConnected || !input.trim()}
        >
          Send
        </button>
        
        <button 
          onClick={isRecording ? stopRecording : () => startRecording()}
          disabled={!isConnected}
        >
          {isRecording ? '🔴' : '🎤'}
        </button>
      </footer>
    </div>
  );
}
```

## Custom Hooks

You can create custom hooks that combine the base hooks:

```tsx
// Custom hook for authenticated voice chat
function useVoiceChat() {
  const { isConnected, isAuthenticated } = useConnection();
  const { sendMessage } = useChat();
  const { startRecording, stopRecording, isRecording } = useAudio();
  const { isUserTurn } = useTurnState();
  
  const startVoiceChat = useCallback(async () => {
    if (!isAuthenticated) throw new Error('Not authenticated');
    if (!isConnected) throw new Error('Not connected');
    if (!isUserTurn) throw new Error('Not your turn');
    
    await startRecording();
  }, [isAuthenticated, isConnected, isUserTurn, startRecording]);
  
  const stopVoiceChat = useCallback(() => {
    stopRecording();
  }, [stopRecording]);
  
  return {
    startVoiceChat,
    stopVoiceChat,
    isVoiceChatActive: isRecording && isUserTurn,
    canStartChat: isAuthenticated && isConnected && isUserTurn
  };
}

// Custom hook for session management
function useSessionManager() {
  const { sessions, currentSessionId, newSession, resumeSession } = useChat();
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  
  const switchSession = useCallback((sessionId: string) => {
    setSelectedSession(sessionId);
    resumeSession(sessionId);
  }, [resumeSession]);
  
  const createNewSession = useCallback(() => {
    newSession();
    setSelectedSession(null);
  }, [newSession]);
  
  return {
    sessions,
    currentSessionId,
    selectedSession,
    switchSession,
    createNewSession
  };
}
```

## TypeScript Support

All hooks are fully typed:

```tsx
import { 
  UseConnectionReturn,
  UseChatReturn,
  UseAudioReturn,
  UseTurnStateReturn,
  UseVoiceModelReturn,
  UseAvatarReturn,
  Message,
  Voice,
  Avatar,
  TurnState,
  ConnectionState
} from '@agentc/realtime-react';
```

## Best Practices

1. **Always check authentication and connection state before operations:**
```tsx
const { isConnected, isAuthenticated } = useConnection();
const { sendMessage } = useChat();

const handleSend = (text: string) => {
  if (!isAuthenticated) {
    showError('Please authenticate first');
    return;
  }
  if (!isConnected) {
    showError('WebSocket not connected');
    return;
  }
  sendMessage(text);
};
```

### Authentication Best Practices

1. **Never hardcode credentials:**
```tsx
// ❌ Bad - hardcoded credentials
const credentials = { username: 'admin', password: 'password123' };

// ✅ Good - use environment variables or user input
const credentials = {
  username: process.env.REACT_APP_USERNAME || userInput.username,
  password: process.env.REACT_APP_PASSWORD || userInput.password
};
```

2. **Handle authentication errors gracefully:**
```tsx
const handleConnect = async () => {
  try {
    await connect({ username, password });
  } catch (error) {
    if (error.code === 'AUTH_FAILED') {
      showError('Invalid credentials');
    } else if (error.code === 'NETWORK_ERROR') {
      showError('Cannot reach authentication server');
    } else {
      showError('Connection failed: ' + error.message);
    }
  }
};
```

3. **Store authentication state properly:**
```tsx
// The SDK handles token storage internally
// Access authentication state through hooks
const { isAuthenticated } = useConnection();

// The WebSocket URL is obtained automatically from login
// No need to configure it manually
```

2. **Handle async operations properly:**
```tsx
const { startRecording } = useAudio();

const handleStart = async () => {
  try {
    await startRecording();
  } catch (error) {
    if (error.name === 'NotAllowedError') {
      showError('Microphone permission denied');
    }
  }
};
```

3. **Clean up subscriptions:**
```tsx
useEffect(() => {
  const client = useRealtimeClient();
  if (!client) return;
  
  const handler = () => {};
  client.on('event', handler);
  
  return () => {
    client.off('event', handler);
  };
}, []);
```

4. **Respect turn management:**
```tsx
const { isUserTurn } = useTurnState();
const { startRecording } = useAudio();

useEffect(() => {
  if (isUserTurn) {
    startRecording();
  }
}, [isUserTurn]);
```

5. **Provide feedback for streaming:**
```tsx
const { isStreaming, streamingText } = useChat();

return (
  <div>
    {isStreaming && <LoadingIndicator />}
    <div>{streamingText}</div>
  </div>
);
```