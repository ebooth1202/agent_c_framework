# React Hooks API Reference

## Overview

The React SDK provides a comprehensive set of hooks for integrating Agent C functionality into React applications. All hooks must be used within an `AgentCProvider` context.

## Core Hooks

### `useAgentCData()`

Access all configuration data received during initialization.

```typescript
function useAgentCData(): {
  user: UserProfile | null;
  voices: Voice[];
  agents: Agent[];
  avatars: Avatar[];
  tools: Tool[];
  currentAgent: Agent | null;
  currentSession: ChatSession | null;
}
```

#### Returns

- `user` - Current user profile from `chat_user_data` event
- `voices` - Available voice models from `voice_list` event
- `agents` - Available agents from `agent_list` event
- `avatars` - Available avatars from `avatar_list` event
- `tools` - Available tools from `tool_catalog` event
- `currentAgent` - Currently selected agent
- `currentSession` - Current chat session

#### Example

```tsx
function UserInfo() {
  const { user, voices, agents } = useAgentCData();
  
  if (!user) {
    return <div>Loading user data...</div>;
  }
  
  return (
    <div>
      <h1>Welcome {user.display_name}</h1>
      <p>You have access to {voices.length} voices and {agents.length} agents</p>
    </div>
  );
}
```

### `useInitializationStatus()`

Track the initialization state of the SDK.

```typescript
function useInitializationStatus(): {
  isInitialized: boolean;
  isConnecting: boolean;
  error: Error | null;
  initializationProgress: {
    userData: boolean;
    voices: boolean;
    agents: boolean;
    avatars: boolean;
    tools: boolean;
    session: boolean;
  };
}
```

#### Returns

- `isInitialized` - True when all initialization events have been received
- `isConnecting` - True while establishing WebSocket connection
- `error` - Connection or initialization error if any
- `initializationProgress` - Individual status for each initialization event

#### Example

```tsx
function App() {
  const { isInitialized, isConnecting, error, initializationProgress } = useInitializationStatus();
  
  if (error) {
    return <ErrorDisplay error={error} />;
  }
  
  if (isConnecting) {
    return <div>Connecting to Agent C...</div>;
  }
  
  if (!isInitialized) {
    return (
      <div>
        <h2>Initializing...</h2>
        <ul>
          <li>User Data: {initializationProgress.userData ? '✓' : '...'}</li>
          <li>Voices: {initializationProgress.voices ? '✓' : '...'}</li>
          <li>Agents: {initializationProgress.agents ? '✓' : '...'}</li>
        </ul>
      </div>
    );
  }
  
  return <ChatInterface />;
}
```

### `useUserData()`

Dedicated hook for accessing user profile data.

```typescript
function useUserData(): {
  user: UserProfile | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}
```

#### Returns

- `user` - User profile from `chat_user_data` event
- `isLoading` - True while waiting for user data
- `error` - Error if user data failed to load
- `refetch` - Function to manually request user data refresh

#### Example

```tsx
function UserProfile() {
  const { user, isLoading, error, refetch } = useUserData();
  
  if (isLoading) return <Skeleton />;
  if (error) return <button onClick={refetch}>Retry</button>;
  if (!user) return null;
  
  return (
    <div className="user-profile">
      <img src={user.avatar_url} alt={user.display_name} />
      <h2>{user.display_name}</h2>
      <p>{user.email}</p>
      <p>Member since: {new Date(user.created_at).toLocaleDateString()}</p>
    </div>
  );
}
```

## Connection Hooks

### `useConnection()`

Manage WebSocket connection state.

```typescript
function useConnection(): {
  isConnected: boolean;
  connectionState: ConnectionState;
  connectionStats: ConnectionStats;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  reconnect: () => Promise<void>;
}
```

#### Returns

- `isConnected` - Simple boolean for connection status
- `connectionState` - Detailed connection state (`connecting`, `connected`, `disconnecting`, `disconnected`, `error`)
- `connectionStats` - Connection statistics (latency, uptime, reconnect count)
- `connect` - Function to establish connection
- `disconnect` - Function to close connection
- `reconnect` - Function to force reconnection

#### Example

```tsx
function ConnectionStatus() {
  const { isConnected, connectionState, connectionStats, reconnect } = useConnection();
  
  return (
    <div className="connection-status">
      <span className={isConnected ? 'connected' : 'disconnected'}>
        {connectionState}
      </span>
      {connectionStats.latency && (
        <span>Latency: {connectionStats.latency}ms</span>
      )}
      {!isConnected && (
        <button onClick={reconnect}>Reconnect</button>
      )}
    </div>
  );
}
```

