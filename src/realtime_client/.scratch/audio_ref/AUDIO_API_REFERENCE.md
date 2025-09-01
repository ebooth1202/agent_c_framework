# Audio System API Reference

## React Hooks API

### useAudio()

Primary hook providing complete audio functionality with turn management and voice model integration.

```typescript
function useAudio(options?: UseAudioOptions): UseAudioReturn
```

#### Parameters
```typescript
interface UseAudioOptions {
  respectTurnState?: boolean;     // Enable turn management (default: true)
  autoStartOnConnect?: boolean;   // Auto-start streaming when Agent C connects (default: false)
  logAudioChunks?: boolean;       // Log audio chunks for debugging (default: false)
  logTurnEvents?: boolean;        // Log turn management events (default: false)
}
```

#### Returns
```typescript
interface UseAudioReturn {
  // Extended status with turn state and voice model info
  status: ExtendedAudioStatus;
  
  // Control methods
  startRecording(): Promise<void>;
  stopRecording(): void;
  startStreaming(): Promise<void>;
  stopStreaming(): void;
  toggleMute(): void;
  requestPermission(): Promise<boolean>;
  
  // UI state
  isMuted: boolean;
  
  // Computed properties
  canRecord: boolean;           // Service is ready
  isRecording: boolean;         // Currently recording
  needsPermission: boolean;     // Permission denied state
  hasError: boolean;           // Service has error
  canStartRecording: boolean;   // Can record (ready + has turn)
  isAudioActive: boolean;      // Recording or streaming
}
```

#### Extended Audio Status
```typescript
interface ExtendedAudioStatus extends AudioServiceStatus {
  // Turn management
  userHasTurn: boolean;
  agentIsSpeaking: boolean;
  chunksSuppressed: number;
  
  // Voice model information
  currentVoice: VoiceModel | null;
  supportsLocalTTS: boolean;
  isAvatarMode: boolean;
  isTextOnly: boolean;
  
  // Streaming status
  isStreaming: boolean;
  chunksStreamed: number;
}
```

#### Example Usage
```typescript
function VoiceConversation() {
  const audio = useAudio({ 
    respectTurnState: true,
    autoStart: false 
  });
  
  const handleStartConversation = async () => {
    try {
      await audio.requestPermission();
      await audio.startRecording();
      await audio.startStreaming();
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };
  
  return (
    <div>
      <button 
        onClick={handleStartConversation}
        disabled={!audio.canStartRecording}
      >
        {audio.isRecording ? 'Recording...' : 'Start Conversation'}
      </button>
      
      <div>
        Audio Level: {Math.round(audio.status.audioLevel * 100)}%
      </div>
      
      {!audio.status.userHasTurn && (
        <div>Waiting for your turn...</div>
      )}
    </div>
  );
}
```

---

### useTurnState()

Hook for managing conversation turn state.

```typescript
function useTurnState(): UseTurnStateReturn
```

#### Returns
```typescript
interface UseTurnStateReturn {
  // Turn state
  userHasTurn: boolean;
  agentIsSpeaking: boolean;
  chunksSuppressed: number;
  
  // Turn control (for testing/manual control)
  requestTurn(): void;
  releaseTurn(): void;
  
  // Turn history
  turnHistory: TurnHistoryEntry[];
}

interface TurnHistoryEntry {
  timestamp: number;
  type: 'user_turn_start' | 'user_turn_end';
  reason?: string;
}
```

#### Example Usage
```typescript
function TurnIndicator() {
  const turn = useTurnState();
  
  return (
    <div className={turn.userHasTurn ? 'user-turn' : 'agent-turn'}>
      {turn.userHasTurn ? 'Your Turn' : 'Agent Speaking'}
      
      {turn.chunksSuppressed > 0 && (
        <small>({turn.chunksSuppressed} chunks suppressed)</small>
      )}
    </div>
  );
}
```

---

### useVoiceModel()

Hook for voice model selection and management.

```typescript
function useVoiceModel(): UseVoiceModelReturn
```

#### Returns
```typescript
interface UseVoiceModelReturn {
  // Current voice state
  currentVoice: VoiceModel | null;
  availableVoices: VoiceModel[];
  isChangingVoice: boolean;
  voiceError: string | null;
  
  // Voice control
  setVoice(voiceId: string): Promise<void>;
  
  // Voice utilities
  getVoicesByFormat(format: string): VoiceModel[];
  findVoiceById(voiceId: string): VoiceModel | undefined;
  
  // Voice capabilities
  supportsLocalTTS: boolean;
  isAvatarMode: boolean;
  isTextOnly: boolean;
}
```

