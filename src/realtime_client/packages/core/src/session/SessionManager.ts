/**
 * Session Manager for Agent C Realtime SDK
 * Manages multiple chat sessions, tracks current session, and handles message history
 */

import { EventEmitter } from '../events/EventEmitter';
import { ChatSession, Message } from '../events/types/CommonTypes';
import { Logger } from '../utils/logger';

/**
 * Event map for SessionManager events
 */
export interface SessionManagerEventMap {
  'session-changed': { 
    previousSession: ChatSession | null; 
    currentSession: ChatSession | null;
  };
  'message-added': { 
    sessionId: string; 
    message: Message; 
  };
  'sessions-updated': { 
    sessions: Map<string, ChatSession>; 
  };
  'session-cleared': { 
    sessionId: string; 
  };
  'all-sessions-cleared': void;
}

/**
 * Configuration options for SessionManager
 */
export interface SessionManagerConfig {
  maxSessions?: number;
  persistSessions?: boolean;
  defaultSessionName?: string;
}

/**
 * Manages chat sessions including history, current session tracking, and message accumulation
 */
export class SessionManager extends EventEmitter<SessionManagerEventMap> {
  private sessions: Map<string, ChatSession>;
  private currentSessionId: string | null;
  private textAccumulator: string;
  private isAccumulating: boolean;
  private config: SessionManagerConfig;
  private logger: Logger;

  /**
   * Create a new SessionManager instance
   * @param config - Optional configuration for the session manager
   */
  constructor(config: SessionManagerConfig = {}) {
    super();
    
    this.sessions = new Map();
    this.currentSessionId = null;
    this.textAccumulator = '';
    this.isAccumulating = false;
    
    this.config = {
      maxSessions: config.maxSessions || 100,
      persistSessions: config.persistSessions || false,
      defaultSessionName: config.defaultSessionName || 'Chat Session'
    };
    
    this.logger = new Logger('SessionManager');
    this.logger.info('SessionManager initialized', this.config);
  }

  /**
   * Set the current active session from server
   * @param session - ChatSession object from server
   * @emits session-changed event
   */
  setCurrentSession(session: ChatSession): void {
    if (!session || !session.session_id) {
      this.logger.error('Invalid session provided to setCurrentSession');
      throw new Error('Invalid session: session must have a session_id');
    }

    const previousSession = this.getCurrentSession();
    const previousId = this.currentSessionId;

    // Update or add the session
    this.sessions.set(session.session_id, session);
    this.currentSessionId = session.session_id;

    // Check if we're at max capacity
    if (this.sessions.size > this.config.maxSessions!) {
      this.pruneOldestSession();
    }

    this.logger.info(`Current session set to: ${session.session_id}`, {
      sessionName: session.session_name,
      messageCount: session.messages.length,
      tokenCount: session.token_count
    });

    // Emit events if session actually changed
    if (previousId !== session.session_id) {
      this.emit('session-changed', {
        previousSession,
        currentSession: session
      });
    }

    this.emit('sessions-updated', {
      sessions: this.sessions
    });
  }

  /**
   * Get the current active session
   * @returns Current ChatSession or null if no session is active
   */
  getCurrentSession(): ChatSession | null {
    if (!this.currentSessionId) {
      return null;
    }
    return this.sessions.get(this.currentSessionId) || null;
  }

  /**
   * Get the current session ID
   * @returns Current session ID or null
   */
  getCurrentSessionId(): string | null {
    return this.currentSessionId;
  }

  /**
   * Get a specific session by ID
   * @param sessionId - ID of the session to retrieve
   * @returns ChatSession or null if not found
   */
  getSession(sessionId: string): ChatSession | null {
    return this.sessions.get(sessionId) || null;
  }

  /**
   * Get all sessions
   * @returns Map of all sessions
   */
  getAllSessions(): Map<string, ChatSession> {
    return new Map(this.sessions);
  }

  /**
   * Get all session IDs
   * @returns Array of session IDs
   */
  getSessionIds(): string[] {
    return Array.from(this.sessions.keys());
  }

  /**
   * Add a user message to the current session
   * @param content - Message content from the user
   * @returns The created message or null if no current session
   * @emits message-added event
   */
  addUserMessage(content: string): Message | null {
    const session = this.getCurrentSession();
    if (!session) {
      this.logger.warn('Cannot add user message: no current session');
      return null;
    }

    const message: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      format: 'text'
    };

    session.messages.push(message);
    
    // Update token count (rough estimate: ~4 chars per token)
    session.token_count += Math.ceil(content.length / 4);
    session.updated_at = new Date().toISOString();

    this.logger.debug(`User message added to session ${session.session_id}`, {
      contentLength: content.length,
      totalMessages: session.messages.length
    });

    this.emit('message-added', {
      sessionId: session.session_id,
      message
    });

