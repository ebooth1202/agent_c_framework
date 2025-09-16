import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { MessageList } from '../MessageList'
import { AgentCProvider } from '@agentc/realtime-react'
import { RealtimeClient } from '@agentc/realtime-core'
import type { ChatMessage } from '@agentc/realtime-core'
import { 
  createSentinelMocks, 
  mockScrollMeasurements, 
  createBulkMessages,
  waitForScroll,
  mockPerformanceTimer
} from '../__mocks__/sentinelTestUtils'

// Mock the Logger to prevent console output
vi.mock('../../../utils/logger', () => ({
  Logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}))

describe('MessageList Auto-Scroll Behavior', () => {
  let mockClient: RealtimeClient
  let mockMessages: ChatMessage[]
  
  beforeEach(() => {
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
    
    // Initial messages
    mockMessages = [
      { role: 'user', content: 'Hello', timestamp: new Date().toISOString() },
      { role: 'assistant', content: 'Hi there!', timestamp: new Date().toISOString() }
    ]
    
    // Mock scrollIntoView
    Element.prototype.scrollIntoView = vi.fn()
    
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
  
  it('should auto-scroll to sentinel element when new messages arrive', async () => {
    // Set up sentinel mocks
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    mockClient.chat.messages = mockMessages
    
    const { rerender } = render(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Add a new message
    const newMessage: ChatMessage = {
      role: 'user',
      content: 'New message',
      timestamp: new Date().toISOString()
    }
    
    mockClient.chat.messages = [...mockMessages, newMessage]
    
    // Re-render with new messages
    rerender(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Wait for auto-scroll to trigger
    await waitFor(() => {
      expect(scrollSpy).toHaveBeenCalled()
    }, { timeout: 200 })
    
    // Verify smooth scrolling was used on the sentinel
    expect(scrollSpy).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
    
    // Verify the sentinel was the target, not other elements
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
    
    cleanup()
  })
  
  it('should disable auto-scroll when user scrolls up', async () => {
    mockClient.chat.messages = mockMessages
    
    const { container, rerender } = render(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).toBeTruthy()
    
    // Simulate user scrolling up (away from bottom)
    act(() => {
      Object.defineProperty(scrollContainer, 'scrollTop', {
        configurable: true,
        writable: true,
        value: 200 // Scrolled up (distance from bottom = 1000 - 200 - 500 = 300px)
      })
      
      fireEvent.scroll(scrollContainer!)
    })
    
    // Clear previous calls
    vi.clearAllMocks()
    
    // Add a new message
    const newMessage: ChatMessage = {
      role: 'assistant',
      content: 'Should not auto-scroll',
      timestamp: new Date().toISOString()
    }
    
    mockClient.chat.messages = [...mockMessages, newMessage]
    
    // Re-render with new message
    rerender(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Wait a bit to ensure no auto-scroll happens
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })
    
    // Should NOT auto-scroll since user scrolled up
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
  })
  
  it('should re-enable auto-scroll when user scrolls back to bottom', async () => {
    mockClient.chat.messages = mockMessages
    
    const { container, rerender } = render(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).toBeTruthy()
    
    // First, scroll up to disable auto-scroll
    act(() => {
      Object.defineProperty(scrollContainer, 'scrollTop', {
        configurable: true,
        writable: true,
        value: 200
      })
      fireEvent.scroll(scrollContainer!)
    })
    
    // Then scroll back to near bottom (within threshold)
    act(() => {
      Object.defineProperty(scrollContainer, 'scrollTop', {
        configurable: true,
        writable: true,
        value: 460 // Distance from bottom = 1000 - 460 - 500 = 40px (within 50px threshold)
      })
      fireEvent.scroll(scrollContainer!)
    })
    
    // Clear previous calls
    vi.clearAllMocks()
    
    // Add a new message
    const newMessage: ChatMessage = {
      role: 'user',
      content: 'Should auto-scroll again',
      timestamp: new Date().toISOString()
    }
    
    mockClient.chat.messages = [...mockMessages, newMessage]
    
    // Re-render with new message
    rerender(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Wait for auto-scroll to trigger
    await waitFor(() => {
      expect(Element.prototype.scrollIntoView).toHaveBeenCalled()
    }, { timeout: 200 })
  })
  
  it('should auto-scroll to sentinel when streaming message appears', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    mockClient.chat.messages = mockMessages
    mockClient.chat.streamingMessage = null
    
    const { rerender } = render(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Clear any initial calls
    vi.clearAllMocks()
    
    // Add streaming message
    mockClient.chat.streamingMessage = {
      role: 'assistant',
      content: 'Streaming...',
      timestamp: new Date().toISOString()
    }
    
    // Re-render with streaming message
    rerender(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Wait for auto-scroll to trigger
    await waitFor(() => {
      expect(scrollSpy).toHaveBeenCalled()
    }, { timeout: 200 })
    
    // Verify sentinel remains the scroll target during streaming
    expect(scrollSpy).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
    
    cleanup()
  })
  
  it('should auto-scroll to sentinel when typing indicator appears', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    mockClient.chat.messages = mockMessages
    mockClient.chat.isAgentTyping = false
    
    const { rerender } = render(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Clear any initial calls
    vi.clearAllMocks()
    
    // Show typing indicator
    mockClient.chat.isAgentTyping = true
    
    // Re-render with typing indicator
    rerender(
      <AgentCProvider client={mockClient}>
        <MessageList />
      </AgentCProvider>
    )
    
    // Wait for auto-scroll to trigger
    await waitFor(() => {
      expect(scrollSpy).toHaveBeenCalled()
    }, { timeout: 200 })
    
    // Verify sentinel is scroll target even with typing indicator
    expect(scrollSpy).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
    
    cleanup()
  })
})