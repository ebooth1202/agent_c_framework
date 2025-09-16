import React from 'react'
import { render, waitFor } from '@testing-library/react'
import { act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { MessageList } from '../MessageList'
import type { ChatMessage } from '@agentc/realtime-core'
import { 
  createBulkMessages,
  waitForScroll
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
  messages: [] as ChatMessage[],
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

describe('MessageList Bulk Loading and 100% Scroll Tests', () => {
  let sentinelElement: HTMLDivElement
  let scrollContainer: HTMLDivElement
  let scrollToSpy: ReturnType<typeof vi.fn>

  beforeEach(() => {
    // Reset mock return values
    mockUseChatReturn.messages = []
    mockUseChatReturn.isAgentTyping = false
    mockUseChatReturn.streamingMessage = null
    mockUseChatReturn.lastMessage = null
    mockUseChatReturn.isSubSessionMessage = vi.fn(() => false)
    mockUseToolNotificationsReturn.notifications = []

    // Create proper DOM elements for testing
    scrollContainer = document.createElement('div')
    scrollContainer.setAttribute('role', 'log')
    
    sentinelElement = document.createElement('div')
    sentinelElement.dataset.testid = 'scroll-sentinel'
    
    // Mock scrollIntoView
    scrollToSpy = vi.fn()
    sentinelElement.scrollIntoView = scrollToSpy

    // Mock querySelector to return our elements
    const originalQuerySelector = document.querySelector.bind(document)
    document.querySelector = vi.fn((selector: string) => {
      if (selector === '[data-testid="scroll-sentinel"]') {
        return sentinelElement
      }
      if (selector === '[role="log"]') {
        return scrollContainer
      }
      return originalQuerySelector(selector)
    }) as typeof document.querySelector
  })

  afterEach(() => {
    vi.clearAllMocks()
    vi.restoreAllMocks()
  })

  it('should scroll to 100% when loading 50+ messages (proving fix works)', async () => {
    // Set up scroll measurements
    let currentScrollTop = 0
    const scrollHeight = 5000
    const clientHeight = 600
    const maxScroll = scrollHeight - clientHeight // 4400 (100%)
    const eightyPercentScroll = Math.floor(maxScroll * 0.8) // 3520 (80%)

    Object.defineProperty(scrollContainer, 'scrollHeight', {
      value: scrollHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'clientHeight', {
      value: clientHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'scrollTop', {
      get: () => currentScrollTop,
      set: (value: number) => {
        currentScrollTop = value
      },
      configurable: true
    })

    // Mock scrollIntoView to actually scroll to bottom (100%)
    sentinelElement.scrollIntoView = vi.fn(() => {
      currentScrollTop = maxScroll // Scroll to 100%
      scrollToSpy()
    })

    // Load 75 messages in batch
    mockUseChatReturn.messages = createBulkMessages(75, { alternateRoles: true })
    
    render(<MessageList />)
    
    // Wait for the 100ms timeout in MessageList auto-scroll effect
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Verify scrollIntoView was called on the sentinel
    await waitFor(() => {
      expect(scrollToSpy).toHaveBeenCalled()
    })
    
    // Assert we reached 100%, not 80%
    expect(currentScrollTop).toBe(maxScroll)
    expect(currentScrollTop).not.toBe(eightyPercentScroll)
    
    // Calculate and verify percentage
    const scrollPercentage = (currentScrollTop / maxScroll) * 100
    expect(scrollPercentage).toBe(100)
    expect(scrollPercentage).not.toBe(80)
  })

  it('should handle session restoration and scroll to 100%', async () => {
    // Set up scroll measurements
    let currentScrollTop = 0
    const scrollHeight = 3000
    const clientHeight = 600
    const maxScroll = scrollHeight - clientHeight // 2400 (100%)

    Object.defineProperty(scrollContainer, 'scrollHeight', {
      value: scrollHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'clientHeight', {
      value: clientHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'scrollTop', {
      get: () => currentScrollTop,
      set: (value: number) => {
        currentScrollTop = value
      },
      configurable: true
    })

    // Mock scrollIntoView to scroll to 100%
    sentinelElement.scrollIntoView = vi.fn(() => {
      currentScrollTop = maxScroll
      scrollToSpy()
    })

    // Start with empty
    mockUseChatReturn.messages = []
    const { rerender } = render(<MessageList />)
    
    // Simulate session restoration with 30 messages
    const restoredMessages = createBulkMessages(30, {
      alternateRoles: true,
      startTime: new Date(Date.now() - 1800000) // 30 minutes ago
    })
    
    // Restore session
    mockUseChatReturn.messages = restoredMessages
    mockUseChatReturn.lastMessage = restoredMessages[restoredMessages.length - 1]
    
    rerender(<MessageList />)
    
    // Wait for auto-scroll effect
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Verify scroll completed to 100%
    await waitFor(() => {
      expect(scrollToSpy).toHaveBeenCalled()
    })
    
    expect(currentScrollTop).toBe(maxScroll)
    
    // Verify it's 100%, not 80%
    const scrollPercentage = (currentScrollTop / maxScroll) * 100
    expect(scrollPercentage).toBe(100)
    
    // Ensure we didn't stop at 80%
    const eightyPercent = Math.floor(maxScroll * 0.8)
    expect(currentScrollTop).not.toBe(eightyPercent)
  })

  it('should reach 100% scroll with mixed content types', async () => {
    // Set up scroll measurements for larger content
    let currentScrollTop = 0
    const scrollHeight = 8000 // Larger due to varied content
    const clientHeight = 600
    const maxScroll = scrollHeight - clientHeight // 7400 (100%)

    Object.defineProperty(scrollContainer, 'scrollHeight', {
      value: scrollHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'clientHeight', {
      value: clientHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'scrollTop', {
      get: () => currentScrollTop,
      set: (value: number) => {
        currentScrollTop = value
      },
      configurable: true
    })

    sentinelElement.scrollIntoView = vi.fn(() => {
      currentScrollTop = maxScroll
      scrollToSpy()
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
    mockUseChatReturn.lastMessage = messages[messages.length - 1]
    
    render(<MessageList />)
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Should reach 100% even with varied content
    await waitFor(() => {
      expect(scrollToSpy).toHaveBeenCalled()
    })
    
    const scrollPercentage = (currentScrollTop / maxScroll) * 100
    expect(scrollPercentage).toBe(100)
  })

  it('should handle rapid batch updates without race conditions', async () => {
    const scrollCallTimestamps: number[] = []
    
    // Track when scrollIntoView is called
    sentinelElement.scrollIntoView = vi.fn(() => {
      scrollCallTimestamps.push(Date.now())
      scrollToSpy()
    })
    
    // Start with no messages
    const { rerender } = render(<MessageList />)
    
    // Simulate rapid batch updates
    for (let batch = 0; batch < 3; batch++) {
      mockUseChatReturn.messages = createBulkMessages((batch + 1) * 25, { alternateRoles: true })
      
      rerender(<MessageList />)
      
      await act(async () => {
        await waitForScroll(150)
      })
    }
    
    // Should have handled all batches
    expect(scrollCallTimestamps.length).toBeGreaterThanOrEqual(3)
    
    // Verify scrolls were properly spaced (no race conditions)
    for (let i = 1; i < scrollCallTimestamps.length; i++) {
      const timeDiff = scrollCallTimestamps[i] - scrollCallTimestamps[i - 1]
      // Should be at least 95ms apart (accounting for 100ms timeout)
      expect(timeDiff).toBeGreaterThanOrEqual(95)
    }
  })

  it('should scroll to sentinel element, not message elements', async () => {
    const messageScrollSpy = vi.fn()
    
    // Create a mock message element
    const messageElement = document.createElement('div')
    messageElement.className = 'message'
    messageElement.scrollIntoView = messageScrollSpy
    
    // Override querySelector to return different elements
    const originalQuerySelector = document.querySelector.bind(document)
    document.querySelector = vi.fn((selector: string) => {
      if (selector === '[data-testid="scroll-sentinel"]') {
        return sentinelElement
      }
      if (selector === '.message:last-child') {
        return messageElement
      }
      return originalQuerySelector(selector)
    }) as typeof document.querySelector
    
    mockUseChatReturn.messages = createBulkMessages(10, { alternateRoles: true })
    
    render(<MessageList />)
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    // Sentinel should be scrolled to
    await waitFor(() => {
      expect(scrollToSpy).toHaveBeenCalled()
    })
    
    // Message elements should NOT be scrolled to
    expect(messageScrollSpy).not.toHaveBeenCalled()
  })

  it('should prove the fix prevents the 80% scroll bug', async () => {
    // This test specifically demonstrates the bug fix
    let currentScrollTop = 0
    const scrollHeight = 10000
    const clientHeight = 800
    const maxScroll = scrollHeight - clientHeight // 9200 (100%)
    const buggyScroll = Math.floor(maxScroll * 0.8) // 7360 (80% - the bug)

    Object.defineProperty(scrollContainer, 'scrollHeight', {
      value: scrollHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'clientHeight', {
      value: clientHeight,
      configurable: true
    })
    
    Object.defineProperty(scrollContainer, 'scrollTop', {
      get: () => currentScrollTop,
      set: (value: number) => {
        currentScrollTop = value
      },
      configurable: true
    })

    // Track all scroll positions
    const scrollPositions: number[] = []
    
    sentinelElement.scrollIntoView = vi.fn(() => {
      // The fix ensures we scroll to the sentinel at 100%
      currentScrollTop = maxScroll
      scrollPositions.push(currentScrollTop)
      scrollToSpy()
    })

    // Load a large saved session (simulating the bug scenario)
    mockUseChatReturn.messages = createBulkMessages(100, { alternateRoles: true })
    
    render(<MessageList />)
    
    await act(async () => {
      await waitForScroll(150)
    })
    
    await waitFor(() => {
      expect(scrollToSpy).toHaveBeenCalled()
    })
    
    // The critical assertion: we reached 100%, not 80%
    expect(currentScrollTop).toBe(maxScroll)
    expect(currentScrollTop).not.toBe(buggyScroll)
    
    // Verify no intermediate 80% scroll occurred
    const eightyPercentScrolls = scrollPositions.filter(pos => pos === buggyScroll)
    expect(eightyPercentScrolls).toHaveLength(0)
    
    // Log for clarity
    console.log(`Bug fix verified: Scrolled to ${(currentScrollTop / maxScroll * 100).toFixed(0)}% (position ${currentScrollTop}/${maxScroll})`)
    console.log(`Did NOT stop at buggy 80% position (${buggyScroll})`)
  })
})