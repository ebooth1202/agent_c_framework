/**
 * Tests for useChatSessionList hook
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChatSessionList } from '../../src/hooks/useChatSessionList';
import { AgentCProvider } from '../../src/providers/AgentCProvider';
import { RealtimeClient, ConnectionState } from '@agentc/realtime-core';
import type { ChatSessionIndexEntry } from '@agentc/realtime-core';
import React from 'react';

// Mock client for testing
const createMockClient = () => {
  const listeners = new Map<string, Set<Function>>();
  
  const mockClient = {
    isConnected: vi.fn(() => true),
    getConnectionState: vi.fn(() => ConnectionState.CONNECTED),
    connect: vi.fn(),
    disconnect: vi.fn(),
    sendEvent: vi.fn(),
    resumeChatSession: vi.fn(),
    getSessionManager: vi.fn(() => ({
      getCurrentSession: vi.fn(() => null)
    })),
    on: vi.fn((event: string, handler: Function) => {
      if (!listeners.has(event)) {
        listeners.set(event, new Set());
      }
      listeners.get(event)!.add(handler);
    }),
    off: vi.fn((event: string, handler: Function) => {
      listeners.get(event)?.delete(handler);
    }),
    emit: (event: string, data: any) => {
      listeners.get(event)?.forEach(handler => handler(data));
    },
    destroy: vi.fn()
  };
  
  return mockClient;
};

describe('useChatSessionList', () => {
  let mockClient: ReturnType<typeof createMockClient>;
  
  beforeEach(() => {
    mockClient = createMockClient();
  });
  
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AgentCProvider 
      client={mockClient as any}
      apiUrl="https://test.example.com"
      authToken="test-token"
    >
      {children}
    </AgentCProvider>
  );
  
  it('should initialize with default state', () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    expect(result.current.sessions).toEqual([]);
    expect(result.current.filteredSessions).toEqual([]);
    expect(result.current.searchQuery).toBe('');
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isPaginationLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.hasMore).toBe(true);
    expect(result.current.totalCount).toBe(0);
    expect(result.current.currentSessionId).toBeNull();
  });
  
  it('should load sessions on mount when autoLoad is true', async () => {
    const { result } = renderHook(
      () => useChatSessionList({ autoLoad: true }),
      { wrapper }
    );
    
    // Wait for effect to run
    await waitFor(() => {
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'get_user_sessions',
        offset: 0,
        limit: 50
      });
    });
  });
  
  it('should handle session response event', async () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    const mockSessions: ChatSessionIndexEntry[] = [
      {
        session_id: 'session-1',
        session_name: 'Test Session 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1',
        agent_key: 'agent-1',
        agent_name: 'Test Agent'
      },
      {
        session_id: 'session-2',
        session_name: 'Test Session 2',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user_id: 'user-1',
        agent_key: 'agent-2',
        agent_name: 'Another Agent'
      }
    ];
    
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: mockSessions,
          total_sessions: 2,
          offset: 0
        }
      });
    });
    
    expect(result.current.sessions).toEqual(mockSessions);
    expect(result.current.filteredSessions).toEqual(mockSessions);
    expect(result.current.totalCount).toBe(2);
    expect(result.current.hasMore).toBe(false);
  });
  
  it('should filter sessions based on search query', async () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    const mockSessions: ChatSessionIndexEntry[] = [
      {
        session_id: 'session-1',
        session_name: 'Customer Support',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      },
      {
        session_id: 'session-2',
        session_name: 'Technical Help',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user_id: 'user-1'
      }
    ];
    
    // Load sessions first
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: mockSessions,
          total_sessions: 2,
          offset: 0
        }
      });
    });
    
    // Search for "support"
    act(() => {
      result.current.searchSessions('support');
    });
    
    // Wait for debounce
    await waitFor(() => {
      expect(result.current.searchQuery).toBe('support');
    }, { timeout: 500 });
    
    await waitFor(() => {
      expect(result.current.filteredSessions).toHaveLength(1);
      expect(result.current.filteredSessions[0]?.session_name).toBe('Customer Support');
    });
  });
  
  it('should select a session', () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    act(() => {
      result.current.selectSession('session-123');
    });
    
    expect(mockClient.resumeChatSession).toHaveBeenCalledWith('session-123');
    expect(result.current.currentSessionId).toBe('session-123');
  });
  
  it('should handle delete with optimistic update', async () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    const mockSessions: ChatSessionIndexEntry[] = [
      {
        session_id: 'session-1',
        session_name: 'Session to Keep',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      },
      {
        session_id: 'session-2',
        session_name: 'Session to Delete',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user_id: 'user-1'
      }
    ];
    
    // Load sessions
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: mockSessions,
          total_sessions: 2,
          offset: 0
        }
      });
    });
    
    expect(result.current.sessions).toHaveLength(2);
    
    // Delete a session
    await act(async () => {
      await result.current.deleteSession('session-2');
    });
    
    // Should be removed optimistically
    expect(result.current.sessions).toHaveLength(1);
    expect(result.current.sessions[0]?.session_id).toBe('session-1');
    
    // Should send delete event
    expect(mockClient.sendEvent).toHaveBeenCalledWith({
      type: 'delete_chat_session',
      session_id: 'session-2'
    });
  });
  
  it('should handle pagination', async () => {
    const { result } = renderHook(
      () => useChatSessionList({ pageSize: 2 }),
      { wrapper }
    );
    
    const firstBatch: ChatSessionIndexEntry[] = [
      {
        session_id: 'session-1',
        session_name: 'Session 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      },
      {
        session_id: 'session-2',
        session_name: 'Session 2',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user_id: 'user-1'
      }
    ];
    
    // First page
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: firstBatch,
          total_sessions: 4,
          offset: 0
        }
      });
    });
    
    expect(result.current.sessions).toHaveLength(2);
    expect(result.current.hasMore).toBe(true);
    
    // Load more
    act(() => {
      result.current.loadMore();
    });
    
    expect(mockClient.sendEvent).toHaveBeenCalledWith({
      type: 'get_user_sessions',
      offset: 2,
      limit: 2
    });
    
    const secondBatch: ChatSessionIndexEntry[] = [
      {
        session_id: 'session-3',
        session_name: 'Session 3',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
        user_id: 'user-1'
      },
      {
        session_id: 'session-4',
        session_name: 'Session 4',
        created_at: '2024-01-04T00:00:00Z',
        updated_at: '2024-01-04T00:00:00Z',
        user_id: 'user-1'
      }
    ];
    
    // Second page
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: secondBatch,
          total_sessions: 4,
          offset: 2
        }
      });
    });
    
    expect(result.current.sessions).toHaveLength(4);
    expect(result.current.hasMore).toBe(false);
  });
  
  it('should handle refresh', () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    // Add some sessions first
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: [{
            session_id: 'session-1',
            session_name: 'Test',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            user_id: 'user-1'
          }],
          total_sessions: 1,
          offset: 0
        }
      });
    });
    
    expect(result.current.sessions).toHaveLength(1);
    
    // Refresh
    act(() => {
      result.current.refresh();
    });
    
    // Should clear sessions and reload
    expect(result.current.sessions).toHaveLength(0);
    expect(mockClient.sendEvent).toHaveBeenCalledWith({
      type: 'get_user_sessions',
      offset: 0,
      limit: 50
    });
  });
  
  it('should handle connection state changes', () => {
    mockClient.isConnected = vi.fn(() => false);
    
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    act(() => {
      result.current.loadMore();
    });
    
    expect(result.current.error?.message).toBe('Not connected to server');
  });
  
  it('should handle session name change event', () => {
    const { result } = renderHook(() => useChatSessionList(), { wrapper });
    
    // Set current session
    act(() => {
      result.current.selectSession('session-1');
    });
    
    // Load a session
    act(() => {
      mockClient.emit('get_user_sessions_response', {
        sessions: {
          chat_sessions: [{
            session_id: 'session-1',
            session_name: 'Original Name',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            user_id: 'user-1'
          }],
          total_sessions: 1,
          offset: 0
        }
      });
    });
    
    // Emit name change event
    act(() => {
      mockClient.emit('chat_session_name_changed', {
        session_name: 'New Name'
      });
    });
    
    expect(result.current.sessions[0]?.session_name).toBe('New Name');
  });
});