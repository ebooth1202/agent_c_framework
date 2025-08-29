# Audio System Troubleshooting Guide

## Common Issues and Solutions

### 1. Microphone Permission Issues

#### Symptoms
- "Permission denied" error when starting recording
- `audio.status.state` shows `'permission-denied'`
- No audio level indicators showing

#### Causes
- User denied microphone permission
- Browser security restrictions
- HTTPS requirement not met in production

#### Solutions

1. **Check Browser Permissions**:
```typescript
// Check current permission state
const checkPermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop()); // Clean up
    console.log('✅ Microphone permission granted');
  } catch (error) {
    console.error('❌ Microphone permission denied:', error);
  }
};
```

2. **Request Permission Explicitly**:
```typescript
const audio = useAudio();

const requestMicAccess = async () => {
  try {
    const granted = await audio.requestPermission();
    if (!granted) {
      // Show user instructions to enable microphone
      showPermissionInstructions();
    }
  } catch (error) {
    console.error('Permission request failed:', error);
  }
};
```

3. **User Instructions**:
```typescript
function PermissionInstructions() {
  return (
    <div className="permission-help">
      <h3>🎤 Microphone Access Required</h3>
      <p>To use voice conversation:</p>
      <ol>
        <li>Click the microphone icon in your browser's address bar</li>
        <li>Select "Allow" for microphone access</li>
        <li>Refresh the page and try again</li>
      </ol>
      <p>Chrome: Look for 🎤 icon in address bar</p>
      <p>Firefox: Look for 🎤 icon in address bar</p>
      <p>Safari: Check Safari → Settings → Websites → Microphone</p>
    </div>
  );
}
```

---

### 2. AudioWorklet Initialization Failures

#### Symptoms
- Audio recording fails to start
- Error: "Failed to load AudioWorklet processor"
- `audio.status.state` shows `'failed'`

#### Causes
- Browser doesn't support AudioWorklet
- HTTPS requirement not met
- Audio processor file not loading

#### Solutions

1. **Check AudioWorklet Support**:
```typescript
// Feature detection
const supportsAudioWorklet = () => {
  return typeof AudioWorklet !== 'undefined' && 
         typeof AudioContext !== 'undefined';
};

if (!supportsAudioWorklet()) {
  console.warn('AudioWorklet not supported, falling back to ScriptProcessor');
  // Implement fallback or show compatibility message
}
```

2. **Verify Audio Processor Path**:
```typescript
// Check if audio-processor.js is accessible
const checkProcessorFile = async () => {
  try {
    const response = await fetch('/audio-processor.js');
    if (!response.ok) {
      throw new Error(`Audio processor not found: ${response.status}`);
    }
    console.log('✅ Audio processor file accessible');
  } catch (error) {
    console.error('❌ Audio processor file missing:', error);
  }
};
```

3. **HTTPS Requirement**:
```typescript
// AudioWorklet requires secure context (HTTPS or localhost)
const isSecureContext = () => {
  return window.isSecureContext || 
         location.hostname === 'localhost' ||
         location.hostname === '127.0.0.1';
};

if (!isSecureContext()) {
  console.error('AudioWorklet requires HTTPS or localhost');
  // Show message to user about HTTPS requirement
}
```

---

### 3. WebSocket Connection Issues

#### Symptoms
- Agent C client shows `'disconnected'` state
- Audio streaming fails silently
- Turn management not working

#### Causes
- Network connectivity issues
- Invalid authentication token
- WebSocket server unavailable

#### Solutions

1. **Connection Diagnostics**:
```typescript
const agentClient = useSharedAgentCClient();

const diagnoseConnection = () => {
  console.log('Connection Status:', {
    state: agentClient?.state.connectionState,
    isConnected: agentClient?.isConnected(),
    websocketState: agentClient?.websocket?.readyState,
    lastError: agentClient?.state.lastError
  });
};
```

2. **Authentication Check**:
```typescript
// Verify token validity
const checkAuthentication = async () => {
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ /* auth data */ })
    });
    
    if (!response.ok) {
      console.error('Authentication failed:', response.status);
    }
  } catch (error) {
    console.error('Auth check failed:', error);
  }
};
```

3. **Reconnection Logic**:
```typescript
const handleConnectionLoss = () => {
  const agentClient = useSharedAgentCClient();
  
  useEffect(() => {
    if (!agentClient?.isConnected()) {
      console.log('Connection lost, attempting reconnect...');
      // Implement exponential backoff reconnection
      setTimeout(() => {
        agentClient?.connect();
      }, 2000);
    }
  }, [agentClient?.state.connectionState]);
};
```

