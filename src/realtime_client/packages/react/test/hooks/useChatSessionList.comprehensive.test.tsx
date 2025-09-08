/**
 * Comprehensive unit tests for useChatSessionList hook
 * Tests state management, event handlers, and all functionality
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useChatSessionList } from '../../src/hooks/useChatSessionList'
import { AgentCProvider } from '../../src/providers/AgentCProvider'
import type { ChatSessionIndexEntry, RealtimeClient } from '@agentc/realtime-core'
import React from 'react'

// Mock fetch globally
global.fetch = vi.fn()

// Helper to create mock client
function createMockClient(): Partial<RealtimeClient> {
  const listeners = new Map<string, Set<Function>>()
  
  return {
    isConnected: vi.fn(() => true),
    sendEvent: vi.fn(),
    on: vi.fn((event: string, handler: Function) => {
      if (!listeners.has(event)) {
        listeners.set(event, new Set())
      }
      listeners.get(event)!.add(handler)
      return () => listeners.get(event)?.delete(handler)
    }),
    off: vi.fn((event: string, handler: Function) => {
      listeners.get(event)?.delete(handler)
    }),
    emit: vi.fn((event: string, ...args: any[]) => {
      listeners.get(event)?.forEach(handler => handler(...args))
    }),
    getSessionManager: vi.fn(() => ({
      getCurrentSessionId: vi.fn(() => 'current-session-id')
    }))
  }
}

// Helper to create test sessions
function createTestSessions(count: number, options: {
  startDate?: Date,
  prefix?: string
} = {}): ChatSessionIndexEntry[] {
  const sessions: ChatSessionIndexEntry[] = []
  const startDate = options.startDate || new Date()
  const prefix = options.prefix || 'session'
  
  for (let i = 0; i < count; i++) {
    const hoursAgo = i * 2
    const date = new Date(startDate.getTime() - (hoursAgo * 60 * 60 * 1000))
    
    sessions.push({
      session_id: `${prefix}-${i}`,
      session_name: i % 3 === 0 ? null : `Test Session ${i}`,
      created_at: date.toISOString(),
      updated_at: date.toISOString(),
      user_id: 'test-user',
      agent_key: 'test-agent',
      agent_name: `Agent ${i % 3}`
    })
  }
  
  return sessions
}

// Wrapper component for tests
function createWrapper(client: Partial<RealtimeClient>) {
  return ({ children }: { children: React.ReactNode }) => (
    <AgentCProvider client={client as RealtimeClient}>
      {children}
    </AgentCProvider>
  )
}

describe('useChatSessionList Hook', () => {
  let mockClient: Partial<RealtimeClient>
  
  beforeEach(() => {
    mockClient = createMockClient()
    vi.clearAllMocks()
    
    // Default fetch mock
    ;(global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ sessions: [], total: 0, hasMore: false })
    })
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  describe('Initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      expect(result.current.sessions).toEqual([])
      expect(result.current.filteredSessions).toEqual([])
      expect(result.current.sessionGroups).toEqual([])
      expect(result.current.searchQuery).toBe('')
      expect(result.current.isLoading).toBe(false)
      expect(result.current.isPaginationLoading).toBe(false)
      expect(result.current.error).toBe(null)
      expect(result.current.hasMore).toBe(true)
      expect(result.current.totalCount).toBe(0)
    })
    
    it('should auto-load sessions when autoLoad is true', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions, 
          total: 5, 
          hasMore: false 
        })
      })
      
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: true }),
        { wrapper: createWrapper(mockClient) }
      )
      
      expect(result.current.isLoading).toBe(true)
      
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
        expect(result.current.sessions).toHaveLength(5)
      })
    })
    
    it('should not auto-load when autoLoad is false', async () => {
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: false }),
        { wrapper: createWrapper(mockClient) }
      )
      
      expect(result.current.isLoading).toBe(false)
      expect(global.fetch).not.toHaveBeenCalled()
    })
    
    it('should respect pageSize option', async () => {
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: true, pageSize: 25 }),
        { wrapper: createWrapper(mockClient) }
      )
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('pageSize=25'),
          expect.any(Object)
        )
      })
    })
  })
  
  describe('Session Loading', () => {
    it('should load sessions successfully', async () => {
      const sessions = createTestSessions(10)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions, 
          total: 10, 
          hasMore: false 
        })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(10)
        expect(result.current.totalCount).toBe(10)
        expect(result.current.hasMore).toBe(false)
      })
    })
    
    it('should handle load error gracefully', async () => {
      const error = new Error('Failed to load')
      ;(global.fetch as any).mockRejectedValue(error)
      
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: true }),
        { wrapper: createWrapper(mockClient) }
      )
      
      await waitFor(() => {
        expect(result.current.error).toEqual(error)
        expect(result.current.isLoading).toBe(false)
      })
    })
    
    it('should handle pagination correctly', async () => {
      // First page
      const firstPage = createTestSessions(50, { prefix: 'page1' })
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          sessions: firstPage, 
          total: 100, 
          hasMore: true 
        })
      })
      
      const { result } = renderHook(
        () => useChatSessionList({ pageSize: 50 }),
        { wrapper: createWrapper(mockClient) }
      )
      
      // Load first page
      await act(async () => {
        result.current.loadMore()
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(50)
        expect(result.current.hasMore).toBe(true)
      })
      
      // Second page
      const secondPage = createTestSessions(50, { prefix: 'page2' })
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          sessions: secondPage, 
          total: 100, 
          hasMore: false 
        })
      })
      
      // Load second page
      await act(async () => {
        result.current.loadMore()
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(100)
        expect(result.current.hasMore).toBe(false)
      })
    })
    
    it('should prevent duplicate load requests', async () => {
      const sessions = createTestSessions(10)
      ;(global.fetch as any).mockImplementation(() => 
        new Promise(resolve => {
          setTimeout(() => {
            resolve({
              ok: true,
              json: async () => ({ sessions, total: 10, hasMore: false })
            })
          }, 100)
        })
      )
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      // Try to load multiple times
      act(() => {
        result.current.loadMore()
        result.current.loadMore()
        result.current.loadMore()
      })
      
      // Should only make one request
      expect(global.fetch).toHaveBeenCalledTimes(1)
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(10)
      })
    })
  })
  
  describe('Search Functionality', () => {
    it('should filter sessions based on search query', async () => {
      const sessions = createTestSessions(10)
      sessions[0].session_name = 'Special Session'
      sessions[1].session_name = 'Another Special'
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 10, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      // Load sessions
      await act(async () => {
        result.current.loadMore()
      })
      
      // Search for "Special"
      act(() => {
        result.current.searchSessions('Special')
      })
      
      await waitFor(() => {
        expect(result.current.searchQuery).toBe('Special')
        expect(result.current.filteredSessions).toHaveLength(2)
        expect(result.current.filteredSessions[0].session_name).toContain('Special')
      })
    })
    
    it('should search case-insensitively', async () => {
      const sessions = createTestSessions(5)
      sessions[0].session_name = 'UPPERCASE'
      sessions[1].session_name = 'lowercase'
      sessions[2].session_name = 'MixedCase'
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Search with different cases
      act(() => {
        result.current.searchSessions('case')
      })
      
      await waitFor(() => {
        expect(result.current.filteredSessions).toHaveLength(3)
      })
    })
    
    it('should debounce search input', async () => {
      const sessions = createTestSessions(10)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 10, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList({ searchDebounceMs: 100 }),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      const filterSpy = vi.spyOn(result.current.filteredSessions, 'filter' as any)
      
      // Type rapidly
      act(() => {
        result.current.searchSessions('t')
        result.current.searchSessions('te')
        result.current.searchSessions('tes')
        result.current.searchSessions('test')
      })
      
      // Should update search query immediately
      expect(result.current.searchQuery).toBe('test')
      
      // But filtering should be debounced
      await waitFor(() => {
        // Filter should only run once after debounce
        expect(result.current.filteredSessions).toBeDefined()
      }, { timeout: 200 })
    })
    
    it('should clear search and show all sessions', async () => {
      const sessions = createTestSessions(10)
      sessions[0].session_name = 'Searchable'
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 10, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Search first
      act(() => {
        result.current.searchSessions('Searchable')
      })
      
      await waitFor(() => {
        expect(result.current.filteredSessions).toHaveLength(1)
      })
      
      // Clear search
      act(() => {
        result.current.searchSessions('')
      })
      
      await waitFor(() => {
        expect(result.current.searchQuery).toBe('')
        expect(result.current.filteredSessions).toHaveLength(10)
      })
    })
    
    it('should search by agent name', async () => {
      const sessions = createTestSessions(5)
      sessions[0].agent_name = 'Special Agent'
      sessions[1].agent_name = 'Another Agent'
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      act(() => {
        result.current.searchSessions('Special')
      })
      
      await waitFor(() => {
        expect(result.current.filteredSessions).toHaveLength(1)
        expect(result.current.filteredSessions[0].agent_name).toBe('Special Agent')
      })
    })
  })
  
  describe('Session Grouping', () => {
    it('should group sessions by time periods', async () => {
      const now = new Date()
      const sessions = [
        // Today - within last 24 hours
        createTestSessions(3, { 
          startDate: new Date(now.getTime() - 2 * 60 * 60 * 1000),
          prefix: 'today'
        }),
        // Recent - 1-7 days ago
        createTestSessions(4, { 
          startDate: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000),
          prefix: 'recent'
        }),
        // Past - more than 7 days ago
        createTestSessions(3, { 
          startDate: new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000),
          prefix: 'past'
        })
      ].flat()
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 10, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      await waitFor(() => {
        expect(result.current.sessionGroups).toHaveLength(3)
        
        const [today, recent, past] = result.current.sessionGroups
        
        expect(today.group).toBe('today')
        expect(today.label).toBe('Today')
        expect(today.count).toBe(3)
        
        expect(recent.group).toBe('recent')
        expect(recent.label).toBe('Recent')
        expect(recent.count).toBe(4)
        
        expect(past.group).toBe('past')
        expect(past.label).toBe('Past Sessions')
        expect(past.count).toBe(3)
      })
    })
    
    it('should handle empty groups correctly', async () => {
      // Only old sessions
      const sessions = createTestSessions(5, {
        startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      })
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      await waitFor(() => {
        // Should only have past group
        expect(result.current.sessionGroups).toHaveLength(1)
        expect(result.current.sessionGroups[0].group).toBe('past')
        expect(result.current.sessionGroups[0].count).toBe(5)
      })
    })
    
    it('should update groups when sessions are filtered', async () => {
      const now = new Date()
      const sessions = [
        {
          session_id: 'today-1',
          session_name: 'Today Special',
          created_at: new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(),
          user_id: 'user',
          agent_key: 'agent',
          agent_name: 'Agent'
        },
        {
          session_id: 'recent-1',
          session_name: 'Recent Special',
          created_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          user_id: 'user',
          agent_key: 'agent',
          agent_name: 'Agent'
        },
        {
          session_id: 'past-1',
          session_name: 'Past Normal',
          created_at: new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          user_id: 'user',
          agent_key: 'agent',
          agent_name: 'Agent'
        }
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 3, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Filter for "Special"
      act(() => {
        result.current.searchSessions('Special')
      })
      
      await waitFor(() => {
        expect(result.current.filteredSessions).toHaveLength(2)
        expect(result.current.sessionGroups).toHaveLength(2) // Only today and recent
        expect(result.current.sessionGroups[0].count).toBe(1)
        expect(result.current.sessionGroups[1].count).toBe(1)
      })
    })
  })
  
  describe('Session Selection', () => {
    it('should select a session', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      act(() => {
        result.current.selectSession('session-2')
      })
      
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'session:select',
        sessionId: 'session-2'
      })
    })
    
    it('should update current session ID from session manager', async () => {
      const sessionManager = {
        getCurrentSessionId: vi.fn(() => 'session-3')
      }
      mockClient.getSessionManager = vi.fn(() => sessionManager)
      
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      expect(result.current.currentSessionId).toBe('session-3')
    })
  })
  
  describe('Session Deletion', () => {
    it('should delete a session successfully', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Mock delete response
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })
      
      await act(async () => {
        await result.current.deleteSession('session-2')
      })
      
      // Should remove from local state
      expect(result.current.sessions).toHaveLength(4)
      expect(result.current.sessions.find(s => s.session_id === 'session-2')).toBeUndefined()
    })
    
    it('should handle delete error gracefully', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Mock delete error
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Delete failed'))
      
      await expect(
        act(async () => {
          await result.current.deleteSession('session-2')
        })
      ).rejects.toThrow('Delete failed')
      
      // Session should still be in the list
      expect(result.current.sessions).toHaveLength(5)
      expect(result.current.sessions.find(s => s.session_id === 'session-2')).toBeDefined()
    })
  })
  
  describe('Real-time Updates', () => {
    it('should handle session:created event', async () => {
      const sessions = createTestSessions(3)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 3, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      const newSession: ChatSessionIndexEntry = {
        session_id: 'new-session',
        session_name: 'Brand New Session',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user',
        agent_key: 'agent',
        agent_name: 'Agent'
      }
      
      // Emit session:created event
      act(() => {
        ;(mockClient as any).emit('session:created', { session: newSession })
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(4)
        expect(result.current.sessions[0]).toEqual(newSession)
      })
    })
    
    it('should handle session:updated event', async () => {
      const sessions = createTestSessions(3)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 3, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      const updatedSession = {
        ...sessions[1],
        session_name: 'Updated Name',
        updated_at: new Date().toISOString()
      }
      
      // Emit session:updated event
      act(() => {
        ;(mockClient as any).emit('session:updated', { session: updatedSession })
      })
      
      await waitFor(() => {
        const session = result.current.sessions.find(s => s.session_id === 'session-1')
        expect(session?.session_name).toBe('Updated Name')
      })
    })
    
    it('should handle session:deleted event', async () => {
      const sessions = createTestSessions(3)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 3, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Emit session:deleted event
      act(() => {
        ;(mockClient as any).emit('session:deleted', { sessionId: 'session-1' })
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(2)
        expect(result.current.sessions.find(s => s.session_id === 'session-1')).toBeUndefined()
      })
    })
  })
  
  describe('Refresh Functionality', () => {
    it('should refresh sessions list', async () => {
      const initialSessions = createTestSessions(3)
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessions: initialSessions, total: 3, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      expect(result.current.sessions).toHaveLength(3)
      
      // Prepare new sessions for refresh
      const newSessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessions: newSessions, total: 5, hasMore: false })
      })
      
      await act(async () => {
        result.current.refresh()
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(5)
        expect(result.current.sessions[0].session_id).toBe('session-0')
      })
    })
    
    it('should clear search when refreshing', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Set search query
      act(() => {
        result.current.searchSessions('test')
      })
      
      expect(result.current.searchQuery).toBe('test')
      
      // Refresh
      await act(async () => {
        result.current.refresh()
      })
      
      expect(result.current.searchQuery).toBe('')
    })
  })
  
  describe('Cache Management', () => {
    it('should cache sessions up to maxCachedSessions', async () => {
      const sessions = createTestSessions(100)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 100, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList({ maxCachedSessions: 50 }),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Should only keep 50 sessions in memory
      expect(result.current.sessions).toHaveLength(50)
    })
    
    it('should use LRU strategy for cache eviction', async () => {
      const sessions = createTestSessions(60)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 60, hasMore: false })
      })
      
      const { result } = renderHook(
        () => useChatSessionList({ maxCachedSessions: 50 }),
        { wrapper: createWrapper(mockClient) }
      )
      
      await act(async () => {
        result.current.loadMore()
      })
      
      // Should keep the most recent 50 sessions
      expect(result.current.sessions).toHaveLength(50)
      expect(result.current.sessions[0].session_id).toBe('session-0')
      expect(result.current.sessions[49].session_id).toBe('session-49')
    })
  })
  
  describe('Connection State', () => {
    it('should handle disconnection gracefully', async () => {
      mockClient.isConnected = vi.fn(() => false)
      
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: true }),
        { wrapper: createWrapper(mockClient) }
      )
      
      // Should not attempt to load when disconnected
      expect(global.fetch).not.toHaveBeenCalled()
      expect(result.current.isLoading).toBe(false)
    })
    
    it('should reload on reconnection', async () => {
      const sessions = createTestSessions(5)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      // Start disconnected
      mockClient.isConnected = vi.fn(() => false)
      
      const { result } = renderHook(
        () => useChatSessionList({ autoLoad: true }),
        { wrapper: createWrapper(mockClient) }
      )
      
      expect(result.current.sessions).toHaveLength(0)
      
      // Simulate reconnection
      mockClient.isConnected = vi.fn(() => true)
      act(() => {
        ;(mockClient as any).emit('connection:open')
      })
      
      await waitFor(() => {
        expect(result.current.sessions).toHaveLength(5)
      })
    })
  })
  
  describe('Performance Optimizations', () => {
    it('should memoize filtered sessions', () => {
      const sessions = createTestSessions(100)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 100, hasMore: false })
      })
      
      const { result, rerender } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      const firstFiltered = result.current.filteredSessions
      
      // Re-render without changes
      rerender()
      
      const secondFiltered = result.current.filteredSessions
      
      // Should be the same reference (memoized)
      expect(firstFiltered).toBe(secondFiltered)
    })
    
    it('should memoize session groups', () => {
      const sessions = createTestSessions(100)
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 100, hasMore: false })
      })
      
      const { result, rerender } = renderHook(
        () => useChatSessionList(),
        { wrapper: createWrapper(mockClient) }
      )
      
      const firstGroups = result.current.sessionGroups
      
      // Re-render without changes
      rerender()
      
      const secondGroups = result.current.sessionGroups
      
      // Should be the same reference (memoized)
      expect(firstGroups).toBe(secondGroups)
    })
  })
})