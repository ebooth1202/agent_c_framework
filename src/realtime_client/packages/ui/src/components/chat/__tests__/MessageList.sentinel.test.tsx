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

// Mock the hooks we need
const mockUseChatReturn = {
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
}

const mockUseToolNotificationsReturn = {
  notifications: [],
  clearNotifications: vi.fn(),
  getNotificationStatus: vi.fn()
}

vi.mock('@agentc/realtime-react', () => ({
  AgentCProvider: ({ children }: any) => children,
  useChat: () => mockUseChatReturn,
  useToolNotifications: () => mockUseToolNotificationsReturn
}))

describe('Sentinel Element Implementation', () => {
  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render sentinel element at bottom of message list', () => {
    const { container } = render(
      <MessageList />
    )
    
    const sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(sentinel).toBeInTheDocument()
    expect(sentinel).toHaveStyle({ 
      height: '1px', 
      visibility: 'hidden'
    })
    
    // Verify it's within the scroll container
    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer?.querySelector('[data-testid="scroll-sentinel"]')).toBeTruthy()
  })

  it('should maintain sentinel position during all content changes', async () => {
    mockUseChatReturn.messages = [
      { role: 'user', content: 'Initial message' }
    ]

    const { container, rerender } = render(
      <MessageList />
    )

    const scrollContainer = container.querySelector('[role="log"]')
    let sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    
    // Verify sentinel is last child initially
    expect(scrollContainer?.lastElementChild).toBe(sentinel)

    // Add a message
    mockUseChatReturn.messages = [
      { role: 'user', content: 'Initial message' },
      { role: 'assistant', content: 'Response' }
    ]
    rerender(
      <MessageList />
    )

    sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(scrollContainer?.lastElementChild).toBe(sentinel)

    // Add streaming message
    mockUseChatReturn.streamingMessage = { role: 'assistant', content: 'Streaming...' }
    rerender(
      <MessageList />
    )

    sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(scrollContainer?.lastElementChild).toBe(sentinel)

    // Add typing indicator
    mockUseChatReturn.isAgentTyping = true
    mockUseChatReturn.streamingMessage = null
    rerender(
      <MessageList />
    )

    sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(scrollContainer?.lastElementChild).toBe(sentinel)
  })

  it('should scroll to sentinel instead of last message', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const messageScrollSpy = vi.fn()
    
    // Mock message element scroll
    const originalScrollIntoView = Element.prototype.scrollIntoView
    Element.prototype.scrollIntoView = vi.fn(function() {
      if (this !== sentinel) {
        messageScrollSpy()
      }
    })
    
    mockUseChatReturn.messages = [
      { role: 'user', content: 'Test message' }
    ]
    
    render(
      <MessageList />
    )
    
    await waitFor(() => {
      expect(scrollSpy).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'end'
      })
    })
    
    // Should NOT scroll to message elements
    expect(messageScrollSpy).not.toHaveBeenCalled()
    
    Element.prototype.scrollIntoView = originalScrollIntoView
    cleanup()
  })

  it('should handle sentinel with empty message list', () => {
    mockUseChatReturn.messages = []
    
    const { container } = render(
      <MessageList />
    )
    
    // Sentinel should exist even with no messages
    const sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(sentinel).toBeInTheDocument()
    
    // Should be child of scroll container
    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer?.querySelector('[data-testid="scroll-sentinel"]')).toBeTruthy()
  })
})