#### Voice Model Interface
```typescript
interface VoiceModel {
  voice_id: string;
  name: string;
  language: string;
  gender: 'male' | 'female' | 'neutral';
  format: 'pcm16' | 'special' | 'none';
  vendor: string;
  sample_text?: string;
}
```

#### Example Usage
```typescript
function VoiceSelector() {
  const voice = useVoiceModel();
  
  const handleVoiceChange = async (voiceId: string) => {
    try {
      await voice.setVoice(voiceId);
    } catch (error) {
      console.error('Failed to change voice:', error);
    }
  };
  
  return (
    <select 
      value={voice.currentVoice?.voice_id || ''}
      onChange={(e) => handleVoiceChange(e.target.value)}
      disabled={voice.isChangingVoice}
    >
      <option value="">Select Voice</option>
      {voice.availableVoices.map(v => (
        <option key={v.voice_id} value={v.voice_id}>
          {v.name} ({v.vendor})
        </option>
      ))}
    </select>
  );
}
```

## Service Classes API

### AudioService

Singleton service managing microphone access and audio processing.

```typescript
class AudioService {
  static getInstance(): AudioService;
  
  // Recording control
  startRecording(): Promise<void>;
  stopRecording(): void;
  
  // Status monitoring
  getStatus(): AudioServiceStatus;
  onStatusChange(callback: (status: AudioServiceStatus) => void): () => void;
  
  // Audio data
  onAudioChunk(callback: (chunk: AudioChunkData) => void): () => void;
  
  // Permissions
  requestPermission(): Promise<boolean>;
  hasPermission(): boolean;
}
```

#### AudioServiceStatus
```typescript
interface AudioServiceStatus {
  state: 'idle' | 'initializing' | 'ready' | 'recording' | 'failed' | 'permission-denied';
  isRecording: boolean;
  audioLevel: number;          // 0.0 to 1.0
  frameCount: number;
  error?: string;
  
  // Device information
  deviceId?: string;
  sampleRate: number;
  channelCount: number;
}
```

#### AudioChunkData
```typescript
interface AudioChunkData {
  content: ArrayBuffer;        // PCM16 audio data
  content_type: string;        // "audio/L16"
  audio_level: number;         // RMS audio level (0.0-1.0)
  frame_count: number;         // Sequential frame counter
  timestamp: number;           // Capture timestamp
  sample_rate: number;         // 16000
}
```

---

### AudioAgentCBridge

Singleton service bridging AudioService to Agent C WebSocket.

```typescript
class AudioAgentCBridge {
  static getInstance(config?: AudioAgentCBridgeConfig): AudioAgentCBridge;
  
  // Client management
  setAgentCClient(client: AgentCRealtimeClient | null): void;
  
  // Streaming control
  startStreaming(): Promise<void>;
  stopStreaming(): void;
  
  // Status monitoring
  getStatus(): AudioAgentCBridgeStatus;
  onStatusChange(callback: (status: AudioAgentCBridgeStatus) => void): () => void;
  
  // Configuration
  updateConfig(config: Partial<AudioAgentCBridgeConfig>): void;
  reset(): void;
}
```

#### AudioAgentCBridgeConfig
```typescript
interface AudioAgentCBridgeConfig {
  autoStartOnConnect?: boolean;    // Auto-start streaming when connected
  logAudioChunks?: boolean;       // Debug logging for audio chunks
  respectTurnState?: boolean;     // Enable turn-based audio gating
  logTurnEvents?: boolean;        // Debug logging for turn events
}
```

#### AudioAgentCBridgeStatus
```typescript
interface AudioAgentCBridgeStatus {
  isStreaming: boolean;           // Currently sending audio to Agent C
  isConnected: boolean;           // Agent C WebSocket connected
  userHasTurn: boolean;          // User has conversational turn
  chunksStreamed: number;        // Total chunks sent
  chunksSuppressed: number;      // Chunks suppressed due to turn state
  lastError?: string;            // Last error encountered
}
```

---

### AudioOutputService

Singleton service managing TTS audio playback.

```typescript
class AudioOutputService {
  static getInstance(): AudioOutputService;
  
  // Playback control
  playAudioChunk(audioData: ArrayBuffer): void;
  stopPlayback(): void;
  clearBuffers(): void;
  
  // Configuration
  setVolume(volume: number): void;        // 0.0 to 1.0
  setVoiceModel(voiceModel: VoiceModel): void;
  setEnabled(enabled: boolean): void;
  
  // Status monitoring
  getStatus(): AudioOutputStatus;
  onStatusChange(callback: (status: AudioOutputStatus) => void): () => void;
}
```

