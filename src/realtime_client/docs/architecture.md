# SDK Architecture Overview

This document provides a comprehensive overview of the Agent C Realtime SDK architecture, explaining the design decisions, component relationships, and data flow patterns.

## Design Philosophy

The Agent C Realtime SDK is built on several core principles:

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility. Audio handling doesn't know about WebSocket details, and authentication doesn't depend on UI components.

### 2. **Framework Agnostic Core**
The core SDK (`@agentc/realtime-core`) is pure TypeScript with no framework dependencies. React bindings are a thin layer on top.

### 3. **Binary-First Communication**
Audio is transmitted as raw binary ArrayBuffer over WebSocket, avoiding base64 encoding overhead for 33% bandwidth savings.

### 4. **Event-Driven Architecture**
All state changes and data flow through a type-safe event system, enabling reactive UIs and clean component decoupling.

### 5. **Progressive Enhancement**
Start with text chat, add voice when needed, integrate avatars if desired. Each feature layer builds on the previous without requiring all features.

## Package Structure

```
@agentc/realtime-sdk
├── packages/
│   ├── core/                 # Framework-agnostic core
│   │   ├── client/          # WebSocket and connection management
│   │   ├── auth/            # Authentication and tokens
│   │   ├── audio/           # Audio capture and playback
│   │   ├── session/         # Chat sessions and turns
│   │   ├── voice/           # Voice model management
│   │   ├── avatar/          # HeyGen avatar integration
│   │   ├── events/          # Event types and emitter
│   │   └── utils/           # Shared utilities
│   └── react/               # React-specific bindings
│       ├── providers/       # Context providers
│       ├── hooks/           # React hooks
│       └── components/      # Optional UI components
└── worklets/                # Audio worklet scripts
```

## Core Components

### RealtimeClient

The central hub that orchestrates all SDK functionality:

```typescript
┌─────────────────────────────────────────────────┐
│                RealtimeClient                   │
├─────────────────────────────────────────────────┤
│ • WebSocket connection management               │
│ • Event routing and emission                    │
│ • Binary/JSON message handling                  │
│ • Component lifecycle coordination              │
└─────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌───────────┐  ┌────────────┐  ┌────────────┐
    │WebSocket  │  │   Auth     │  │   Audio    │
    │ Manager   │  │  Manager   │  │  System    │
    └───────────┘  └────────────┘  └────────────┘
          ▼               ▼               ▼
    ┌───────────┐  ┌────────────┐  ┌────────────┐
    │   Turn    │  │   Voice    │  │  Session   │
    │  Manager  │  │  Manager   │  │  Manager   │
    └───────────┘  └────────────┘  └────────────┘
```

### WebSocket Layer

Handles the low-level WebSocket connection with automatic reconnection:

```
┌──────────────────────────────────────┐
│         WebSocketManager             │
├──────────────────────────────────────┤
│ • Binary frame support               │
│ • JSON message parsing               │
│ • Ping/pong heartbeat                │
│ • Connection state tracking          │
└──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       ReconnectionManager            │
├──────────────────────────────────────┤
│ • Exponential backoff                │
│ • Max retry attempts                 │
│ • Automatic reconnection             │
│ • Connection recovery                │
└──────────────────────────────────────┘
```

### Authentication System

Manages API keys, JWT tokens, and HeyGen credentials:

```
┌──────────────────────────────────────┐
│           AuthManager                │
├──────────────────────────────────────┤
│ • API key validation                 │
│ • JWT token management               │
│ • Token refresh scheduling           │
│ • HeyGen token storage              │
│ • Available voices/avatars          │
└──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────┐
        │   TokenPair      │
        ├──────────────────┤
        │ • agentCToken    │
        │ • heygenToken    │
        │ • expiresAt      │
        └──────────────────┘
```

### Audio System Architecture

The audio system uses Web Audio API with worklets for optimal performance:

```
     Microphone                          Server Audio
         │                                    │
         ▼                                    ▼
┌──────────────────┐              ┌────────────────────┐
│   AudioService   │              │ AudioOutputService │
├──────────────────┤              ├────────────────────┤
│ • getUserMedia() │              │ • Audio queuing    │
│ • AudioContext   │              │ • Format detection │
│ • Worklet setup  │              │ • Playback control │
└──────────────────┘              └────────────────────┘
         │                                    ▲
         ▼                                    │
┌──────────────────┐                    Binary Audio
│  AudioProcessor  │                     from Server
│   (Worklet)      │
├──────────────────┤
│ • Float32→PCM16  │
│ • Chunking       │
│ • Level detection│
└──────────────────┘
         │
         ▼
┌────────────────────┐
│AudioAgentCBridge   │
├────────────────────┤
│ • Turn checking    │
│ • Binary streaming │
│ • Client binding   │
└────────────────────┘
         │
         ▼
    WebSocket (Binary)
```

