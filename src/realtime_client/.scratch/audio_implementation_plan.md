# Audio System Implementation Plan

## Overview
Port the virt_joe audio architecture to the new SDK with fixes for binary transmission and integration with our simpler Turn Manager.

## Implementation Steps

### Step 1: Audio Worklet and Processor Setup
**Goal**: Create the foundation for audio processing in a separate thread

**Tasks**:
1. Create `/worklets/audio-processor.worklet.js` for PCM16 conversion
2. Create `/packages/core/src/audio/AudioProcessor.ts` to manage the worklet
3. Define core audio types and interfaces
4. Test worklet loading and basic audio capture

**Deliverables**:
- Working audio worklet that can capture microphone input
- AudioProcessor class that manages worklet lifecycle
- Basic types for audio chunks

**Dependencies**: None

---

### Step 2: AudioService Core Implementation
**Goal**: Singleton service for microphone access and recording

**Tasks**:
1. Create `/packages/core/src/audio/AudioService.ts` singleton
2. Implement microphone permission handling
3. Implement start/stop recording with AudioContext
4. Add audio level monitoring
5. Add status tracking and event emission

**Deliverables**:
- AudioService singleton with recording capabilities
- Permission management
- Observable status changes
- Audio chunk events with ArrayBuffer data

**Dependencies**: Step 1 (Audio Worklet)

---

### Step 3: WebSocket Binary Transmission
**Goal**: Ensure RealtimeClient can send raw binary frames correctly

**Tasks**:
1. Update RealtimeClient to handle binary frame transmission
2. Add `sendBinaryFrame(data: ArrayBuffer)` method
3. Ensure WebSocket binaryType is set to 'arraybuffer'
4. Add binary frame reception handling

**Deliverables**:
- RealtimeClient can send/receive binary audio frames
- No base64 encoding anywhere in the audio path

**Dependencies**: Existing RealtimeClient

---

### Step 4: AudioAgentCBridge Implementation
**Goal**: Bridge between AudioService and RealtimeClient with turn awareness

**Tasks**:
1. Create `/packages/core/src/audio/AudioAgentCBridge.ts` singleton
2. Connect to AudioService for audio chunks
3. Connect to RealtimeClient for transmission
4. Integrate with TurnManager for chunk gating
5. Add chunk suppression tracking

**Deliverables**:
- Bridge singleton that connects audio to WebSocket
- Turn-aware audio transmission (respects canSendInput)
- Chunk counting and suppression metrics

**Dependencies**: Steps 2, 3, and existing TurnManager

---

### Step 5: AudioOutputService Implementation
**Goal**: Handle TTS audio playback from server

**Tasks**:
1. Create `/packages/core/src/audio/AudioOutputService.ts` singleton
2. Implement audio buffering and playback queue
3. Add voice model awareness (skip in avatar mode)
4. Handle binary audio chunks from server
5. Add volume control and playback management

**Deliverables**:
- AudioOutputService for TTS playback
- Voice-aware playback (avatar mode handling)
- Smooth audio playback with buffering

**Dependencies**: Step 3 (binary reception)

---

### Step 6: Integration with RealtimeClient
**Goal**: Wire everything together in the main client

**Tasks**:
1. Add audio system initialization to RealtimeClient
2. Create configuration options for audio
3. Wire up audio output events from server
4. Ensure proper cleanup on disconnect
5. Add audio-related methods to client API

**Deliverables**:
- RealtimeClient with integrated audio system
- Clean initialization and cleanup
- Exposed audio control methods

**Dependencies**: Steps 4 and 5

---

### Step 7: React Hooks (useAudio)
**Goal**: Create React bindings for the audio system

**Tasks**:
1. Create `/packages/react/src/hooks/useAudio.ts`
2. Implement status monitoring and control methods
3. Add turn state integration
4. Add voice model integration
5. Handle cleanup on unmount

**Deliverables**:
- useAudio() hook with full functionality
- Clean React integration
- Proper cleanup and lifecycle management

**Dependencies**: Step 6 (integrated client)

---

### Step 8: Testing and Debugging Tools
**Goal**: Ensure everything works correctly

**Tasks**:
1. Create audio test page/component
2. Add debug logging controls
3. Create audio level visualization
4. Test binary transmission end-to-end
5. Verify turn management integration

**Deliverables**:
- Test harness for audio system
- Debug tools and visualizations
- Confirmed working audio streaming

**Dependencies**: Step 7

---

## Success Criteria

Each step should:
1. Build without TypeScript errors
2. Follow the singleton pattern where specified
3. Use ArrayBuffer for all audio data (no base64)
4. Include proper error handling
5. Be testable independently

## Risk Mitigation

1. **Browser Compatibility**: Test AudioWorklet support early
2. **Permission Handling**: Graceful degradation if mic access denied
3. **Binary Transmission**: Verify WebSocket binary frame support
4. **Turn Synchronization**: Ensure turn state is properly synchronized

## Notes

- Each step builds on previous ones but should be independently functional
- We can test each component in isolation before integration
- The architecture maintains separation of concerns throughout
- No gold plating - implement only what's specified in each step