---

### 4. Turn Management Issues

#### Symptoms
- Audio chunks not suppressed during agent speech
- User can't interrupt agent
- Turn indicators stuck or incorrect

#### Causes
- Turn events not being received
- Turn state not properly synchronized
- Client-side turn logic errors

#### Solutions

1. **Turn Event Debugging**:
```typescript
const turn = useTurnState();

// Enable turn event logging
const debugTurnEvents = () => {
  const bridge = AudioAgentCBridge.getInstance();
  bridge.updateConfig({ logTurnEvents: true });
  
  console.log('Turn State:', {
    userHasTurn: turn.userHasTurn,
    agentIsSpeaking: turn.agentIsSpeaking,
    chunksSuppressed: turn.chunksSuppressed
  });
};
```

2. **Manual Turn Control** (for testing):
```typescript
function TurnDebugControls() {
  const turn = useTurnState();
  
  return (
    <div className="debug-controls">
      <button onClick={() => turn.requestTurn()}>
        Force User Turn
      </button>
      <button onClick={() => turn.releaseTurn()}>
        Force Agent Turn  
      </button>
      <div>Current: {turn.userHasTurn ? 'User' : 'Agent'}</div>
    </div>
  );
}
```

3. **Turn State Reset**:
```typescript
// Reset turn state if stuck
const resetTurnState = () => {
  const bridge = AudioAgentCBridge.getInstance();
  bridge.reset();
  console.log('Turn state reset');
};
```

---

### 5. Audio Quality Issues

#### Symptoms
- Choppy or distorted audio
- Audio dropouts or gaps
- Poor audio quality

#### Causes
- Network bandwidth limitations
- Audio buffer underruns
- Sample rate mismatches
- CPU performance issues

#### Solutions

1. **Audio Buffer Monitoring**:
```typescript
const output = AudioOutputService.getInstance();

// Monitor audio output status
const monitorAudioQuality = () => {
  const status = output.getStatus();
  console.log('Audio Quality Metrics:', {
    queueLength: status.queueLength,
    chunksPlayed: status.chunksPlayed,
    chunksSkipped: status.chunksSkipped,
    volume: status.volume
  });
  
  if (status.queueLength > 10) {
    console.warn('Audio buffer getting full - possible playback delay');
  }
  
  if (status.chunksSkipped > status.chunksPlayed * 0.1) {
    console.warn('High skip rate - possible performance issues');
  }
};
```

2. **Network Performance Check**:
```typescript
const checkNetworkPerformance = async () => {
  const startTime = performance.now();
  const testData = new ArrayBuffer(1600); // 100ms of audio at 16kHz
  
  try {
    // Send test audio chunk
    agentClient?.sendAudioChunk(testData);
    const latency = performance.now() - startTime;
    
    console.log('Network Latency:', latency, 'ms');
    
    if (latency > 100) {
      console.warn('High network latency detected');
    }
  } catch (error) {
    console.error('Network test failed:', error);
  }
};
```

3. **Performance Optimization**:
```typescript
// Adjust audio chunk size for performance
const optimizeForPerformance = () => {
  const audioService = AudioService.getInstance();
  
  // Reduce chunk duration for lower latency
  audioService.updateConfig({
    chunkDurationMs: 50 // Smaller chunks for better response
  });
};
```

---

### 6. Voice Model Issues

#### Symptoms
- Voice changes not taking effect
- Audio playing when avatar mode active
- Text-only mode still processing audio

#### Causes
- Voice model synchronization issues
- Audio output not adapting to voice model
- Race conditions in voice changes

#### Solutions

1. **Voice Model Debugging**:
```typescript
const voice = useVoiceModel();

const debugVoiceModel = () => {
  console.log('Voice Model Status:', {
    currentVoice: voice.currentVoice,
    supportsLocalTTS: voice.supportsLocalTTS,
    isAvatarMode: voice.isAvatarMode,
    isTextOnly: voice.isTextOnly,
    isChangingVoice: voice.isChangingVoice,
    voiceError: voice.voiceError
  });
};
```

2. **Force Voice Sync**:
```typescript
// Manually synchronize voice model with audio output
const syncVoiceModel = () => {
  const voice = useVoiceModel();
  const output = AudioOutputService.getInstance();
  
  if (voice.currentVoice) {
    output.setVoiceModel(voice.currentVoice);
    console.log('Voice model synchronized');
  }
};
```