describe('Bulk Message Loading', () => {
  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should scroll to 100% when loading 50+ messages at once', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 5000,
      clientHeight: 600,
      initialScrollTop: 0
    })
    
    // Mock sentinel scrollIntoView to actually update scroll position
    sentinel.scrollIntoView = vi.fn(() => {
      scrollMetrics.scrollToBottom()
      scrollSpy()
    })
    
    // Load 75 messages in batch
    mockUseChatReturn.messages = createBulkMessages(75, { alternateRoles: true })
    
    render(
      <MessageList />
    )
    
    // Wait for React batching and scroll timeout
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Calculate positions
    const expectedFullScroll = scrollMetrics.getMaxScroll() // 4400 (100%)
    const eightyPercentScroll = Math.floor(expectedFullScroll * 0.8) // 3520 (80%)
    
    // Assert we reached 100%, not 80%
    expect(scrollMetrics.getScrollTop()).toBe(expectedFullScroll)
    expect(scrollMetrics.getScrollTop()).not.toBe(eightyPercentScroll)
    
    // Verify percentage
    expect(scrollMetrics.getScrollPercentage()).toBe(100)
    
    cleanup()
  })

  it('should handle batch rendering without race conditions', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollCalls: number[] = []
    
    // Track when scrollIntoView is called
    sentinel.scrollIntoView = vi.fn(() => {
      scrollCalls.push(Date.now())
      scrollSpy()
    })
    
    // Start with no messages
    const { rerender } = render(
      <MessageList />
    )
    
    // Simulate rapid batch updates
    for (let batch = 0; batch < 3; batch++) {
      mockUseChatReturn.messages = createBulkMessages((batch + 1) * 25, { alternateRoles: true })
      
      rerender(
        <MessageList />
      )
      
      await act(async () => {
        await waitForScroll(150)
      })
    }
    
    // Should have handled all batches
    expect(scrollCalls.length).toBeGreaterThanOrEqual(3)
    
    // Verify scrolls were properly spaced (no race conditions)
    for (let i = 1; i < scrollCalls.length; i++) {
      const timeDiff = scrollCalls[i] - scrollCalls[i - 1]
      expect(timeDiff).toBeGreaterThanOrEqual(95) // Account for 100ms timeout
    }
    
    cleanup()
  })

  it('should complete scroll for mixed content types', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 8000, // Larger due to varied content
      clientHeight: 600,
      initialScrollTop: 0
    })
    
    sentinel.scrollIntoView = vi.fn(() => {
      scrollMetrics.scrollToBottom()
      scrollSpy()
    })
    
    // Create messages with varied content
    const messages: ChatMessage[] = [
      { role: 'user', content: 'Short text' },
      { role: 'assistant', content: '```javascript\nconst longCode = () => {\n  // Multiple lines\n  // of code\n  return "test";\n};\n```' },
      { role: 'user', content: '# Heading\n\nParagraph with **bold** and _italic_ text.\n\n- List item 1\n- List item 2\n- List item 3' },
      { role: 'assistant', content: 'A very long response that contains multiple paragraphs.\n\nThis is the second paragraph with more content to ensure proper height calculation.\n\nAnd a third paragraph for good measure.' },
      ...createBulkMessages(46, { alternateRoles: true }) // Add 46 more for total of 50
    ]
    
    mockUseChatReturn.messages = messages
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Should reach 100% even with varied content
    expect(scrollMetrics.getScrollPercentage()).toBe(100)
    expect(scrollSpy).toHaveBeenCalled()
    
    cleanup()
  })

  it('should handle messages with varying heights', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    // Create messages with significantly different heights
    const messages: ChatMessage[] = []
    for (let i = 0; i < 60; i++) {
      const contentLength = (i % 5) + 1 // Varies from 1 to 5
      let content = ''
      
      for (let j = 0; j < contentLength; j++) {
        content += `Line ${j} of message ${i}.\n`
      }
      
      messages.push({
        role: i % 2 === 0 ? 'user' : 'assistant',
        content,
        timestamp: new Date().toISOString()
      })
    }
    
    mockUseChatReturn.messages = messages
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Verify sentinel was scrolled to
    expect(scrollSpy).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
    
    cleanup()
  })
})

describe('Session Restoration', () => {
  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should scroll to 100% when restoring saved session', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 3000,
      clientHeight: 600,
      initialScrollTop: 0
    })
    
    // Track scroll calls with positions
    const scrollCalls: { time: number; percentage: number }[] = []
    
    sentinel.scrollIntoView = vi.fn(() => {
      scrollMetrics.scrollToBottom()
      scrollCalls.push({
        time: Date.now(),
        percentage: scrollMetrics.getScrollPercentage()
      })
      scrollSpy()
    })
    
    // Start with empty
    mockUseChatReturn.messages = []
    const { rerender } = render(
      <MessageList />
    )
    
    // Simulate session restoration with 30 messages
    const restoredMessages = createBulkMessages(30, {
      alternateRoles: true,
      startTime: new Date(Date.now() - 1800000) // 30 minutes ago
    })
    
    // Restore session
    mockUseChatReturn.messages = restoredMessages
    
    rerender(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Verify scroll completed to 100%
    expect(scrollCalls.length).toBeGreaterThan(0)
    const lastScroll = scrollCalls[scrollCalls.length - 1]
    expect(lastScroll.percentage).toBe(100)
    
    // Ensure no 80% scroll
    const eightyPercentScrolls = scrollCalls.filter(s => Math.round(s.percentage) === 80)
    expect(eightyPercentScrolls).toHaveLength(0)
    
    cleanup()
  })

  it('should handle restoration with streaming in progress', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    // Restore session with streaming
    mockUseChatReturn.messages = createBulkMessages(20, { alternateRoles: true })
    mockUseChatReturn.streamingMessage = {
      role: 'assistant',
      content: 'Currently streaming this response...',
      timestamp: new Date().toISOString()
    }
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Should scroll to sentinel even with streaming
    expect(scrollSpy).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'end'
    })
    
    cleanup()
  })

  it('should work with subsession dividers present', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    // Set up subsession detection
    const messages = createBulkMessages(25, { alternateRoles: true })
    mockUseChatReturn.messages = messages
    mockUseChatReturn.isSubSessionMessage = vi.fn((msg) => {
      // Mark every 5th message as subsession
      const index = messages.indexOf(msg)
      return index > 0 && index % 5 === 0
    })
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Should still scroll to sentinel with subsessions
    expect(scrollSpy).toHaveBeenCalled()
    
    cleanup()
  })

  it('should handle rapid session switches', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    
    const { rerender } = render(
      <MessageList />
    )
    
    // Rapidly switch between sessions
    const sessions = [
      createBulkMessages(10, { alternateRoles: true }),
      createBulkMessages(20, { alternateRoles: true }),
      createBulkMessages(15, { alternateRoles: true }),
      createBulkMessages(30, { alternateRoles: true })
    ]
    
    for (const session of sessions) {
      mockUseChatReturn.messages = session
      
      rerender(
        <MessageList />
      )
      
      await act(async () => {
        await waitForScroll(50) // Shorter wait for rapid switching
      })
    }
    
    // Should have scrolled for each session
    expect(scrollSpy).toHaveBeenCalledTimes(sessions.length)
    
    cleanup()
  })
})

