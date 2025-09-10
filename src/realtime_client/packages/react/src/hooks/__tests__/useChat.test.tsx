/**
 * Tests for useChat hook
 * Tests message history, text communication, and session management
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '../useChat';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';
import type { ChatMessage, ChatRole } from '@agentc/realtime-core';

describe('useChat', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockClient = {
      ...createMockClient(),
      sendText: vi.fn().mockResolvedValue({ messageId: 'msg-123' }),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      }),
      emit: vi.fn((event: string, ...args: any[]) => {
        eventHandlers.get(event)?.forEach(handler => handler(...args));
      })
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns empty message list initially', () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.messages).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.hasMore).toBe(false);
    });

    it('initializes with correct typing state', () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.isTyping).toBe(false);
      expect(result.current.typingUsers).toEqual([]);
    });

    it('provides session information', () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.sessionId).toBeNull();
      expect(result.current.sessionMetadata).toEqual({});
    });
  });

  describe('Message Sending', () => {
    it('sends text message successfully', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const messageText = 'Hello, AI!';
      
      await act(async () => {
        await result.current.sendMessage(messageText);
      });

      expect(mockClient.sendText).toHaveBeenCalledWith(messageText);
      
      // Should add optimistic message
      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].content).toBe(messageText);
      expect(result.current.messages[0].role).toBe('user');
    });

    it('handles send message with metadata', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const messageText = 'Test message';
      const metadata = { priority: 'high', category: 'question' };
      
      await act(async () => {
        await result.current.sendMessage(messageText, metadata);
      });

      expect(mockClient.sendText).toHaveBeenCalledWith(messageText);
      expect(result.current.messages[0].metadata).toEqual(metadata);
    });

    it('handles send message failure', async () => {
      const error = new Error('Failed to send message');
      mockClient.sendText.mockRejectedValue(error);

      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.sendMessage('Test')).rejects.toThrow('Failed to send message');
      });

      expect(result.current.error).toEqual(error);
      // Optimistic message should be removed
      expect(result.current.messages).toHaveLength(0);
    });

    it('prevents sending empty messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.sendMessage('');
      });

      expect(mockClient.sendText).not.toHaveBeenCalled();
      expect(result.current.messages).toHaveLength(0);
    });

    it('trims whitespace from messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.sendMessage('  Hello World  ');
      });

      expect(mockClient.sendText).toHaveBeenCalledWith('Hello World');
      expect(result.current.messages[0].content).toBe('Hello World');
    });
  });

  describe('Message Reception', () => {
    it('handles incoming user message', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const message: ChatMessage = {
        id: 'msg-001',
        role: 'user' as ChatRole,
        content: 'User message',
        timestamp: new Date().toISOString(),
        metadata: {}
      };

      act(() => {
        eventHandlers.get('message')?.forEach(handler => handler(message));
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0]).toEqual(message);
      });
    });

    it('handles incoming assistant message', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const message: ChatMessage = {
        id: 'msg-002',
        role: 'assistant' as ChatRole,
        content: 'AI response',
        timestamp: new Date().toISOString(),
        metadata: {}
      };

      act(() => {
        eventHandlers.get('message')?.forEach(handler => handler(message));
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0].role).toBe('assistant');
      });
    });

    it('handles system message', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const message: ChatMessage = {
        id: 'msg-003',
        role: 'system' as ChatRole,
        content: 'System notification',
        timestamp: new Date().toISOString(),
        metadata: { type: 'notification' }
      };

      act(() => {
        eventHandlers.get('message')?.forEach(handler => handler(message));
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0].role).toBe('system');
      });
    });

    it('maintains message order', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const messages = [
        { id: '1', role: 'user' as ChatRole, content: 'First', timestamp: '2024-01-01T10:00:00Z', metadata: {} },
        { id: '2', role: 'assistant' as ChatRole, content: 'Second', timestamp: '2024-01-01T10:00:01Z', metadata: {} },
        { id: '3', role: 'user' as ChatRole, content: 'Third', timestamp: '2024-01-01T10:00:02Z', metadata: {} }
      ];

      act(() => {
        messages.forEach(msg => {
          eventHandlers.get('message')?.forEach(handler => handler(msg));
        });
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(3);
        expect(result.current.messages[0].content).toBe('First');
        expect(result.current.messages[2].content).toBe('Third');
      });
    });

    it('prevents duplicate messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const message: ChatMessage = {
        id: 'duplicate-msg',
        role: 'user' as ChatRole,
        content: 'Duplicate test',
        timestamp: new Date().toISOString(),
        metadata: {}
      };

      act(() => {
        // Send same message twice
        eventHandlers.get('message')?.forEach(handler => handler(message));
        eventHandlers.get('message')?.forEach(handler => handler(message));
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
      });
    });
  });

  describe('Message Management', () => {
    it('clears all messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Add some messages
      await act(async () => {
        await result.current.sendMessage('Message 1');
        await result.current.sendMessage('Message 2');
      });

      expect(result.current.messages).toHaveLength(2);

      act(() => {
        result.current.clearMessages();
      });

      expect(result.current.messages).toHaveLength(0);
    });

    it('deletes specific message', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Add messages
      await act(async () => {
        await result.current.sendMessage('Message 1');
        await result.current.sendMessage('Message 2');
      });

      const messageId = result.current.messages[0].id;

      act(() => {
        result.current.deleteMessage(messageId);
      });

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].content).toBe('Message 2');
    });

    it('edits message content', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.sendMessage('Original message');
      });

      const messageId = result.current.messages[0].id;

      act(() => {
        result.current.editMessage(messageId, 'Edited message');
      });

      expect(result.current.messages[0].content).toBe('Edited message');
      expect(result.current.messages[0].metadata?.edited).toBe(true);
      expect(result.current.messages[0].metadata?.editedAt).toBeDefined();
    });

    it('retries failed message', async () => {
      mockClient.sendText
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ messageId: 'retry-success' });

      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // First attempt fails
      await act(async () => {
        try {
          await result.current.sendMessage('Retry test');
        } catch (e) {
          // Expected to fail
        }
      });

      expect(result.current.error).toBeDefined();

      // Retry
      await act(async () => {
        await result.current.retryLastMessage();
      });

      expect(result.current.error).toBeNull();
      expect(result.current.messages).toHaveLength(1);
      expect(mockClient.sendText).toHaveBeenCalledTimes(2);
    });
  });

  describe('Typing Indicators', () => {
    it('handles typing start event', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        eventHandlers.get('typing_start')?.forEach(handler => 
          handler({ userId: 'user-1', userName: 'Assistant' })
        );
      });

      await waitFor(() => {
        expect(result.current.isTyping).toBe(true);
        expect(result.current.typingUsers).toContain('Assistant');
      });
    });

    it('handles typing stop event', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start typing
      act(() => {
        eventHandlers.get('typing_start')?.forEach(handler => 
          handler({ userId: 'user-1', userName: 'Assistant' })
        );
      });

      expect(result.current.isTyping).toBe(true);

      // Stop typing
      act(() => {
        eventHandlers.get('typing_stop')?.forEach(handler => 
          handler({ userId: 'user-1' })
        );
      });

      await waitFor(() => {
        expect(result.current.isTyping).toBe(false);
        expect(result.current.typingUsers).toHaveLength(0);
      });
    });

    it('handles multiple users typing', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        eventHandlers.get('typing_start')?.forEach(handler => {
          handler({ userId: 'user-1', userName: 'User 1' });
        });
        eventHandlers.get('typing_start')?.forEach(handler => {
          handler({ userId: 'user-2', userName: 'User 2' });
        });
      });

      await waitFor(() => {
        expect(result.current.typingUsers).toHaveLength(2);
        expect(result.current.typingUsers).toContain('User 1');
        expect(result.current.typingUsers).toContain('User 2');
      });
    });

    it('sends typing indicator when user types', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        result.current.setTyping(true);
      });

      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'typing_start'
      });

      act(() => {
        result.current.setTyping(false);
      });

      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'typing_stop'
      });
    });
  });

  describe('Session Management', () => {
    it('handles session change event', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const sessionData = {
        sessionId: 'session-123',
        metadata: {
          startTime: new Date().toISOString(),
          agent: 'AI Assistant'
        }
      };

      act(() => {
        eventHandlers.get('session_changed')?.forEach(handler => handler(sessionData));
      });

      await waitFor(() => {
        expect(result.current.sessionId).toBe('session-123');
        expect(result.current.sessionMetadata).toEqual(sessionData.metadata);
      });
    });

    it('clears messages on session change', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Add messages
      await act(async () => {
        await result.current.sendMessage('Old session message');
      });

      expect(result.current.messages).toHaveLength(1);

      // Change session
      act(() => {
        eventHandlers.get('session_changed')?.forEach(handler => 
          handler({ sessionId: 'new-session', metadata: {} })
        );
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(0);
        expect(result.current.sessionId).toBe('new-session');
      });
    });

    it('loads message history for session', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const history = [
        { id: '1', role: 'user' as ChatRole, content: 'Historical 1', timestamp: '2024-01-01T10:00:00Z', metadata: {} },
        { id: '2', role: 'assistant' as ChatRole, content: 'Historical 2', timestamp: '2024-01-01T10:00:01Z', metadata: {} }
      ];

      act(() => {
        eventHandlers.get('message_history')?.forEach(handler => 
          handler({ messages: history })
        );
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(2);
        expect(result.current.messages[0].content).toBe('Historical 1');
      });
    });
  });

  describe('Pagination', () => {
    it('loads more messages', async () => {
      mockClient.loadMoreMessages = vi.fn().mockResolvedValue({
        messages: [
          { id: 'old-1', role: 'user', content: 'Older message', timestamp: '2024-01-01T09:00:00Z', metadata: {} }
        ],
        hasMore: true
      });

      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.loadMore();
      });

      expect(mockClient.loadMoreMessages).toHaveBeenCalled();
      expect(result.current.hasMore).toBe(true);
      expect(result.current.messages).toHaveLength(1);
    });

    it('handles loading state during pagination', async () => {
      mockClient.loadMoreMessages = vi.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const loadPromise = act(async () => {
        await result.current.loadMore();
      });

      expect(result.current.isLoading).toBe(true);

      await loadPromise;

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('handles message event errors', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const error = new Error('Message processing error');

      act(() => {
        eventHandlers.get('error')?.forEach(handler => 
          handler({ type: 'message_error', error })
        );
      });

      await waitFor(() => {
        expect(result.current.error).toEqual(error);
      });
    });

    it('clears error on successful action', async () => {
      mockClient.sendText.mockRejectedValueOnce(new Error('First error'));

      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Cause an error
      await act(async () => {
        try {
          await result.current.sendMessage('Error test');
        } catch (e) {
          // Expected
        }
      });

      expect(result.current.error).toBeDefined();

      // Successful action should clear error
      mockClient.sendText.mockResolvedValueOnce({ messageId: 'success' });
      
      await act(async () => {
        await result.current.sendMessage('Success test');
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('message', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('typing_start', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('typing_stop', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('session_changed', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('message_history', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('error', expect.any(Function));
    });

    it('cancels pending operations on unmount', async () => {
      const abortSpy = vi.spyOn(AbortController.prototype, 'abort');

      const { result, unmount } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start an async operation
      const sendPromise = result.current.sendMessage('Test');

      unmount();

      expect(abortSpy).toHaveBeenCalled();
      
      await expect(sendPromise).rejects.toThrow();
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result } = renderHook(() => useChat(), {
        wrapper: StrictModeWrapper
      });

      await act(async () => {
        await result.current.sendMessage('StrictMode test');
      });

      expect(result.current.messages).toHaveLength(1);
      expect(mockClient.sendText).toHaveBeenCalledTimes(1);
    });
  });

  describe('Message Filtering and Search', () => {
    it('filters messages by role', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Add mixed messages
      const messages = [
        { id: '1', role: 'user' as ChatRole, content: 'User 1', timestamp: '2024-01-01T10:00:00Z', metadata: {} },
        { id: '2', role: 'assistant' as ChatRole, content: 'Assistant 1', timestamp: '2024-01-01T10:00:01Z', metadata: {} },
        { id: '3', role: 'user' as ChatRole, content: 'User 2', timestamp: '2024-01-01T10:00:02Z', metadata: {} }
      ];

      act(() => {
        messages.forEach(msg => {
          eventHandlers.get('message')?.forEach(handler => handler(msg));
        });
      });

      const userMessages = result.current.getMessagesByRole('user');
      expect(userMessages).toHaveLength(2);
      expect(userMessages[0].content).toBe('User 1');
    });

    it('searches messages by content', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.sendMessage('Hello world');
        await result.current.sendMessage('Goodbye world');
        await result.current.sendMessage('Something else');
      });

      const searchResults = result.current.searchMessages('world');
      expect(searchResults).toHaveLength(2);
    });
  });

  describe('Edge Cases', () => {
    it('handles very long messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const longMessage = 'a'.repeat(10000);
      
      await act(async () => {
        await result.current.sendMessage(longMessage);
      });

      expect(mockClient.sendText).toHaveBeenCalledWith(longMessage);
      expect(result.current.messages[0].content).toHaveLength(10000);
    });

    it('handles rapid message sending', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await Promise.all([
          result.current.sendMessage('Message 1'),
          result.current.sendMessage('Message 2'),
          result.current.sendMessage('Message 3')
        ]);
      });

      expect(result.current.messages).toHaveLength(3);
      expect(mockClient.sendText).toHaveBeenCalledTimes(3);
    });

    it('handles special characters in messages', async () => {
      const { result } = renderHook(() => useChat(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const specialMessage = '🎉 Hello <script>alert("XSS")</script> & "quotes" \'apostrophe\'';
      
      await act(async () => {
        await result.current.sendMessage(specialMessage);
      });

      expect(mockClient.sendText).toHaveBeenCalledWith(specialMessage);
      expect(result.current.messages[0].content).toBe(specialMessage);
    });
  });
});