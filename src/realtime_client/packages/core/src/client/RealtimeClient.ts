/**
 * Realtime Client - Main client class for Agent C Realtime API
 */

import { EventEmitter } from '../events/EventEmitter';
import {
    RealtimeEventMap,
    ClientEventMap,
    ChatSessionChangedEvent,
    TextDeltaEvent,
    CompletionEvent,
    ChatSessionNameChangedEvent,
    AgentVoiceChangedEvent,
    TextInputEvent,
    NewChatSessionEvent,
    GetUserSessionsEvent,
    GetUserSessionsResponseEvent
} from '../events';
import {
    RealtimeClientConfig,
    ConnectionState,
    ReconnectionConfig,
    AudioConfig,
    mergeConfig
} from './ClientConfig';
import { WebSocketManager } from './WebSocketManager';
import { ReconnectionManager } from './ReconnectionManager';
import { AuthManager, TokenPair } from '../auth';
import { TurnManager, SessionManager } from '../session';
import { AudioService, AudioAgentCBridge, AudioOutputService } from '../audio';
import type { AudioStatus, VoiceModel } from '../audio/types';
import { VoiceManager } from '../voice';
import type { Voice, Message, User, Agent, AgentConfiguration, Avatar, Toolset } from '../events/types/CommonTypes';
import { AvatarManager } from '../avatar';

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
    private voiceManager: VoiceManager | null = null;
    private sessionManager: SessionManager | null = null;
    private avatarManager: AvatarManager | null = null;
    
    // Audio system components
    private audioService: AudioService | null = null;
    private audioBridge: AudioAgentCBridge | null = null;
    private audioOutputService: AudioOutputService | null = null;
    private audioConfig: AudioConfig | null = null;
    
    // Configuration data from WebSocket initialization events
    private userData: User | null = null;
    private agents: Agent[] = [];
    private avatars: Avatar[] = [];
    private voices: Voice[] = [];
    private toolsets: Toolset[] = [];
    private initializationState: Set<string> = new Set();
    private isInitialized: boolean = false;

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
            
            // Note: Voice and avatar data will come from WebSocket initialization events
            this.avatarManager = new AvatarManager({ availableAvatars: [] });
        }
        
        // Initialize voice manager if not already created
        if (!this.voiceManager) {
            this.voiceManager = new VoiceManager({ enableLogging: this.config.debug });
            this.setupVoiceManagerHandlers();
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
        
        // Initialize session manager
        this.sessionManager = new SessionManager({
            maxSessions: 50,
            persistSessions: false
        });
        
        // Setup session manager handlers for fetching sessions
        this.setupSessionFetchingHandlers();
        
        // Initialize audio system if enabled
        if (this.config.enableAudio && this.config.audioConfig) {
            this.audioConfig = this.config.audioConfig;
            this.initializeAudioSystem();
        }
        
        // Setup initialization event handlers
        this.setupInitializationHandlers();
    }
    
    /**
     * Setup session fetching handlers
     */
    private setupSessionFetchingHandlers(): void {
        if (!this.sessionManager) return;
        
        // Listen for session fetch requests from SessionManager
        this.sessionManager.on('request-user-sessions', ({ offset, limit }) => {
            this.fetchUserSessions(offset, limit);
        });
        
        // Handle the response from server
        this.on('get_user_sessions_response', (event: GetUserSessionsResponseEvent) => {
            if (this.sessionManager && event.sessions) {
                // Append new sessions to the index
                this.sessionManager.setSessionIndex(event.sessions, true);
                
                if (this.config.debug) {
                    console.debug('Received user sessions:', {
                        count: event.sessions.chat_sessions.length,
                        total: event.sessions.total_sessions,
                        offset: event.sessions.offset
                    });
                }
            }
        });
        
        // Note: Session data will come from WebSocket initialization events
    }
    
    /**
     * Setup session manager event handlers
     */
    private setupSessionManagerHandlers(): void {
        if (!this.sessionManager) return;
        
        // Handle chat session changes from server
        this.on('chat_session_changed', (event: ChatSessionChangedEvent) => {
            if (event.chat_session) {
                this.sessionManager!.setCurrentSession(event.chat_session);
                
                if (this.config.debug) {
                    // console.debug('Session changed:', event.chat_session.session_id);
                }
            }
        });
        
        // Handle text delta events for accumulation
        this.on('text_delta', (event: TextDeltaEvent) => {
            if (event.content) {
                this.sessionManager!.handleTextDelta(event.content);
            }
        });
        
        // Handle completion events to finalize text
        this.on('completion', (event: CompletionEvent) => {
            // When completion.running becomes false, the text is done
            if (event.running === false) {
                this.sessionManager!.handleTextDone();
            }
        });
        
        // Handle session name changes
        this.on('chat_session_name_changed', (event: ChatSessionNameChangedEvent) => {
            if (event.session_name) {
                const currentSessionId = this.sessionManager!.getCurrentSessionId();
                if (currentSessionId) {
                    this.sessionManager!.updateSessionName(currentSessionId, event.session_name);
                    
                    if (this.config.debug) {
                        // console.debug('Session name updated:', event.session_name);
                    }
                }
            }
        });
    }
    
    /**
     * Setup voice manager event handlers
     */
    private setupVoiceManagerHandlers(): void {
        if (!this.voiceManager) return;
        
        // Subscribe to voice changes from the voice manager
        this.voiceManager.on('voice-changed', (event) => {
            if (this.audioOutputService) {
                // Convert Voice to VoiceModel for AudioOutputService
                const voiceModel = this.convertVoiceToVoiceModel(event.currentVoice);
                this.audioOutputService.setVoiceModel(voiceModel);
                
                if (this.config.debug) {
                    // console.debug('Voice model updated in AudioOutputService:', voiceModel?.voice_id || 'null');
                }
            }
        });
    }
    
    /**
     * Convert Voice to VoiceModel format for AudioOutputService
     */
    private convertVoiceToVoiceModel(voice: Voice | null): VoiceModel | null {
        if (!voice) return null;
        
        return {
            voice_id: voice.voice_id,
            format: voice.output_format || 'pcm16',
            vendor: voice.vendor,
            description: voice.description,
            sampleRate: 16000 // Default sample rate for PCM16
        };
    }
    
    /**
     * Setup handlers for initialization events sent by server on connection
     * Server sends 6 events in sequence: chat_user_data, avatar_list, voice_list,
     * agent_list, tool_catalog, chat_session_changed
     */
    private setupInitializationHandlers(): void {
        // Handle user data event
        this.on('chat_user_data', (event: any) => {
            if (event.user) {
                this.userData = event.user;
                this.initializationState.add('chat_user_data');
                
                // Update auth manager's user state if available
                if (this.authManager) {
                    (this.authManager as any).updateState({
                        user: event.user
                    });
                }
                
                if (this.config.debug) {
                    console.debug('Received user data:', event.user.user_name);
                }
                
                this.checkInitializationComplete();
            }
        });
        
        // Handle avatar list event
        this.on('avatar_list', (event: any) => {
            if (event.avatars) {
                this.avatars = event.avatars;
                this.initializationState.add('avatar_list');
                
                // Update avatar manager
                if (this.avatarManager) {
                    this.avatarManager.updateAvailableAvatars(event.avatars);
                }
                
                if (this.config.debug) {
                    console.debug('Received avatars:', event.avatars.length);
                }
                
                this.checkInitializationComplete();
            }
        });
        
        // Handle voice list event
        this.on('voice_list', (event: any) => {
            if (event.voices) {
                this.voices = event.voices;
                this.initializationState.add('voice_list');
                
                // Update voice manager
                if (this.voiceManager) {
                    this.voiceManager.setAvailableVoices(event.voices);
                }
                
                if (this.config.debug) {
                    console.debug('Received voices:', event.voices.length);
                }
                
                this.checkInitializationComplete();
            }
        });
        
        // Handle agent list event
        this.on('agent_list', (event: any) => {
            if (event.agents) {
                this.agents = event.agents;
                this.initializationState.add('agent_list');
                
                if (this.config.debug) {
                    console.debug('Received agents:', event.agents.length);
                }
                
                this.checkInitializationComplete();
            }
        });
        
        // Handle tool catalog event
        this.on('tool_catalog', (event: any) => {
            if (event.toolsets) {
                this.toolsets = event.toolsets;
                this.initializationState.add('tool_catalog');
                
                if (this.config.debug) {
                    console.debug('Received toolsets:', event.toolsets.length);
                }
                
                this.checkInitializationComplete();
            }
        });
        
        // The 6th event (chat_session_changed) is already handled in setupSessionManagerHandlers
        // We track it for initialization completion
        this.on('chat_session_changed', () => {
            if (!this.initializationState.has('chat_session_changed')) {
                this.initializationState.add('chat_session_changed');
                this.checkInitializationComplete();
            }
        });
        
        // Handle agent configuration changes
        this.on('agent_configuration_changed', (event: any) => {
            if (event.agent_config && this.sessionManager) {
                // Update the current session's agent configuration
                const currentSession = this.sessionManager.getCurrentSession();
                if (currentSession) {
                    currentSession.agent_config = event.agent_config;
                    
                    if (this.config.debug) {
                        console.debug('Agent configuration updated:', event.agent_config.key);
                    }
                }
            }
        });
    }
    
    /**
     * Check if all initialization events have been received
     */
    private checkInitializationComplete(): void {
        const requiredEvents = [
            'chat_user_data',
            'avatar_list', 
            'voice_list',
            'agent_list',
            'tool_catalog',
            'chat_session_changed'
        ];
        
        const allReceived = requiredEvents.every(event => this.initializationState.has(event));
        
        if (allReceived && !this.isInitialized) {
            this.isInitialized = true;
            
            if (this.config.debug) {
                console.debug('Initialization complete - all 6 events received');
            }
            
            // Emit a custom event to signal initialization is complete
            this.emit('initialized' as any, undefined);
        }
    }
    
    /**
     * Initialize the audio system components
     */
    private initializeAudioSystem(): void {
        if (!this.audioConfig) return;
        
        try {
            // Get singleton instances
            this.audioService = AudioService.getInstance();
            this.audioBridge = AudioAgentCBridge.getInstance();
            this.audioOutputService = AudioOutputService.getInstance();
            
            // Configure audio bridge with this client
            this.audioBridge.setClient(this);
            
            // The turn manager integration is handled by the AudioAgentCBridge
            // which checks turn state before streaming if respectTurnState is enabled
            
            // Set initial volume
            if (this.audioConfig.initialVolume !== undefined) {
                this.audioOutputService.setVolume(this.audioConfig.initialVolume);
            }
            
            // Subscribe to audio output events for playback
            this.on('audio:output', (audioData: ArrayBuffer) => {
                if (this.audioConfig?.enableOutput && this.audioOutputService) {
                    this.audioOutputService.playAudioChunk(audioData);
                }
            });
            
            // Subscribe to voice model changes from server
            this.on('agent_voice_changed', (event: AgentVoiceChangedEvent) => {
                if (this.voiceManager && event.voice) {
                    // Let voice manager handle the server voice change
                    this.voiceManager.handleServerVoiceChange(event.voice.voice_id);
                }
            });
            
            if (this.config.debug) {
                console.warn('Audio system initialized');
            }
        } catch (error) {
            console.error('Failed to initialize audio system:', error);
            this.emit('error', {
                type: 'error',
                message: 'Failed to initialize audio system',
                source: 'audio_init'
            });
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
                            
                            // Setup session manager handlers when connected
                            this.setupSessionManagerHandlers();
                            
                            // Reconnect audio bridge if audio is enabled
                            if (this.audioBridge && this.audioConfig?.enableInput) {
                                this.audioBridge.setClient(this);
                            }
                            
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
        
        // Stop audio streaming if active
        if (this.audioBridge?.getStatus().isStreaming) {
            this.audioBridge.stopStreaming();
        }
        
        // Stop audio recording if active
        if (this.audioService?.getStatus().isRecording) {
            this.audioService.stopRecording();
        }
        
        // Clear audio output buffers
        if (this.audioOutputService) {
            this.audioOutputService.clearBuffers();
        }
        
        // Clear session manager accumulator
        if (this.sessionManager) {
            this.sessionManager.resetAccumulator();
        }
        
        // Reset initialization state for next connection
        this.initializationState.clear();
        this.isInitialized = false;

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
            // const byteLength = data instanceof ArrayBuffer ? data.byteLength : data.byteLength;
            // console.debug('Sent binary audio frame:', byteLength, 'bytes');
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
     * Set avatar session after HeyGen STREAM_READY event.
     * This notifies Agent C that an avatar session is active.
     * 
     * @param sessionId - HeyGen session ID from StreamingEvents.STREAM_READY
     * @param avatarId - Avatar ID that was used to create the session
     */
    setAvatarSession(sessionId: string, avatarId: string): void {
        // Update avatar manager state
        if (this.avatarManager) {
            this.avatarManager.setAvatarSession(sessionId, avatarId);
        }
        
        // Send event to Agent C with avatar_id included
        this.sendEvent({
            type: 'set_avatar_session',
            session_id: sessionId,
            avatar_id: avatarId
        });
        
        // Voice manager will automatically switch to avatar voice when server responds
        if (this.config.debug) {
            // console.debug('Avatar session set:', { sessionId, avatarId });
        }
    }
    
    /**
     * Clear avatar session when HeyGen session ends
     */
    clearAvatarSession(): void {
        if (this.avatarManager) {
            const sessionId = this.avatarManager.getSessionId();
            this.avatarManager.clearAvatarSession();
            
            // Optionally send clear event to server
            // The server should detect this from HeyGen webhooks but we can be explicit
            if (sessionId) {
                this.sendEvent({
                    type: 'clear_avatar_session',
                    session_id: sessionId
                });
            }
        }
    }

    /**
     * Set agent voice
     */
    setAgentVoice(voiceId: string): void {
        // Update voice manager locally
        if (this.voiceManager) {
            this.voiceManager.setCurrentVoice(voiceId, 'client');
        }
        // Send to server
        this.sendEvent({ type: 'set_agent_voice', voice_id: voiceId });
    }

    /**
     * Send text input to the agent
     */
    sendText(text: string, fileIds?: string[]): void {
        // Add user message to session history
        if (this.sessionManager) {
            this.sessionManager.addUserMessage(text);
        }
        
        const event: TextInputEvent = { type: 'text_input', text };
        if (fileIds && fileIds.length > 0) {
            event.file_ids = fileIds;
        }
        this.sendEvent(event);
    }

    /**
     * Create a new chat session
     */
    newChatSession(agentKey?: string): void {
        // Reset accumulator when creating new session
        if (this.sessionManager) {
            this.sessionManager.resetAccumulator();
        }
        
        const event: NewChatSessionEvent = { type: 'new_chat_session' };
        if (agentKey) {
            event.agent_key = agentKey;
        }
        this.sendEvent(event);
    }

    /**
     * Resume an existing chat session
     */
    resumeChatSession(sessionId: string): void {
        // Reset accumulator when switching sessions
        if (this.sessionManager) {
            this.sessionManager.resetAccumulator();
        }
        
        this.sendEvent({ type: 'resume_chat_session', session_id: sessionId });
    }

    /**
     * Set chat session name
     */
    setChatSessionName(sessionName: string): void {
        // Update local session name immediately for better UX
        if (this.sessionManager) {
            const currentSessionId = this.sessionManager.getCurrentSessionId();
            if (currentSessionId) {
                this.sessionManager.updateSessionName(currentSessionId, sessionName);
            }
        }
        
        this.sendEvent({ type: 'set_chat_session_name', session_name: sessionName });
    }

    /**
     * Set session metadata
     */
    setSessionMetadata(meta: Record<string, unknown>): void {
        this.sendEvent({ type: 'set_session_metadata', meta });
    }

    /**
     * Set session messages
     */
    setSessionMessages(messages: Message[]): void {
        this.sendEvent({ type: 'set_session_messages', messages });
    }
    
    /**
     * Fetch paginated list of user sessions
     * @param offset Starting offset for pagination (default 0)
     * @param limit Number of sessions to fetch (default 50)
     */
    fetchUserSessions(offset: number = 0, limit: number = 50): void {
        const event: GetUserSessionsEvent = {
            type: 'get_user_sessions',
            offset,
            limit
        };
        this.sendEvent(event);
        
        if (this.config.debug) {
            console.debug('Requesting user sessions:', { offset, limit });
        }
    }
    
    /**
     * Request list of available voices from server
     * Server responds with voice_list event
     */
    getVoices(): void {
        this.sendEvent({ type: 'get_voices' });
    }
    
    /**
     * Request tool catalog from server
     * Server responds with tool_catalog event
     */
    getToolCatalog(): void {
        this.sendEvent({ type: 'get_tool_catalog' });
    }
    
    /**
     * Send ping to server for connection health check
     * Server responds with pong event
     */
    ping(): void {
        this.sendEvent({ type: 'ping' });
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
     * Get the voice manager instance
     */
    getVoiceManager(): VoiceManager | null {
        return this.voiceManager;
    }
    
    /**
     * Get the session manager instance
     */
    getSessionManager(): SessionManager | null {
        return this.sessionManager;
    }
    
    /**
     * Get the avatar manager instance
     */
    getAvatarManager(): AvatarManager | null {
        return this.avatarManager;
    }
    
    /**
     * Get available avatars from initialization events or avatar manager
     */
    getAvailableAvatars() {
        return this.avatars.length > 0 ? this.avatars : (this.avatarManager?.getAvailableAvatars() || []);
    }
    
    /**
     * Get HeyGen access token for avatar session creation
     */
    getHeyGenAccessToken(): string | null {
        if (this.authManager) {
            const tokens = this.authManager.getTokens();
            return tokens?.heygenToken || null;
        }
        return null;
    }
    
    /**
     * Get current user data from initialization events
     */
    getUserData(): User | null {
        return this.userData;
    }
    
    /**
     * Get available agents from initialization events
     */
    getAgentsList(): Agent[] {
        return this.agents;
    }
    
    /**
     * Get current agent configuration from the active session
     * Returns null if no session is active
     */
    getCurrentAgentConfig(): AgentConfiguration | null {
        if (this.sessionManager) {
            const currentSession = this.sessionManager.getCurrentSession();
            return currentSession?.agent_config || null;
        }
        return null;
    }
    
    /**
     * Get available voices from initialization events
     */
    getVoicesList(): Voice[] {
        return this.voices;
    }
    
    /**
     * Get available toolsets from initialization events
     */
    getToolsets(): Toolset[] {
        return this.toolsets;
    }
    
    /**
     * Check if client has completed initialization
     * All 6 initialization events must be received
     */
    isFullyInitialized(): boolean {
        return this.isInitialized;
    }
    
    /**
     * Wait for initialization to complete
     * Returns a promise that resolves when all 6 initialization events are received
     */
    waitForInitialization(): Promise<void> {
        return new Promise((resolve) => {
            if (this.isInitialized) {
                resolve();
            } else {
                this.once('initialized' as any, () => {
                    resolve();
                });
            }
        });
    }
    
    // Audio control methods
    
    /**
     * Start audio recording from microphone
     */
    async startAudioRecording(): Promise<void> {
        if (!this.audioService) {
            throw new Error('Audio system not initialized');
        }
        if (!this.audioConfig?.enableInput) {
            throw new Error('Audio input is disabled');
        }
        await this.audioService.startRecording();
    }
    
    /**
     * Stop audio recording
     */
    stopAudioRecording(): void {
        if (!this.audioService) {
            throw new Error('Audio system not initialized');
        }
        this.audioService.stopRecording();
    }
    
    /**
     * Start streaming audio to server
     */
    startAudioStreaming(): void {
        if (!this.audioBridge) {
            throw new Error('Audio system not initialized');
        }
        if (!this.isConnected()) {
            throw new Error('Not connected to server');
        }
        this.audioBridge.startStreaming();
    }
    
    /**
     * Stop streaming audio to server
     */
    stopAudioStreaming(): void {
        if (!this.audioBridge) {
            throw new Error('Audio system not initialized');
        }
        this.audioBridge.stopStreaming();
    }
    
    /**
     * Set audio playback volume
     * @param volume Volume level (0-1)
     */
    setAudioVolume(volume: number): void {
        if (!this.audioOutputService) {
            throw new Error('Audio output not initialized');
        }
        if (volume < 0 || volume > 1) {
            throw new Error('Volume must be between 0 and 1');
        }
        this.audioOutputService.setVolume(volume);
    }
    
    /**
     * Get combined audio system status
     */
    getAudioStatus(): AudioStatus {
        const inputStatus = this.audioService?.getStatus();
        const bridgeStatus = this.audioBridge?.getStatus();
        const outputStatus = this.audioOutputService?.getStatus();
        
        return {
            // Input status
            isRecording: inputStatus?.isRecording || false,
            isStreaming: bridgeStatus?.isStreaming || false,
            isProcessing: inputStatus?.state === 'recording' || false,
            hasPermission: inputStatus?.state !== 'permission-denied' && inputStatus?.state !== 'idle',
            currentLevel: inputStatus?.audioLevel || 0,
            averageLevel: inputStatus?.audioLevel || 0,  // Using current level as average for now
            
            // Output status
            isPlaying: outputStatus?.isPlaying || false,
            bufferSize: outputStatus?.queueLength || 0,
            volume: outputStatus?.volume || 1,
            
            // System status
            isAudioEnabled: !!this.audioService,
            isInputEnabled: !!this.audioConfig?.enableInput,
            isOutputEnabled: !!this.audioConfig?.enableOutput
        };
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
        
        // Note: Voice and avatar data will come from WebSocket initialization events
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

        // Build the WebSocket URL with the correct endpoint path
        const baseUrl = this.config.apiUrl;
        const wsUrl = baseUrl.endsWith('/') ? baseUrl + 'rt/ws' : baseUrl + '/rt/ws';
        
        const url = new URL(wsUrl);
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
                    // Handle ping events with pong response
                    if (event.type === 'ping') {
                        // Send pong directly via WebSocket, not through sendEvent
                        this.wsManager?.sendJSON({ type: 'pong' });
                        if (this.config.debug) {
                            // console.debug('Received ping, sent pong');
                        }
                        return;
                    }
                    
                    // Handle pong events (no action needed, just acknowledge)
                    if (event.type === 'pong') {
                        if (this.config.debug) {
                            // console.debug('Received pong');
                        }
                        return;
                    }
                    
                    // Emit the specific event
                    this.emit(event.type as keyof RealtimeEventMap, event as RealtimeEventMap[keyof RealtimeEventMap]);
                    
                    if (this.config.debug) {
                        // console.debug('Received event:', event.type, event);
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
                // console.debug('Received binary audio frame:', data.byteLength, 'bytes');
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
                // console.debug('Connection state changed:', ConnectionState[state]);
            }
        }
    }

    /**
     * Clean up resources
     */
    destroy(): void {
        // Stop and clean up audio first
        if (this.audioBridge?.getStatus().isStreaming) {
            this.audioBridge.stopStreaming();
        }
        
        if (this.audioService?.getStatus().isRecording) {
            this.audioService.stopRecording();
        }
        
        // Note: We don't destroy the singletons, just clean up our references
        this.audioService = null;
        
        if (this.audioBridge) {
            this.audioBridge.setClient(null);
            this.audioBridge = null;
        }
        
        if (this.audioOutputService) {
            this.audioOutputService.clearBuffers();
            this.audioOutputService = null;
        }
        
        this.disconnect();
        
        if (this.authManager) {
            this.authManager.removeAllListeners();
        }
        
        if (this.turnManager) {
            this.turnManager.destroy();
            this.turnManager = null;
        }
        
        if (this.voiceManager) {
            this.voiceManager.removeAllListeners();
            this.voiceManager = null;
        }
        
        if (this.sessionManager) {
            this.sessionManager.destroy();
            this.sessionManager = null;
        }
        
        if (this.avatarManager) {
            this.avatarManager.dispose();
            this.avatarManager = null;
        }
        
        this.removeAllListeners();
    }
}