/**
 * Simplified tests for SessionManager
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { SessionManager } from '../SessionManager';
import { ChatSession } from '../../events/types/CommonTypes';

describe('SessionManager - Simple Tests', () => {
  let sessionManager: SessionManager;

  beforeEach(() => {
    sessionManager = new SessionManager();
  });

  // Helper to create a mock ChatSession
  function createMockSession(id: string, name: string = 'Test Session'): ChatSession {
    return {
      session_id: id,
      session_name: name,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [],
      token_count: 0,
      metadata: {}
    };
  }

  describe('Session Management', () => {
    it('should set and get current session from server', () => {
      const session = createMockSession('session-1', 'Test Session');
      
      // Initially no current session
      expect(sessionManager.getCurrentSessionId()).toBeNull();
      expect(sessionManager.getCurrentSession()).toBeNull();
      
      // Set session from server event
      sessionManager.setCurrentSession(session);
      
      expect(sessionManager.getCurrentSessionId()).toBe('session-1');
      expect(sessionManager.getCurrentSession()).toEqual(session);
    });

    it('should handle multiple sessions', () => {
      const session1 = createMockSession('session-1', 'Session 1');
      const session2 = createMockSession('session-2', 'Session 2');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      
      // Current should be session2
      expect(sessionManager.getCurrentSessionId()).toBe('session-2');
      
      // Both sessions should be stored
      expect(sessionManager.getSession('session-1')).toBeTruthy();
      expect(sessionManager.getSession('session-2')).toBeTruthy();
      
      // Should have 2 sessions
      const allSessions = sessionManager.getAllSessions();
      expect(allSessions.size).toBe(2);
    });

    it('should clear a specific session', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      const deleted = sessionManager.clearSession('session-1');
      expect(deleted).toBe(true);
      expect(sessionManager.getSession('session-1')).toBeNull();
      expect(sessionManager.getCurrentSessionId()).toBeNull();
    });

    it('should list all session IDs', () => {
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      const session3 = createMockSession('session-3');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      sessionManager.setCurrentSession(session3);
      
      const sessionIds = sessionManager.getSessionIds();
      expect(sessionIds).toHaveLength(3);
      expect(sessionIds).toContain('session-1');
      expect(sessionIds).toContain('session-2');
      expect(sessionIds).toContain('session-3');
    });
  });

  describe('Message Handling', () => {
    beforeEach(() => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
    });

    it('should add user message to current session', () => {
      const message = sessionManager.addUserMessage('Hello!');
      
      expect(message).toBeTruthy();
      expect(message?.role).toBe('user');
      expect(message?.content).toBe('Hello!');
      
      const session = sessionManager.getCurrentSession();
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0].content).toBe('Hello!');
    });

    it('should accumulate text deltas from assistant', () => {
      // Initially not accumulating
      expect(sessionManager.isAccumulatingText()).toBe(false);
      expect(sessionManager.getAccumulatedText()).toBe('');
      
      // Accumulate text deltas
      sessionManager.handleTextDelta('Hello');
      sessionManager.handleTextDelta(' ');
      sessionManager.handleTextDelta('there!');
      
      expect(sessionManager.isAccumulatingText()).toBe(true);
      expect(sessionManager.getAccumulatedText()).toBe('Hello there!');
    });

    it('should finalize assistant message from accumulated text', () => {
      // Accumulate text
      sessionManager.handleTextDelta('Hi there!');
      
      // Finalize the message
      const message = sessionManager.handleTextDone();
      
      expect(message).toBeTruthy();
      expect(message?.role).toBe('assistant');
      expect(message?.content).toBe('Hi there!');
      
      // Accumulator should be reset
      expect(sessionManager.isAccumulatingText()).toBe(false);
      expect(sessionManager.getAccumulatedText()).toBe('');
      
      // Message should be in session
      const session = sessionManager.getCurrentSession();
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0].role).toBe('assistant');
    });
  });

  describe('Session Updates', () => {
    it('should update session metadata', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      const metadata = { user: 'test', purpose: 'testing' };
      const updated = sessionManager.updateSessionMetadata('session-1', metadata);
      
      expect(updated).toBe(true);
      const updatedSession = sessionManager.getSession('session-1');
      expect(updatedSession?.metadata).toEqual(metadata);
    });

    it('should update session name', () => {
      const session = createMockSession('session-1', 'Original Name');
      sessionManager.setCurrentSession(session);
      
      const updated = sessionManager.updateSessionName('session-1', 'New Name');
      
      expect(updated).toBe(true);
      const updatedSession = sessionManager.getSession('session-1');
      expect(updatedSession?.session_name).toBe('New Name');
    });
  });

  describe('Reset and Cleanup', () => {
    it('should reset all sessions', () => {
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      
      sessionManager.reset();
      
      expect(sessionManager.getAllSessions().size).toBe(0);
      expect(sessionManager.getCurrentSessionId()).toBeNull();
      expect(sessionManager.getAccumulatedText()).toBe('');
    });
  });
});