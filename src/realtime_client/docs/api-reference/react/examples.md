# React Examples

Complete examples demonstrating how to build applications with the Agent C Realtime React SDK.

## Table of Contents

- [Basic Chat Application](#basic-chat-application)
- [Voice Assistant](#voice-assistant)
- [Avatar Integration](#avatar-integration)
- [Multi-Session Manager](#multi-session-manager)
- [Custom UI Components](#custom-ui-components)
- [Advanced Features](#advanced-features)

---

## Basic Chat Application

A simple text chat interface with Agent C.

```tsx
// BasicChat.tsx
import React, { useState } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat
} from '@agentc/realtime-react';

function BasicChatApp() {
  return (
    <AgentCProvider 
      config={{
        apiUrl: process.env.REACT_APP_AGENTC_URL!,
        apiKey: process.env.REACT_APP_AGENTC_KEY!
      }}
      autoConnect={true}
    >
      <ChatInterface />
    </AgentCProvider>
  );
}

function ChatInterface() {
  const { isConnected, connectionState } = useConnection();
  const { messages, sendMessage, isStreaming, streamingText } = useChat();
  const [input, setInput] = useState('');
  
  const handleSend = () => {
    if (input.trim() && isConnected) {
      sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div className="chat-container">
      <div className="status-bar">
        <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {connectionState}
        </span>
      </div>
      
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-role">{message.role}</div>
            <div className="message-content">{message.content}</div>
            <div className="message-time">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {isStreaming && (
          <div className="message assistant streaming">
            <div className="message-role">assistant</div>
            <div className="message-content">
              {streamingText}
              <span className="typing-indicator">...</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          disabled={!isConnected}
        />
        <button 
          onClick={handleSend}
          disabled={!isConnected || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default BasicChatApp;
```

---

## Voice Assistant

Voice-enabled assistant with turn management.

```tsx
// VoiceAssistant.tsx
import React, { useEffect, useState } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat,
  useAudio,
  useTurnState,
  useVoiceModel
} from '@agentc/realtime-react';

function VoiceAssistantApp() {
  return (
    <AgentCProvider 
      config={{
        apiUrl: process.env.REACT_APP_AGENTC_URL!,
        apiKey: process.env.REACT_APP_AGENTC_KEY!,
        enableAudio: true,
        audioConfig: {
          enableInput: true,
          enableOutput: true,
          respectTurnState: true,
          initialVolume: 0.8
        }
      }}
    >
      <VoiceInterface />
    </AgentCProvider>
  );
}

function VoiceInterface() {
  const { connect, isConnected } = useConnection();
  const { messages, sendMessage } = useChat();
  const { 
    startRecording, 
    stopRecording, 
    isRecording,
    startStreaming,
    stopStreaming,
    isStreaming,
    audioLevel,
    volume,
    setVolume,
    error: audioError
  } = useAudio();
  const { currentTurn, isUserTurn, isAgentTurn } = useTurnState();
  const { currentVoice, availableVoices, setVoice } = useVoiceModel();
  
  const [isListening, setIsListening] = useState(false);
  
  // Auto-connect on mount
  useEffect(() => {
    connect().catch(console.error);
  }, []);
  
  // Handle turn-based audio
  useEffect(() => {
    if (isUserTurn && isListening && !isStreaming) {
      startStreaming();
    } else if (!isUserTurn && isStreaming) {
      stopStreaming();
    }
  }, [isUserTurn, isListening, isStreaming]);
  
  const toggleListening = async () => {
    if (!isListening) {
      try {
        await startRecording();
        setIsListening(true);
        if (isUserTurn) {
          startStreaming();
        }
      } catch (err) {
        console.error('Microphone error:', err);
        if (err.name === 'NotAllowedError') {
          alert('Please allow microphone access to use voice features');
        }
      }
    } else {
      stopStreaming();
      stopRecording();
      setIsListening(false);
    }
  };
  
  return (
    <div className="voice-assistant">
      <header className="control-panel">
        <div className="connection-status">
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
        
        <div className="voice-selector">
          <label>Voice:</label>
          <select 
            value={currentVoice?.voice_id || 'none'}
            onChange={(e) => setVoice(e.target.value)}
          >
            <option value="none">Text Only</option>
            {availableVoices.map(voice => (
              <option key={voice.voice_id} value={voice.voice_id}>
                {voice.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="volume-control">
          <label>Volume:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
          />
          <span>{Math.round(volume * 100)}%</span>
        </div>
      </header>
      
      <main className="conversation">
        <div className="turn-indicator">
          <div className={`turn-state ${currentTurn}`}>
            {isUserTurn && '🎤 Your turn to speak'}
            {isAgentTurn && '🤖 Agent is speaking'}
            {!isUserTurn && !isAgentTurn && '⏸️ Ready'}
          </div>
        </div>
        
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="content">
                {msg.content}
              </div>
            </div>
          ))}
        </div>
        
        {audioError && (
          <div className="error-message">
            Audio Error: {audioError.message}
          </div>
        )}
      </main>
      
      <footer className="voice-controls">
        <button 
          className={`mic-button ${isListening ? 'active' : ''}`}
          onClick={toggleListening}
          disabled={!isConnected}
        >
          {isListening ? '🔴 Stop' : '🎤 Start'} Listening
        </button>
        
        <div className="audio-visualizer">
          <div className="level-meter">
            <div 
              className="level-bar"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
          <span className="level-label">
            {isStreaming ? 'Streaming' : isRecording ? 'Recording' : 'Idle'}
          </span>
        </div>
        
        <button 
          className="text-input-toggle"
          onClick={() => {
            const text = prompt('Enter your message:');
            if (text) sendMessage(text);
          }}
        >
          ⌨️ Type Instead
        </button>
      </footer>
    </div>
  );
}

export default VoiceAssistantApp;
```

---

## Avatar Integration

HeyGen avatar with synchronized audio.

```tsx
// AvatarChat.tsx
import React, { useRef, useState, useEffect } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat,
  useAvatar,
  useVoiceModel
} from '@agentc/realtime-react';
import NewStreamingAvatar, { StreamingEvents } from '@heygen/streaming-avatar';

function AvatarChatApp() {
  return (
    <AgentCProvider 
      config={{
        apiUrl: process.env.REACT_APP_AGENTC_URL!,
        apiKey: process.env.REACT_APP_AGENTC_KEY!,
        enableAudio: true
      }}
    >
      <AvatarInterface />
    </AgentCProvider>
  );
}

function AvatarInterface() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const heygenRef = useRef<NewStreamingAvatar | null>(null);
  
  const { connect, isConnected } = useConnection();
  const { messages, sendMessage } = useChat();
  const {
    availableAvatars,
    currentAvatar,
    isSessionActive,
    startAvatarSession,
    endAvatarSession
  } = useAvatar();
  const { setVoice } = useVoiceModel();
  
  const [selectedAvatarId, setSelectedAvatarId] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const [input, setInput] = useState('');
  
  useEffect(() => {
    connect().catch(console.error);
  }, []);
  
  const initializeAvatar = async () => {
    if (!selectedAvatarId) return;
    
    setIsInitializing(true);
    
    try {
      // Get HeyGen token from client
      const client = (window as any).__agentc_client;
      const heygenToken = client?.getHeyGenAccessToken();
      
      if (!heygenToken) {
        throw new Error('HeyGen token not available');
      }
      
      // Create HeyGen instance
      const avatar = new NewStreamingAvatar({ token: heygenToken });
      heygenRef.current = avatar;
      
      // Set up event listeners
      avatar.on(StreamingEvents.STREAM_READY, (event) => {
        console.log('Avatar stream ready');
        if (videoRef.current && event.stream) {
          videoRef.current.srcObject = event.stream;
          videoRef.current.play();
        }
        
        // Notify Agent C about avatar session
        startAvatarSession(selectedAvatarId);
        
        // Switch to avatar voice mode
        setVoice('avatar');
      });
      
      avatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {
        console.log('Avatar stream disconnected');
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
        endAvatarSession();
      });
      
      // Start avatar
      await avatar.createStartAvatar({
        avatarName: selectedAvatarId,
        quality: 'high',
        voice: {
          voiceId: 'avatar' // Agent C handles voice
        }
      });
      
    } catch (error) {
      console.error('Failed to initialize avatar:', error);
      alert('Failed to start avatar. Please try again.');
    } finally {
      setIsInitializing(false);
    }
  };
  
  const stopAvatar = async () => {
    if (heygenRef.current) {
      await heygenRef.current.stopAvatar();
      heygenRef.current = null;
    }
    endAvatarSession();
    setVoice('nova'); // Switch back to default voice
  };
  
  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div className="avatar-chat">
      <div className="avatar-section">
        {!isSessionActive ? (
          <div className="avatar-selector">
            <h3>Select an Avatar</h3>
            <div className="avatar-grid">
              {availableAvatars.map(avatar => (
                <div 
                  key={avatar.avatar_id}
                  className={`avatar-card ${selectedAvatarId === avatar.avatar_id ? 'selected' : ''}`}
                  onClick={() => setSelectedAvatarId(avatar.avatar_id)}
                >
                  {avatar.preview_url && (
                    <img src={avatar.preview_url} alt={avatar.name} />
                  )}
                  <h4>{avatar.name}</h4>
                  <p>{avatar.description}</p>
                </div>
              ))}
            </div>
            
            <button 
              onClick={initializeAvatar}
              disabled={!selectedAvatarId || !isConnected || isInitializing}
              className="start-avatar-btn"
            >
              {isInitializing ? 'Starting...' : 'Start Avatar'}
            </button>
          </div>
        ) : (
          <div className="avatar-view">
            <video 
              ref={videoRef}
              className="avatar-video"
              autoPlay
              playsInline
            />
            <div className="avatar-info">
              <h3>{currentAvatar?.name}</h3>
              <button onClick={stopAvatar} className="stop-avatar-btn">
                Stop Avatar
              </button>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-section">
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <strong>{msg.role}:</strong> {msg.content}
            </div>
          ))}
        </div>
        
        <div className="input-area">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            disabled={!isConnected}
          />
          <button onClick={handleSend} disabled={!isConnected}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default AvatarChatApp;
```

---

## Multi-Session Manager

Manage multiple chat sessions with history.

```tsx
// MultiSessionManager.tsx
import React, { useState } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat
} from '@agentc/realtime-react';

function MultiSessionApp() {
  return (
    <AgentCProvider 
      config={{
        apiUrl: process.env.REACT_APP_AGENTC_URL!,
        apiKey: process.env.REACT_APP_AGENTC_KEY!
      }}
      autoConnect={true}
    >
      <SessionManager />
    </AgentCProvider>
  );
}

function SessionManager() {
  const { isConnected } = useConnection();
  const {
    messages,
    sendMessage,
    currentSessionId,
    sessions,
    newSession,
    resumeSession,
    setSessionName,
    clearMessages
  } = useChat();
  
  const [input, setInput] = useState('');
  const [isRenamingSession, setIsRenamingSession] = useState(false);
  const [newName, setNewName] = useState('');
  
  const handleNewSession = () => {
    const agentKey = prompt('Enter agent key (optional):');
    newSession(agentKey || undefined);
  };
  
  const handleRenameSession = () => {
    if (newName.trim()) {
      setSessionName(newName);
      setIsRenamingSession(false);
      setNewName('');
    }
  };
  
  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };
  
  return (
    <div className="session-manager">
      <aside className="session-list">
        <div className="session-header">
          <h3>Sessions</h3>
          <button onClick={handleNewSession} disabled={!isConnected}>
            + New
          </button>
        </div>
        
        <ul className="sessions">
          {sessions.map(session => (
            <li
              key={session.session_id}
              className={session.session_id === currentSessionId ? 'active' : ''}
              onClick={() => resumeSession(session.session_id)}
            >
              <div className="session-name">
                {session.session_name || `Session ${session.session_id.slice(0, 8)}`}
              </div>
              <div className="session-meta">
                {session.messages.length} messages
              </div>
              <div className="session-time">
                {new Date(session.updated_at).toLocaleDateString()}
              </div>
            </li>
          ))}
        </ul>
      </aside>
      
      <main className="chat-area">
        <header className="chat-header">
          {currentSessionId && (
            <div className="session-info">
              {isRenamingSession ? (
                <div className="rename-form">
                  <input
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleRenameSession()}
                    placeholder="Session name..."
                    autoFocus
                  />
                  <button onClick={handleRenameSession}>Save</button>
                  <button onClick={() => setIsRenamingSession(false)}>Cancel</button>
                </div>
              ) : (
                <div className="session-title">
                  <h2>
                    {sessions.find(s => s.session_id === currentSessionId)?.session_name || 
                     `Session ${currentSessionId?.slice(0, 8)}`}
                  </h2>
                  <button onClick={() => setIsRenamingSession(true)}>
                    ✏️ Rename
                  </button>
                  <button onClick={clearMessages}>
                    🗑️ Clear
                  </button>
                </div>
              )}
            </div>
          )}
        </header>
        
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-header">
                <span className="role">{msg.role}</span>
                <span className="time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
        </div>
        
        <footer className="input-area">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            disabled={!isConnected || !currentSessionId}
          />
          <button 
            onClick={handleSend}
            disabled={!isConnected || !currentSessionId || !input.trim()}
          >
            Send
          </button>
        </footer>
      </main>
    </div>
  );
}

export default MultiSessionApp;
```

---

## Custom UI Components

Reusable components for Agent C applications.

```tsx
// CustomComponents.tsx
import React from 'react';
import {
  useConnection,
  useAudio,
  useTurnState,
  useVoiceModel
} from '@agentc/realtime-react';

// Connection Status Badge
export function ConnectionBadge() {
  const { isConnected, connectionState, reconnectAttempt } = useConnection();
  
  return (
    <div className={`connection-badge ${connectionState.toLowerCase()}`}>
      {isConnected && '🟢'}
      {!isConnected && '🔴'}
      {reconnectAttempt > 0 && '🔄'}
      <span>{connectionState}</span>
      {reconnectAttempt > 0 && (
        <span className="reconnect-info">
          Attempt {reconnectAttempt}
        </span>
      )}
    </div>
  );
}

// Audio Level Meter
export function AudioLevelMeter() {
  const { audioLevel, isRecording } = useAudio();
  
  const bars = 20;
  const activeBars = Math.round(audioLevel * bars);
  
  return (
    <div className="audio-level-meter">
      {Array.from({ length: bars }).map((_, i) => (
        <div 
          key={i}
          className={`bar ${i < activeBars ? 'active' : ''} ${
            i > bars * 0.8 ? 'high' : i > bars * 0.5 ? 'medium' : 'low'
          }`}
        />
      ))}
      {!isRecording && <div className="muted-overlay">Muted</div>}
    </div>
  );
}

// Turn Status Indicator
export function TurnIndicator() {
  const { currentTurn, isUserTurn, isAgentTurn, turnDuration } = useTurnState();
  
  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return minutes > 0 
      ? `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
      : `${seconds}s`;
  };
  
  return (
    <div className={`turn-indicator ${currentTurn}`}>
      <div className="turn-icon">
        {isUserTurn && '🎤'}
        {isAgentTurn && '🤖'}
        {!isUserTurn && !isAgentTurn && '⏸️'}
      </div>
      <div className="turn-text">
        {isUserTurn && 'Your Turn'}
        {isAgentTurn && 'Agent Speaking'}
        {!isUserTurn && !isAgentTurn && 'Ready'}
      </div>
      <div className="turn-duration">
        {formatDuration(turnDuration)}
      </div>
    </div>
  );
}

// Voice Selector Dropdown
export function VoiceSelector() {
  const { currentVoice, availableVoices, setVoice, isAvatarMode, isTextOnly } = useVoiceModel();
  
  return (
    <div className="voice-selector">
      <label htmlFor="voice-select">Voice:</label>
      <select 
        id="voice-select"
        value={currentVoice?.voice_id || 'none'}
        onChange={(e) => setVoice(e.target.value)}
      >
        <option value="none">📝 Text Only</option>
        {availableVoices.map(voice => (
          <option key={voice.voice_id} value={voice.voice_id}>
            🔊 {voice.name} ({voice.vendor})
          </option>
        ))}
        <option value="avatar">🎭 Avatar Mode</option>
      </select>
      
      <div className="voice-status">
        {isTextOnly && <span className="text-only">No Audio</span>}
        {isAvatarMode && <span className="avatar-mode">Avatar Active</span>}
        {!isTextOnly && !isAvatarMode && currentVoice && (
          <span className="voice-active">{currentVoice.name}</span>
        )}
      </div>
    </div>
  );
}

// Microphone Button with States
export function MicrophoneButton() {
  const { 
    startRecording, 
    stopRecording, 
    isRecording,
    startStreaming,
    stopStreaming,
    isStreaming,
    hasPermission,
    error
  } = useAudio();
  const { isUserTurn } = useTurnState();
  const { isConnected } = useConnection();
  
  const handleClick = async () => {
    if (!isRecording) {
      try {
        await startRecording();
        if (isUserTurn) {
          startStreaming();
        }
      } catch (err) {
        console.error('Microphone error:', err);
      }
    } else {
      stopStreaming();
      stopRecording();
    }
  };
  
  const getButtonState = () => {
    if (!isConnected) return 'disabled';
    if (!hasPermission) return 'no-permission';
    if (isStreaming) return 'streaming';
    if (isRecording) return 'recording';
    return 'idle';
  };
  
  const state = getButtonState();
  
  return (
    <button 
      className={`microphone-button ${state}`}
      onClick={handleClick}
      disabled={!isConnected}
      title={
        !hasPermission ? 'Click to grant microphone permission' :
        isStreaming ? 'Streaming audio' :
        isRecording ? 'Recording (not streaming)' :
        'Click to start recording'
      }
    >
      {state === 'streaming' && '🔴'}
      {state === 'recording' && '🟠'}
      {state === 'idle' && '🎤'}
      {state === 'no-permission' && '🔇'}
      {state === 'disabled' && '⏸️'}
      
      <span className="button-label">
        {state === 'streaming' && 'Streaming'}
        {state === 'recording' && 'Recording'}
        {state === 'idle' && 'Start'}
        {state === 'no-permission' && 'Enable Mic'}
        {state === 'disabled' && 'Offline'}
      </span>
      
      {error && (
        <span className="error-tooltip">{error.message}</span>
      )}
    </button>
  );
}
```

---

## Advanced Features

Complete application with all features integrated.

```tsx
// AdvancedApp.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  AgentCProvider,
  useRealtimeClient,
  useConnection,
  useChat,
  useAudio,
  useTurnState,
  useVoiceModel,
  useAvatar
} from '@agentc/realtime-react';

// Import custom components
import {
  ConnectionBadge,
  AudioLevelMeter,
  TurnIndicator,
  VoiceSelector,
  MicrophoneButton
} from './CustomComponents';

function AdvancedApp() {
  const [config] = useState({
    apiUrl: process.env.REACT_APP_AGENTC_URL!,
    apiKey: process.env.REACT_APP_AGENTC_KEY!,
    enableAudio: true,
    audioConfig: {
      enableInput: true,
      enableOutput: true,
      respectTurnState: true,
      initialVolume: 0.8
    }
  });
  
  return (
    <AgentCProvider config={config}>
      <AdvancedInterface />
    </AgentCProvider>
  );
}

function AdvancedInterface() {
  const client = useRealtimeClient();
  const { connect, disconnect, isConnected } = useConnection();
  const { 
    messages, 
    sendMessage, 
    streamingText, 
    isStreaming,
    newSession,
    sessions,
    currentSessionId
  } = useChat();
  const { volume, setVolume } = useAudio();
  const { currentTurn } = useTurnState();
  const { availableAvatars } = useAvatar();
  
  const [input, setInput] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  // Auto-connect on mount
  useEffect(() => {
    connect().catch(console.error);
  }, []);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
          case 'n':
            e.preventDefault();
            newSession();
            break;
          case 'd':
            e.preventDefault();
            if (isConnected) disconnect();
            else connect();
            break;
          case ',':
            e.preventDefault();
            setShowSettings(!showSettings);
            break;
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isConnected, showSettings]);
  
  // Custom event handling
  useEffect(() => {
    if (!client) return;
    
    const handleCustomEvent = (event: any) => {
      console.log('Custom event:', event);
      // Handle custom events from server
    };
    
    client.on('custom_event', handleCustomEvent);
    
    return () => {
      client.off('custom_event', handleCustomEvent);
    };
  }, [client]);
  
  const handleSend = useCallback(() => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  }, [input, sendMessage]);
  
  return (
    <div className={`advanced-app theme-${theme}`}>
      <header className="app-header">
        <div className="header-left">
          <h1>Agent C Advanced</h1>
          <ConnectionBadge />
        </div>
        
        <div className="header-center">
          <TurnIndicator />
          <AudioLevelMeter />
        </div>
        
        <div className="header-right">
          <VoiceSelector />
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className="settings-button"
          >
            ⚙️
          </button>
        </div>
      </header>
      
      {showSettings && (
        <aside className="settings-panel">
          <h3>Settings</h3>
          
          <div className="setting-group">
            <label>Theme</label>
            <select 
              value={theme} 
              onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
          
          <div className="setting-group">
            <label>Volume: {Math.round(volume * 100)}%</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
            />
          </div>
          
          <div className="setting-group">
            <h4>Sessions ({sessions.length})</h4>
            <button onClick={() => newSession()}>New Session</button>
          </div>
          
          <div className="setting-group">
            <h4>Avatars ({availableAvatars.length})</h4>
            {availableAvatars.map(avatar => (
              <div key={avatar.avatar_id}>
                {avatar.name}
              </div>
            ))}
          </div>
          
          <div className="setting-group">
            <h4>Keyboard Shortcuts</h4>
            <ul>
              <li>Ctrl+N - New session</li>
              <li>Ctrl+D - Toggle connection</li>
              <li>Ctrl+, - Toggle settings</li>
              <li>Enter - Send message</li>
            </ul>
          </div>
        </aside>
      )}
      
      <main className="app-main">
        <div className="chat-container">
          <div className="messages-area">
            {messages.map((msg, i) => (
              <div 
                key={i} 
                className={`message ${msg.role}`}
                data-timestamp={msg.timestamp}
              >
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-body">
                  <div className="message-header">
                    <span className="role">{msg.role}</span>
                    <span className="time">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            
            {isStreaming && streamingText && (
              <div className="message assistant streaming">
                <div className="message-avatar">🤖</div>
                <div className="message-body">
                  <div className="message-content">
                    {streamingText}
                    <span className="typing-dots">
                      <span>.</span><span>.</span><span>.</span>
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
      
      <footer className="app-footer">
        <div className="input-group">
          <MicrophoneButton />
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              !isConnected ? 'Connecting...' :
              currentTurn === 'user_turn' ? 'Type your message...' :
              currentTurn === 'agent_turn' ? 'Agent is responding...' :
              'Type your message...'
            }
            disabled={!isConnected}
            className="message-input"
          />
          
          <button 
            onClick={handleSend}
            disabled={!isConnected || !input.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
        
        <div className="footer-info">
          <span>Session: {currentSessionId?.slice(0, 8) || 'None'}</span>
          <span>•</span>
          <span>{messages.length} messages</span>
          <span>•</span>
          <span>Turn: {currentTurn}</span>
        </div>
      </footer>
    </div>
  );
}

export default AdvancedApp;
```

## Styling Examples

```css
/* styles.css */

/* Basic Chat Styles */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}

.message {
  margin-bottom: 15px;
  padding: 10px 15px;
  border-radius: 10px;
  max-width: 70%;
}

.message.user {
  background: #007bff;
  color: white;
  margin-left: auto;
  text-align: right;
}

.message.assistant {
  background: white;
  border: 1px solid #ddd;
}

.message.streaming {
  opacity: 0.8;
}

.typing-indicator {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Voice Assistant Styles */
.voice-assistant {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
}

.turn-indicator {
  padding: 10px;
  text-align: center;
  font-weight: bold;
}

.turn-indicator.user_turn {
  background: #4caf50;
  color: white;
}

.turn-indicator.agent_turn {
  background: #ff9800;
  color: white;
}

.audio-visualizer {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-meter {
  width: 200px;
  height: 20px;
  background: #ddd;
  border-radius: 10px;
  overflow: hidden;
}

.level-bar {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a, #ffeb3b, #ff9800, #f44336);
  transition: width 100ms;
}

.mic-button {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  font-size: 30px;
  border: 3px solid #ddd;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.mic-button.active {
  background: #f44336;
  color: white;
  animation: recording 1s infinite;
}

@keyframes recording {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* Avatar Styles */
.avatar-video {
  width: 100%;
  max-width: 600px;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
}

.avatar-card {
  border: 2px solid #ddd;
  border-radius: 10px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-card.selected {
  border-color: #007bff;
  background: #f0f8ff;
}

.avatar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

## Testing Components

```tsx
// ComponentTests.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AgentCProvider } from '@agentc/realtime-react';
import { ChatInterface } from './ChatInterface';

describe('ChatInterface', () => {
  const mockConfig = {
    apiUrl: 'wss://test.api.com',
    apiKey: 'test-key'
  };
  
  it('renders without crashing', () => {
    render(
      <AgentCProvider config={mockConfig}>
        <ChatInterface />
      </AgentCProvider>
    );
    
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
  });
  
  it('sends message on button click', async () => {
    render(
      <AgentCProvider config={mockConfig} autoConnect={true}>
        <ChatInterface />
      </AgentCProvider>
    );
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });
});
```

## Deployment

```tsx
// Production configuration
const productionConfig = {
  apiUrl: process.env.REACT_APP_AGENTC_URL!,
  apiKey: process.env.REACT_APP_AGENTC_KEY!,
  enableAudio: true,
  audioConfig: {
    enableInput: true,
    enableOutput: true,
    respectTurnState: true
  },
  reconnection: {
    maxAttempts: 10,
    initialDelay: 1000,
    maxDelay: 30000
  },
  debug: false
};
```

## Best Practices Summary

1. **Always handle connection state**
2. **Provide visual feedback for all states**
3. **Handle errors gracefully**
4. **Respect turn management in voice apps**
5. **Clean up resources on unmount**
6. **Use TypeScript for type safety**
7. **Test components thoroughly**
8. **Optimize for performance**
9. **Provide keyboard shortcuts**
10. **Make UI accessible**