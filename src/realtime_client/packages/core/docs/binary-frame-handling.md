# Binary Frame Handling in Agent C Realtime SDK

## Overview

The Agent C Realtime SDK supports mixed message types over WebSocket:
- **JSON messages** for control events (text messages, configuration, etc.)
- **Binary frames** for audio data transmission (no base64 encoding)

This dual approach provides optimal performance for real-time audio streaming while maintaining clean APIs for control messages.

## Architecture

### WebSocket Configuration

The WebSocket is configured with `binaryType: 'arraybuffer'` to properly handle binary data:

```typescript
const wsManager = new WebSocketManager({
  url: wsUrl,
  binaryType: 'arraybuffer',  // Critical for binary audio
  // ... other options
});
```

### Sending Data

#### Binary Audio (Raw PCM16)
Audio is sent directly as binary frames, NOT wrapped in JSON events:

```typescript
// CORRECT: Send raw binary audio
const audioBuffer: ArrayBuffer = ... // PCM16 audio data
client.sendBinaryFrame(audioBuffer);

// INCORRECT: Don't wrap audio in JSON events
// client.send({ type: 'audio_input_delta', audio: base64Audio }); // ❌ Wrong
```

#### Control Messages (JSON)
Control messages are sent as JSON-encoded events:

```typescript
// Send text input
client.sendText("Hello, agent!");

// Change voice
client.setAgentVoice("voice_id");
```

### Receiving Data

The client automatically distinguishes between message types:

```typescript
// Binary audio from server (TTS output)
client.on('audio:output', (audioData: ArrayBuffer) => {
  // audioData is raw binary audio (format depends on voice model)
  audioPlayer.playAudio(audioData);
});

// JSON events from server
client.on('text_delta', (event) => {
  console.log('Agent said:', event.content);
});
```

## Implementation Details

### WebSocketManager

The `WebSocketManager` class handles low-level WebSocket operations:

- **supportsBinary()**: Verifies the connection supports binary data
- **sendBinary()**: Dedicated method for sending binary frames
- **Message handling**: Automatically detects and routes JSON vs binary messages

### RealtimeClient

The `RealtimeClient` provides high-level APIs:

- **sendBinaryFrame(data: ArrayBuffer)**: Send raw audio to server
- **'audio:output' event**: Emitted when binary audio is received
- **Mixed message handling**: Seamlessly handles both JSON and binary

## Key Differences from JSON-wrapped Audio

### Before (Wrong Approach)
```typescript
// Audio wrapped in JSON - 33% overhead from base64
const event = {
  type: 'audio_input_delta',
  audio: btoa(audioData)  // Base64 encoding adds overhead
};
client.send(JSON.stringify(event));
```

### After (Correct Approach)
```typescript
// Direct binary transmission - no encoding overhead
client.sendBinaryFrame(audioBuffer);  // Raw PCM16 bytes
```

## Benefits

1. **Performance**: 33% bandwidth reduction by eliminating base64 encoding
2. **Simplicity**: Audio is just binary data, not wrapped in events
3. **Separation**: Clear distinction between control (JSON) and media (binary)
4. **Compatibility**: Works with standard WebSocket binary frame handling

## Testing

To verify binary frame handling:

```typescript
// 1. Check WebSocket configuration
const client = new RealtimeClient(config);
await client.connect();
// WebSocket should have binaryType = 'arraybuffer'

// 2. Send binary audio
const testAudio = new ArrayBuffer(1024);  // Test data
client.sendBinaryFrame(testAudio);  // Should send raw binary

// 3. Receive binary audio
client.on('audio:output', (data) => {
  console.log('Received binary audio:', data.byteLength, 'bytes');
});
```

## Migration Guide

If migrating from JSON-wrapped audio:

1. Replace `AudioInputDelta` events with `sendBinaryFrame()`
2. Listen for `'audio:output'` instead of parsing JSON audio events
3. Remove any base64 encoding/decoding of audio data
4. Ensure WebSocket binaryType is set to 'arraybuffer'