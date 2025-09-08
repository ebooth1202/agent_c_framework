/**
 * Unit tests for ChatSessionList component
 * Tests all states, interactions, and accessibility features
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ChatSessionList } from '../../src/components/session/ChatSessionList'
import { AgentCProvider } from '@agentc/realtime-react'
import type { ChatSessionIndexEntry } from '@agentc/realtime-core'

// Mock the useChatSessionList hook
vi.mock('@agentc/realtime-react', async () => {
  const actual = await vi.importActual('@agentc/realtime-react')
  return {
    ...actual,
    useChatSessionList: vi.fn()
  }
})

// Mock client
const mockClient = {
  isConnected: () => true,
  sendEvent: vi.fn(),
  resumeChatSession: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  getSessionManager: () => null
}

// Helper to generate test sessions
function generateTestSessions(count: number, options: { startDate?: Date } = {}): ChatSessionIndexEntry[] {
  const sessions: ChatSessionIndexEntry[] = []
  const startDate = options.startDate || new Date()
  
  for (let i = 0; i < count; i++) {
    const hoursAgo = i * 2
    const date = new Date(startDate.getTime() - (hoursAgo * 60 * 60 * 1000))
    
    sessions.push({
      session_id: `session-${i}`,
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

// Helper to setup mock hook return
function setupMockHook(overrides: any = {}) {
  const { useChatSessionList } = require('@agentc/realtime-react')
  
  const defaultReturn = {
    sessions: [],
    filteredSessions: [],
    sessionGroups: [],
    searchQuery: '',
    isLoading: false,
    isPaginationLoading: false,
    error: null,
    hasMore: false,
    totalCount: 0,
    currentSessionId: null,
    loadMore: vi.fn(),
    selectSession: vi.fn(),
    deleteSession: vi.fn(),
    searchSessions: vi.fn(),
    refresh: vi.fn(),
    ...overrides
  }
  
  useChatSessionList.mockReturnValue(defaultReturn)
  
  return defaultReturn
}

describe('ChatSessionList Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  describe('Rendering States', () => {
    it('should render loading state when loading with no sessions', () => {
      setupMockHook({ isLoading: true })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Should show loading skeletons
      const skeletons = screen.getAllByTestId(/skeleton/i)
      expect(skeletons.length).toBeGreaterThan(0)
    })
    
    it('should render empty state when no sessions exist', () => {
      setupMockHook()
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('No conversations yet')).toBeInTheDocument()
      expect(screen.getByText(/Start a new chat/i)).toBeInTheDocument()
    })
    
    it('should render empty state with search message when search returns no results', () => {
      setupMockHook({ 
        searchQuery: 'nonexistent',
        sessions: generateTestSessions(5),
        filteredSessions: []
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('No matching sessions')).toBeInTheDocument()
      expect(screen.getByText(/No sessions found matching "nonexistent"/)).toBeInTheDocument()
    })
    
    it('should render error state with retry button', () => {
      const error = new Error('Failed to load sessions')
      const refresh = vi.fn()
      setupMockHook({ error, refresh })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('Failed to load sessions')).toBeInTheDocument()
      expect(screen.getByText(error.message)).toBeInTheDocument()
      
      const retryButton = screen.getByRole('button', { name: /try again/i })
      fireEvent.click(retryButton)
      
      expect(refresh).toHaveBeenCalled()
    })
    
    it('should render sessions grouped by time periods', () => {
      const sessions = generateTestSessions(10)
      const sessionGroups = [
        {
          group: 'today',
          label: 'Today',
          count: 3,
          sessions: sessions.slice(0, 3)
        },
        {
          group: 'recent',
          label: 'Recent',
          count: 4,
          sessions: sessions.slice(3, 7)
        },
        {
          group: 'past',
          label: 'Past Sessions',
          count: 3,
          sessions: sessions.slice(7, 10)
        }
      ]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Check group headers
      expect(screen.getByText('Today')).toBeInTheDocument()
      expect(screen.getByText('(3)')).toBeInTheDocument()
      expect(screen.getByText('Recent')).toBeInTheDocument()
      expect(screen.getByText('(4)')).toBeInTheDocument()
      expect(screen.getByText('Past Sessions')).toBeInTheDocument()
      
      // Check session items
      const sessionItems = screen.getAllByRole('option')
      expect(sessionItems).toHaveLength(10)
    })
    
    it('should highlight active session', () => {
      const sessions = generateTestSessions(5)
      const currentSessionId = 'session-2'
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }],
        currentSessionId
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const activeSession = screen.getByRole('option', { selected: true })
      expect(activeSession).toHaveAttribute('aria-selected', 'true')
    })
    
    it('should render collapsed view when isCollapsed is true', () => {
      const sessions = generateTestSessions(10)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        currentSessionId: 'session-1'
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList isCollapsed={true} />
        </AgentCProvider>
      )
      
      // Should show icon buttons instead of full list
      const iconButtons = screen.getAllByRole('button')
      // Should show max 5 sessions + 1 expand button
      expect(iconButtons.length).toBeLessThanOrEqual(6)
    })
  })
  
  describe('Search Functionality', () => {
    it('should render search input and handle search', async () => {
      const searchSessions = vi.fn()
      const sessions = generateTestSessions(10)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        searchSessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 10,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const searchInput = screen.getByRole('searchbox', { name: /search sessions/i })
      expect(searchInput).toBeInTheDocument()
      
      // Type in search
      await userEvent.type(searchInput, 'test query')
      
      // Should call searchSessions for each character typed
      expect(searchSessions).toHaveBeenCalled()
    })
    
    it('should clear search when Escape is pressed', async () => {
      const searchSessions = vi.fn()
      
      setupMockHook({ 
        searchQuery: 'test query',
        searchSessions
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const searchInput = screen.getByRole('searchbox')
      
      // Press escape
      fireEvent.keyDown(searchInput, { key: 'Escape' })
      
      expect(searchSessions).toHaveBeenCalledWith('')
    })
    
    it('should show search spinner when searching', () => {
      setupMockHook({ 
        searchQuery: 'test',
        isSearching: true
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })
  
  describe('Session Selection', () => {
    it('should handle session selection on click', () => {
      const selectSession = vi.fn()
      const onSessionSelect = vi.fn()
      const sessions = generateTestSessions(5)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        selectSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList onSessionSelect={onSessionSelect} />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.click(firstSession)
      
      expect(selectSession).toHaveBeenCalledWith('session-0')
      expect(onSessionSelect).toHaveBeenCalledWith('session-0')
    })
    
    it('should handle session selection with Enter key', () => {
      const selectSession = vi.fn()
      const sessions = generateTestSessions(5)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        selectSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.keyDown(firstSession, { key: 'Enter' })
      
      expect(selectSession).toHaveBeenCalledWith('session-0')
    })
    
    it('should handle session selection with Space key', () => {
      const selectSession = vi.fn()
      const sessions = generateTestSessions(5)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        selectSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.keyDown(firstSession, { key: ' ' })
      
      expect(selectSession).toHaveBeenCalledWith('session-0')
    })
  })
  
  describe('Session Deletion', () => {
    it('should show delete button on hover', async () => {
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      
      // Delete button should be hidden initially
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      expect(deleteButton).toHaveClass('opacity-0')
      
      // Hover over session
      fireEvent.mouseEnter(firstSession)
      
      // Delete button should become visible
      await waitFor(() => {
        expect(deleteButton).toHaveClass('group-hover:opacity-100')
      })
    })
    
    it('should open confirmation dialog when delete is clicked', () => {
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      
      fireEvent.click(deleteButton)
      
      // Confirmation dialog should appear
      expect(screen.getByText('Delete Session?')).toBeInTheDocument()
      expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument()
    })
    
    it('should delete session when confirmed', async () => {
      const deleteSession = vi.fn().mockResolvedValue(undefined)
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        deleteSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      
      fireEvent.click(deleteButton)
      
      // Click confirm in dialog
      const confirmButton = screen.getByRole('button', { name: 'Delete' })
      fireEvent.click(confirmButton)
      
      await waitFor(() => {
        expect(deleteSession).toHaveBeenCalledWith('session-0')
      })
    })
    
    it('should cancel deletion when dialog is cancelled', () => {
      const deleteSession = vi.fn()
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        deleteSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      
      fireEvent.click(deleteButton)
      
      // Click cancel in dialog
      const cancelButton = screen.getByRole('button', { name: 'Cancel' })
      fireEvent.click(cancelButton)
      
      expect(deleteSession).not.toHaveBeenCalled()
    })
    
    it('should handle delete with Delete key', () => {
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.keyDown(firstSession, { key: 'Delete' })
      
      // Should open confirmation dialog
      expect(screen.getByText('Delete Session?')).toBeInTheDocument()
    })
  })
  
  describe('Keyboard Navigation', () => {
    it('should navigate with arrow keys', () => {
      const sessions = generateTestSessions(5)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const listbox = screen.getByRole('listbox')
      
      // Navigate down
      fireEvent.keyDown(listbox, { key: 'ArrowDown' })
      
      // First session should be focused
      const firstSession = screen.getAllByRole('option')[0]
      expect(firstSession).toHaveAttribute('tabIndex', '0')
      
      // Navigate down again
      fireEvent.keyDown(listbox, { key: 'ArrowDown' })
      
      // Second session should be focused
      const secondSession = screen.getAllByRole('option')[1]
      expect(secondSession).toHaveAttribute('tabIndex', '0')
      
      // Navigate up
      fireEvent.keyDown(listbox, { key: 'ArrowUp' })
      
      // First session should be focused again
      expect(firstSession).toHaveAttribute('tabIndex', '0')
    })
    
    it('should navigate to first item with Home key', () => {
      const sessions = generateTestSessions(10)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 10,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const listbox = screen.getByRole('listbox')
      
      // Press Home
      fireEvent.keyDown(listbox, { key: 'Home' })
      
      const firstSession = screen.getAllByRole('option')[0]
      expect(firstSession).toHaveAttribute('tabIndex', '0')
    })
    
    it('should navigate to last item with End key', () => {
      const sessions = generateTestSessions(10)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 10,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const listbox = screen.getByRole('listbox')
      
      // Press End
      fireEvent.keyDown(listbox, { key: 'End' })
      
      const sessions = screen.getAllByRole('option')
      const lastSession = sessions[sessions.length - 1]
      expect(lastSession).toHaveAttribute('tabIndex', '0')
    })
  })
  
  describe('Pagination and Infinite Scroll', () => {
    it('should show load more trigger when hasMore is true', () => {
      const sessions = generateTestSessions(50)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        hasMore: true,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 50,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('Scroll for more')).toBeInTheDocument()
    })
    
    it('should show loading spinner when loading more', () => {
      const sessions = generateTestSessions(50)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        hasMore: true,
        isPaginationLoading: true,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 50,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('Loading more sessions...')).toBeInTheDocument()
    })
  })
  
  describe('Session Display', () => {
    it('should display session with custom name', () => {
      const sessions = [{
        session_id: 'test-1',
        session_name: 'My Custom Session',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1',
        agent_key: 'agent-1',
        agent_name: 'Test Agent'
      }]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 1,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('My Custom Session')).toBeInTheDocument()
    })
    
    it('should generate default name for session without custom name', () => {
      const date = new Date('2024-01-15T14:30:00')
      const sessions = [{
        session_id: 'test-1',
        session_name: null,
        created_at: date.toISOString(),
        updated_at: date.toISOString(),
        user_id: 'user-1',
        agent_key: 'agent-1',
        agent_name: 'Test Agent'
      }]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 1,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText(/Chat from 1\/15, 2:30 PM/)).toBeInTheDocument()
    })
    
    it('should display agent name', () => {
      const sessions = [{
        session_id: 'test-1',
        session_name: 'Test Session',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1',
        agent_key: 'agent-1',
        agent_name: 'My Custom Agent'
      }]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 1,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('My Custom Agent')).toBeInTheDocument()
    })
    
    it('should fall back to agent_key when agent_name is not available', () => {
      const sessions = [{
        session_id: 'test-1',
        session_name: 'Test Session',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1',
        agent_key: 'agent-key-123',
        agent_name: null
      }]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 1,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('agent-key-123')).toBeInTheDocument()
    })
    
    it('should display relative time correctly', () => {
      const now = new Date()
      const sessions = [
        {
          session_id: 'test-1',
          session_name: 'Just now',
          created_at: now.toISOString(),
          updated_at: now.toISOString(),
          user_id: 'user-1',
          agent_key: 'agent-1',
          agent_name: 'Agent'
        },
        {
          session_id: 'test-2',
          session_name: '30 minutes ago',
          created_at: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
          user_id: 'user-1',
          agent_key: 'agent-1',
          agent_name: 'Agent'
        },
        {
          session_id: 'test-3',
          session_name: '2 hours ago',
          created_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
          user_id: 'user-1',
          agent_key: 'agent-1',
          agent_name: 'Agent'
        },
        {
          session_id: 'test-4',
          session_name: '3 days ago',
          created_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          user_id: 'user-1',
          agent_key: 'agent-1',
          agent_name: 'Agent'
        }
      ]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'various',
          label: 'Sessions',
          count: 4,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      expect(screen.getByText('Just now')).toBeInTheDocument()
      expect(screen.getByText('30m')).toBeInTheDocument()
      expect(screen.getByText('2h')).toBeInTheDocument()
      expect(screen.getByText('3d')).toBeInTheDocument()
    })
  })
  
  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      const sessions = generateTestSessions(5)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        currentSessionId: 'session-2',
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 5,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Listbox should have proper role
      const listbox = screen.getByRole('listbox')
      expect(listbox).toHaveAttribute('aria-label', 'Chat sessions')
      
      // Options should have proper roles and attributes
      const options = screen.getAllByRole('option')
      expect(options).toHaveLength(5)
      
      // Active session should be marked as selected
      const activeOption = screen.getByRole('option', { selected: true })
      expect(activeOption).toHaveAttribute('aria-selected', 'true')
      
      // Each option should have aria-label
      options.forEach((option, index) => {
        expect(option).toHaveAttribute('aria-label')
        expect(option).toHaveAttribute('aria-posinset', String(index + 1))
        expect(option).toHaveAttribute('aria-setsize', '5')
      })
    })
    
    it('should announce changes to screen readers', async () => {
      const selectSession = vi.fn()
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        selectSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Check for announcement region
      const announcement = container.querySelector('[role="status"][aria-live="assertive"]')
      expect(announcement).toBeInTheDocument()
      
      // Select a session
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.click(firstSession)
      
      // Should announce the selection
      await waitFor(() => {
        expect(announcement).toHaveTextContent('Session selected')
      })
    })
    
    it('should have accessible search input', () => {
      setupMockHook()
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const searchInput = screen.getByRole('searchbox')
      expect(searchInput).toHaveAttribute('aria-label', 'Search sessions')
      expect(searchInput).toHaveAttribute('placeholder', 'Search sessions...')
    })
    
    it('should support keyboard-only navigation', () => {
      const sessions = generateTestSessions(3)
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 3,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const listbox = screen.getByRole('listbox')
      
      // Should be focusable
      expect(listbox).toHaveAttribute('tabIndex', '0')
      
      // Focus the listbox
      listbox.focus()
      expect(document.activeElement).toBe(listbox)
      
      // Navigate with keyboard
      fireEvent.keyDown(listbox, { key: 'ArrowDown' })
      
      // First session should become focusable
      const firstSession = screen.getAllByRole('option')[0]
      expect(firstSession).toHaveAttribute('tabIndex', '0')
    })
    
    it('should have proper heading structure', () => {
      const sessions = generateTestSessions(10)
      const sessionGroups = [
        {
          group: 'today',
          label: 'Today',
          count: 3,
          sessions: sessions.slice(0, 3)
        },
        {
          group: 'recent',
          label: 'Recent',
          count: 4,
          sessions: sessions.slice(3, 7)
        },
        {
          group: 'past',
          label: 'Past Sessions',
          count: 3,
          sessions: sessions.slice(7, 10)
        }
      ]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Group headers should have heading role
      const headings = screen.getAllByRole('heading', { level: 3 })
      expect(headings).toHaveLength(3)
      
      // Check heading IDs for navigation
      expect(headings[0]).toHaveAttribute('id', 'header-today')
      expect(headings[1]).toHaveAttribute('id', 'header-recent')
      expect(headings[2]).toHaveAttribute('id', 'header-past')
    })
  })
  
  describe('Group Header Navigation', () => {
    it('should scroll to section when header is clicked', () => {
      const sessions = generateTestSessions(30)
      const sessionGroups = [
        {
          group: 'today',
          label: 'Today',
          count: 10,
          sessions: sessions.slice(0, 10)
        },
        {
          group: 'recent',
          label: 'Recent',
          count: 10,
          sessions: sessions.slice(10, 20)
        },
        {
          group: 'past',
          label: 'Past Sessions',
          count: 10,
          sessions: sessions.slice(20, 30)
        }
      ]
      
      setupMockHook({ 
        sessions,
        filteredSessions: sessions,
        sessionGroups
      })
      
      // Mock scrollIntoView
      const scrollIntoViewMock = vi.fn()
      Element.prototype.scrollIntoView = scrollIntoViewMock
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Click on "Recent" header
      const recentHeader = screen.getByText('Recent').parentElement
      fireEvent.click(recentHeader!)
      
      // Should scroll to that section
      expect(scrollIntoViewMock).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'start'
      })
    })
  })
})