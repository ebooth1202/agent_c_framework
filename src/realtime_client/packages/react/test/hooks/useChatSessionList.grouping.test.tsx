/**
 * Tests for useChatSessionList date parsing and grouping logic
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatSessionList } from '../../src/hooks/useChatSessionList';
import type { ChatSessionIndexEntry } from '@agentc/realtime-core';

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
}));

describe('useChatSessionList Date Grouping', () => {
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
  });
  
  const emitEvent = (eventName: string, data: any) => {
    const handler = eventHandlers.get(eventName);
    if (handler) {
      handler(data);
    }
  };
  
  describe('Date Parsing with Microseconds', () => {
    it('should correctly parse dates with microseconds format', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      // Create test sessions with various date formats
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterday = new Date(today.getTime() - (24 * 60 * 60 * 1000));
      const twoWeeksAgo = new Date(today.getTime() - (15 * 24 * 60 * 60 * 1000));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'today-1',
          session_name: 'Today Session',
          created_at: today.toISOString(),
          updated_at: `${today.toISOString().slice(0, 19)}.515250`, // Microseconds format
          user_id: 'user-1'
        },
        {
          session_id: 'yesterday-1',
          session_name: 'Yesterday Session',
          created_at: yesterday.toISOString(),
          updated_at: `${yesterday.toISOString().slice(0, 19)}.123456`, // Microseconds format
          user_id: 'user-1'
        },
        {
          session_id: 'old-1',
          session_name: 'Old Session',
          created_at: twoWeeksAgo.toISOString(),
          updated_at: `${twoWeeksAgo.toISOString().slice(0, 19)}.999999`, // Microseconds format
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 3,
            offset: 0
          }
        });
      });
      
      // Check grouping
      expect(result.current.groupedSessions.today).toHaveLength(1);
      expect(result.current.groupedSessions.recent).toHaveLength(1);
      expect(result.current.groupedSessions.past).toHaveLength(1);
      
      expect(result.current.groupedSessions.today[0].session_id).toBe('today-1');
      expect(result.current.groupedSessions.recent[0].session_id).toBe('yesterday-1');
      expect(result.current.groupedSessions.past[0].session_id).toBe('old-1');
    });
    
    it('should handle server date format like 2025-09-06T20:16:26.515250', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'future-1',
          session_name: 'Future Date Session',
          created_at: '2025-09-06T20:16:26.515250',
          updated_at: '2025-09-06T20:16:26.515250',
          user_id: 'user-1'
        },
        {
          session_id: 'normal-1',
          session_name: 'Normal Session',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 2,
            offset: 0
          }
        });
      });
      
      // Future dates should be placed in 'recent' group
      expect(result.current.groupedSessions.recent).toContainEqual(
        expect.objectContaining({ session_id: 'future-1' })
      );
    });
  });
  
  describe('Session Grouping', () => {
    it('should group sessions into today, recent, and past', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const fiveHoursAgo = new Date(now.getTime() - (5 * 60 * 60 * 1000));
      const threeDaysAgo = new Date(today.getTime() - (3 * 24 * 60 * 60 * 1000));
      const oneWeekAgo = new Date(today.getTime() - (7 * 24 * 60 * 60 * 1000));
      const threeWeeksAgo = new Date(today.getTime() - (21 * 24 * 60 * 60 * 1000));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'today-morning',
          session_name: 'Morning Session',
          created_at: today.toISOString(),
          updated_at: today.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'today-recent',
          session_name: '5 Hours Ago',
          created_at: fiveHoursAgo.toISOString(),
          updated_at: fiveHoursAgo.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'recent-1',
          session_name: '3 Days Ago',
          created_at: threeDaysAgo.toISOString(),
          updated_at: threeDaysAgo.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'recent-2',
          session_name: 'Week Ago',
          created_at: oneWeekAgo.toISOString(),
          updated_at: oneWeekAgo.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'past-1',
          session_name: 'Three Weeks Ago',
          created_at: threeWeeksAgo.toISOString(),
          updated_at: threeWeeksAgo.toISOString(),
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 5,
            offset: 0
          }
        });
      });
      
      // Verify grouping
      expect(result.current.groupedSessions.today).toHaveLength(2);
      expect(result.current.groupedSessions.recent).toHaveLength(2);
      expect(result.current.groupedSessions.past).toHaveLength(1);
      
      // Verify session IDs in correct groups
      const todayIds = result.current.groupedSessions.today.map(s => s.session_id);
      expect(todayIds).toContain('today-morning');
      expect(todayIds).toContain('today-recent');
      
      const recentIds = result.current.groupedSessions.recent.map(s => s.session_id);
      expect(recentIds).toContain('recent-1');
      expect(recentIds).toContain('recent-2');
      
      const pastIds = result.current.groupedSessions.past.map(s => s.session_id);
      expect(pastIds).toContain('past-1');
    });
    
    it('should provide sessionGroups with metadata', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterday = new Date(today.getTime() - (24 * 60 * 60 * 1000));
      const oneMonthAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'today-1',
          session_name: 'Today',
          created_at: today.toISOString(),
          updated_at: today.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'yesterday-1',
          session_name: 'Yesterday',
          created_at: yesterday.toISOString(),
          updated_at: yesterday.toISOString(),
          user_id: 'user-1'
        },
        {
          session_id: 'old-1',
          session_name: 'Old',
          created_at: oneMonthAgo.toISOString(),
          updated_at: oneMonthAgo.toISOString(),
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 3,
            offset: 0
          }
        });
      });
      
      // Check sessionGroups structure
      expect(result.current.sessionGroups).toHaveLength(3);
      
      const todayGroup = result.current.sessionGroups.find(g => g.group === 'today');
      expect(todayGroup).toMatchObject({
        group: 'today',
        label: 'Today',
        count: 1,
        sessions: expect.arrayContaining([
          expect.objectContaining({ session_id: 'today-1' })
        ])
      });
      
      const recentGroup = result.current.sessionGroups.find(g => g.group === 'recent');
      expect(recentGroup).toMatchObject({
        group: 'recent',
        label: 'Recent',
        count: 1,
        sessions: expect.arrayContaining([
          expect.objectContaining({ session_id: 'yesterday-1' })
        ])
      });
      
      const pastGroup = result.current.sessionGroups.find(g => g.group === 'past');
      expect(pastGroup).toMatchObject({
        group: 'past',
        label: 'Past Sessions',
        count: 1,
        sessions: expect.arrayContaining([
          expect.objectContaining({ session_id: 'old-1' })
        ])
      });
    });
    
    it('should only include groups with sessions', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'today-only',
          session_name: 'Today Only',
          created_at: today.toISOString(),
          updated_at: today.toISOString(),
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 1,
            offset: 0
          }
        });
      });
      
      // Should only have today group
      expect(result.current.sessionGroups).toHaveLength(1);
      expect(result.current.sessionGroups[0].group).toBe('today');
      
      // Other groups should be empty
      expect(result.current.groupedSessions.recent).toHaveLength(0);
      expect(result.current.groupedSessions.past).toHaveLength(0);
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle sessions with missing dates', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'no-dates',
          session_name: 'No Dates',
          created_at: null,
          updated_at: null,
          user_id: 'user-1'
        },
        {
          session_id: 'only-created',
          session_name: 'Only Created',
          created_at: new Date().toISOString(),
          updated_at: null,
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response
      act(() => {
        emitEvent('get_user_sessions_response', {
          sessions: {
            chat_sessions: testSessions,
            total_sessions: 2,
            offset: 0
          }
        });
      });
      
      // Sessions with null dates should go to 'past' (epoch 0)
      expect(result.current.groupedSessions.past).toContainEqual(
        expect.objectContaining({ session_id: 'no-dates' })
      );
      
      // Session with only created_at should use that date
      expect(result.current.sessions).toContainEqual(
        expect.objectContaining({ session_id: 'only-created' })
      );
    });
    
    it('should handle invalid date strings', () => {
      const { result } = renderHook(() => useChatSessionList({ autoLoad: false }));
      
      const testSessions: ChatSessionIndexEntry[] = [
        {
          session_id: 'invalid-date',
          session_name: 'Invalid Date',
          created_at: 'not-a-date',
          updated_at: 'invalid',
          user_id: 'user-1'
        }
      ];
      
      // Emit sessions response - should not throw
      expect(() => {
        act(() => {
          emitEvent('get_user_sessions_response', {
            sessions: {
              chat_sessions: testSessions,
              total_sessions: 1,
              offset: 0
            }
          });
        });
      }).not.toThrow();
      
      // Invalid dates should go to 'past' group
      expect(result.current.groupedSessions.past).toContainEqual(
        expect.objectContaining({ session_id: 'invalid-date' })
      );
    });
  });
});