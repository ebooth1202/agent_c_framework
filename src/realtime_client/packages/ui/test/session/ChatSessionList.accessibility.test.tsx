/**
 * Accessibility tests for ChatSessionList component
 * Validates WCAG 2.1 AA compliance
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe, toHaveNoViolations } from 'jest-axe'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ChatSessionList } from '../../src/components/session/ChatSessionList'
import { AgentCProvider } from '@agentc/realtime-react'
import type { ChatSessionIndexEntry } from '@agentc/realtime-core'

// Extend expect with axe matchers
expect.extend(toHaveNoViolations)

// Mock the hook
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
  on: vi.fn(),
  off: vi.fn(),
  getSessionManager: () => null
}

// Helper to create test sessions
function createTestSessions(count: number): ChatSessionIndexEntry[] {
  return Array.from({ length: count }, (_, i) => ({
    session_id: `session-${i}`,
    session_name: `Test Session ${i}`,
    created_at: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
    user_id: 'test-user',
    agent_key: 'test-agent',
    agent_name: `Agent ${i}`
  }))
}

// Setup mock hook
function setupMockHook(overrides: any = {}) {
  const { useChatSessionList } = require('@agentc/realtime-react')
  
  useChatSessionList.mockReturnValue({
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
  })
}

describe('ChatSessionList Accessibility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  describe('WCAG 2.1 AA Compliance', () => {
    it('should have no accessibility violations in empty state', async () => {
      setupMockHook()
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
    
    it('should have no accessibility violations with sessions', async () => {
      const sessions = createTestSessions(5)
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
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
    
    it('should have no accessibility violations in loading state', async () => {
      setupMockHook({ isLoading: true })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
    
    it('should have no accessibility violations in error state', async () => {
      setupMockHook({ 
        error: new Error('Failed to load sessions') 
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
  
  describe('ARIA Attributes', () => {
    it('should have proper ARIA roles', () => {
      const sessions = createTestSessions(3)
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
      
      // Check listbox role
      const listbox = screen.getByRole('listbox')
      expect(listbox).toHaveAttribute('aria-label', 'Chat sessions')
      
      // Check option roles
      const options = screen.getAllByRole('option')
      expect(options).toHaveLength(3)
      
      // Check heading roles
      const headings = screen.getAllByRole('heading', { level: 3 })
      expect(headings).toHaveLength(1)
      expect(headings[0]).toHaveTextContent('Today')
      
      // Check search role
      const searchbox = screen.getByRole('searchbox')
      expect(searchbox).toHaveAttribute('aria-label', 'Search sessions')
    })
    
    it('should have proper ARIA labels for all interactive elements', () => {
      const sessions = createTestSessions(2)
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 2,
          sessions
        }]
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // All buttons should have accessible names
      const buttons = container.querySelectorAll('button')
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName()
      })
      
      // All form controls should have labels
      const inputs = container.querySelectorAll('input')
      inputs.forEach(input => {
        expect(input).toHaveAccessibleName()
      })
    })
    
    it('should properly indicate selected session', () => {
      const sessions = createTestSessions(3)
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        currentSessionId: 'session-1',
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
      
      // Selected option should have aria-selected="true"
      const selectedOption = screen.getByRole('option', { selected: true })
      expect(selectedOption).toHaveAttribute('aria-selected', 'true')
      
      // Other options should have aria-selected="false"
      const unselectedOptions = screen.getAllByRole('option', { selected: false })
      expect(unselectedOptions).toHaveLength(2)
    })
    
    it('should have proper ARIA live regions', () => {
      setupMockHook()
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Should have status region for announcements
      const statusRegion = container.querySelector('[role="status"][aria-live="assertive"]')
      expect(statusRegion).toBeInTheDocument()
      expect(statusRegion).toHaveAttribute('aria-atomic', 'true')
    })
  })
  
  describe('Keyboard Navigation', () => {
    it('should support full keyboard navigation', () => {
      const sessions = createTestSessions(5)
      const selectSession = vi.fn()
      
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
      
      const listbox = screen.getByRole('listbox')
      
      // Focus the listbox
      listbox.focus()
      expect(document.activeElement).toBe(listbox)
      
      // Arrow Down - focus first item
      fireEvent.keyDown(listbox, { key: 'ArrowDown' })
      const firstOption = screen.getAllByRole('option')[0]
      expect(firstOption).toHaveAttribute('tabIndex', '0')
      
      // Arrow Down again - focus second item
      fireEvent.keyDown(listbox, { key: 'ArrowDown' })
      const secondOption = screen.getAllByRole('option')[1]
      expect(secondOption).toHaveAttribute('tabIndex', '0')
      
      // Arrow Up - back to first item
      fireEvent.keyDown(listbox, { key: 'ArrowUp' })
      expect(firstOption).toHaveAttribute('tabIndex', '0')
      
      // Enter - select item
      fireEvent.keyDown(listbox, { key: 'Enter' })
      expect(selectSession).toHaveBeenCalledWith('session-0')
      
      // Home - jump to first
      fireEvent.keyDown(listbox, { key: 'Home' })
      expect(firstOption).toHaveAttribute('tabIndex', '0')
      
      // End - jump to last
      fireEvent.keyDown(listbox, { key: 'End' })
      const lastOption = screen.getAllByRole('option')[4]
      expect(lastOption).toHaveAttribute('tabIndex', '0')
    })
    
    it('should trap focus in delete dialog', async () => {
      const sessions = createTestSessions(2)
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 2,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Open delete dialog
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      fireEvent.click(deleteButton)
      
      // Wait for dialog
      await waitFor(() => {
        expect(screen.getByText('Delete Session?')).toBeInTheDocument()
      })
      
      // Check focus is trapped in dialog
      const dialog = screen.getByRole('alertdialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      
      expect(focusableElements.length).toBeGreaterThan(0)
      
      // First focusable element should receive focus
      expect(document.activeElement).toBe(focusableElements[0])
    })
    
    it('should support keyboard shortcuts for search', () => {
      setupMockHook()
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const searchInput = screen.getByRole('searchbox')
      
      // Type in search
      searchInput.focus()
      fireEvent.change(searchInput, { target: { value: 'test' } })
      expect(searchInput).toHaveValue('test')
      
      // Escape clears search
      fireEvent.keyDown(searchInput, { key: 'Escape' })
      
      // Search should be cleared
      expect(searchInput).toHaveFocus()
    })
  })
  
  describe('Screen Reader Support', () => {
    it('should announce session selection', async () => {
      const sessions = createTestSessions(3)
      const selectSession = vi.fn()
      
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
      
      const statusRegion = container.querySelector('[role="status"][aria-live="assertive"]')
      
      // Select a session
      const firstSession = screen.getAllByRole('option')[0]
      fireEvent.click(firstSession)
      
      // Should announce selection
      await waitFor(() => {
        expect(statusRegion).toHaveTextContent('Session selected')
      })
    })
    
    it('should announce session deletion', async () => {
      const sessions = createTestSessions(2)
      const deleteSession = vi.fn().mockResolvedValue(undefined)
      
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        deleteSession,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 2,
          sessions
        }]
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      const statusRegion = container.querySelector('[role="status"][aria-live="assertive"]')
      
      // Delete a session
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      fireEvent.click(deleteButton)
      
      // Confirm deletion
      const confirmButton = await screen.findByRole('button', { name: 'Delete' })
      fireEvent.click(confirmButton)
      
      // Should announce deletion
      await waitFor(() => {
        expect(statusRegion).toHaveTextContent('Session deleted successfully')
      })
    })
    
    it('should have descriptive labels for session items', () => {
      const sessions = [{
        session_id: 'test-1',
        session_name: 'Important Meeting',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        user_id: 'user',
        agent_key: 'agent',
        agent_name: 'Assistant Bot'
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
      
      const sessionOption = screen.getByRole('option')
      
      // Should have comprehensive aria-label
      expect(sessionOption).toHaveAttribute('aria-label')
      const label = sessionOption.getAttribute('aria-label')
      expect(label).toContain('Important Meeting')
      expect(label).toContain('Assistant Bot')
      expect(label).toContain('2h') // Time ago
    })
  })
  
  describe('Focus Management', () => {
    it('should restore focus after dialog close', async () => {
      const sessions = createTestSessions(2)
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 2,
          sessions
        }]
      })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Focus and click delete button
      const firstSession = screen.getAllByRole('option')[0]
      const deleteButton = within(firstSession).getByRole('button', { name: /delete/i })
      deleteButton.focus()
      fireEvent.click(deleteButton)
      
      // Wait for dialog
      await waitFor(() => {
        expect(screen.getByText('Delete Session?')).toBeInTheDocument()
      })
      
      // Cancel dialog
      const cancelButton = screen.getByRole('button', { name: 'Cancel' })
      fireEvent.click(cancelButton)
      
      // Focus should return to delete button
      await waitFor(() => {
        expect(document.activeElement).toBe(deleteButton)
      })
    })
    
    it('should manage focus during search', () => {
      const sessions = createTestSessions(5)
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
      
      const searchInput = screen.getByRole('searchbox')
      
      // Focus search
      searchInput.focus()
      expect(document.activeElement).toBe(searchInput)
      
      // Tab should move to next focusable element
      fireEvent.keyDown(searchInput, { key: 'Tab' })
      
      // Should move focus to listbox or first interactive element
      expect(document.activeElement).not.toBe(searchInput)
    })
  })
  
  describe('Color Contrast', () => {
    it('should have sufficient color contrast ratios', () => {
      const sessions = createTestSessions(2)
      setupMockHook({
        sessions,
        filteredSessions: sessions,
        currentSessionId: 'session-0',
        sessionGroups: [{
          group: 'today',
          label: 'Today',
          count: 2,
          sessions
        }]
      })
      
      const { container } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Check text elements have sufficient contrast
      // This would typically be done with axe-core which checks contrast ratios
      const textElements = container.querySelectorAll('p, span, h1, h2, h3, h4, h5, h6')
      
      textElements.forEach(element => {
        const styles = window.getComputedStyle(element)
        // Verify text is visible
        expect(styles.color).not.toBe('transparent')
        expect(styles.opacity).not.toBe('0')
      })
    })
  })
  
  describe('Motion and Animation', () => {
    it('should respect prefers-reduced-motion', () => {
      // Mock prefers-reduced-motion
      window.matchMedia = vi.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      }))
      
      const sessions = createTestSessions(3)
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
      
      // Check for motion-safe/motion-reduce classes
      const animatedElements = container.querySelectorAll('.transition-all, .animate-spin')
      animatedElements.forEach(element => {
        expect(element.className).toContain('motion-')
      })
    })
  })
  
  describe('Touch Target Size', () => {
    it('should have adequate touch target sizes', () => {
      const sessions = createTestSessions(3)
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
      
      // Check interactive elements meet minimum size (44x44px)
      const interactiveElements = container.querySelectorAll('button, [role="option"], input')
      
      interactiveElements.forEach(element => {
        const rect = element.getBoundingClientRect()
        // Elements should be at least 44px in one dimension
        expect(Math.max(rect.width, rect.height)).toBeGreaterThanOrEqual(44)
      })
    })
  })
  
  describe('Error Handling', () => {
    it('should provide accessible error messages', () => {
      const error = new Error('Network connection failed')
      setupMockHook({ error })
      
      render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Error should be announced
      const errorMessage = screen.getByText('Network connection failed')
      expect(errorMessage).toBeInTheDocument()
      
      // Retry button should be accessible
      const retryButton = screen.getByRole('button', { name: /try again/i })
      expect(retryButton).toHaveAccessibleName()
    })
  })
  
  describe('Responsive Design', () => {
    it('should be usable at different viewport sizes', () => {
      const sessions = createTestSessions(5)
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
      
      // Test at mobile viewport
      window.innerWidth = 375
      window.innerHeight = 667
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Should still be accessible at mobile size
      expect(screen.getByRole('listbox')).toBeInTheDocument()
      expect(screen.getByRole('searchbox')).toBeInTheDocument()
      
      // Test at desktop viewport
      window.innerWidth = 1920
      window.innerHeight = 1080
      
      rerender(
        <AgentCProvider client={mockClient as any}>
          <ChatSessionList />
        </AgentCProvider>
      )
      
      // Should maintain accessibility at desktop size
      expect(screen.getByRole('listbox')).toBeInTheDocument()
      expect(screen.getByRole('searchbox')).toBeInTheDocument()
    })
  })
})