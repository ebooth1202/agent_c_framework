# React Examples

Complete examples demonstrating how to build applications with the Agent C Realtime React SDK.

## Authentication

Agent C uses username/password authentication, not API keys. All examples below demonstrate proper authentication patterns:

- Login with credentials using `AuthManager`
- WebSocket URL is provided by the login response
- Use `localhost:8000` for development or environment variables for production
- Token refresh is handled automatically

## Table of Contents

- [Authentication Setup](#authentication-setup)
- [Basic Chat Application](#basic-chat-application)
- [Voice Assistant](#voice-assistant)
- [Avatar Integration](#avatar-integration)
- [Multi-Session Manager](#multi-session-manager)
- [Custom UI Components](#custom-ui-components)
- [Advanced Features](#advanced-features)

---

## Authentication Setup

Proper authentication flow with Agent C:

```tsx
// AuthenticationExample.tsx
import React, { useState, useEffect } from 'react';
import { AgentCProvider, useAuth, useConnection } from '@agentc/realtime-react';

function App() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [authConfig, setAuthConfig] = useState<any>(null);

  const handleLogin = async () => {
    try {
      // Use AuthManager to login
      const authManager = new AuthManager({
        apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
      });
      
      const loginResponse = await authManager.login({
        username: credentials.username,
        password: credentials.password
      });
      
      // Extract WebSocket URL and token from login response
      setAuthConfig({
        wsUrl: loginResponse.ws_url,
        authToken: loginResponse.access_token,
        refreshToken: loginResponse.refresh_token,
        heygenToken: loginResponse.heygen_access_token
      });
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please check your credentials.');
    }
  };

  // Render login form if not authenticated
  if (!authConfig) {
    return (
      <div className="login-form">
        <h2>Login to Agent C</h2>
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
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  }

  // Render app with authentication
  return (
    <AgentCProvider 
      config={{
        wsUrl: authConfig.wsUrl,
        authToken: authConfig.authToken,
        refreshToken: authConfig.refreshToken,
        heygenToken: authConfig.heygenToken,
        autoConnect: true
      }}
    >
      <YourApplication />
    </AgentCProvider>
  );
}
```

---

## Basic Chat Application

A simple text chat interface with Agent C.

```tsx
// BasicChat.tsx
import React, { useState, useEffect } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat,
  AuthManager
} from '@agentc/realtime-react';

function BasicChatApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    // Initialize authentication
    const authenticate = async () => {
      const authManager = new AuthManager({
        apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
      });

      try {
        // Try to restore session or login with stored credentials
        const credentials = {
          username: process.env.REACT_APP_USERNAME || 'demo_user',
          password: process.env.REACT_APP_PASSWORD || 'demo_password'
        };
        
        const loginResponse = await authManager.login(credentials);
        
        setConfig({
          wsUrl: loginResponse.ws_url,
          authToken: loginResponse.access_token,
          refreshToken: loginResponse.refresh_token
        });
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Authentication failed:', error);
      }
    };

    authenticate();
  }, []);

  if (!isAuthenticated || !config) {
    return <div>Authenticating...</div>;
  }

  return (
    <AgentCProvider 
      config={config}
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
  useVoiceModel,
  AuthManager
} from '@agentc/realtime-react';

function VoiceAssistantApp() {
  const [authConfig, setAuthConfig] = useState<any>(null);

  useEffect(() => {
    const login = async () => {
      const authManager = new AuthManager({
        apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
      });

      const response = await authManager.login({
        username: process.env.REACT_APP_USERNAME!,
        password: process.env.REACT_APP_PASSWORD!
      });

      setAuthConfig({
        wsUrl: response.ws_url,
        authToken: response.access_token,
        refreshToken: response.refresh_token,
        enableAudio: true,
        audioConfig: {
          enableInput: true,
          enableOutput: true,
          respectTurnState: true,
          initialVolume: 0.8
        }
      });
    };

    login().catch(console.error);
  }, []);

  if (!authConfig) {
    return <div>Authenticating...</div>;
  }

  return (
    <AgentCProvider config={authConfig}>
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
  useVoiceModel,
  AuthManager
} from '@agentc/realtime-react';
import NewStreamingAvatar, { StreamingEvents } from '@heygen/streaming-avatar';

function AvatarChatApp() {
  const [authConfig, setAuthConfig] = useState<any>(null);

  useEffect(() => {
    const authenticate = async () => {
      const authManager = new AuthManager({
        apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
      });

      const loginResponse = await authManager.login({
        username: process.env.REACT_APP_USERNAME!,
        password: process.env.REACT_APP_PASSWORD!
      });

      setAuthConfig({
        wsUrl: loginResponse.ws_url,
        authToken: loginResponse.access_token,
        refreshToken: loginResponse.refresh_token,
        heygenToken: loginResponse.heygen_access_token, // HeyGen token from login
        enableAudio: true
      });
    };

    authenticate().catch(console.error);
  }, []);

  if (!authConfig) {
    return <div>Authenticating...</div>;
  }

  return (
    <AgentCProvider config={authConfig}>
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
      // Get HeyGen token from authentication config
      const { heygenToken } = useAuth();
      
      if (!heygenToken) {
        throw new Error('HeyGen token not available. Please re-authenticate.');
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
import React, { useState, useEffect } from 'react';
import {
  AgentCProvider,
  useConnection,
  useChat,
  AuthManager
} from '@agentc/realtime-react';

function MultiSessionApp() {
  const [authConfig, setAuthConfig] = useState<any>(null);
  const [loginError, setLoginError] = useState<string>('');

  useEffect(() => {
    const authenticate = async () => {
      const authManager = new AuthManager({
        apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
      });

      try {
        const loginResponse = await authManager.login({
          username: process.env.REACT_APP_USERNAME!,
          password: process.env.REACT_APP_PASSWORD!
        });

        setAuthConfig({
          wsUrl: loginResponse.ws_url,
          authToken: loginResponse.access_token,
          refreshToken: loginResponse.refresh_token
        });
      } catch (error: any) {
        setLoginError(error.message || 'Authentication failed');
      }
    };

    authenticate();
  }, []);

  if (loginError) {
    return <div className="error">Login Error: {loginError}</div>;
  }

  if (!authConfig) {
    return <div>Authenticating...</div>;
  }

  return (
    <AgentCProvider 
      config={authConfig}
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
  useAvatar,
  AuthManager,
  useAuth
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
  const [config, setConfig] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [showLoginForm, setShowLoginForm] = useState(false);

  useEffect(() => {
    // Try to authenticate with environment variables first
    const tryAutoLogin = async () => {
      const username = process.env.REACT_APP_USERNAME;
      const password = process.env.REACT_APP_PASSWORD;
      
      if (!username || !password) {
        setShowLoginForm(true);
        setIsLoading(false);
        return;
      }

      await authenticate(username, password);
    };

    tryAutoLogin();
  }, []);

  const authenticate = async (username: string, password: string) => {
    setIsLoading(true);
    
    const authManager = new AuthManager({
      apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
    });

    try {
      const loginResponse = await authManager.login({ username, password });
      
      setConfig({
        wsUrl: loginResponse.ws_url,
        authToken: loginResponse.access_token,
        refreshToken: loginResponse.refresh_token,
        heygenToken: loginResponse.heygen_access_token,
        enableAudio: true,
        audioConfig: {
          enableInput: true,
          enableOutput: true,
          respectTurnState: true,
          initialVolume: 0.8
        }
      });
      
      setShowLoginForm(false);
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Login failed. Please check your credentials.');
      setShowLoginForm(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = () => {
    if (credentials.username && credentials.password) {
      authenticate(credentials.username, credentials.password);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (showLoginForm) {
    return (
      <div className="login-container">
        <h2>Login to Agent C</h2>
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
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
        />
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  }
  
  if (!config) {
    return null;
  }

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
import { AgentCProvider, AuthManager } from '@agentc/realtime-react';
import { ChatInterface } from './ChatInterface';

// Mock AuthManager for testing
jest.mock('@agentc/realtime-react', () => ({
  ...jest.requireActual('@agentc/realtime-react'),
  AuthManager: jest.fn().mockImplementation(() => ({
    login: jest.fn().mockResolvedValue({
      ws_url: 'wss://test.api.com/rt/ws',
      access_token: 'test-token',
      refresh_token: 'test-refresh-token',
      heygen_access_token: 'test-heygen-token'
    })
  }))
}));

describe('ChatInterface', () => {
  const mockConfig = {
    wsUrl: 'wss://test.api.com/rt/ws',
    authToken: 'test-token',
    refreshToken: 'test-refresh-token'
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

### Environment Variables

Create a `.env` file for development:

```bash
# Development environment
REACT_APP_API_URL=https://localhost:8000
REACT_APP_USERNAME=your_username
REACT_APP_PASSWORD=your_password
```

For production:

```bash
# Production environment
REACT_APP_API_URL=https://api.agentc.com
REACT_APP_USERNAME=prod_username
REACT_APP_PASSWORD=prod_password
```

### Production Configuration

```tsx
// productionConfig.ts
import { AuthManager } from '@agentc/realtime-react';

export async function getProductionConfig() {
  const authManager = new AuthManager({
    apiUrl: process.env.REACT_APP_API_URL!,
    // Optional: Configure retry and timeout settings
    requestTimeout: 30000,
    maxRetries: 3
  });

  try {
    // Authenticate with credentials
    const loginResponse = await authManager.login({
      username: process.env.REACT_APP_USERNAME!,
      password: process.env.REACT_APP_PASSWORD!
    });

    return {
      wsUrl: loginResponse.ws_url,
      authToken: loginResponse.access_token,
      refreshToken: loginResponse.refresh_token,
      heygenToken: loginResponse.heygen_access_token,
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
      debug: process.env.NODE_ENV !== 'production'
    };
  } catch (error) {
    console.error('Failed to authenticate:', error);
    throw error;
  }
}

// Usage in your app
import { getProductionConfig } from './productionConfig';

function App() {
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    getProductionConfig()
      .then(setConfig)
      .catch(error => {
        // Handle authentication failure
        console.error('Setup failed:', error);
      });
  }, []);

  if (!config) {
    return <div>Initializing...</div>;
  }

  return (
    <AgentCProvider config={config}>
      <YourApp />
    </AgentCProvider>
  );
}
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application files
COPY . .

# Build the app
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Use HTTPS in production** - Ensure all API calls are encrypted
3. **Implement token refresh** - AuthManager handles this automatically
4. **Store tokens securely** - Use httpOnly cookies or secure storage
5. **Validate input** - Always validate user input before sending

```tsx
// Secure token storage example
import { SecureStorage } from '@agentc/realtime-react';

const storage = new SecureStorage({
  encryptionKey: process.env.REACT_APP_ENCRYPTION_KEY,
  storageType: 'sessionStorage' // or 'localStorage' for persistence
});

// Store tokens securely
storage.setItem('auth_token', loginResponse.access_token);
storage.setItem('refresh_token', loginResponse.refresh_token);

// Retrieve tokens
const authToken = storage.getItem('auth_token');
```

## Best Practices Summary

### Authentication
1. **Use environment variables** for credentials, never hardcode them
2. **Implement proper login flow** with username/password
3. **Handle authentication errors** gracefully with user feedback
4. **Store tokens securely** using appropriate storage mechanisms
5. **Let AuthManager handle token refresh** automatically

### Connection Management
1. **Always handle connection state** and show status to users
2. **Implement reconnection logic** for network failures
3. **Use the WebSocket URL from login response**, not hardcoded values
4. **Clean up connections** on component unmount

### Development
1. **Use localhost:8000** for local development
2. **Provide visual feedback** for all states
3. **Handle errors gracefully** with informative messages
4. **Respect turn management** in voice applications
5. **Use TypeScript** for type safety throughout

### Testing
1. **Mock AuthManager** in tests
2. **Test authentication flows** including failure cases
3. **Verify token refresh** behavior
4. **Test connection handling** and reconnection

### Security
1. **Never expose credentials** in client-side code
2. **Use HTTPS** in production environments
3. **Implement proper logout** to clear tokens
4. **Validate all user input** before sending to server
5. **Monitor for authentication failures** and handle appropriately

### Performance
1. **Lazy load authentication** when needed
2. **Cache authentication state** appropriately
3. **Optimize WebSocket message handling**
4. **Clean up event listeners** to prevent memory leaks
5. **Use React.memo** for expensive components

## Common Authentication Patterns

### Login with Redirect

```tsx
function LoginRedirect() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  
  const handleLogin = async () => {
    const authManager = new AuthManager({
      apiUrl: process.env.REACT_APP_API_URL || 'https://localhost:8000'
    });
    
    try {
      const response = await authManager.login(credentials);
      
      // Store auth data in context or state management
      sessionStorage.setItem('auth_config', JSON.stringify({
        wsUrl: response.ws_url,
        authToken: response.access_token,
        refreshToken: response.refresh_token
      }));
      
      navigate('/chat');
    } catch (error) {
      alert('Login failed');
    }
  };
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        placeholder="Username"
        required
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Protected Route Pattern

```tsx
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [authConfig, setAuthConfig] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Check for stored auth config
    const stored = sessionStorage.getItem('auth_config');
    
    if (stored) {
      setAuthConfig(JSON.parse(stored));
    }
    setIsLoading(false);
  }, []);
  
  if (isLoading) return <div>Loading...</div>;
  if (!authConfig) return <Navigate to="/login" />;
  
  return (
    <AgentCProvider config={authConfig}>
      {children}
    </AgentCProvider>
  );
}

// Usage
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/chat" element={
    <ProtectedRoute>
      <ChatInterface />
    </ProtectedRoute>
  } />
</Routes>
```

### Logout Pattern

```tsx
function LogoutButton() {
  const { disconnect } = useConnection();
  const navigate = useNavigate();
  
  const handleLogout = async () => {
    // Disconnect WebSocket
    await disconnect();
    
    // Clear stored tokens
    sessionStorage.removeItem('auth_config');
    localStorage.removeItem('refresh_token');
    
    // Clear any other auth state
    // ...
    
    // Redirect to login
    navigate('/login');
  };
  
  return <button onClick={handleLogout}>Logout</button>;
}
```