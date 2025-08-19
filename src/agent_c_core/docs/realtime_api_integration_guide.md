# Agent C Realtime API Integration Guide

This guide provides practical examples and patterns for integrating with the Agent C Realtime API. It includes working code examples and best practices for building robust clients.

## Prerequisites

- Valid JWT token for authentication
- WebSocket client library
- Basic understanding of event-driven programming

## Quick Start

### 1. Basic Connection Setup

```javascript
class AgentCRealtimeClient {
    constructor(jwtToken, baseUrl = 'wss://your-api-domain.com') {
        this.token = jwtToken;
        this.wsUrl = `${baseUrl}/api/avatar/ws`;
        this.ws = null;
        this.isConnected = false;
        this.eventHandlers = new Map();
        this.currentInteraction = null;
        this.agents = [];
        this.avatars = [];
    }

    async connect() {
        return new Promise((resolve, reject) => {
            // Include JWT token in connection (implementation varies by platform)
            this.ws = new WebSocket(`${this.wsUrl}?token=${this.token}`);

            this.ws.onopen = () => {
                console.log('Connected to Agent C Realtime API');
                this.isConnected = true;
                resolve();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.ws.onclose = () => {
                console.log('Disconnected from Agent C Realtime API');
                this.isConnected = false;
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    sendEvent(event) {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify(event));
        } else {
            throw new Error('Not connected to API');
        }
    }
}
```

### 2. Event Handling System

```javascript
class AgentCRealtimeClient {
    // ... previous code ...

    handleMessage(event) {
        console.log('Received event:', event.type, event);

        // Call registered handlers
        const handler = this.eventHandlers.get(event.type);
        if (handler) {
            handler(event);
        } else {
            console.warn('No handler for event type:', event.type);
        }
    }

    on(eventType, handler) {
        this.eventHandlers.set(eventType, handler);
    }

    off(eventType) {
        this.eventHandlers.delete(eventType);
    }
}
```

### 3. Session Setup

```javascript
class AgentCRealtimeClient {
    // ... previous code ...

    async setupSession(agentKey, avatarId) {
        // Wait for initial agent and avatar lists
        await this.waitForInitialData();

        // Set the agent
        await this.setAgent(agentKey);

        // Set the avatar
        await this.setAvatar(avatarId);

        console.log('Session setup complete');
    }

    waitForInitialData() {
        return new Promise((resolve) => {
            let receivedAgents = false;
            let receivedAvatars = false;

            const checkComplete = () => {
                if (receivedAgents && receivedAvatars) {
                    resolve();
                }
            };

            this.on('agent_list', (event) => {
                this.agents = event.agents;
                receivedAgents = true;
                checkComplete();
            });

            this.on('avatar_list', (event) => {
                this.avatars = event.avatars;
                receivedAvatars = true;
                checkComplete();
            });
        });
    }

    async setAgent(agentKey) {
        return new Promise((resolve, reject) => {
            // Set up response handler
            const timeout = setTimeout(() => {
                reject(new Error('Agent setup timeout'));
            }, 5000);

            this.on('agent_configuration_changed', (event) => {
                clearTimeout(timeout);
                console.log('Agent set:', event.agent_config);
                resolve(event.agent_config);
            });

            this.on('error', (event) => {
                clearTimeout(timeout);
                reject(new Error(event.message));
            });

            // Send the request
            this.sendEvent({
                type: 'set_agent',
                agent_key: agentKey
            });
        });
    }

    async setAvatar(avatarId, quality = 'medium', videoEncoding = 'VP8') {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Avatar setup timeout'));
            }, 10000); // Avatar setup can take longer

            this.on('avatar_connection_changed', (event) => {
                clearTimeout(timeout);
                console.log('Avatar set:', event.avatar_session);
                resolve(event.avatar_session);
            });

            this.on('error', (event) => {
                clearTimeout(timeout);
                reject(new Error(event.message));
            });

            this.sendEvent({
                type: 'set_avatar',
                avatar_id: avatarId,
                quality: quality,
                video_encoding: videoEncoding
            });
        });
    }
}
```

## Complete Working Example

