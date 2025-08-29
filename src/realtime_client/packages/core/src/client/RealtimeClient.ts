/**
 * Realtime Client - Main client class for Agent C Realtime API
 */

import { EventEmitter } from '../events/EventEmitter';
import {
    RealtimeEventMap,
    ClientEventMap
} from '../events';
import {
    RealtimeClientConfig,
    ConnectionState,
    ReconnectionConfig,
    mergeConfig
} from './ClientConfig';
import { WebSocketManager } from './WebSocketManager';
import { ReconnectionManager } from './ReconnectionManager';
import { AuthManager, TokenPair } from '../auth';
import { TurnManager } from '../session';

/**
 * Main client class for connecting to Agent C Realtime API
 */
export class RealtimeClient extends EventEmitter<RealtimeEventMap> {
    private config: Required<Omit<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'>> & Pick<RealtimeClientConfig, 'sessionId' | 'headers' | 'protocols' | 'authToken' | 'authManager'>;
    private wsManager: WebSocketManager | null = null;
    private reconnectionManager: ReconnectionManager;
    private connectionState: ConnectionState = ConnectionState.DISCONNECTED;
    private authToken: string | null = null;
    private sessionId: string | null = null;
    private authManager: AuthManager | null = null;
    private turnManager: TurnManager | null = null;

    constructor(config: RealtimeClientConfig) {
        super();
        this.config = mergeConfig(config);
        this.authToken = config.authToken || null;
        this.sessionId = config.sessionId || null;

        // Initialize auth manager if provided
        if (config.authManager) {
            this.authManager = config.authManager;
            // Subscribe to token refresh events
            this.authManager.on('auth:tokens-refreshed', (tokens: TokenPair) => {
                this.authToken = tokens.agentCToken;
                // If connected, reconnect with new token
                if (this.isConnected()) {
                    this.disconnect();
                    this.connect();
                }
            });
            // Get initial token if available
            const tokens = this.authManager.getTokens();
            if (tokens) {
                this.authToken = tokens.agentCToken;
            }
        }

        // Initialize reconnection manager - cast is safe because mergeConfig ensures it's defined
        this.reconnectionManager = new ReconnectionManager(this.config.reconnection as ReconnectionConfig);
        
        // Subscribe to reconnection events
        this.reconnectionManager.on('reconnecting', ({ attempt, delay }) => {
            this.setConnectionState(ConnectionState.RECONNECTING);
            this.emit('reconnecting', { attempt, delay });
        });
        
        this.reconnectionManager.on('reconnected', () => {
            this.setConnectionState(ConnectionState.CONNECTED);
            this.emit('reconnected', undefined);
        });
        
        this.reconnectionManager.on('reconnection_failed', ({ reason }) => {
            this.setConnectionState(ConnectionState.DISCONNECTED);
            this.emit('disconnected', { code: 1006, reason });
        });
        
        // Initialize turn manager if enabled
        if (this.config.enableTurnManager) {
            this.turnManager = new TurnManager(this);
        }
    }

    /**
     * Connect to the Realtime API
     */
    async connect(): Promise<void> {
        if (this.connectionState === ConnectionState.CONNECTED) {
            return;
        }

        if (this.connectionState === ConnectionState.CONNECTING) {
            throw new Error('Already connecting');
        }

        // Get auth token from manager if available
        if (this.authManager && !this.authToken) {
            const tokens = this.authManager.getTokens();
            if (tokens) {
                this.authToken = tokens.agentCToken;
            }
        }

        // Get UI session ID from auth manager if available
        if (this.authManager && !this.sessionId) {
            const uiSessionId = this.authManager.getUiSessionId();
            if (uiSessionId) {
                this.sessionId = uiSessionId;
            }
        }

        this.setConnectionState(ConnectionState.CONNECTING);

        return new Promise((resolve, reject) => {
            try {
                const wsUrl = this.buildWebSocketUrl();

                this.wsManager = new WebSocketManager(
                    {
                        url: wsUrl,
                        protocols: this.config.protocols,
                        // Ensure binaryType is always 'arraybuffer' for proper audio handling
                        binaryType: 'arraybuffer',
                        pingInterval: this.config.pingInterval,
                        pongTimeout: this.config.pongTimeout
                    },
                    {
                        onOpen: () => {
                            this.setConnectionState(ConnectionState.CONNECTED);
                            this.reconnectionManager.reset();
                            this.emit('connected', undefined);
                            resolve();
                        },
                        onClose: (event) => {
                            this.handleDisconnection(event.code, event.reason);
                        },
                        onError: () => {
                            this.emit('error', {
                                type: 'error',
                                message: 'WebSocket error occurred',
                                source: 'websocket'
                            });
                            if (this.connectionState === ConnectionState.CONNECTING) {
                                reject(new Error('Failed to connect'));
                            }
                        },
                        onMessage: (data) => {
                            this.handleMessage(data);
                        }
                    }
                );

                this.wsManager.connect();

                // Set connection timeout
                if (this.config.connectionTimeout) {
                    setTimeout(() => {
                        if (this.connectionState === ConnectionState.CONNECTING) {
                            this.wsManager?.disconnect(1000, 'Connection timeout');
                            reject(new Error('Connection timeout'));
                        }
                    }, this.config.connectionTimeout);
                }
            } catch (error) {
                this.setConnectionState(ConnectionState.DISCONNECTED);
                reject(error);
            }
        });
    }

