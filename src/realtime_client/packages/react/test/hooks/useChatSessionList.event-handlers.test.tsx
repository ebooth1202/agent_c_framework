/**
 * Event handler tests for useChatSessionList hook
 * Tests real-time event handling without full provider setup
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatSessionList } from '../../src/hooks/useChatSessionList';
import type {
  ChatSessionIndexEntry,
  ChatSession,
  AgentConfiguration
} from '@agentc/realtime-core';

// Mock the provider hook to return our mock client
const mockClient = {
  connect: vi.fn().mockResolvedValue(undefined),
  disconnect: vi.fn(),
  isConnected: vi.fn().mockReturnValue(true),
  sendEvent: vi.fn(),
  resumeChatSession: vi.fn(),
  getSessionManager: vi.fn().mockReturnValue({
    getCurrentSession: vi.fn().mockReturnValue(null)
  }),
  on: vi.fn(),
  off: vi.fn(),
  once: vi.fn(),
  emit: vi.fn(),
  destroy: vi.fn()
};

vi.mock('../../src/providers/AgentCContext', () => ({
  useRealtimeClientSafe: () => mockClient,
  useAgentCContext: () => ({
    client: mockClient,
    isInitializing: false,
    error: null,
    initialization: {
      isInitialized: true,
      receivedEvents: new Set(),
      user: null,
      agents: [],
      avatars: [],
      voices: [],
      toolsets: [],
      currentSession: null
    }
  })
}));

describe('useChatSessionList Event Handlers', () => {
  let eventHandlers: Map<string, Function>;
  
  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    // Capture event handlers when on() is called
    mockClient.on.mockImplementation((event: string, handler: Function) => {
      eventHandlers.set(event, handler);
    });
    
    mockClient.off.mockImplementation((event: string) => {
      eventHandlers.delete(event);
    });
    
    // Helper to emit events by calling the registered handler
    mockClient.emit.mockImplementation((event: string, data: any) => {
      const handler = eventHandlers.get(event);
      if (handler) {
        handler(data);
      }
    });
  });
  
  afterEach(() => {
    vi.clearAllMocks();
  });
  
  const emitEvent = (eventName: string, data: any) => {
    const handler = eventHandlers.get(eventName);
    if (handler) {
      handler(data);
    }
  };
  
  describe('ChatSessionChangedEvent', () => {
    it('should update session with new data including updated_at timestamp', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Set initial sessions
      const initialSession: ChatSessionIndexEntry = {
        session_id: 'session-1',
        session_name: 'Old Name',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1',
        agent_key: 'agent-1',
        agent_name: 'Agent 1'
      };
      
      // Simulate initial load
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: [initialSession],
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      expect(result.current.sessions).toHaveLength(1);
      expect(result.current.sessions[0].session_name).toBe('Old Name');
      
      // Emit chat_session_changed event
      const updatedSession: ChatSession = {
        session_id: 'session-1',
        session_name: 'Updated Name',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z', // New timestamp
        user_id: 'user-1',
        token_count: 100,
        context_window_size: 1000,
        deleted_at: null,
        metadata: {},
        messages: [],
        agent_config: {
          key: 'agent-1',
          name: 'Agent 1'
        } as AgentConfiguration
      };
      
      act(() => {
        emitEvent('chat_session_changed', {
          type: 'chat_session_changed',
          chat_session: updatedSession
        });
      });
      
      // Verify session was updated
      expect(result.current.sessions[0].session_name).toBe('Updated Name');
      expect(result.current.sessions[0].updated_at).toBe('2024-01-02T00:00:00Z');
      expect(result.current.currentSessionId).toBe('session-1');
    });
    
    it('should add new session if not in list', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Start with empty list
      expect(result.current.sessions).toHaveLength(0);
      
      // Emit chat_session_changed for new session
      const newSession: ChatSession = {
        session_id: 'new-session',
        session_name: 'New Session',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1',
        token_count: 0,
        context_window_size: 1000,
        deleted_at: null,
        metadata: {},
        messages: [],
        agent_config: {
          key: 'agent-1',
          name: 'Agent 1'
        } as AgentConfiguration
      };
      
      act(() => {
        emitEvent('chat_session_changed', {
          type: 'chat_session_changed',
          chat_session: newSession
        });
      });
      
      // Verify session was added
      expect(result.current.sessions).toHaveLength(1);
      expect(result.current.sessions[0].session_id).toBe('new-session');
    });
  });
  
  describe('ChatSessionNameChangedEvent', () => {
    it('should update session name using provided session_id', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Set initial sessions
      const sessions: ChatSessionIndexEntry[] = [
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
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: sessions,
            total_sessions: 2,
            offset: 0
          }
        });
      });
      
      // Emit name change event with specific session_id
      act(() => {
        emitEvent('chat_session_name_changed', {
          type: 'chat_session_name_changed',
          session_name: 'Renamed Session',
          session_id: 'session-2'
        });
      });
      
      // Verify correct session was updated
      expect(result.current.sessions.find(s => s.session_id === 'session-1')?.session_name).toBe('Session 1');
      expect(result.current.sessions.find(s => s.session_id === 'session-2')?.session_name).toBe('Renamed Session');
    });
    
    it('should use current session_id if not provided in event', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Set initial session
      const session: ChatSessionIndexEntry = {
        session_id: 'current-session',
        session_name: 'Current Session',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      };
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: [session],
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Set current session
      act(() => {
        result.current.selectSession('current-session');
      });
      
      // Emit name change without session_id
      act(() => {
        emitEvent('chat_session_name_changed', {
          type: 'chat_session_name_changed',
          session_name: 'Renamed Current'
        });
      });
      
      // Verify current session was updated
      expect(result.current.sessions[0].session_name).toBe('Renamed Current');
    });
  });
  
  describe('ChatSessionAddedEvent', () => {
    it('should add new session to the beginning of the list', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Set initial session
      const existingSession: ChatSessionIndexEntry = {
        session_id: 'existing',
        session_name: 'Existing',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      };
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: [existingSession],
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Emit session added event
      const newSession: ChatSessionIndexEntry = {
        session_id: 'new-session',
        session_name: 'New Session',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user_id: 'user-1'
      };
      
      act(() => {
        emitEvent('chat_session_added', {
          type: 'chat_session_added',
          chat_session: newSession
        });
      });
      
      // Verify new session is at the beginning
      expect(result.current.sessions).toHaveLength(2);
      expect(result.current.sessions[0].session_id).toBe('new-session');
      expect(result.current.sessions[1].session_id).toBe('existing');
      expect(result.current.totalCount).toBe(2);
    });
    
    it('should not add duplicate sessions', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const session: ChatSessionIndexEntry = {
        session_id: 'session-1',
        session_name: 'Session 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      };
      
      // Add initial session
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: [session],
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Try to add same session again
      act(() => {
        emitEvent('chat_session_added', {
          type: 'chat_session_added',
          chat_session: session
        });
      });
      
      // Should still have only one session
      expect(result.current.sessions).toHaveLength(1);
    });
  });
  
  describe('ChatSessionDeletedEvent', () => {
    it('should remove session from list using provided session_id', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Set initial sessions
      const sessions: ChatSessionIndexEntry[] = [
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
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: sessions,
            total_sessions: 2,
            offset: 0
          }
        });
      });
      
      // Delete session-1
      act(() => {
        emitEvent('chat_session_deleted', {
          type: 'chat_session_deleted',
          session_id: 'session-1'
        });
      });
      
      // Verify session was removed
      expect(result.current.sessions).toHaveLength(1);
      expect(result.current.sessions[0].session_id).toBe('session-2');
      expect(result.current.totalCount).toBe(1);
    });
    
    it('should clear currentSessionId if deleted session was current', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const session: ChatSessionIndexEntry = {
        session_id: 'current-session',
        session_name: 'Current',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        user_id: 'user-1'
      };
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: [session],
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Select the session
      act(() => {
        result.current.selectSession('current-session');
      });
      
      expect(result.current.currentSessionId).toBe('current-session');
      
      // Delete current session
      act(() => {
        emitEvent('chat_session_deleted', {
          type: 'chat_session_deleted',
          session_id: 'current-session'
        });
      });
      
      // Current session should be cleared
      expect(result.current.currentSessionId).toBeNull();
      expect(result.current.sessions).toHaveLength(0);
    });
  });
  
  describe('Connection Events', () => {
    it('should load sessions on connected event if autoLoad is true', async () => {
      // Create the hook with autoLoad true but start disconnected
      mockClient.isConnected.mockReturnValue(false);
      const { result } = renderHook(() => useChatSessionList({ autoLoad: true }));
      
      // Now simulate connection
      mockClient.isConnected.mockReturnValue(true);
      
      // Clear previous calls to isolate the connected event
      mockClient.sendEvent.mockClear();
      
      // Emit connected event
      act(() => {
        emitEvent('connected', {});
      });
      
      // Should have called sendEvent to load sessions
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'get_user_sessions',
        offset: 0,
        limit: 50
      });
    });
    
    it('should refresh sessions on reconnected event', async () => {
      vi.useFakeTimers();
      
      const { result } = renderHook(() => useChatSessionList({ autoLoad: true }));
      
      // Add some initial sessions
      const sessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'session-1',
          session_name: 'Session 1',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: sessions,
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Clear sendEvent calls
      mockClient.sendEvent.mockClear();
      
      // Emit reconnected event
      act(() => {
        emitEvent('reconnected', {});
      });
      
      // Fast-forward timers (500ms delay in reconnected handler)
      act(() => {
        vi.advanceTimersByTime(500);
      });
      
      // Should have called sendEvent to refresh sessions
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'get_user_sessions',
        offset: 0,
        limit: 50
      });
      
      vi.useRealTimers();
    });
    
    it('should handle disconnected event properly', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Start a load operation
      act(() => {
        result.current.loadMore();
      });
      
      expect(result.current.isPaginationLoading).toBe(true);
      
      // Emit disconnected event
      act(() => {
        emitEvent('disconnected', {});
      });
      
      // Loading states should be cleared
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isPaginationLoading).toBe(false);
    });
  });
  
  describe('GetUserSessionsResponse', () => {
    it('should handle paginated responses correctly', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false, pageSize: 2 }));
      
      // First page
      const firstPage: ChatSessionIndexEntry[] = [
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
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: firstPage,
            total_sessions: 4,
            offset: 0
          }
        });
      });
      
      expect(result.current.sessions).toHaveLength(2);
      expect(result.current.hasMore).toBe(true);
      expect(result.current.totalCount).toBe(4);
      
      // Load more
      act(() => {
        result.current.loadMore();
      });
      
      // Second page
      const secondPage: ChatSessionIndexEntry[] = [
        {
          session_id: 'session-3',
          session_name: 'Session 3',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        },
        {
          session_id: 'session-4',
          session_name: 'Session 4',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: secondPage,
            total_sessions: 4,
            offset: 2
          }
        });
      });
      
      // Should have all 4 sessions
      expect(result.current.sessions).toHaveLength(4);
      expect(result.current.hasMore).toBe(false);
    });
  });
  
  describe('Session Sorting', () => {
    it('should maintain sort order by updated_at descending', async () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Add sessions with different updated_at times - note they are not sorted initially
      const sessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'old',
          session_name: 'Old Session',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          user_id: 'user-1'
        },
        {
          session_id: 'newest',
          session_name: 'Newest Session',
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-05T00:00:00Z',
          user_id: 'user-1'
        },
        {
          session_id: 'newer',
          session_name: 'Newer Session',
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-03T00:00:00Z',
          user_id: 'user-1'
        }
      ];
      
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: sessions,
            total_sessions: 3,
            offset: 0
          }
        });
      });
      
      // The sessions should be in the order they were received (no automatic sorting in initial load)
      expect(result.current.sessions[0].session_id).toBe('old');
      expect(result.current.sessions[1].session_id).toBe('newest');
      expect(result.current.sessions[2].session_id).toBe('newer');
      
      // Update the old session to make it the newest
      const updatedOld: ChatSession = {
        session_id: 'old',
        session_name: 'Old Session Updated',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-06T00:00:00Z', // Now the newest
        user_id: 'user-1',
        token_count: 0,
        context_window_size: 1000,
        deleted_at: null,
        metadata: {},
        messages: [],
        agent_config: {} as AgentConfiguration
      };
      
      act(() => {
        emitEvent('chat_session_changed', {
          type: 'chat_session_changed',
          chat_session: updatedOld
        });
      });
      
      // After update, sessions should be re-sorted with 'old' first
      expect(result.current.sessions[0].session_id).toBe('old');
      expect(result.current.sessions[0].session_name).toBe('Old Session Updated');
      expect(result.current.sessions[1].session_id).toBe('newest');
      expect(result.current.sessions[2].session_id).toBe('newer');
    });
  });
});