```javascript
class AgentCChatClient extends AgentCRealtimeClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.setupEventHandlers();
        this.messageBuffer = new Map(); // Buffer messages by role
        this.thoughtBuffer = '';
    }

    setupEventHandlers() {
        // Interaction management
        this.on('interaction', (event) => {
            this.currentInteraction = event.started ? event.id : null;
            this.onInteractionStateChange(event.started);
        });

        // Text streaming
        this.on('text_delta', (event) => {
            this.appendToBuffer(event.role, event.content);
            this.onTextDelta(event);
        });

        // Thought streaming
        this.on('thought_delta', (event) => {
            this.thoughtBuffer += event.content;
            this.onThoughtDelta(event);
        });

        // Completion tracking
        this.on('completion', (event) => {
            this.onCompletion(event);
        });

        // Error handling
        this.on('error', (event) => {
            this.onError(event);
        });

        // History updates
        this.on('history_delta', (event) => {
            this.onHistoryUpdate(event);
        });
    }

    appendToBuffer(role, content) {
        if (!this.messageBuffer.has(role)) {
            this.messageBuffer.set(role, '');
        }
        this.messageBuffer.set(role, this.messageBuffer.get(role) + content);
    }

    async sendMessage(text, fileIds = []) {
        if (!this.isConnected) {
            throw new Error('Not connected');
        }

        if (this.currentInteraction) {
            throw new Error('Interaction already in progress');
        }

        // Clear buffers
        this.messageBuffer.clear();
        this.thoughtBuffer = '';

        this.sendEvent({
            type: 'text_input',
            text: text,
            file_ids: fileIds
        });
    }

    // Override these methods in your implementation
    onInteractionStateChange(isActive) {
        console.log('Interaction active:', isActive);
        // Update UI to disable/enable input
    }

    onTextDelta(event) {
        console.log('Text delta:', event.content);
        // Update UI with streaming text
    }

    onThoughtDelta(event) {
        console.log('Thought delta:', event.content);
        // Show thinking process in UI
    }

    onCompletion(event) {
        console.log('Completion:', event);
        // Handle completion (token usage, etc.)
    }

    onError(event) {
        console.error('API Error:', event.message);
        // Show error to user
    }

    onHistoryUpdate(event) {
        console.log('History updated:', event.messages);
        // Update chat history in UI
    }
}
```

## Usage Examples

### Basic Chat Session

```javascript
async function startChatSession() {
    const client = new AgentCChatClient('your-jwt-token');

    try {
        // Connect to API
        await client.connect();

        // Setup session with specific agent and avatar
        await client.setupSession('helpful_assistant', 'anna_public_3_20240108');

        // Send a message
        await client.sendMessage('Hello! Can you help me understand quantum physics?');

        // The response will come through event handlers

    } catch (error) {
        console.error('Session setup failed:', error);
    }
}
```

### Avatar Integration with HeyGen

```javascript
class AvatarChatClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.heygenSession = null;
        this.avatarWebSocket = null;
    }

    async setAvatar(avatarId, quality, videoEncoding) {
        const avatarSession = await super.setAvatar(avatarId, quality, videoEncoding);
        this.heygenSession = avatarSession;

        // Connect to HeyGen for avatar video/audio
        await this.connectToHeyGenAvatar(avatarSession);

        return avatarSession;
    }

    async connectToHeyGenAvatar(session) {
        // Connect to HeyGen WebSocket for avatar stream
        // Note: HeyGen uses the access token as session_token in the WebSocket URL
        const wsUrl = `wss://${new URL(session.url).hostname}/v1/ws/streaming.chat?session_id=${session.session_id}&session_token=${session.access_token}`;
        this.avatarWebSocket = new WebSocket(wsUrl);

        this.avatarWebSocket.onopen = () => {
            console.log('Connected to HeyGen WebSocket');
            // No additional authentication needed - token is in URL
        };

        this.avatarWebSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleHeyGenEvent(data);
        };
    }

    handleHeyGenEvent(event) {
        switch (event.type) {
            case 'avatar_start_talking':
                this.onAvatarStartTalking();
                break;
            case 'avatar_stop_talking':
                this.onAvatarStopTalking();
                break;
            case 'stream_ready':
                this.onAvatarStreamReady(event.detail);
                break;
        }
    }

    onAvatarStartTalking() {
        console.log('Avatar started talking');
        // Update UI to show avatar is speaking
    }

    onAvatarStopTalking() {
        console.log('Avatar stopped talking');
        // Update UI to show avatar is idle
    }

    onAvatarStreamReady(streamDetail) {
        console.log('Avatar stream ready:', streamDetail);
        // Connect video element to MediaStream (not URL)
        const video = document.getElementById('avatar-video');
        if (streamDetail instanceof MediaStream) {
            video.srcObject = streamDetail;
            video.play();
        }
    }
}
```

### Error Handling and Reconnection

```javascript
class RobustAgentCClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
    }

    async connect() {
        try {
            await super.connect();
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        } catch (error) {
            console.error('Connection failed:', error);
            await this.handleReconnection();
        }
    }

    async handleReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.onMaxReconnectAttemptsReached();
            return;
        }

        this.reconnectAttempts++;
        console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, this.reconnectDelay));
        this.reconnectDelay *= 2;

        try {
            await this.connect();
        } catch (error) {
            await this.handleReconnection();
        }
    }

    onMaxReconnectAttemptsReached() {
        // Notify user that connection failed
        console.error('Unable to connect to Agent C API');
    }
}
```

## React Integration Example

```jsx
import React, { useState, useEffect, useCallback } from 'react';