    /**
     * Disconnect from the Realtime API
     */
    disconnect(): void {
        this.reconnectionManager.stopReconnection();

        if (this.wsManager) {
            this.wsManager.disconnect(1000, 'Client disconnect');
            this.wsManager = null;
        }

        this.setConnectionState(ConnectionState.DISCONNECTED);
    }

    /**
     * Send a raw event to the server
     */
    private sendEvent<K extends keyof ClientEventMap>(event: ClientEventMap[K]): void {
        if (!this.wsManager || !this.wsManager.isConnected()) {
            throw new Error('Not connected to server');
        }

        this.wsManager.sendJSON(event);
    }

    /**
     * Send binary audio data to the server
     * @deprecated Use sendBinaryFrame instead
     */
    sendAudio(audioData: ArrayBuffer | ArrayBufferView): void {
        this.sendBinaryFrame(audioData);
    }

    /**
     * Send raw binary frame to the server
     * This sends audio data directly as binary, NOT wrapped in JSON events
     * @param data Raw binary audio data (PCM16 format)
     */
    sendBinaryFrame(data: ArrayBuffer | ArrayBufferView): void {
        if (!this.wsManager || !this.wsManager.isConnected()) {
            throw new Error('Not connected to server');
        }

        if (!this.wsManager.supportsBinary()) {
            throw new Error('WebSocket connection does not support binary frames');
        }

        // Send the raw binary data directly over the WebSocket
        // This is NOT wrapped in an AudioInputDelta event - it's raw PCM16 audio
        this.wsManager.sendBinary(data);
        
        if (this.config.debug) {
            const byteLength = data instanceof ArrayBuffer ? data.byteLength : data.byteLength;
            console.debug('Sent binary audio frame:', byteLength, 'bytes');
        }
    }

    // Client command methods

    /**
     * Get list of available agents
     */
    getAgents(): void {
        this.sendEvent({ type: 'get_agents' });
    }

    /**
     * Set the active agent
     */
    setAgent(agentKey: string): void {
        this.sendEvent({ type: 'set_agent', agent_key: agentKey });
    }

    /**
     * Get list of available avatars
     */
    getAvatars(): void {
        this.sendEvent({ type: 'get_avatars' });
    }

    /**
     * Set avatar session
     */
    setAvatarSession(accessToken: string, avatarSessionId: string): void {
        this.sendEvent({
            type: 'set_avatar_session',
            access_token: accessToken,
            avatar_session_id: avatarSessionId
        });
    }

    /**
     * Set agent voice
     */
    setAgentVoice(voiceId: string): void {
        this.sendEvent({ type: 'set_agent_voice', voice_id: voiceId });
    }

    /**
     * Send text input to the agent
     */
    sendText(text: string, fileIds?: string[]): void {
        const event: any = { type: 'text_input', text };
        if (fileIds && fileIds.length > 0) {
            event.file_ids = fileIds;
        }
        this.sendEvent(event);
    }

    /**
     * Create a new chat session
     */
    newChatSession(agentKey?: string): void {
        const event: any = { type: 'new_chat_session' };
        if (agentKey) {
            event.agent_key = agentKey;
        }
        this.sendEvent(event);
    }

    /**
     * Resume an existing chat session
     */
    resumeChatSession(sessionId: string): void {
        this.sendEvent({ type: 'resume_chat_session', session_id: sessionId });
    }

    /**
     * Set chat session name
     */
    setChatSessionName(sessionName: string): void {
        this.sendEvent({ type: 'set_chat_session_name', session_name: sessionName });
    }

    /**
     * Set session metadata
     */
    setSessionMetadata(meta: Record<string, any>): void {
        this.sendEvent({ type: 'set_session_metadata', meta });
    }

    /**
     * Set session messages
     */
    setSessionMessages(messages: any[]): void {
        this.sendEvent({ type: 'set_session_messages', messages });
    }