    return message;
  }

  /**
   * Handle text delta from assistant (accumulate text)
   * @param delta - Text chunk to accumulate
   */
  handleTextDelta(delta: string): void {
    if (!delta) {
      return;
    }

    if (!this.getCurrentSession()) {
      this.logger.warn('Received text delta but no current session');
      return;
    }

    this.isAccumulating = true;
    this.textAccumulator += delta;
    
    this.logger.debug(`Text delta accumulated`, {
      deltaLength: delta.length,
      totalAccumulated: this.textAccumulator.length
    });
  }

  /**
   * Finalize assistant message from accumulated text
   * @returns The created message or null if no accumulation or session
   * @emits message-added event
   */
  handleTextDone(): Message | null {
    if (!this.isAccumulating || !this.textAccumulator) {
      this.logger.debug('handleTextDone called but nothing to finalize');
      return null;
    }

    const session = this.getCurrentSession();
    if (!session) {
      this.logger.warn('Cannot finalize assistant message: no current session');
      this.resetAccumulator();
      return null;
    }

    const message: Message = {
      role: 'assistant',
      content: this.textAccumulator,
      timestamp: new Date().toISOString(),
      format: 'text'
    };

    session.messages.push(message);
    
    // Update token count
    session.token_count += Math.ceil(this.textAccumulator.length / 4);
    session.updated_at = new Date().toISOString();

    this.logger.info(`Assistant message finalized in session ${session.session_id}`, {
      contentLength: this.textAccumulator.length,
      totalMessages: session.messages.length,
      tokenCount: session.token_count
    });

    this.emit('message-added', {
      sessionId: session.session_id,
      message
    });

    // Reset accumulator
    const finalMessage = message;
    this.resetAccumulator();
    
    return finalMessage;
  }

  /**
   * Clear the text accumulator
   */
  resetAccumulator(): void {
    this.textAccumulator = '';
    this.isAccumulating = false;
  }

  /**
   * Get the current accumulated text
   * @returns Current accumulated text
   */
  getAccumulatedText(): string {
    return this.textAccumulator;
  }

  /**
   * Check if currently accumulating text
   * @returns True if accumulating
   */
  isAccumulatingText(): boolean {
    return this.isAccumulating;
  }

  /**
   * Clear a specific session
   * @param sessionId - ID of the session to clear
   * @returns True if session was cleared, false if not found
   * @emits session-cleared event
   */
  clearSession(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) {
      this.logger.warn(`Cannot clear session: ${sessionId} not found`);
      return false;
    }

    // If clearing current session, reset current session ID
    if (this.currentSessionId === sessionId) {
      this.currentSessionId = null;
      this.resetAccumulator();
    }

    this.sessions.delete(sessionId);
    
    this.logger.info(`Session cleared: ${sessionId}`);
    
    this.emit('session-cleared', { sessionId });
    this.emit('sessions-updated', { sessions: this.sessions });
    
    return true;
  }

  /**
   * Clear all sessions and reset state
   * @emits all-sessions-cleared event
   */
  reset(): void {
    const sessionCount = this.sessions.size;
    
    this.sessions.clear();
    this.currentSessionId = null;
    this.resetAccumulator();
    
    this.logger.info(`All sessions cleared (${sessionCount} sessions removed)`);
    
    this.emit('all-sessions-cleared', undefined);
    this.emit('sessions-updated', { sessions: this.sessions });
  }

  /**
   * Update session metadata
   * @param sessionId - Session ID to update
   * @param metadata - Metadata to merge with existing metadata
   * @returns True if updated, false if session not found
   */
  updateSessionMetadata(sessionId: string, metadata: Record<string, unknown>): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) {
      this.logger.warn(`Cannot update metadata: session ${sessionId} not found`);
      return false;
    }

    session.metadata = {
      ...session.metadata,
      ...metadata
    };
    session.updated_at = new Date().toISOString();

    this.logger.debug(`Session metadata updated for ${sessionId}`, metadata);
    
    this.emit('sessions-updated', { sessions: this.sessions });
    
    return true;
  }

  /**
   * Update session name
   * @param sessionId - Session ID to update
   * @param name - New session name
   * @returns True if updated, false if session not found
   */
  updateSessionName(sessionId: string, name: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) {
      this.logger.warn(`Cannot update name: session ${sessionId} not found`);
      return false;
    }

    session.session_name = name;
    session.updated_at = new Date().toISOString();

    this.logger.info(`Session name updated for ${sessionId}: ${name}`);
    
    this.emit('sessions-updated', { sessions: this.sessions });
    
    return true;
  }

  /**
   * Prune the oldest session when at max capacity
   */
  private pruneOldestSession(): void {
    if (this.sessions.size === 0) return;

    let oldestSessionId: string | null = null;
    let oldestTime: Date | null = null;

    // Find the oldest session (excluding current)
    for (const [id, session] of this.sessions) {
      if (id === this.currentSessionId) continue;
      
      const sessionTime = new Date(session.updated_at || session.created_at || 0);
      if (!oldestTime || sessionTime < oldestTime) {
        oldestTime = sessionTime;
        oldestSessionId = id;
      }
    }

    if (oldestSessionId) {
      this.logger.info(`Pruning oldest session: ${oldestSessionId}`);
      this.clearSession(oldestSessionId);
    }
  }

  /**
   * Get session statistics
   * @returns Statistics about current sessions
   */
  getStatistics(): {
    totalSessions: number;
    totalMessages: number;
    totalTokens: number;
    currentSessionId: string | null;
    hasActiveAccumulation: boolean;
  } {
    let totalMessages = 0;
    let totalTokens = 0;

    for (const session of this.sessions.values()) {
      totalMessages += session.messages.length;
      totalTokens += session.token_count;
    }

    return {
      totalSessions: this.sessions.size,
      totalMessages,
      totalTokens,
      currentSessionId: this.currentSessionId,
      hasActiveAccumulation: this.isAccumulating
    };
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    this.reset();
    this.removeAllListeners();
    this.logger.info('SessionManager cleaned up');
  }

  /**
   * Destroy the session manager
   * Alias for cleanup for consistency
   */
  destroy(): void {
    this.cleanup();
  }
}