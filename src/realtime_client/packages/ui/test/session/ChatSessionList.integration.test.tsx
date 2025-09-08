/**
 * Integration tests for ChatSessionList
 * Tests WebSocket events, CRUD operations, and multi-session scenarios
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ChatSessionList } from '../../src/components/session/ChatSessionList'
import { AgentCProvider } from '@agentc/realtime-react'
import type { ChatSessionIndexEntry, RealtimeClient } from '@agentc/realtime-core'

// Mock fetch for API calls
global.fetch = vi.fn()

// Helper to create mock WebSocket client with event emitter
function createMockWebSocketClient(): Partial<RealtimeClient> & { 
  emit: (event: string, data: any) => void 
} {
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
    emit: (event: string, data: any) => {
      listeners.get(event)?.forEach(handler => handler(data))
    },
    getSessionManager: vi.fn(() => ({
      getCurrentSessionId: vi.fn(() => null)
    }))
  }
}

// Helper to create test sessions
function createTestSession(id: string, hoursAgo: number = 0): ChatSessionIndexEntry {
  const date = new Date(Date.now() - hoursAgo * 60 * 60 * 1000)
  return {
    session_id: id,
    session_name: `Session ${id}`,
    created_at: date.toISOString(),
    updated_at: date.toISOString(),
    user_id: 'test-user',
    agent_key: 'test-agent',
    agent_name: 'Test Agent'
  }
}

describe('ChatSessionList Integration Tests', () => {
  let mockClient: ReturnType<typeof createMockWebSocketClient>
  
  beforeEach(() => {
    mockClient = createMockWebSocketClient()
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
  
  describe('WebSocket Event Handling', () => {
    it('should handle real-time session creation', async () => {
      // Start with 2 sessions
      const initialSessions = [
        createTestSession('session-1', 2),
        createTestSession('session-2', 4)
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: initialSessions, 
          total: 2, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Wait for initial load
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(2)
      })
      
      // Simulate WebSocket event for new session
      const newSession = createTestSession('session-3', 0)
      mockClient.emit('session:created', { session: newSession })
      
      // New session should appear at the top
      await waitFor(() => {
        const sessions = screen.getAllByRole('option')
        expect(sessions).toHaveLength(3)
        expect(within(sessions[0]).getByText('Session session-3')).toBeInTheDocument()
      })
    })
    
    it('should handle real-time session updates', async () => {
      const initialSessions = [
        createTestSession('session-1', 1),
        createTestSession('session-2', 2)
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: initialSessions, 
          total: 2, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getByText('Session session-1')).toBeInTheDocument()
      })
      
      // Update session name via WebSocket
      const updatedSession = {
        ...initialSessions[0],
        session_name: 'Updated Session Name',
        updated_at: new Date().toISOString()
      }
      
      mockClient.emit('session:updated', { session: updatedSession })
      
      await waitFor(() => {
        expect(screen.getByText('Updated Session Name')).toBeInTheDocument()
        expect(screen.queryByText('Session session-1')).not.toBeInTheDocument()
      })
    })
    
    it('should handle real-time session deletion', async () => {
      const initialSessions = [
        createTestSession('session-1', 1),
        createTestSession('session-2', 2),
        createTestSession('session-3', 3)
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: initialSessions, 
          total: 3, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(3)
      })
      
      // Delete middle session via WebSocket
      mockClient.emit('session:deleted', { sessionId: 'session-2' })
      
      await waitFor(() => {
        const sessions = screen.getAllByRole('option')
        expect(sessions).toHaveLength(2)
        expect(screen.queryByText('Session session-2')).not.toBeInTheDocument()
      })
    })
    
    it('should handle multiple rapid WebSocket events', async () => {
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions: [], total: 0, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Rapid fire multiple events
      const newSessions = Array.from({ length: 5 }, (_, i) => 
        createTestSession(`rapid-${i}`, 0)
      )
      
      newSessions.forEach(session => {
        mockClient.emit('session:created', { session })
      })
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(5)
      })
    })
  })
  
  describe('Session CRUD Operations', () => {
    it('should create and immediately select a new session', async () => {
      const initialSessions = [createTestSession('existing-1', 2)]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: initialSessions, 
          total: 1, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(1)
      })
      
      // Create new session and auto-select it
      const newSession = createTestSession('new-session', 0)
      mockClient.emit('session:created', { 
        session: newSession,
        autoSelect: true 
      })
      
      // Update current session
      mockClient.getSessionManager = vi.fn(() => ({
        getCurrentSessionId: vi.fn(() => 'new-session')
      }))
      
      await waitFor(() => {
        const newOption = screen.getByRole('option', { selected: true })
        expect(within(newOption).getByText('Session new-session')).toBeInTheDocument()
      })
    })
    
    it('should handle batch session updates', async () => {
      const initialSessions = Array.from({ length: 10 }, (_, i) => 
        createTestSession(`batch-${i}`, i)
      )
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: initialSessions, 
          total: 10, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(10)
      })
      
      // Batch update multiple sessions
      const updates = initialSessions.slice(0, 5).map(session => ({
        ...session,
        session_name: `Updated ${session.session_id}`,
        updated_at: new Date().toISOString()
      }))
      
      // Emit batch update event
      mockClient.emit('sessions:batch-update', { sessions: updates })
      
      await waitFor(() => {
        updates.forEach(update => {
          expect(screen.getByText(`Updated ${update.session_id}`)).toBeInTheDocument()
        })
      })
    })
    
    it('should handle session deletion with confirmation', async () => {
      const sessions = [
        createTestSession('to-delete', 1),
        createTestSession('to-keep', 2)
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 2, hasMore: false })
      })
      
      // Mock delete API call
      ;(global.fetch as any).mockImplementation((url: string) => {
        if (url.includes('/delete')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true })
          })
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ sessions, total: 2, hasMore: false })
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(2)
      })
      
      // Click delete on first session
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      
      fireEvent.click(deleteButton)
      
      // Confirm deletion
      const confirmButton = await screen.findByRole('button', { name: 'Delete' })
      fireEvent.click(confirmButton)
      
      // Emit deletion event from server
      mockClient.emit('session:deleted', { sessionId: 'to-delete' })
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(1)
        expect(screen.queryByText('Session to-delete')).not.toBeInTheDocument()
      })
    })
  })
  
  describe('Connection and Disconnection Scenarios', () => {
    it('should show connection status and handle disconnection', async () => {
      const sessions = [createTestSession('session-1', 1)]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 1, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getByText('Session session-1')).toBeInTheDocument()
      })
      
      // Simulate disconnection
      mockClient.isConnected = vi.fn(() => false)
      mockClient.emit('connection:close', {})
      
      // Should show some indication or disable interactions
      // (Implementation dependent on UI requirements)
      
      // Simulate reconnection
      mockClient.isConnected = vi.fn(() => true)
      mockClient.emit('connection:open', {})
      
      // Should reload sessions
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2) // Initial + reconnect
      })
    })
    
    it('should queue events during disconnection and apply on reconnect', async () => {
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions: [], total: 0, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Disconnect
      mockClient.isConnected = vi.fn(() => false)
      mockClient.emit('connection:close', {})
      
      // Try to create sessions while disconnected
      const queuedSessions = [
        createTestSession('queued-1', 0),
        createTestSession('queued-2', 0)
      ]
      
      // These events should be queued
      queuedSessions.forEach(session => {
        mockClient.emit('session:created', { session })
      })
      
      // Sessions shouldn't appear yet
      expect(screen.queryByRole('option')).not.toBeInTheDocument()
      
      // Reconnect
      mockClient.isConnected = vi.fn(() => true)
      
      // Mock server response with queued sessions
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          sessions: queuedSessions, 
          total: 2, 
          hasMore: false 
        })
      })
      
      mockClient.emit('connection:open', {})
      
      // Sessions should appear after reconnection
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(2)
      })
    })
  })
  
  describe('Multi-Session Scenarios', () => {
    it('should handle switching between multiple active sessions', async () => {
      const sessions = Array.from({ length: 5 }, (_, i) => 
        createTestSession(`multi-${i}`, i)
      )
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      const onSessionSelect = vi.fn()
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList onSessionSelect={onSessionSelect} />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(5)
      })
      
      // Select different sessions rapidly
      const sessionOptions = screen.getAllByRole('option')
      
      fireEvent.click(sessionOptions[0])
      expect(onSessionSelect).toHaveBeenCalledWith('multi-0')
      
      fireEvent.click(sessionOptions[2])
      expect(onSessionSelect).toHaveBeenCalledWith('multi-2')
      
      fireEvent.click(sessionOptions[4])
      expect(onSessionSelect).toHaveBeenCalledWith('multi-4')
      
      expect(onSessionSelect).toHaveBeenCalledTimes(3)
    })
    
    it('should maintain session order during real-time updates', async () => {
      const sessions = Array.from({ length: 5 }, (_, i) => 
        createTestSession(`order-${i}`, i * 2)
      )
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 5, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(5)
      })
      
      // Update a middle session to be most recent
      const updatedSession = {
        ...sessions[2],
        session_name: 'Recently Updated',
        updated_at: new Date().toISOString()
      }
      
      mockClient.emit('session:updated', { session: updatedSession })
      
      await waitFor(() => {
        const sessionOptions = screen.getAllByRole('option')
        // Updated session should move to top
        expect(within(sessionOptions[0]).getByText('Recently Updated')).toBeInTheDocument()
      })
    })
    
    it('should handle concurrent operations on same session', async () => {
      const session = createTestSession('concurrent-1', 1)
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions: [session], total: 1, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getByText('Session concurrent-1')).toBeInTheDocument()
      })
      
      // Simulate concurrent updates
      const update1 = {
        ...session,
        session_name: 'Update 1',
        updated_at: new Date(Date.now() - 1000).toISOString()
      }
      
      const update2 = {
        ...session,
        session_name: 'Update 2',
        updated_at: new Date().toISOString()
      }
      
      // Send both updates rapidly
      mockClient.emit('session:updated', { session: update1 })
      mockClient.emit('session:updated', { session: update2 })
      
      // Latest update should win
      await waitFor(() => {
        expect(screen.getByText('Update 2')).toBeInTheDocument()
        expect(screen.queryByText('Update 1')).not.toBeInTheDocument()
      })
    })
    
    it('should handle session with long names and truncation', async () => {
      const longNameSession = {
        ...createTestSession('long-1', 0),
        session_name: 'This is a very long session name that should be truncated in the UI to prevent layout issues and maintain a clean appearance'
      }
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ 
          sessions: [longNameSession], 
          total: 1, 
          hasMore: false 
        })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        const sessionOption = screen.getByRole('option')
        // Check that the long name is present but truncated (CSS handles this)
        const nameElement = within(sessionOption).getByText(/This is a very long session name/i)
        expect(nameElement).toBeInTheDocument()
      })
    })
  })
  
  describe('Search with Real-time Updates', () => {
    it('should maintain search filter during real-time updates', async () => {
      const sessions = [
        { ...createTestSession('search-1', 1), session_name: 'Alpha Session' },
        { ...createTestSession('search-2', 2), session_name: 'Beta Session' },
        { ...createTestSession('search-3', 3), session_name: 'Gamma Session' }
      ]
      
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({ sessions, total: 3, hasMore: false })
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(3)
      })
      
      // Apply search filter
      const searchInput = screen.getByRole('searchbox')
      await userEvent.type(searchInput, 'Alpha')
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(1)
      })
      
      // Add new session that matches filter
      const newMatchingSession = {
        ...createTestSession('search-4', 0),
        session_name: 'Alpha New Session'
      }
      
      mockClient.emit('session:created', { session: newMatchingSession })
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(2)
      })
      
      // Add new session that doesn't match filter
      const newNonMatchingSession = {
        ...createTestSession('search-5', 0),
        session_name: 'Delta Session'
      }
      
      mockClient.emit('session:created', { session: newNonMatchingSession })
      
      // Should still only show matching sessions
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(2)
      })
    })
  })
  
  describe('Pagination with Real-time Updates', () => {
    it('should handle new sessions while paginating', async () => {
      // Create 60 sessions for pagination
      const page1Sessions = Array.from({ length: 50 }, (_, i) => 
        createTestSession(`page1-${i}`, i)
      )
      
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          sessions: page1Sessions, 
          total: 60, 
          hasMore: true 
        })
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      await waitFor(() => {
        expect(screen.getAllByRole('option')).toHaveLength(50)
      })
      
      // Add new session while more pages exist
      const newSession = createTestSession('new-during-pagination', 0)
      mockClient.emit('session:created', { session: newSession })
      
      await waitFor(() => {
        // New session should appear at top
        const sessions = screen.getAllByRole('option')
        expect(sessions).toHaveLength(51)
        expect(within(sessions[0]).getByText('Session new-during-pagination')).toBeInTheDocument()
      })
      
      // Scroll to load more
      const scrollContainer = container.querySelector('[role="listbox"]')
      if (scrollContainer) {
        fireEvent.scroll(scrollContainer, { target: { scrollTop: 1000 } })
      }
      
      const page2Sessions = Array.from({ length: 10 }, (_, i) => 
        createTestSession(`page2-${i}`, 50 + i)
      )
      
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          sessions: page2Sessions, 
          total: 61, 
          hasMore: false 
        })
      })
      
      await waitFor(() => {
        expect(screen.getAllByRole('option').length).toBeGreaterThan(51)
      })
    })
  })
})