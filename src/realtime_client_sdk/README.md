# Agent C Realtime SDK

A TypeScript SDK for real-time AI conversations with support for HeyGen interactive avatars, WebSocket communication, and Agent C API integration.

## Features

### Core Capabilities
- **HeyGen Avatar Integration** - Full support for HeyGen interactive avatars
- **Agent C API Integration** - WebSocket-based AI conversation support  
- **Real-time Communication** - WebRTC and WebSocket transport options
- **Voice Chat** - Bidirectional voice communication with avatars
- **Quality Monitoring** - Connection quality indicators and adaptive streaming
- **TypeScript Support** - Full TypeScript definitions and type safety

### Agent C Integration
- **WebSocket API Client** - Direct integration with Agent C realtime API
- **AI Conversation Flow** - Seamless AI-powered avatar conversations
- **Session Management** - Support for Agent C-managed avatar sessions
- **Event-driven Architecture** - Real-time event handling for AI interactions

## Installation 

```
npm install @agentc/realtime-sdk
```

To build and compile the typescript sources to javascript run install then:
```
npm run build
```

## Basic Usage

For a demo of this SDK in action, see the Virtual Joe reference implementation that showcases Agent C API integration with HeyGen avatars.

```JS
import StreamingAvatar, { AvatarQuality, StreamingEvents } from '@agentc/realtime-sdk';

let streamingAvatar;
async function startChatCreation(){
    streamingAvatar = new StreamingAvatar({token: 'ENTER_ACCESS_TOKEN_HERE'});

    // some events
    streamingAvatar.on(StreamingEvents.AVATAR_START_TALKING, (e) => {});
    streamingAvatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {});
    streamingAvatar.on(StreamingEvents.STREAM_READY, (event) => {});

    const sessionInfo = await streamingAvatar.createStartAvatar({
        quality: AvatarQuality.Low,
        avatarName: avatarId,
        knowledgeId: knowledgeId, // from labs.heygen.com
        // knowledgeBase: knowledgeBase, // your customized prompt content
        voice: {
          voiceId: voiceId,
          rate: 1.5, // 0.5 ~ 1.5
          emotion: VoiceEmotion.EXCITED,
          // elevenlabsSettings: {} // https://docs.heygen.com/reference/new-session#voicesetting
          // model: ElevenLabsModel.MULTILINGUAL, elevenlabs audio model
        },
        sttSettings: {
          provider: STTProvider.DEEPGRAM, // STT provider to use. The default is DEEPGRAM.
          confidence: 0.55, // The default is 0.55.
        },
        language: language,
        // disableIdleTimeout: false, // Default is false; enable cautiously.
        voiceChatTransport?: VoiceChatTransport.WEBSOCKET, // user input transport. The default is WEBSOCKET
        // number of seconds that avatar will wait before closing session after last activity, 
        // expects value from 30 to 3600 (1h)
        activityIdleTimeout?: number, // The default is 120 (2 minutes)
    });
    
    // switch to voice chat. in this mode, we will record your voice and keep chatting with avatar in real time.
    await streamingAvatar.startVoiceChat({
      useSilencePrompt: true, // the default is false. true means you will receive silence prompts.
      isInputAudioMuted: true, // the default is false. you can also handle `mute` by using streamingAvatar.muteInputAudio(), streamingAvatar.unmuteInputAudio().
    });
}

// In text mode, please use the speak method (Default TALK type).
streamingAvatar.speak({ text: text, task_type: TaskType.REPEAT, taskMode: TaskMode.SYNC });

// Please note, you can use the speak method in voice chat, but only the TALK type is supported in voice chat mode.
streamingAvatar.speak({ text: text })

// close voice chat, will stop recording your voice.
streamingAvatar.closeVoiceChat();

// close the session
streamingAvatar.stopAvatar();

// keep session alive, will be count as an activity to keep session for additional `activityIdleTimeout` seconds
// after last activity.
streamingAvatar.keepAlive();

// interrupt the avatar's talking
streamingAvatar.interrupt();

// it's helpful in text mode. `startListening` will let the avatar switch to listening state.
streamingAvatar.startListening();
streamingAvatar.stopListening();
```

## Agent C Integration

This SDK is part of the [Agent C Framework](https://github.com/centricconsulting/agent_c_framework) and is designed to work seamlessly with the Agent C API for AI-powered conversations:

```typescript
import { AgentCClient } from '@agentc/realtime-sdk';

// Connect to Agent C WebSocket API
const agentCClient = new AgentCClient({
  apiUrl: 'ws://localhost:8000/ws',
  jwtToken: 'your-jwt-token'
});

// Use Agent C session data with HeyGen avatars
const avatar = new StreamingAvatar({ 
  token: agentCSession.access_token 
});
```

## Troubleshooting FAQ

### How do I get an Access token Key?

For HeyGen integration, you can get access tokens through:
1. **Agent C API** - Agent C will provide HeyGen access tokens automatically
2. **Direct HeyGen API** - For standalone usage (Enterprise customers only)

```
curl -X POST https://api.heygen.com/v1/streaming.create_token -H "x-api-key: <api-key>"
```

### Which Avatars can I use with this project?

By default, there are several Public Interactive Avatars that can be used. You can find the Avatar IDs for these Avatars by navigating to labs.heygen.com/interactive-avatar and clicking 'Select Avatar'.

You can create your own Interactive Avatar to use with this API by visiting labs.heygen.com/interactive-avatar and clicking 'Create Interactive Avatar' at the bottom of the screen.

### Why am I encountering issues with testing?

Most likely, you are hitting your concurrent session limit. While testing this API with your Trial Token, only 3 concurrent sessions can be created. Please endeavor to close unused sessions with the Close Session endpoint when they are no longer being used; they will automatically close after some minutes.

You can check how many active sessions you have open with the List Sessions endpoint: https://docs.heygen.com/reference/list-sessions

## Version History

### 1.0.0 (Agent C Realtime SDK)
- Forked from HeyGen StreamingAvatarSDK 2.0.16
- Rebranded as Agent C Realtime SDK
- Added Agent C API integration foundation
- Updated package identity and documentation

### Previous HeyGen SDK Features
- Activity idle timeout control and keepAlive method
- LiveKit support for user audio and text input
- Quality indicators and connection monitoring
- ElevenLabs voice model support (eleven_flash_v2_5, eleven_multilingual_v2)
- Gladia STT provider option
- Audio muting during voice chat
- Voice chat functionality
- Improved API events and smoother video experience
- Avatar listening state control
- Duration reporting in avatar_stop_talking events
- Knowledge base and chat mode support
- Voice rate and emotion control
- Jitter buffer target configuration
- Interrupt streaming support
- Event callbacks for start/stop