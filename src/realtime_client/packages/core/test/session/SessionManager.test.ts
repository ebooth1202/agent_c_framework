/**
 * Tests for SessionManager
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SessionManager } from '../../src/session/SessionManager';
import { EventEmitter } from '../../src/events/EventEmitter';
import { createMockAgentCEvent } from '@test/utils/test-helpers';

describe('SessionManager', () => {
  let sessionManager: SessionManager;
  let mockEventEmitter: EventEmitter;

  beforeEach(() => {
    mockEventEmitter = new EventEmitter();
    sessionManager = new SessionManager(mockEventEmitter);
  });

  describe('Session Creation', () => {
    it('should create a new session', () => {
      const sessionId = sessionManager.createSession('Test Session');
      
      expect(sessionId).toBeDefined();
      expect(sessionManager.hasSession(sessionId)).toBe(true);
      
      const session = sessionManager.getSession(sessionId);
      expect(session).toBeDefined();
      expect(session?.name).toBe('Test Session');
      expect(session?.messages).toEqual([]);
    });

    it('should create session with metadata', () => {
      const metadata = { user: 'test', purpose: 'testing' };
      const sessionId = sessionManager.createSession('Test Session', metadata);
      
      const session = sessionManager.getSession(sessionId);
      expect(session?.metadata).toEqual(metadata);
    });

    it('should generate unique session IDs', () => {
      const id1 = sessionManager.createSession('Session 1');
      const id2 = sessionManager.createSession('Session 2');
      
      expect(id1).not.toBe(id2);
    });
  });

  describe('Session Management', () => {
    let sessionId: string;

    beforeEach(() => {
      sessionId = sessionManager.createSession('Test Session');
    });

    it('should set and get current session', () => {
      expect(sessionManager.getCurrentSessionId()).toBeNull();
      
      sessionManager.setCurrentSession(sessionId);
      expect(sessionManager.getCurrentSessionId()).toBe(sessionId);
      
      const currentSession = sessionManager.getCurrentSession();
      expect(currentSession?.id).toBe(sessionId);
    });

    it('should delete a session', () => {
      expect(sessionManager.hasSession(sessionId)).toBe(true);
      
      const deleted = sessionManager.deleteSession(sessionId);
      expect(deleted).toBe(true);
      expect(sessionManager.hasSession(sessionId)).toBe(false);
    });

    it('should not delete non-existent session', () => {
      const deleted = sessionManager.deleteSession('non-existent');
      expect(deleted).toBe(false);
    });

    it('should clear current session when deleted', () => {
      sessionManager.setCurrentSession(sessionId);
      expect(sessionManager.getCurrentSessionId()).toBe(sessionId);
      
      sessionManager.deleteSession(sessionId);
      expect(sessionManager.getCurrentSessionId()).toBeNull();
    });

    it('should list all sessions', () => {
      const id2 = sessionManager.createSession('Session 2');
      const id3 = sessionManager.createSession('Session 3');
      
      const sessions = sessionManager.listSessions();
      expect(sessions).toHaveLength(3);
      
      const sessionIds = sessions.map(s => s.id);
      expect(sessionIds).toContain(sessionId);
      expect(sessionIds).toContain(id2);
      expect(sessionIds).toContain(id3);
    });

    it('should update session metadata', () => {
      const newMetadata = { updated: true, timestamp: Date.now() };
      
      sessionManager.updateSessionMetadata(sessionId, newMetadata);
      
      const session = sessionManager.getSession(sessionId);
      expect(session?.metadata).toEqual(newMetadata);
    });

    it('should clear all sessions', () => {
      sessionManager.createSession('Session 2');
      sessionManager.createSession('Session 3');
      
      expect(sessionManager.listSessions()).toHaveLength(3);
      
      sessionManager.clearAllSessions();
      expect(sessionManager.listSessions()).toHaveLength(0);
      expect(sessionManager.getCurrentSessionId()).toBeNull();
    });
  });

  describe('Message Handling', () => {
    let sessionId: string;

    beforeEach(() => {
      sessionId = sessionManager.createSession('Test Session');
      sessionManager.setCurrentSession(sessionId);
    });

    it('should add user message', () => {
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'Hello, assistant!',
        timestamp: new Date().toISOString(),
      });
      
      const session = sessionManager.getSession(sessionId);
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0]).toMatchObject({
        role: 'user',
        content: 'Hello, assistant!',
      });
    });

    it('should add assistant message', () => {
      sessionManager.addMessage(sessionId, {
        role: 'assistant',
        content: 'Hello! How can I help you?',
        timestamp: new Date().toISOString(),
      });
      
      const session = sessionManager.getSession(sessionId);
      expect(session?.messages).toHaveLength(1);
      expect(session?.messages[0]).toMatchObject({
        role: 'assistant',
        content: 'Hello! How can I help you?',
      });
    });

    it('should maintain message order', () => {
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'First message',
        timestamp: new Date().toISOString(),
      });
      
      sessionManager.addMessage(sessionId, {
        role: 'assistant',
        content: 'Response',
        timestamp: new Date().toISOString(),
      });
      
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'Second message',
        timestamp: new Date().toISOString(),
      });
      
      const session = sessionManager.getSession(sessionId);
      expect(session?.messages).toHaveLength(3);
      expect(session?.messages[0].content).toBe('First message');
      expect(session?.messages[1].content).toBe('Response');
      expect(session?.messages[2].content).toBe('Second message');
    });

    it('should not add message to non-existent session', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      sessionManager.addMessage('non-existent', {
        role: 'user',
        content: 'Test',
        timestamp: new Date().toISOString(),
      });
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Session not found')
      );
      
      consoleSpy.mockRestore();
    });

    it('should get message history', () => {
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'Message 1',
        timestamp: new Date().toISOString(),
      });
      
      sessionManager.addMessage(sessionId, {
        role: 'assistant',
        content: 'Message 2',
        timestamp: new Date().toISOString(),
      });
      
      const history = sessionManager.getMessageHistory(sessionId);
      expect(history).toHaveLength(2);
      expect(history[0].content).toBe('Message 1');
      expect(history[1].content).toBe('Message 2');
    });

    it('should return empty array for non-existent session history', () => {
      const history = sessionManager.getMessageHistory('non-existent');
      expect(history).toEqual([]);
    });

    it('should clear session messages', () => {
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'Test message',
        timestamp: new Date().toISOString(),
      });
      
      expect(sessionManager.getMessageHistory(sessionId)).toHaveLength(1);
      
      sessionManager.clearSessionMessages(sessionId);
      expect(sessionManager.getMessageHistory(sessionId)).toHaveLength(0);
    });
  });

  describe('Event Handling', () => {
    let sessionId: string;

    beforeEach(() => {
      sessionId = sessionManager.createSession('Test Session');
      sessionManager.setCurrentSession(sessionId);
    });

    it('should handle text_start event', () => {
      const event = createMockAgentCEvent('text_start', {
        timestamp: new Date().toISOString(),
      });
      
      mockEventEmitter.emit('text_start', event);
      
      // Should start collecting assistant message
      const session = sessionManager.getSession(sessionId);
      expect(session).toBeDefined();
    });

    it('should handle text_delta event', () => {
      // Start text first
      mockEventEmitter.emit('text_start', createMockAgentCEvent('text_start'));
      
      // Send delta
      const event = createMockAgentCEvent('text_delta', {
        content: 'Hello ',
      });
      
      mockEventEmitter.emit('text_delta', event);
      
      // Should accumulate content
      const session = sessionManager.getSession(sessionId);
      expect(session).toBeDefined();
    });

    it('should handle text_end event', () => {
      // Start and send deltas
      mockEventEmitter.emit('text_start', createMockAgentCEvent('text_start'));
      mockEventEmitter.emit('text_delta', createMockAgentCEvent('text_delta', { content: 'Hello ' }));
      mockEventEmitter.emit('text_delta', createMockAgentCEvent('text_delta', { content: 'world!' }));
      
      // End text
      const event = createMockAgentCEvent('text_end', {
        timestamp: new Date().toISOString(),
      });
      
      mockEventEmitter.emit('text_end', event);
      
      // Should have complete message
      const session = sessionManager.getSession(sessionId);
      const messages = session?.messages || [];
      expect(messages).toHaveLength(1);
      expect(messages[0].content).toBe('Hello world!');
      expect(messages[0].role).toBe('assistant');
    });

    it('should handle user input event', () => {
      const event = createMockAgentCEvent('user_input', {
        content: 'User message',
        timestamp: new Date().toISOString(),
      });
      
      mockEventEmitter.emit('user_input', event);
      
      const session = sessionManager.getSession(sessionId);
      const messages = session?.messages || [];
      expect(messages).toHaveLength(1);
      expect(messages[0].content).toBe('User message');
      expect(messages[0].role).toBe('user');
    });

    it('should not process events without current session', () => {
      sessionManager.setCurrentSession(null);
      
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      mockEventEmitter.emit('text_start', createMockAgentCEvent('text_start'));
      
      expect(consoleSpy).not.toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });

  describe('Session Persistence', () => {
    it('should export session data', () => {
      const sessionId = sessionManager.createSession('Export Test', { test: true });
      
      sessionManager.addMessage(sessionId, {
        role: 'user',
        content: 'Test message',
        timestamp: new Date().toISOString(),
      });
      
      const exported = sessionManager.exportSession(sessionId);
      
      expect(exported).toBeDefined();
      expect(exported?.name).toBe('Export Test');
      expect(exported?.metadata).toEqual({ test: true });
      expect(exported?.messages).toHaveLength(1);
    });

    it('should import session data', () => {
      const sessionData = {
        id: 'imported-session',
        name: 'Imported Session',
        createdAt: new Date().toISOString(),
        messages: [
          {
            role: 'user' as const,
            content: 'Imported message',
            timestamp: new Date().toISOString(),
          },
        ],
        metadata: { imported: true },
      };
      
      sessionManager.importSession(sessionData);
      
      expect(sessionManager.hasSession('imported-session')).toBe(true);
      
      const session = sessionManager.getSession('imported-session');
      expect(session?.name).toBe('Imported Session');
      expect(session?.messages).toHaveLength(1);
      expect(session?.metadata).toEqual({ imported: true });
    });

    it('should export all sessions', () => {
      sessionManager.createSession('Session 1');
      sessionManager.createSession('Session 2');
      sessionManager.createSession('Session 3');
      
      const allSessions = sessionManager.exportAllSessions();
      
      expect(allSessions).toHaveLength(3);
      expect(allSessions.map(s => s.name)).toContain('Session 1');
      expect(allSessions.map(s => s.name)).toContain('Session 2');
      expect(allSessions.map(s => s.name)).toContain('Session 3');
    });

    it('should import multiple sessions', () => {
      const sessions = [
        {
          id: 'import-1',
          name: 'Import 1',
          createdAt: new Date().toISOString(),
          messages: [],
          metadata: {},
        },
        {
          id: 'import-2',
          name: 'Import 2',
          createdAt: new Date().toISOString(),
          messages: [],
          metadata: {},
        },
      ];
      
      sessionManager.importSessions(sessions);
      
      expect(sessionManager.hasSession('import-1')).toBe(true);
      expect(sessionManager.hasSession('import-2')).toBe(true);
    });
  });
});