### Session Management

Tracks chat sessions and conversation history:

```
┌──────────────────────────────────────┐
│         SessionManager               │
├──────────────────────────────────────┤
│ • Multiple session support           │
│ • Message history                    │
│ • Text accumulation                  │
│ • Session metadata                   │
└──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│Session 1│  │Session 2│  │Session 3│
├─────────┤  ├─────────┤  ├─────────┤
│Messages │  │Messages │  │Messages │
│Metadata │  │Metadata │  │Metadata │
└─────────┘  └─────────┘  └─────────┘
```

### Turn Management

Prevents audio conflicts and manages conversation flow:

```
┌──────────────────────────────────────┐
│          TurnManager                 │
├──────────────────────────────────────┤
│ • Server-driven turn control         │
│ • Audio gate integration             │
│ • Turn history tracking              │
│ • State change events                │
└──────────────────────────────────────┘
                   │
         State Transitions
                   │
    ┌──────────────▼──────────────┐
    │                              │
    ▼                              ▼
USER_TURN ────────────────► AGENT_TURN
    ▲                              │
    │                              │
    └──────────────────────────────┘
```

## Data Flow Patterns

### Text Message Flow

```
User Input
    │
    ▼
sendText()
    │
    ▼
WebSocket (JSON)
    │
    ▼
Agent C Server
    │
    ▼
text_delta events
    │
    ▼
SessionManager (accumulate)
    │
    ▼
UI Update
```

### Audio Input Flow

```
Microphone
    │
    ▼
getUserMedia()
    │
    ▼
AudioContext
    │
    ▼
AudioWorklet
    │
    ▼
Float32 → PCM16
    │
    ▼
AudioAgentCBridge
    │
    ├─► Turn Check
    │
    ▼
WebSocket (Binary)
    │
    ▼
Agent C Server
```

### Audio Output Flow

```
Agent C Server
    │
    ▼
WebSocket (Binary)
    │
    ▼
audio:output event
    │
    ▼
AudioOutputService
    │
    ├─► Voice Model Check
    ├─► Format Detection
    │
    ▼
Audio Queue
    │
    ▼
AudioContext
    │
    ▼
Speakers
```

### Avatar Session Flow

```
HeyGen SDK Init
    │
    ▼
Create Avatar Session
    │
    ▼
STREAM_READY event
    │
    ▼
setAvatarSession()
    │
    ▼
Agent C Server
    │
    ├─► Voice → "avatar"
    ├─► Route audio to HeyGen
    │
    ▼
HeyGen Streaming
    │
    ▼
Video Element
```

## Event System

The SDK uses a type-safe event emitter pattern:

### Event Categories

1. **Connection Events**
   - `connected` - WebSocket connection established
   - `disconnected` - Connection closed
   - `reconnecting` - Attempting to reconnect
   - `reconnected` - Successfully reconnected

2. **Message Events**
   - `text_delta` - Streaming text chunks
   - `completion` - Response completion status
   - `error` - Error messages

3. **Audio Events**
   - `audio:output` - Binary audio from server
   - `audio:input:start` - Recording started
   - `audio:input:stop` - Recording stopped
   - `audio:level` - Audio level updates

4. **Turn Events**
   - `user_turn_start` - User can speak
   - `user_turn_end` - Agent is responding
   - `turn_state_changed` - Turn state update

5. **Session Events**
   - `chat_session_changed` - Active session changed
   - `chat_session_name_changed` - Session renamed
   - `session_metadata_changed` - Metadata updated

### Event Flow Example

```typescript
// Event emission flow
Client.sendText("Hello")
    ↓
WebSocket.send({ type: "text_input", text: "Hello" })
    ↓
Server processes
    ↓
Server sends: { type: "text_delta", content: "Hi" }
    ↓
WebSocket.onMessage()
    ↓
Client.handleMessage()
    ↓
Client.emit("text_delta", { content: "Hi" })
    ↓
Subscribers receive event
```

## Binary Protocol

The SDK supports both JSON and binary WebSocket frames:

### JSON Frames
Used for control messages and text data:
```json
{
  "type": "event_type",
  "property": "value"
}
```

### Binary Frames
Used for audio data transmission:
```
[ArrayBuffer: PCM16 audio data]
```

Binary audio is sent directly without JSON wrapping, reducing overhead:
- **Traditional**: JSON({ type: "audio", data: "base64..." }) = 133% size
- **Our approach**: ArrayBuffer(pcm16_data) = 100% size

## React Integration

The React package provides a thin wrapper around the core SDK:

```
┌─────────────────────────────────────┐
│         AgentCProvider              │
├─────────────────────────────────────┤
│ • Creates RealtimeClient            │
│ • Manages client lifecycle          │
│ • Provides React context            │
└─────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
useConnection  useAudio    useChat
    │              │              │
    ▼              ▼              ▼
Connection    Audio APIs   Message
Control                     Handling
```

### Hook Architecture

Each hook subscribes to relevant events and manages state:

```typescript
function useChat() {
    const client = useContext(AgentCContext);
    const [messages, setMessages] = useState([]);
    
    useEffect(() => {
        const handler = (event) => {
            setMessages(prev => [...prev, event.content]);
        };
        
        client.on('text_delta', handler);
        return () => client.off('text_delta', handler);
    }, [client]);
    
    return { messages, sendMessage: client.sendText };
}
```

## Performance Considerations

### Audio Processing
- **AudioWorklet** runs on separate thread, preventing main thread blocking
- **Binary transmission** reduces bandwidth by 33%
- **PCM16 format** minimizes conversion overhead

### Memory Management
- **Audio queuing** prevents memory leaks
- **Event cleanup** on component unmount
- **Singleton services** for shared resources

### Network Optimization
- **Automatic reconnection** with exponential backoff
- **Ping/pong heartbeat** for connection health
- **Binary frames** for efficient audio streaming

## Security Considerations

### Authentication
- JWT tokens with automatic refresh
- Secure token storage abstractions
- API key validation

### Data Transmission
- WSS (WebSocket Secure) for encryption
- Token-based authentication
- No sensitive data in URLs

### Browser Security
- HTTPS required for microphone access
- Permission prompts for audio
- Content Security Policy compatible

## Extensibility

The SDK is designed for extensibility:

### Custom Event Handlers
```typescript
client.on('custom_event', (data) => {
    // Handle custom server events
});
```

### Custom Audio Processing
```typescript
class CustomAudioProcessor extends AudioProcessor {
    processAudio(inputData: Float32Array): Int16Array {
        // Custom processing logic
        return super.processAudio(inputData);
    }
}
```

### Plugin System (Future)
```typescript
client.use(new TranscriptionPlugin());
client.use(new AnalyticsPlugin());
```

## Best Practices

### 1. **Lifecycle Management**
Always clean up resources:
```typescript
useEffect(() => {
    return () => client.destroy();
}, []);
```

### 2. **Error Boundaries**
Implement error handling at every level:
```typescript
try {
    await client.connect();
} catch (error) {
    handleConnectionError(error);
}
```

### 3. **State Synchronization**
Keep UI state synchronized with SDK state:
```typescript
client.on('connection_state_changed', updateUI);
```

### 4. **Performance Monitoring**
Track key metrics:
```typescript
client.on('metrics', (data) => {
    analytics.track('sdk_performance', data);
});
```

## Future Architecture Considerations

### Planned Enhancements

1. **Plugin Architecture**
   - Modular feature extensions
   - Third-party plugin support

2. **Worker Thread Audio**
   - Move more processing off main thread
   - Better performance on low-end devices

3. **WebRTC Integration**
   - Lower latency for voice
   - P2P capabilities

4. **Offline Support**
   - Message queuing
   - Automatic sync on reconnection

5. **Multi-Modal Support**
   - Screen sharing
   - File uploads
   - Image generation

### Scalability Patterns

The architecture supports horizontal scaling through:
- Stateless client design
- Server-side session management
- CDN distribution of SDK assets
- Regional WebSocket endpoints

## Conclusion

The Agent C Realtime SDK architecture prioritizes:
- **Developer experience** through clean APIs and TypeScript
- **Performance** through binary protocols and worklets
- **Reliability** through automatic reconnection and error handling
- **Flexibility** through modular design and progressive enhancement

This architecture enables developers to build production-ready real-time AI applications while maintaining the flexibility to adapt to changing requirements.