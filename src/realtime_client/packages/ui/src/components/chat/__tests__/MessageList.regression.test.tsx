import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach, MockedFunction } from 'vitest'
import { MessageList } from '../MessageList'
import * as AgentCReact from '@agentc/realtime-react'
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

// Mock the hooks module
vi.mock('@agentc/realtime-react', () => ({
  AgentCProvider: ({ children }: any) => children,
  useChat: vi.fn(),
  useToolNotifications: vi.fn()
}))

describe('MessageList Regression Tests', () => {
  let mockMessages: ChatMessage[]
  let mockUseChat: MockedFunction<typeof AgentCReact.useChat>
  let mockUseToolNotifications: MockedFunction<typeof AgentCReact.useToolNotifications>

  beforeEach(() => {
    // Get the mocked functions
    mockUseChat = vi.mocked(AgentCReact.useChat)
    mockUseToolNotifications = vi.mocked(AgentCReact.useToolNotifications)
    
    // Initial messages
    mockMessages = [
      { role: 'user' as const, content: 'Hello', timestamp: new Date().toISOString() },
      { role: 'assistant' as const, content: 'Hi there!', timestamp: new Date().toISOString() }
    ]

    // Set up default mock return values
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: mockMessages[mockMessages.length - 1] || null,
      getMessagesByRole: vi.fn((role: string) => mockMessages.filter(m => m.role === role)),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    mockUseToolNotifications.mockReturnValue({
      notifications: [],
      clearNotifications: vi.fn(),
      getNotificationStatus: vi.fn()
    } as any)

    // Mock scrollIntoView
    Element.prototype.scrollIntoView = vi.fn()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render messages correctly', () => {
    render(<MessageList />)

    // Messages should be rendered
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Hi there!')).toBeInTheDocument()
  })

  it('should show empty state when no messages', () => {
    mockUseChat.mockReturnValue({
      messages: [],
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: null,
      getMessagesByRole: vi.fn(() => []),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    render(<MessageList />)

    expect(screen.getByText('No messages yet')).toBeInTheDocument()
    expect(screen.getByText('Start a conversation to see messages appear here')).toBeInTheDocument()
  })

  it('should render custom empty state component', () => {
    mockUseChat.mockReturnValue({
      messages: [],
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: null,
      getMessagesByRole: vi.fn(() => []),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    const customEmpty = <div>Custom empty state</div>

    render(<MessageList emptyStateComponent={customEmpty} />)

    expect(screen.getByText('Custom empty state')).toBeInTheDocument()
  })

  it('should show typing indicator when agent is typing', () => {
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: true,
      streamingMessage: null,
      error: null,
      lastMessage: mockMessages[mockMessages.length - 1],
      getMessagesByRole: vi.fn((role: string) => mockMessages.filter(m => m.role === role)),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    const { container } = render(<MessageList />)

    // Typing indicator should be visible - look for the container
    const typingIndicator = container.querySelector('[role="status"][aria-label="Assistant is typing"]')
    expect(typingIndicator).toBeInTheDocument()
    
    // Check for typing dots (default variant is dots with bounce animation)
    const typingDots = container.querySelectorAll('[style*="typing-bounce"]')
    expect(typingDots).toHaveLength(3)
  })

  it('should not show typing indicator when streaming', () => {
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: true,
      streamingMessage: {
        role: 'assistant' as const,
        content: 'Streaming...'
      },
      error: null,
      lastMessage: mockMessages[mockMessages.length - 1],
      getMessagesByRole: vi.fn((role: string) => mockMessages.filter(m => m.role === role)),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    const { container } = render(<MessageList />)

    // Typing indicator should not be visible when streaming
    const typingIndicator = container.querySelector('[role="status"][aria-label="Assistant is typing"]')
    expect(typingIndicator).not.toBeInTheDocument()
    
    // Streaming message should be visible
    expect(screen.getByText('Streaming...')).toBeInTheDocument()
  })

  it('should render tool notifications', () => {
    mockUseToolNotifications.mockReturnValue({
      notifications: [
        {
          id: 'tool-1',
          toolName: 'search',
          status: 'executing' as const,
          timestamp: new Date(),
          arguments: JSON.stringify({ query: 'test' })
        }
      ],
      clearNotifications: vi.fn(),
      getNotificationStatus: vi.fn()
    } as any)

    render(<MessageList />)

    // Tool notification should be visible with the status text
    expect(screen.getByText('Agent is using search')).toBeInTheDocument()
  })

  it('should handle subsession dividers', () => {
    const isSubSessionMessage = vi.fn((msg) => {
      // Mark second message as subsession
      return msg === mockMessages[1]
    })

    mockUseChat.mockReturnValue({
      messages: mockMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: mockMessages[mockMessages.length - 1],
      getMessagesByRole: vi.fn((role: string) => mockMessages.filter(m => m.role === role)),
      isSubSessionMessage
    } as any)

    render(<MessageList />)

    // Subsession divider should be rendered
    const dividers = screen.getAllByText(/Subsession/)
    expect(dividers.length).toBeGreaterThan(0)
  })

  it('should respect showTimestamps prop', () => {
    const timestamp = new Date().toISOString()
    const messagesWithTimestamp = [
      { role: 'user' as const, content: 'Test', timestamp }
    ]

    mockUseChat.mockReturnValue({
      messages: messagesWithTimestamp,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: messagesWithTimestamp[0],
      getMessagesByRole: vi.fn(() => messagesWithTimestamp),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    const { container, rerender } = render(<MessageList showTimestamps={true} />)

    // Timestamp should be visible when enabled - look for Clock icon (svg)
    // The MessageFooter shows timestamp with a Clock icon from lucide
    const clockIcon = container.querySelector('[class*="lucide-clock"]')
    expect(clockIcon).toBeInTheDocument()
    
    // Also check for the formatted time string
    const date = new Date(timestamp)
    const formattedTime = date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
    expect(screen.getByText(formattedTime)).toBeInTheDocument()

    // Re-render without timestamps
    rerender(<MessageList showTimestamps={false} />)

    // Timestamp should not be visible when disabled
    const noClockIcon = container.querySelector('[class*="lucide-clock"]')
    expect(noClockIcon).not.toBeInTheDocument()
    const noTimeText = screen.queryByText(formattedTime)
    expect(noTimeText).not.toBeInTheDocument()
  })

  it('should respect maxHeight prop', () => {
    const { container } = render(<MessageList maxHeight="400px" />)

    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).toHaveStyle({ maxHeight: '400px' })
  })

  it('should handle maxHeight="none"', () => {
    const { container } = render(<MessageList maxHeight="none" />)

    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).not.toHaveStyle({ maxHeight: expect.any(String) })
  })

  it('should apply custom className', () => {
    const { container } = render(<MessageList className="custom-class" />)

    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).toHaveClass('custom-class')
  })

  it('should have proper ARIA attributes', () => {
    const { container } = render(<MessageList />)

    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer).toHaveAttribute('aria-label', 'Chat messages')
    expect(scrollContainer).toHaveAttribute('aria-live', 'polite')
  })

  it('should forward ref correctly', () => {
    const ref = React.createRef<HTMLDivElement>()

    render(<MessageList ref={ref} />)

    expect(ref.current).toBeInstanceOf(HTMLElement)
    expect(ref.current).toHaveAttribute('role', 'log')
  })

  it('should animate messages on entry', () => {
    render(<MessageList />)

    // Check for animation classes
    const messageElements = screen.getByText('Hello').closest('.animate-in')
    expect(messageElements).toHaveClass('slide-in-from-bottom-2')
    expect(messageElements).toHaveClass('duration-200')
  })

  it('should handle message content as string', () => {
    const stringMessages = [
      { role: 'user' as const, content: 'String content' }
    ]

    mockUseChat.mockReturnValue({
      messages: stringMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: stringMessages[0],
      getMessagesByRole: vi.fn(() => stringMessages),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    render(<MessageList />)

    expect(screen.getByText('String content')).toBeInTheDocument()
  })

  it('should handle message content as array', () => {
    const arrayMessages = [
      { 
        role: 'user' as const, 
        content: [
          { type: 'text', text: 'Array content' }
        ] as any
      }
    ]

    mockUseChat.mockReturnValue({
      messages: arrayMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: arrayMessages[0],
      getMessagesByRole: vi.fn(() => arrayMessages),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    render(<MessageList />)

    expect(screen.getByText('Array content')).toBeInTheDocument()
  })

  it('should clean up event listeners on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(HTMLElement.prototype, 'removeEventListener')

    const { unmount } = render(<MessageList />)

    unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
    
    removeEventListenerSpy.mockRestore()
  })

  it('should clear timeout on unmount', async () => {
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')

    const { unmount } = render(<MessageList />)

    // Unmount quickly before timeout fires
    unmount()

    expect(clearTimeoutSpy).toHaveBeenCalled()
    
    clearTimeoutSpy.mockRestore()
  })

  it('should handle multiple tool notifications', () => {
    mockUseToolNotifications.mockReturnValue({
      notifications: [
        {
          id: 'tool-1',
          toolName: 'search',
          status: 'executing' as const,
          timestamp: new Date(),
          arguments: JSON.stringify({ query: 'test' })
        },
        {
          id: 'tool-2',
          toolName: 'calculate',
          status: 'complete' as const,
          timestamp: new Date(),
          arguments: JSON.stringify({ expression: '1+1' })
        },
        {
          id: 'tool-3',
          toolName: 'analyze',
          status: 'preparing' as const,
          timestamp: new Date(),
          arguments: JSON.stringify({ data: 'sample' })
        }
      ],
      clearNotifications: vi.fn(),
      getNotificationStatus: vi.fn()
    } as any)

    render(<MessageList />)

    // All tool notifications should be visible with their status text
    expect(screen.getByText('Agent is using search')).toBeInTheDocument()
    expect(screen.getByText('Completed calculate')).toBeInTheDocument()
    expect(screen.getByText('Agent is preparing to use analyze')).toBeInTheDocument()
  })

  it('should not show typing indicator when tool notifications are active', () => {
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: true,
      streamingMessage: null,
      error: null,
      lastMessage: mockMessages[mockMessages.length - 1],
      getMessagesByRole: vi.fn((role: string) => mockMessages.filter(m => m.role === role)),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    mockUseToolNotifications.mockReturnValue({
      notifications: [
        {
          id: 'tool-1',
          toolName: 'search',
          status: 'executing' as const,
          timestamp: new Date(),
          arguments: JSON.stringify({ query: 'test' })
        }
      ],
      clearNotifications: vi.fn(),
      getNotificationStatus: vi.fn()
    } as any)

    const { container } = render(<MessageList />)

    // Typing indicator should not be visible when tools are active
    const typingIndicator = container.querySelector('[role="status"][aria-label="Assistant is typing"]')
    expect(typingIndicator).not.toBeInTheDocument()
    
    // Tool notification should be visible with its status text
    expect(screen.getByText('Agent is using search')).toBeInTheDocument()
  })

  it('should handle undefined timestamps gracefully', () => {
    const noTimestampMessages = [
      { role: 'user' as const, content: 'No timestamp message' },
      { role: 'assistant' as const, content: 'Also no timestamp' }
    ]

    mockUseChat.mockReturnValue({
      messages: noTimestampMessages,
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: noTimestampMessages[noTimestampMessages.length - 1],
      getMessagesByRole: vi.fn((role: string) => noTimestampMessages.filter(m => m.role === role)),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    expect(() => {
      render(<MessageList />)
    }).not.toThrow()

    expect(screen.getByText('No timestamp message')).toBeInTheDocument()
    expect(screen.getByText('Also no timestamp')).toBeInTheDocument()
  })

  it('should render sentinel element even in empty state', () => {
    mockUseChat.mockReturnValue({
      messages: [],
      currentSession: null,
      currentSessionId: null,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isSending: false,
      isAgentTyping: false,
      streamingMessage: null,
      error: null,
      lastMessage: null,
      getMessagesByRole: vi.fn(() => []),
      isSubSessionMessage: vi.fn(() => false)
    } as any)

    const { container } = render(<MessageList />)

    // Sentinel should exist even with no messages
    const sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(sentinel).toBeInTheDocument()
    expect(sentinel).toHaveStyle({ height: '1px', visibility: 'hidden' })
  })
})