describe('Scroll Position Verification', () => {
  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should reach exactly 100% scroll, not 80%', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 5000,
      clientHeight: 800,
      initialScrollTop: 0
    })
    
    // Mock sentinel to scroll to 100%
    sentinel.scrollIntoView = vi.fn(() => {
      scrollMetrics.scrollToBottom()
      scrollSpy()
    })
    
    mockUseChatReturn.messages = createBulkMessages(50, { alternateRoles: true })
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    const maxScroll = scrollMetrics.getMaxScroll()
    const currentScroll = scrollMetrics.getScrollTop()
    const scrollPercentage = scrollMetrics.getScrollPercentage()
    
    // Verify exact 100% scroll
    expect(currentScroll).toBe(maxScroll)
    expect(scrollPercentage).toBe(100)
    
    // Explicitly verify it's not 80%
    const eightyPercentScroll = Math.floor(maxScroll * 0.8)
    expect(currentScroll).not.toBe(eightyPercentScroll)
    expect(scrollPercentage).not.toBe(80)
    
    cleanup()
  })

  it('should verify scroll completion percentage', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 4000,
      clientHeight: 600,
      initialScrollTop: 0
    })
    
    const percentageHistory: number[] = []
    
    sentinel.scrollIntoView = vi.fn(() => {
      // Simulate gradual scrolling
      const steps = [0.2, 0.4, 0.6, 0.8, 1.0]
      const maxScroll = scrollMetrics.getMaxScroll()
      
      steps.forEach(step => {
        scrollMetrics.setScrollTop(Math.floor(maxScroll * step))
        percentageHistory.push(scrollMetrics.getScrollPercentage())
      })
      
      scrollSpy()
    })
    
    mockUseChatReturn.messages = createBulkMessages(40, { alternateRoles: true })
    
    render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Verify we reached 100%
    const finalPercentage = percentageHistory[percentageHistory.length - 1]
    expect(finalPercentage).toBe(100)
    
    // Verify progression through percentages
    expect(percentageHistory).toContain(20)
    expect(percentageHistory).toContain(40)
    expect(percentageHistory).toContain(60)
    expect(percentageHistory).toContain(80)
    expect(percentageHistory).toContain(100)
    
    cleanup()
  })

  it('should measure actual vs expected scroll positions', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollMetrics = mockScrollMeasurements({
      scrollHeight: 6000,
      clientHeight: 700,
      initialScrollTop: 0
    })
    
    const actualPositions: number[] = []
    const expectedPosition = scrollMetrics.getMaxScroll() // 5300
    
    sentinel.scrollIntoView = vi.fn(() => {
      // Simulate multiple scroll attempts
      actualPositions.push(scrollMetrics.getScrollTop())
      
      // First attempt: 80% (incorrect)
      if (actualPositions.length === 1) {
        scrollMetrics.scrollTo80Percent()
      }
      // Second attempt: 100% (correct)
      else {
        scrollMetrics.scrollToBottom()
      }
      
      scrollSpy()
    })
    
    mockUseChatReturn.messages = createBulkMessages(60, { alternateRoles: true })
    
    const { rerender } = render(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Simulate a correction (if 80% was detected)
    if (scrollMetrics.getScrollPercentage() < 100) {
      rerender(
        <MessageList />
      )
      
      await act(async () => {
        await waitForScroll(150)
      })
    }
    
    // Verify final position is correct
    const finalPosition = scrollMetrics.getScrollTop()
    expect(finalPosition).toBe(expectedPosition)
    
    // Verify we corrected from 80% if needed
    if (actualPositions.length > 1) {
      const firstAttempt = actualPositions[0]
      const eightyPercent = Math.floor(expectedPosition * 0.8)
      
      // If first attempt was 80%, verify it was corrected
      if (Math.abs(firstAttempt - eightyPercent) < 10) {
        expect(finalPosition).toBeGreaterThan(firstAttempt)
      }
    }
    
    cleanup()
  })
})