### `useRealtimeClient()`

Direct access to the underlying RealtimeClient instance.

```typescript
function useRealtimeClient(): RealtimeClient | null
```

#### Returns

The RealtimeClient instance or null if not initialized.

#### Example

```tsx
function CustomFeature() {
  const client = useRealtimeClient();
  
  const handleCustomEvent = () => {
    if (client) {
      // Direct client access for advanced use cases
      client.send('custom:event', { data: 'value' });
    }
  };
  
  return <button onClick={handleCustomEvent}>Send Custom Event</button>;
}
```

## Chat Hooks

### `useChat()`

Complete chat functionality including messages and typing indicators.

```typescript
function useChat(): {
  messages: ChatMessage[];
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
  isAgentTyping: boolean;
  typingIndicator: string | null;
  messageStatus: Record<string, 'sending' | 'sent' | 'error'>;
}
```

#### Returns

- `messages` - Array of chat messages
- `sendMessage` - Function to send text message
- `clearMessages` - Function to clear message history
- `isAgentTyping` - True when agent is typing
- `typingIndicator` - Current typing indicator text
- `messageStatus` - Status of each message by ID

#### Example

```tsx
function ChatInterface() {
  const { 
    messages, 
    sendMessage, 
    clearMessages, 
    isAgentTyping,
    messageStatus 
  } = useChat();
  
  const [input, setInput] = useState('');
  
  const handleSend = async () => {
    if (input.trim()) {
      await sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div className="chat">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.content}
            {messageStatus[msg.id] === 'sending' && <span>Sending...</span>}
          </div>
        ))}
        {isAgentTyping && <div className="typing">Agent is typing...</div>}
      </div>
      
      <div className="input-bar">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
        <button onClick={clearMessages}>Clear</button>
      </div>
    </div>
  );
}
```

### `useChatSession()`

Manage chat sessions and history.

```typescript
function useChatSession(): {
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  createSession: (name?: string) => Promise<ChatSession>;
  switchSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  renameSession: (sessionId: string, name: string) => Promise<void>;
}
```

#### Returns

- `currentSession` - Active chat session
- `sessions` - List of all sessions
- `createSession` - Create new chat session
- `switchSession` - Switch to different session
- `deleteSession` - Delete a session
- `renameSession` - Rename a session

#### Example