const AgentCChat = ({ jwtToken }) => {
    const [client, setClient] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [isInteracting, setIsInteracting] = useState(false);
    const [thoughts, setThoughts] = useState('');

    useEffect(() => {
        const chatClient = new AgentCChatClient(jwtToken);

        // Override event handlers for React
        chatClient.onInteractionStateChange = setIsInteracting;

        chatClient.onTextDelta = (event) => {
            setCurrentMessage(prev => prev + event.content);
        };

        chatClient.onThoughtDelta = (event) => {
            setThoughts(prev => prev + event.content);
        };

        chatClient.onHistoryUpdate = (event) => {
            setMessages(event.messages);
            setCurrentMessage(''); // Clear current message buffer
            setThoughts(''); // Clear thoughts
        };

        chatClient.connect()
            .then(() => {
                setIsConnected(true);
                return chatClient.setupSession('helpful_assistant', 'anna_public_3_20240108');
            })
            .catch(console.error);

        setClient(chatClient);

        return () => {
            chatClient.disconnect();
        };
    }, [jwtToken]);

    const sendMessage = useCallback(async (text) => {
        if (client && !isInteracting) {
            try {
                await client.sendMessage(text);
            } catch (error) {
                console.error('Failed to send message:', error);
            }
        }
    }, [client, isInteracting]);

    return (
        <div className="agent-c-chat">
            <div className="connection-status">
                Status: {isConnected ? 'Connected' : 'Disconnected'}
            </div>

            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        <strong>{msg.role}:</strong> {msg.content}
                    </div>
                ))}

                {currentMessage && (
                    <div className="message assistant current">
                        <strong>assistant:</strong> {currentMessage}
                    </div>
                )}
            </div>

            {thoughts && (
                <div className="thoughts">
                    <em>Thinking: {thoughts}</em>
                </div>
            )}

            <ChatInput 
                onSendMessage={sendMessage} 
                disabled={!isConnected || isInteracting} 
            />
        </div>
    );
};
```

## Best Practices

### 1. Connection Management

- Implement exponential backoff for reconnections
- Handle network interruptions gracefully
- Validate JWT token expiration and refresh as needed

### 2. Event Handling

- Always implement error event handlers
- Buffer text deltas appropriately for your UI
- Handle unknown event types gracefully

### 3. State Management

- Track interaction state to prevent concurrent requests
- Maintain local message history for better UX
- Clear buffers appropriately between interactions

### 4. Performance

- Debounce rapid UI updates from text deltas
- Use efficient data structures for message buffering
- Implement proper cleanup on component unmount

### 5. User Experience

- Show loading states during interactions
- Display thinking process when available
- Provide clear error messages to users
- Disable input during active interactions

### 6. Avatar Integration

- Handle HeyGen connection separately from Agent C connection
- Synchronize avatar speech with text display
- Provide fallback UI when avatar is unavailable

## Troubleshooting

### Common Issues

1. **Connection Refused**
   
   - Verify JWT token is valid and not expired
   - Check WebSocket URL format
   - Ensure network connectivity

2. **Agent/Avatar Not Found**
   
   - Verify agent key exists in available agents list
   - Check avatar ID against available avatars list
   - Ensure proper session setup order

3. **Messages Not Streaming**
   
   - Check event handler registration
   - Verify interaction state management
   - Look for JavaScript errors in console

4. **Avatar Not Speaking**
   
   - Verify HeyGen session establishment
   - Check avatar connection event received
   - Ensure text deltas contain newlines for speech triggers

### Debug Mode

```javascript
class DebugAgentCClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.debugMode = true;
    }

    handleMessage(event) {
        if (this.debugMode) {
            console.log('🔍 Debug - Received event:', {
                type: event.type,
                timestamp: new Date().toISOString(),
                data: event
            });
        }
        super.handleMessage(event);
    }

    sendEvent(event) {
        if (this.debugMode) {
            console.log('🔍 Debug - Sending event:', {
                type: event.type,
                timestamp: new Date().toISOString(),
                data: event
            });
        }
        super.sendEvent(event);
    }
}
```

This integration guide provides practical, working examples that developers can adapt for their specific needs. For complete event specifications, refer to the [Client Events Reference](realtime_api_client_events.md) and [Runtime Events Reference](realtime_api_runtime_events.md).