describe('Edge Cases and Performance', () => {
  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should handle empty list with sentinel', () => {
    mockUseChatReturn.messages = []
    
    const { container } = render(
      <MessageList />
    )
    
    // Sentinel should exist even with no messages
    const sentinel = container.querySelector('[data-testid="scroll-sentinel"]')
    expect(sentinel).toBeInTheDocument()
    
    // Should be child of scroll container
    const scrollContainer = container.querySelector('[role="log"]')
    expect(scrollContainer?.querySelector('[data-testid="scroll-sentinel"]')).toBeTruthy()
    
    // Should be the last child even with empty state
    expect(scrollContainer?.lastElementChild).toBe(sentinel)
  })

  it('should handle rapid message additions', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const scrollCalls: number[] = []
    
    sentinel.scrollIntoView = vi.fn(() => {
      scrollCalls.push(Date.now())
      scrollSpy()
    })
    
    const { rerender } = render(
      <MessageList />
    )
    
    // Rapidly add messages
    for (let i = 0; i < 10; i++) {
      mockUseChatReturn.messages = Array.from({ length: i + 1 }, (_, j) => ({
        role: j % 2 === 0 ? 'user' : 'assistant',
        content: `Rapid message ${j}`,
        timestamp: new Date().toISOString()
      }))
      
      rerender(
        <MessageList />
      )
      
      await act(async () => {
        await waitForScroll(20)
      })
    }
    
    // Should handle all updates smoothly
    expect(scrollCalls.length).toBeGreaterThan(0)
    
    // Verify no errors or skipped scrolls
    scrollCalls.forEach((time, index) => {
      if (index > 0) {
        const timeDiff = time - scrollCalls[index - 1]
        expect(timeDiff).toBeGreaterThanOrEqual(15) // Min time between scrolls
      }
    })
    
    cleanup()
  })

  it('should complete scroll within 150ms', async () => {
    const { sentinel, scrollSpy, cleanup } = createSentinelMocks()
    const timer = mockPerformanceTimer()
    
    timer.start()
    
    sentinel.scrollIntoView = vi.fn(() => {
      timer.measure('scroll')
      scrollSpy()
    })
    
    mockUseChatReturn.messages = createBulkMessages(100, { alternateRoles: true })
    
    render(
      <MessageList />
    )
    
    await waitFor(() => {
      expect(scrollSpy).toHaveBeenCalled()
    }, { timeout: 200 })
    
    const measurements = timer.getMeasurements()
    expect(measurements.length).toBeGreaterThan(0)
    
    const scrollTime = measurements[0].duration
    expect(scrollTime).toBeLessThanOrEqual(150)
    expect(scrollTime).toBeGreaterThanOrEqual(95) // Account for 100ms timeout
    
    timer.cleanup()
    cleanup()
  })

  it('should maintain user scroll position when auto-scroll disabled', async () => {
    const mockScrollTop = 200
    
    Object.defineProperty(HTMLElement.prototype, 'scrollTop', {
      writable: true,
      configurable: true,
      value: mockScrollTop
    })
    
    Object.defineProperty(HTMLElement.prototype, 'scrollHeight', {
      configurable: true,
      value: 2000
    })
    
    mockUseChatReturn.messages = [{ role: 'user', content: 'Initial' }]
    
    const { container, rerender } = render(
      <MessageList />
    )
    
    const scrollContainer = container.querySelector('[role="log"]')
    
    // Simulate user scrolling up
    act(() => {
      fireEvent.scroll(scrollContainer!, {
        target: { scrollTop: mockScrollTop }
      })
    })
    
    // Add new message
    mockUseChatReturn.messages = [
      { role: 'user', content: 'Initial' },
      { role: 'assistant', content: 'New message' }
    ]
    rerender(
      <MessageList />
    )
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Should maintain user position (no auto-scroll)
    expect(scrollContainer?.scrollTop).toBe(mockScrollTop)
  })
})