#### AudioOutputStatus
```typescript
interface AudioOutputStatus {
  isPlaying: boolean;
  isEnabled: boolean;             // Based on voice model
  volume: number;                 // 0.0 to 1.0
  chunksReceived: number;
  chunksPlayed: number;
  chunksSkipped: number;          // Skipped due to voice model
  queueLength: number;            // Buffered chunks
  currentVoiceModel: VoiceModel | null;
}
```

## Agent C Client API

### Binary Audio Methods

```typescript
class AgentCRealtimeClient {
  // Binary audio transmission
  sendAudioChunk(audioBuffer: ArrayBuffer): void;
  
  // Voice model management
  setAgentVoice(voiceId: string): Promise<void>;
  
  // Turn state access
  getUserHasTurn(): boolean;
  getCurrentVoice(): VoiceModel | null;
  
  // Event handlers
  on(event: 'onAudioOutput', handler: (audioData: ArrayBuffer) => void): void;
  on(event: 'onUserTurnStart', handler: () => void): void;
  on(event: 'onUserTurnEnd', handler: () => void): void;
  on(event: 'onAgentVoiceChanged', handler: (event: AgentVoiceChangedEvent) => void): void;
}
```

## Error Types

### AudioError
```typescript
class AudioError extends Error {
  code: string;
  details?: any;
  
  constructor(message: string, code: string, details?: any);
}

// Common error codes
const AudioErrorCodes = {
  PERMISSION_DENIED: 'permission_denied',
  DEVICE_NOT_FOUND: 'device_not_found',
  INITIALIZATION_FAILED: 'initialization_failed',
  CONNECTION_LOST: 'connection_lost',
  UNSUPPORTED_FORMAT: 'unsupported_format',
  TURN_VIOLATION: 'turn_violation'
} as const;
```

## Component Props Interfaces

### Audio Visualization Components

```typescript
// AudioLevelMeter
interface AudioLevelMeterProps {
  audioLevel: number;              // 0.0 to 1.0
  style?: 'bars' | 'progress' | 'circular' | 'waveform';
  size?: 'sm' | 'md' | 'lg';
  theme?: 'light' | 'dark' | 'neon';
  showValue?: boolean;
  className?: string;
}

// TurnIndicator  
interface TurnIndicatorProps {
  userHasTurn: boolean;
  agentIsSpeaking?: boolean;
  chunksSuppressed?: number;
  showStats?: boolean;
  className?: string;
}

// StreamingStatusIndicator
interface StreamingStatusProps {
  isStreaming: boolean;
  isRecording: boolean;
  connectionState: 'connected' | 'connecting' | 'disconnected';
  className?: string;
}
```

## Best Practices

### Hook Usage Patterns

1. **Primary Audio Hook**:
```typescript
// Use useAudio() as primary interface
const audio = useAudio({ respectTurnState: true });

// Access extended status for turn/voice info
const { userHasTurn, currentVoice, chunksStreamed } = audio.status;
```

2. **Specialized Hooks**:
```typescript
// Use specialized hooks for specific functionality
const turn = useTurnState();        // For turn-specific UI
const voice = useVoiceModel();      // For voice selection UI
```

3. **Error Handling**:
```typescript
const audio = useAudio();

useEffect(() => {
  if (audio.hasError) {
    // Handle audio errors appropriately
    console.error('Audio error:', audio.status.error);
    // Show user-friendly error message
  }
}, [audio.hasError, audio.status.error]);
```

### Service Integration

1. **Singleton Access**:
```typescript
// Always use getInstance() - never instantiate directly
const audioService = AudioService.getInstance();
const bridge = AudioAgentCBridge.getInstance();
const output = AudioOutputService.getInstance();
```

2. **Event Cleanup**:
```typescript
useEffect(() => {
  const unsubscribe = audioService.onStatusChange(handleStatusChange);
  return unsubscribe; // Always clean up subscriptions
}, []);
```

3. **Error Recovery**:
```typescript
// Implement retry logic for failed operations
const startWithRetry = async (maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await audio.startRecording();
      return;
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
};
```

This API provides comprehensive access to the Virtual Joe audio system while maintaining type safety, error handling, and optimal performance through efficient resource management.