```tsx
function SessionManager() {
  const { 
    currentSession, 
    sessions, 
    createSession, 
    switchSession 
  } = useChatSession();
  
  return (
    <div className="session-manager">
      <button onClick={() => createSession('New Chat')}>
        New Chat
      </button>
      
      <div className="session-list">
        {sessions.map(session => (
          <div 
            key={session.id}
            className={session.id === currentSession?.id ? 'active' : ''}
            onClick={() => switchSession(session.id)}
          >
            {session.name || `Chat ${session.created_at}`}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Audio Hooks

### `useAudio()`

Complete audio control for voice conversations.

```typescript
function useAudio(): {
  // Recording state
  isRecording: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  
  // Audio controls
  isMuted: boolean;
  toggleMute: () => void;
  setMuted: (muted: boolean) => void;
  
  // Volume controls
  inputVolume: number;
  outputVolume: number;
  setInputVolume: (volume: number) => void;
  setOutputVolume: (volume: number) => void;
  
  // Audio state
  audioState: AudioState;
  audioLevel: number;
  isVADActive: boolean;
}
```

#### Returns

- `isRecording` - True when recording audio
- `startRecording` - Start audio recording
- `stopRecording` - Stop audio recording
- `isMuted` - Microphone mute state
- `toggleMute` - Toggle microphone mute
- `setMuted` - Set mute state explicitly
- `inputVolume` - Input volume (0-1)
- `outputVolume` - Output volume (0-1)
- `setInputVolume` - Set input volume
- `setOutputVolume` - Set output volume
- `audioState` - Detailed audio state
- `audioLevel` - Current audio level (0-1)
- `isVADActive` - Voice Activity Detection state

#### Example

```tsx
function AudioControls() {
  const {
    isRecording,
    startRecording,
    stopRecording,
    isMuted,
    toggleMute,
    audioLevel,
    isVADActive
  } = useAudio();
  
  return (
    <div className="audio-controls">
      <button 
        onClick={() => isRecording ? stopRecording() : startRecording()}
        className={isRecording ? 'recording' : ''}
      >
        {isRecording ? '🔴 Stop' : '🎤 Start'}
      </button>
      
      <button onClick={toggleMute}>
        {isMuted ? '🔇 Unmute' : '🔊 Mute'}
      </button>
      
      <div className="audio-meter">
        <div 
          className="level" 
          style={{ width: `${audioLevel * 100}%` }}
        />
      </div>
      
      {isVADActive && <span>Voice detected</span>}
    </div>
  );
}
```

### `useTurnState()`

Monitor conversation turn management.

```typescript
function useTurnState(): {
  turnState: TurnState;
  isUserTurn: boolean;
  isAgentTurn: boolean;
  canSpeak: boolean;
  turnHistory: TurnEvent[];
}
```

#### Returns

- `turnState` - Current turn state (`idle`, `user_speaking`, `agent_speaking`, `processing`)
- `isUserTurn` - True when it's user's turn
- `isAgentTurn` - True when agent is speaking
- `canSpeak` - True when user can speak
- `turnHistory` - Recent turn events

#### Example

```tsx
function TurnIndicator() {
  const { turnState, isUserTurn, isAgentTurn } = useTurnState();
  
  return (
    <div className="turn-indicator">
      {isUserTurn && <span>🎤 Your turn to speak</span>}
      {isAgentTurn && <span>🤖 Agent is speaking</span>}
      {turnState === 'processing' && <span>⏳ Processing...</span>}
    </div>
  );
}
```

## Voice Hooks

### `useVoiceModel()`

Manage voice model selection.

```typescript
function useVoiceModel(): {
  voiceModel: string;
  setVoiceModel: (voiceId: string) => Promise<void>;
  availableVoices: Voice[];
  isChanging: boolean;
  supportsAudio: boolean;
}
```

#### Returns

- `voiceModel` - Current voice model ID
- `setVoiceModel` - Function to change voice
- `availableVoices` - List of available voices
- `isChanging` - True while changing voice
- `supportsAudio` - False for text-only mode

#### Example

```tsx
function VoiceSelector() {
  const { 
    voiceModel, 
    setVoiceModel, 
    availableVoices, 
    isChanging 
  } = useVoiceModel();
  
  return (
    <select 
      value={voiceModel} 
      onChange={(e) => setVoiceModel(e.target.value)}
      disabled={isChanging}
    >
      <option value="none">Text Only</option>
      {availableVoices.map(voice => (
        <option key={voice.voice_id} value={voice.voice_id}>
          {voice.name} ({voice.language})
        </option>
      ))}
    </select>
  );
}
```

## Agent Hooks

### `useAgent()`

Manage agent selection and interaction.

```typescript
function useAgent(): {
  currentAgent: Agent | null;
  availableAgents: Agent[];
  selectAgent: (agentId: string) => Promise<void>;
  agentCapabilities: AgentCapabilities;
  isLoading: boolean;
}
```

#### Returns

- `currentAgent` - Currently selected agent
- `availableAgents` - List of available agents
- `selectAgent` - Function to change agent
- `agentCapabilities` - Current agent's capabilities
- `isLoading` - True while loading agent

#### Example

```tsx
function AgentSelector() {
  const { 
    currentAgent, 
    availableAgents, 
    selectAgent,
    agentCapabilities 
  } = useAgent();
  
  return (
    <div className="agent-selector">
      <select 
        value={currentAgent?.id} 
        onChange={(e) => selectAgent(e.target.value)}
      >
        {availableAgents.map(agent => (
          <option key={agent.id} value={agent.id}>
            {agent.name}
          </option>
        ))}
      </select>
      
      {agentCapabilities && (
        <div className="capabilities">
          <h3>Agent can:</h3>
          <ul>
            {agentCapabilities.tools.map(tool => (
              <li key={tool}>{tool}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## Avatar Hooks

### `useAvatar()`

Manage HeyGen avatar integration.

```typescript
function useAvatar(): {
  isAvatarEnabled: boolean;
  avatarSession: AvatarSession | null;
  availableAvatars: Avatar[];
  startAvatarSession: (avatarId: string) => Promise<void>;
  stopAvatarSession: () => Promise<void>;
  avatarState: AvatarState;
}
```

#### Returns

- `isAvatarEnabled` - True when avatar is active
- `avatarSession` - Current avatar session
- `availableAvatars` - List of available avatars
- `startAvatarSession` - Start avatar session
- `stopAvatarSession` - Stop avatar session
- `avatarState` - Avatar state details

#### Example

```tsx
function AvatarView() {
  const { 
    isAvatarEnabled,
    avatarSession,
    availableAvatars,
    startAvatarSession,
    stopAvatarSession
  } = useAvatar();
  
  if (!isAvatarEnabled) {
    return (
      <div className="avatar-selector">
        {availableAvatars.map(avatar => (
          <button 
            key={avatar.id}
            onClick={() => startAvatarSession(avatar.id)}
          >
            Start {avatar.name}
          </button>
        ))}
      </div>
    );
  }
  
  return (
    <div className="avatar-view">
      <video 
        src={avatarSession?.streamUrl} 
        autoPlay 
        playsInline 
      />
      <button onClick={stopAvatarSession}>Stop Avatar</button>
    </div>
  );
}
```

## Utility Hooks

### `useEventListener()`

Subscribe to specific SDK events.

```typescript
function useEventListener<T = any>(
  eventName: string,
  handler: (event: T) => void,
  deps?: DependencyList
): void
```

#### Parameters

- `eventName` - Name of the event to listen for
- `handler` - Callback function for the event
- `deps` - Optional dependency array for the handler

#### Example

```tsx
function CustomEventHandler() {
  const [customData, setCustomData] = useState(null);
  
  useEventListener('custom:event', (event) => {
    setCustomData(event.data);
  });
  
  return <div>{customData && <pre>{JSON.stringify(customData)}</pre>}</div>;
}
```

### `useConnectionStats()`

Monitor detailed connection statistics.

```typescript
function useConnectionStats(): {
  latency: number | null;
  bandwidth: BandwidthStats;
  messageRate: number;
  reconnectCount: number;
  uptime: number;
  lastError: Error | null;
}
```

#### Returns

- `latency` - Round-trip time in milliseconds
- `bandwidth` - Upload/download bandwidth stats
- `messageRate` - Messages per second
- `reconnectCount` - Number of reconnections
- `uptime` - Connection uptime in seconds
- `lastError` - Last connection error

#### Example

```tsx
function ConnectionMonitor() {
  const stats = useConnectionStats();
  
  return (
    <div className="stats">
      <div>Latency: {stats.latency}ms</div>
      <div>Upload: {stats.bandwidth.upload}kbps</div>
      <div>Download: {stats.bandwidth.download}kbps</div>
      <div>Uptime: {Math.floor(stats.uptime / 60)}m</div>
      {stats.lastError && (
        <div className="error">Last error: {stats.lastError.message}</div>
      )}
    </div>
  );
}
```

## Best Practices

### 1. Always Check Initialization

```tsx
function SafeComponent() {
  const { isInitialized } = useInitializationStatus();
  const { user, voices } = useAgentCData();
  
  // Always check initialization first
  if (!isInitialized) {
    return <LoadingSpinner />;
  }
  
  // Now safe to use data
  return <div>{user?.display_name}</div>;
}
```

### 2. Handle Loading States

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
      {/* Safe access with optional chaining */}
      <h1>{user?.display_name || 'Guest'}</h1>
      <p>{user?.email || 'No email'}</p>
      <span>{voices?.length || 0} voices available</span>
    </div>
  );
}
```

### 4. Cleanup in useEffect

```tsx
function EffectComponent() {
  const client = useRealtimeClient();
  
  useEffect(() => {
    if (!client) return;
    
    const handler = (event) => console.log(event);
    client.on('custom:event', handler);
    
    // Always cleanup
    return () => {
      client.off('custom:event', handler);
    };
  }, [client]);
}
```

## TypeScript Types

All hooks are fully typed. Import types as needed:

```typescript
import type {
  UserProfile,
  Voice,
  Agent,
  Avatar,
  Tool,
  ChatMessage,
  ChatSession,
  ConnectionState,
  AudioState,
  TurnState,
  AgentCapabilities,
  AvatarSession,
  AvatarState,
  BandwidthStats
} from '@agentc/realtime-react';
```

## Hook Dependencies

All hooks require the `AgentCProvider` at the root:

```tsx
import { AgentCProvider } from '@agentc/realtime-react';

function App() {
  return (
    <AgentCProvider client={realtimeClient}>
      {/* All hooks work within this provider */}
      <YourComponents />
    </AgentCProvider>
  );
}
```

## Error Handling

Hooks provide built-in error handling:

```tsx
function ErrorAwareComponent() {
  const { error: initError } = useInitializationStatus();
  const { error: userError } = useUserData();
  
  const error = initError || userError;
  
  if (error) {
    return (
      <ErrorBoundary 
        error={error}
        onRetry={() => window.location.reload()}
      />
    );
  }
  
  return <MainContent />;
}
```