    // Getters

    /**
     * Get current connection state
     */
    getConnectionState(): ConnectionState {
        return this.connectionState;
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.connectionState === ConnectionState.CONNECTED;
    }

    /**
     * Get the auth manager instance
     */
    getAuthManager(): AuthManager | null {
        return this.authManager;
    }

    /**
     * Get the turn manager instance
     */
    getTurnManager(): TurnManager | null {
        return this.turnManager;
    }

    /**
     * Set the auth manager instance
     */
    setAuthManager(authManager: AuthManager): void {
        // Unsubscribe from previous manager
        if (this.authManager) {
            this.authManager.removeAllListeners();
        }

        this.authManager = authManager;
        
        // Subscribe to token refresh events
        this.authManager.on('auth:tokens-refreshed', (tokens: TokenPair) => {
            this.authToken = tokens.agentCToken;
            // If connected, reconnect with new token
            if (this.isConnected()) {
                this.disconnect();
                this.connect();
            }
        });
        
        // Get initial token if available
        const tokens = this.authManager.getTokens();
        if (tokens) {
            this.authToken = tokens.agentCToken;
        }
    }

    /**
     * Update authentication token
     */
    setAuthToken(token: string): void {
        this.authToken = token;
        // If connected, we need to reconnect with new token
        if (this.isConnected()) {
            this.disconnect();
            this.connect();
        }
    }

    /**
     * Update session ID
     */
    setSessionId(sessionId: string | null): void {
        this.sessionId = sessionId;
        // If connected, we need to reconnect with new session ID
        if (this.isConnected()) {
            this.disconnect();
            this.connect();
        }
    }

    // Private methods

    /**
     * Build WebSocket URL with authentication
     */
    private buildWebSocketUrl(): string {
        if (!this.authToken) {
            throw new Error('Authentication token is required');
        }

        const url = new URL(this.config.apiUrl);
        url.searchParams.set('token', this.authToken);
        
        if (this.sessionId) {
            url.searchParams.set('session_id', this.sessionId);
        }

        return url.toString();
    }

    /**
     * Handle incoming messages from WebSocket
     * Supports both JSON events and binary audio frames
     */
    private handleMessage(data: string | ArrayBuffer): void {
        if (typeof data === 'string') {
            // JSON message - parse as event
            try {
                const event = JSON.parse(data);
                if (event && typeof event.type === 'string') {
                    // Emit the specific event
                    this.emit(event.type as any, event);
                    
                    if (this.config.debug) {
                        console.debug('Received event:', event.type, event);
                    }
                } else {
                    console.warn('Invalid event structure:', event);
                }
            } catch (error) {
                console.error('Failed to parse JSON message:', error);
                this.emit('error', {
                    type: 'error',
                    message: 'Failed to parse server message',
                    source: 'message_parser'
                });
            }
        } else if (data instanceof ArrayBuffer) {
            // Binary message - this is raw audio data from the server
            // Emit as 'audio:output' for consistency with the audio system
            this.emit('audio:output', data);
            
            // Also emit the legacy event for backward compatibility
            this.emit('binary_audio', data);
            
            if (this.config.debug) {
                console.debug('Received binary audio frame:', data.byteLength, 'bytes');
            }
        } else {
            console.warn('Unknown message type:', typeof data);
        }
    }

    /**
     * Handle disconnection and trigger reconnection if needed
     */
    private handleDisconnection(code: number, reason: string): void {
        const wasConnected = this.connectionState === ConnectionState.CONNECTED;
        this.setConnectionState(ConnectionState.DISCONNECTED);
        
        this.emit('disconnected', { code, reason });

        // Attempt reconnection if configured and wasn't a clean disconnect
        if (wasConnected && this.config.autoReconnect && code !== 1000) {
            this.attemptReconnection();
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    private attemptReconnection(): void {
        this.reconnectionManager.startReconnection(async () => {
            await this.connect();
        }).catch((error) => {
            if (this.config.debug) {
                console.error('Reconnection failed:', error);
            }
        });
    }

    /**
     * Update connection state and emit event
     */
    private setConnectionState(state: ConnectionState): void {
        if (this.connectionState !== state) {
            this.connectionState = state;
            
            if (this.config.debug) {
                console.debug('Connection state changed:', ConnectionState[state]);
            }
        }
    }

    /**
     * Clean up resources
     */
    destroy(): void {
        this.disconnect();
        if (this.authManager) {
            this.authManager.removeAllListeners();
        }
        if (this.turnManager) {
            this.turnManager.destroy();
            this.turnManager = null;
        }
        this.removeAllListeners();
    }
}