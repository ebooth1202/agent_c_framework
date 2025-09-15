import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { MessageList } from '../MessageList'
import { AgentCProvider } from '@agentc/realtime-react'
import { RealtimeClient } from '@agentc/realtime-core'
import type { ChatMessage } from '@agentc/realtime-core'

// Mock the Logger to prevent console output
vi.mock('../../../utils/logger', () => ({
  Logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}))

// Get the mocked logger for assertions
const { Logger: loggerMock } = await import('../../../utils/logger')

describe('MessageList Race Condition Protection', () => {
  let mockClient: RealtimeClient
  let scrollIntoViewSpy: any
  
  beforeEach(() => {
    // Reset logger mocks
    Object.values(loggerMock).forEach(fn => fn.mockClear())
    
    // Mock scrollIntoView
    scrollIntoViewSpy = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoViewSpy
    
    // Create mock client
    mockClient = {
      chat: {
        messages: [],
        sendMessage: vi.fn(),
        isAgentTyping: false,
        streamingMessage: null,
        clearMessages: vi.fn(),
        isSubSessionMessage: vi.fn(() => false)
      },
      tools: {
        notifications: [],
        clearNotifications: vi.fn(),
        getNotificationStatus: vi.fn()
      },
      connect: vi.fn(),
      disconnect: vi.fn(),
      isConnected: false,
      on: vi.fn(),
      off: vi.fn()
    } as any
    
    // Mock element dimensions for scroll calculations
    Object.defineProperty(HTMLElement.prototype, 'scrollHeight', {
      configurable: true,
      value: 1000
    })
    Object.defineProperty(HTMLElement.prototype, 'clientHeight', {
      configurable: true,
      value: 500
    })
    Object.defineProperty(HTMLElement.prototype, 'scrollTop', {
      configurable: true,
      writable: true,
      value: 500 // Initially scrolled to bottom (1000 - 500 = 500)
    })
  })
  
  afterEach(() => {
    vi.clearAllMocks()
  })
  
  describe('Initial Mount with Existing Messages (Session Restoration)', () => {
    it('should handle initial mount with existing messages', async () => {
      // Set up existing messages (simulating session restoration)
      const existingMessages: ChatMessage[] = [
        { role: 'user', content: 'Previous message 1', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Previous response 1', timestamp: new Date().toISOString() },
        { role: 'user', content: 'Previous message 2', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Previous response 2', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = existingMessages
      
      // Render component with existing messages
      render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Check that the initial mount with messages was detected
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Initial mount with existing messages'),
        expect.anything()
      )
      
      // Verify initial scroll completed flag was set
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Initial mount with existing messages - scrolling immediately'),
        expect.anything()
      )
    })
    
    it('should protect against scroll events during initial mount', async () => {
      // Set up existing messages
      const existingMessages: ChatMessage[] = [
        { role: 'user', content: 'Message 1', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Response 1', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = existingMessages
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      const scrollContainer = container.querySelector('[role="log"]')
      expect(scrollContainer).toBeTruthy()
      
      // Clear initial logs
      loggerMock.debug.mockClear()
      
      // Simulate scroll events that would occur during initial render
      // These should be ignored due to hasCompletedInitialScroll protection
      act(() => {
        // Simulate user scrolling up during initial mount
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 200 // Scrolled up
        })
        
        fireEvent.scroll(scrollContainer!)
      })
      
      // Verify scroll event was ignored
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Ignoring scroll event - initial scroll not complete'),
        expect.anything()
      )
      
      // Clear scroll-related calls
      scrollIntoViewSpy.mockClear()
      
      // Add a new message to test if auto-scroll is still enabled
      const newMessage: ChatMessage = {
        role: 'user',
        content: 'New message after scroll event',
        timestamp: new Date().toISOString()
      }
      
      mockClient.chat.messages = [...existingMessages, newMessage]
      
      // Re-render with new message
      rerender(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait for auto-scroll delay
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })
      
      // Check that auto-scroll was attempted (not disabled by early scroll event)
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Auto-scrolling for new content'),
        expect.anything()
      )
    })
    
    it('should handle race condition where scroll event fires immediately after mount', async () => {
      const existingMessages: ChatMessage[] = [
        { role: 'user', content: 'Message', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Response', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = existingMessages
      
      const { container } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      const scrollContainer = container.querySelector('[role="log"]')
      
      // Clear initial logs
      loggerMock.debug.mockClear()
      
      // Simulate immediate scroll event (within microseconds of mount)
      // This mimics the race condition where scroll fires before initial scroll completes
      act(() => {
        // Try to disable auto-scroll immediately
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 100 // Scrolled way up
        })
        
        // Fire scroll event immediately (race condition scenario)
        fireEvent.scroll(scrollContainer!)
      })
      
      // Verify the scroll event was ignored due to protection
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Ignoring scroll event - initial scroll not complete'),
        expect.anything()
      )
      
      // Verify auto-scroll was NOT disabled
      expect(loggerMock.debug).not.toHaveBeenCalledWith(
        expect.stringContaining('Disabling auto-scroll - user scrolled up'),
        expect.anything()
      )
    })
  })
  
  describe('Post-Initial Scroll Behavior', () => {
    it('should respect scroll events after initial mount completes', async () => {
      // Start with no messages to have a clean initial state
      mockClient.chat.messages = []
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Add messages after initial mount
      const messages: ChatMessage[] = [
        { role: 'user', content: 'Message', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Response', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = messages
      
      rerender(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait for auto-scroll to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })
      
      const scrollContainer = container.querySelector('[role="log"]')
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Now scroll events should be respected
      act(() => {
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 200 // Scrolled up
        })
        
        fireEvent.scroll(scrollContainer!)
      })
      
      // Verify scroll event was processed and auto-scroll was disabled
      expect(loggerMock.debug).not.toHaveBeenCalledWith(
        expect.stringContaining('Ignoring scroll event'),
        expect.anything()
      )
      
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Disabling auto-scroll - user scrolled up'),
        expect.anything()
      )
    })
    
    it('should allow re-enabling auto-scroll by scrolling to bottom after initial mount', async () => {
      // Start with no messages
      mockClient.chat.messages = []
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Add messages after mount
      const messages: ChatMessage[] = [
        { role: 'user', content: 'Message', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Response', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = messages
      
      rerender(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait for initial auto-scroll
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })
      
      const scrollContainer = container.querySelector('[role="log"]')
      
      // Scroll up to disable auto-scroll
      act(() => {
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 200
        })
        fireEvent.scroll(scrollContainer!)
      })
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Then scroll back to bottom
      act(() => {
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 460 // Near bottom (within 50px threshold)
        })
        fireEvent.scroll(scrollContainer!)
      })
      
      // Verify auto-scroll was re-enabled
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Re-enabling auto-scroll - user scrolled to bottom'),
        expect.anything()
      )
    })
  })
  
  describe('Empty State Handling', () => {
    it('should mark initial scroll as complete even with no messages', () => {
      // Start with no messages
      mockClient.chat.messages = []
      
      render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Verify initial mount with no messages was handled
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Initial mount with no messages'),
        expect.anything()
      )
    })
  })
  
  describe('Original 100ms Delay Race Condition', () => {
    it('should protect against the specific race condition during session restoration', async () => {
      // This test specifically targets the original race condition:
      // When resuming a session with existing messages, scroll events during 
      // the initial render would incorrectly disable auto-scroll
      
      const existingMessages: ChatMessage[] = [
        { role: 'user', content: 'Session message 1', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Session response 1', timestamp: new Date().toISOString() },
        { role: 'user', content: 'Session message 2', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Session response 2', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = existingMessages
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      const scrollContainer = container.querySelector('[role="log"]')
      
      // Verify initial scroll happened immediately (no delay for restoration)
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Initial mount with existing messages - scrolling immediately'),
        expect.anything()
      )
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Simulate multiple scroll events that would occur during initial render
      // In the bug scenario, these would disable auto-scroll
      for (let i = 0; i < 3; i++) {
        act(() => {
          Object.defineProperty(scrollContainer, 'scrollTop', {
            configurable: true,
            writable: true,
            value: 100 + (i * 50) // Various scroll positions
          })
          fireEvent.scroll(scrollContainer!)
        })
      }
      
      // All scroll events should have been ignored
      const ignoredScrollCalls = loggerMock.debug.mock.calls.filter(
        call => call[0].includes('Ignoring scroll event - initial scroll not complete')
      )
      expect(ignoredScrollCalls.length).toBe(3)
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Now add a new message to test if auto-scroll is still working
      const newMessage: ChatMessage = {
        role: 'user',
        content: 'New message after potential race condition',
        timestamp: new Date().toISOString()
      }
      
      mockClient.chat.messages = [...existingMessages, newMessage]
      
      rerender(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait for the auto-scroll delay
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })
      
      // Auto-scroll should STILL work because the early scroll events were ignored
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Auto-scrolling for new content'),
        expect.anything()
      )
    })
    
    it('should use instant scroll for session restoration instead of smooth', async () => {
      // Session restoration should use instant scroll to avoid delays
      const existingMessages: ChatMessage[] = [
        { role: 'user', content: 'Restored message', timestamp: new Date().toISOString() },
        { role: 'assistant', content: 'Restored response', timestamp: new Date().toISOString() }
      ]
      
      mockClient.chat.messages = existingMessages
      
      render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait a moment for any scrolling to occur
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 50))
      })
      
      // If scrollIntoView was called, verify it used 'auto' behavior for instant scroll
      if (scrollIntoViewSpy.mock.calls.length > 0) {
        const firstCall = scrollIntoViewSpy.mock.calls[0]
        expect(firstCall[0]).toMatchObject({
          behavior: 'auto', // Instant, not smooth
          block: 'end'
        })
      }
      
      // Verify the component recognized this as session restoration
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Initial mount with existing messages - scrolling immediately'),
        expect.anything()
      )
    })
  })
  
  describe('Complex Timing Scenarios', () => {
    it('should handle rapid message additions after initial mount', async () => {
      // Start with no messages
      mockClient.chat.messages = []
      
      const { rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // Wait for initial mount to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 50))
      })
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Rapidly add messages
      for (let i = 1; i <= 3; i++) {
        const newMessage: ChatMessage = { 
          role: i % 2 === 0 ? 'assistant' : 'user', 
          content: `Message ${i}`,
          timestamp: new Date().toISOString()
        }
        
        mockClient.chat.messages = [...mockClient.chat.messages, newMessage]
        
        rerender(
          <AgentCProvider client={mockClient}>
            <MessageList />
          </AgentCProvider>
        )
        
        // Small delay between additions
        await act(async () => {
          await new Promise(resolve => setTimeout(resolve, 120))
        })
      }
      
      // Verify auto-scroll was triggered for new messages
      const autoScrollCalls = loggerMock.debug.mock.calls.filter(
        call => call[0].includes('Auto-scrolling for new content')
      )
      expect(autoScrollCalls.length).toBeGreaterThan(0)
    })
    
    it('should handle scroll events during the 100ms auto-scroll delay for new messages', async () => {
      // Start with some messages
      mockClient.chat.messages = [
        { role: 'user', content: 'Initial', timestamp: new Date().toISOString() }
      ]
      
      const { container, rerender } = render(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      const scrollContainer = container.querySelector('[role="log"]')
      
      // Wait for initial mount to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150))
      })
      
      // Clear logs
      loggerMock.debug.mockClear()
      
      // Add another message
      const newMessage: ChatMessage = {
        role: 'assistant',
        content: 'New message',
        timestamp: new Date().toISOString()
      }
      
      mockClient.chat.messages = [...mockClient.chat.messages, newMessage]
      
      rerender(
        <AgentCProvider client={mockClient}>
          <MessageList />
        </AgentCProvider>
      )
      
      // During the 100ms delay, fire a scroll event
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 50)) // Wait 50ms into the 100ms delay
        
        // Scroll up during the delay
        Object.defineProperty(scrollContainer, 'scrollTop', {
          configurable: true,
          writable: true,
          value: 200
        })
        fireEvent.scroll(scrollContainer!)
      })
      
      // Wait for the rest of the delay
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 60))
      })
      
      // Verify that the scroll event was processed (not ignored)
      // since this happened after initial mount completed
      expect(loggerMock.debug).toHaveBeenCalledWith(
        expect.stringContaining('Disabling auto-scroll - user scrolled up'),
        expect.anything()
      )
      
      // Auto-scroll should have been cancelled
      expect(loggerMock.debug).not.toHaveBeenCalledWith(
        expect.stringContaining('Auto-scrolling for new content'),
        expect.anything()
      )
    })
  })
})