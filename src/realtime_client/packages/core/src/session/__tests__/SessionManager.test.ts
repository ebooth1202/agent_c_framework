/**
 * Tests for SessionManager
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SessionManager } from '../SessionManager';
import { ChatSession, Message } from '../../events/types/CommonTypes';

describe('SessionManager', () => {
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
    it('should set current session from server', () => {
      const session = createMockSession('session-1', 'Test Session');
      
      expect(sessionManager.getCurrentSessionId()).toBeNull();
      
      sessionManager.setCurrentSession(session);
      
      expect(sessionManager.getCurrentSessionId()).toBe('session-1');
      expect(sessionManager.getCurrentSession()).toEqual(session);
    });

    it('should throw error when setting invalid session', () => {
      expect(() => {
        sessionManager.setCurrentSession(null as any);
      }).toThrow('Invalid session');

      expect(() => {
        sessionManager.setCurrentSession({ session_name: 'Test' } as any);
      }).toThrow('Invalid session: session must have a session_id');
    });

    it('should store multiple sessions', () => {
      const session1 = createMockSession('session-1', 'Session 1');
      const session2 = createMockSession('session-2', 'Session 2');
      const session3 = createMockSession('session-3', 'Session 3');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      sessionManager.setCurrentSession(session3);
      
      const sessions = sessionManager.getAllSessions();
      expect(sessions.size).toBe(3);
      expect(sessions.get('session-1')).toBeTruthy();
      expect(sessions.get('session-2')).toBeTruthy();
      expect(sessions.get('session-3')).toBeTruthy();
    });

    it('should update existing session when set again', () => {
      const session = createMockSession('session-1', 'Original Name');
      sessionManager.setCurrentSession(session);
      
      // Update the session
      const updatedSession = {
        ...session,
        session_name: 'Updated Name',
        messages: [{ role: 'user' as const, content: 'Hello', timestamp: new Date().toISOString(), format: 'text' as const }]
      };
      
      sessionManager.setCurrentSession(updatedSession);
      
      const retrieved = sessionManager.getSession('session-1');
      expect(retrieved?.session_name).toBe('Updated Name');
      expect(retrieved?.messages).toHaveLength(1);
    });

    it('should clear a specific session', () => {
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      
      const deleted = sessionManager.clearSession('session-1');
      expect(deleted).toBe(true);
      expect(sessionManager.getSession('session-1')).toBeNull();
      expect(sessionManager.getSession('session-2')).toBeTruthy();
    });

    it('should not clear non-existent session', () => {
      const deleted = sessionManager.clearSession('non-existent');
      expect(deleted).toBe(false);
    });

    it('should clear current session when it is deleted', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      expect(sessionManager.getCurrentSessionId()).toBe('session-1');
      
      sessionManager.clearSession('session-1');
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

    it('should reset all sessions', () => {
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      
      expect(sessionManager.getAllSessions().size).toBe(2);
      
      sessionManager.reset();
      
      expect(sessionManager.getAllSessions().size).toBe(0);
      expect(sessionManager.getCurrentSessionId()).toBeNull();
    });

    it('should prune oldest session when at max capacity', () => {
      // Create manager with max 3 sessions
      sessionManager = new SessionManager({ maxSessions: 3 });
      
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      const session3 = createMockSession('session-3');
      const session4 = createMockSession('session-4');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.setCurrentSession(session2);
      sessionManager.setCurrentSession(session3);
      
      // Adding 4th session should prune session-1 (oldest)
      sessionManager.setCurrentSession(session4);
      
      expect(sessionManager.getAllSessions().size).toBe(3);
      expect(sessionManager.getSession('session-1')).toBeNull();
      expect(sessionManager.getSession('session-4')).toBeTruthy();
    });
  });

  describe('Message Handling', () => {
    beforeEach(() => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
    });

    it('should add user message to current session', () => {
      const message = sessionManager.addUserMessage('Hello, assistant!');
      
      expect(message).toBeTruthy();
      expect(message?.role).toBe('user');
      expect(message?.content).toBe('Hello, assistant!');
      
      const session = sessionManager.getCurrentSession();
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0]).toMatchObject({
        role: 'user',
        content: 'Hello, assistant!',
      });
    });

    it('should not add user message without current session', () => {
      sessionManager.reset();
      
      const message = sessionManager.addUserMessage('Test');
      expect(message).toBeNull();
    });

    it('should accumulate text deltas', () => {
      expect(sessionManager.isAccumulatingText()).toBe(false);
      
      sessionManager.handleTextDelta('Hello');
      expect(sessionManager.isAccumulatingText()).toBe(true);
      expect(sessionManager.getAccumulatedText()).toBe('Hello');
      
      sessionManager.handleTextDelta(' ');
      sessionManager.handleTextDelta('world!');
      expect(sessionManager.getAccumulatedText()).toBe('Hello world!');
    });

    it('should finalize assistant message from accumulated text', () => {
      sessionManager.handleTextDelta('Hello ');
      sessionManager.handleTextDelta('from assistant!');
      
      const message = sessionManager.handleTextDone();
      
      expect(message).toBeTruthy();
      expect(message?.role).toBe('assistant');
      expect(message?.content).toBe('Hello from assistant!');
      
      // Accumulator should be reset
      expect(sessionManager.isAccumulatingText()).toBe(false);
      expect(sessionManager.getAccumulatedText()).toBe('');
      
      // Message should be in session
      const session = sessionManager.getCurrentSession();
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0].role).toBe('assistant');
    });

    it('should not finalize if not accumulating', () => {
      const message = sessionManager.handleTextDone();
      expect(message).toBeNull();
    });

    it('should reset accumulator', () => {
      sessionManager.handleTextDelta('Test content');
      expect(sessionManager.getAccumulatedText()).toBe('Test content');
      
      sessionManager.resetAccumulator();
      expect(sessionManager.getAccumulatedText()).toBe('');
      expect(sessionManager.isAccumulatingText()).toBe(false);
    });

    it('should maintain message order', () => {
      // User message
      sessionManager.addUserMessage('First message');
      
      // Assistant response
      sessionManager.handleTextDelta('Response');
      sessionManager.handleTextDone();
      
      // Another user message
      sessionManager.addUserMessage('Second message');
      
      const session = sessionManager.getCurrentSession();
      expect(session?.messages).toHaveLength(3);
      expect(session?.messages[0].content).toBe('First message');
      expect(session?.messages[1].content).toBe('Response');
      expect(session?.messages[2].content).toBe('Second message');
    });

    it('should update token count when adding messages', () => {
      const session = sessionManager.getCurrentSession();
      expect(session?.token_count).toBe(0);
      
      sessionManager.addUserMessage('Hello!'); // ~2 tokens
      const updatedSession = sessionManager.getCurrentSession();
      expect(updatedSession?.token_count).toBeGreaterThan(0);
    });
  });

  describe('Session Updates', () => {
    beforeEach(() => {
      const session = createMockSession('session-1', 'Original Name');
      sessionManager.setCurrentSession(session);
    });

    it('should update session metadata', () => {
      const metadata = { user: 'test', purpose: 'testing' };
      
      const updated = sessionManager.updateSessionMetadata('session-1', metadata);
      expect(updated).toBe(true);
      
      const session = sessionManager.getSession('session-1');
      expect(session?.metadata).toEqual(metadata);
    });

    it('should merge metadata updates', () => {
      sessionManager.updateSessionMetadata('session-1', { key1: 'value1' });
      sessionManager.updateSessionMetadata('session-1', { key2: 'value2' });
      
      const session = sessionManager.getSession('session-1');
      expect(session?.metadata).toEqual({
        key1: 'value1',
        key2: 'value2'
      });
    });

    it('should not update metadata for non-existent session', () => {
      const updated = sessionManager.updateSessionMetadata('non-existent', { test: true });
      expect(updated).toBe(false);
    });

    it('should update session name', () => {
      const updated = sessionManager.updateSessionName('session-1', 'New Name');
      expect(updated).toBe(true);
      
      const session = sessionManager.getSession('session-1');
      expect(session?.session_name).toBe('New Name');
    });

    it('should not update name for non-existent session', () => {
      const updated = sessionManager.updateSessionName('non-existent', 'New Name');
      expect(updated).toBe(false);
    });

    it('should update session timestamp on changes', () => {
      const session = sessionManager.getSession('session-1');
      const originalTime = session?.updated_at;
      
      // Wait a bit to ensure timestamp difference
      vi.useFakeTimers();
      vi.advanceTimersByTime(1000);
      
      sessionManager.updateSessionName('session-1', 'Updated');
      
      const updatedSession = sessionManager.getSession('session-1');
      expect(updatedSession?.updated_at).not.toBe(originalTime);
      
      vi.useRealTimers();
    });
  });

  describe('Event Emissions', () => {
    it('should emit session-changed event', () => {
      const listener = vi.fn();
      sessionManager.on('session-changed', listener);
      
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      expect(listener).toHaveBeenCalledWith({
        previousSession: null,
        currentSession: session
      });
    });

    it('should emit message-added event for user messages', () => {
      const listener = vi.fn();
      sessionManager.on('message-added', listener);
      
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      sessionManager.addUserMessage('Test message');
      
      expect(listener).toHaveBeenCalledWith({
        sessionId: 'session-1',
        message: expect.objectContaining({
          role: 'user',
          content: 'Test message'
        })
      });
    });

    it('should emit message-added event for assistant messages', () => {
      const listener = vi.fn();
      sessionManager.on('message-added', listener);
      
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      sessionManager.handleTextDelta('Assistant response');
      sessionManager.handleTextDone();
      
      expect(listener).toHaveBeenCalledWith({
        sessionId: 'session-1',
        message: expect.objectContaining({
          role: 'assistant',
          content: 'Assistant response'
        })
      });
    });

    it('should emit sessions-updated event', () => {
      const listener = vi.fn();
      sessionManager.on('sessions-updated', listener);
      
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      expect(listener).toHaveBeenCalledWith({
        sessions: expect.any(Map)
      });
    });

    it('should emit session-cleared event', () => {
      const listener = vi.fn();
      sessionManager.on('session-cleared', listener);
      
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      sessionManager.clearSession('session-1');
      
      expect(listener).toHaveBeenCalledWith({
        sessionId: 'session-1'
      });
    });

    it('should emit all-sessions-cleared event', () => {
      const listener = vi.fn();
      sessionManager.on('all-sessions-cleared', listener);
      
      sessionManager.reset();
      
      expect(listener).toHaveBeenCalled();
    });
  });

  describe('Statistics', () => {
    it('should provide session statistics', () => {
      const session1 = createMockSession('session-1');
      const session2 = createMockSession('session-2');
      
      sessionManager.setCurrentSession(session1);
      sessionManager.addUserMessage('Test 1');
      
      sessionManager.setCurrentSession(session2);
      sessionManager.addUserMessage('Test 2');
      sessionManager.handleTextDelta('Response');
      sessionManager.handleTextDone();
      
      const stats = sessionManager.getStatistics();
      
      expect(stats.totalSessions).toBe(2);
      expect(stats.totalMessages).toBe(3);
      expect(stats.totalTokens).toBeGreaterThan(0);
      expect(stats.currentSessionId).toBe('session-2');
      expect(stats.hasActiveAccumulation).toBe(false);
    });

    it('should track active accumulation in statistics', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      sessionManager.handleTextDelta('Accumulating...');
      
      const stats = sessionManager.getStatistics();
      expect(stats.hasActiveAccumulation).toBe(true);
    });
  });

  describe('Cleanup', () => {
    it('should cleanup resources', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      sessionManager.handleTextDelta('Test');
      
      sessionManager.cleanup();
      
      expect(sessionManager.getAllSessions().size).toBe(0);
      expect(sessionManager.getCurrentSessionId()).toBeNull();
      expect(sessionManager.getAccumulatedText()).toBe('');
    });

    it('should remove all listeners on cleanup', () => {
      const listener = vi.fn();
      sessionManager.on('session-changed', listener);
      
      sessionManager.cleanup();
      
      // Try to trigger event after cleanup
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      // Listener should not be called after cleanup
      expect(listener).not.toHaveBeenCalled();
    });

    it('should support destroy alias', () => {
      const session = createMockSession('session-1');
      sessionManager.setCurrentSession(session);
      
      sessionManager.destroy();
      
      expect(sessionManager.getAllSessions().size).toBe(0);
    });
  });
});