3. **Voice Change Error Handling**:
```typescript
const handleVoiceChange = async (voiceId: string) => {
  const voice = useVoiceModel();
  
  try {
    await voice.setVoice(voiceId);
    console.log('Voice changed successfully');
  } catch (error) {
    console.error('Voice change failed:', error);
    
    // Retry with fallback
    if (error.message.includes('timeout')) {
      setTimeout(() => voice.setVoice(voiceId), 2000);
    }
  }
};
```

## Diagnostic Tools

### 1. Audio System Health Check

```typescript
function AudioHealthCheck() {
  const audio = useAudio();
  const turn = useTurnState();
  const voice = useVoiceModel();
  const agentClient = useSharedAgentCClient();
  
  const runHealthCheck = async () => {
    const results = {
      permissions: false,
      audioService: false,
      agentConnection: false,
      turnManagement: false,
      voiceModel: false
    };
    
    try {
      // Check permissions
      results.permissions = await audio.requestPermission();
      
      // Check audio service
      results.audioService = audio.status.state === 'ready';
      
      // Check Agent C connection
      results.agentConnection = agentClient?.isConnected() || false;
      
      // Check turn management
      results.turnManagement = typeof turn.userHasTurn === 'boolean';
      
      // Check voice model
      results.voiceModel = voice.currentVoice !== null;
      
    } catch (error) {
      console.error('Health check failed:', error);
    }
    
    console.table(results);
    return results;
  };
  
  return (
    <button onClick={runHealthCheck}>
      Run Audio Health Check
    </button>
  );
}
```

### 2. Real-time Performance Monitor

```typescript
function AudioPerformanceMonitor() {
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    const interval = setInterval(() => {
      const audioService = AudioService.getInstance();
      const bridge = AudioAgentCBridge.getInstance();
      const output = AudioOutputService.getInstance();
      
      const currentMetrics = {
        timestamp: Date.now(),
        audioService: audioService.getStatus(),
        bridge: bridge.getStatus(),
        output: output.getStatus(),
        memory: (performance as any).memory?.usedJSHeapSize || 0
      };
      
      setMetrics(currentMetrics);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="performance-monitor">
      <h3>Audio Performance</h3>
      <pre>{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
}
```

### 3. Debug Console Commands

Add these to your browser console for debugging:

```javascript
// Global debug functions (add to window in development)
window.audioDebug = {
  // Get all service statuses
  getStatus() {
    return {
      audioService: AudioService.getInstance().getStatus(),
      bridge: AudioAgentCBridge.getInstance().getStatus(),
      output: AudioOutputService.getInstance().getStatus()
    };
  },
  
  // Test microphone access
  async testMicrophone() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('✅ Microphone access working');
      stream.getTracks().forEach(track => track.stop());
    } catch (error) {
      console.error('❌ Microphone test failed:', error);
    }
  },
  
  // Reset all audio services
  reset() {
    AudioAgentCBridge.getInstance().reset();
    console.log('Audio services reset');
  },
  
  // Enable debug logging
  enableDebugLogging() {
    AudioAgentCBridge.getInstance().updateConfig({
      logAudioChunks: true,
      logTurnEvents: true
    });
    console.log('Debug logging enabled');
  }
};
```

## Browser-Specific Issues

### Chrome
- **Issue**: AudioWorklet requires user gesture
- **Solution**: Start audio only after user interaction
- **Issue**: Autoplay policy blocks audio
- **Solution**: Ensure user interaction before playback

### Firefox  
- **Issue**: MediaDevices API differences
- **Solution**: Check `navigator.mediaDevices` availability
- **Issue**: WebSocket binary frame handling
- **Solution**: Verify ArrayBuffer support

### Safari
- **Issue**: AudioContext requires user activation
- **Solution**: Resume AudioContext after user gesture
- **Issue**: WebRTC constraints differences  
- **Solution**: Use compatible audio constraints

### Edge/IE
- **Issue**: Limited AudioWorklet support
- **Solution**: Provide ScriptProcessor fallback
- **Issue**: WebSocket compatibility
- **Solution**: Use feature detection

## Performance Optimization Tips

1. **Reduce Audio Latency**:
   - Use smaller chunk sizes (50-100ms)
   - Minimize audio processing in main thread
   - Use AudioWorklet instead of ScriptProcessor

2. **Memory Management**:
   - Clear audio buffers regularly
   - Limit turn history size
   - Use singleton services efficiently

3. **Network Optimization**:
   - Monitor WebSocket frame sizes
   - Implement connection pooling
   - Use binary frames exclusively for audio

4. **CPU Optimization**:
   - Avoid blocking operations in audio callbacks
   - Use requestAnimationFrame for UI updates
   - Profile audio processing performance

When troubleshooting audio issues, always start with the health check, enable debug logging, and verify basic functionality before investigating complex scenarios.