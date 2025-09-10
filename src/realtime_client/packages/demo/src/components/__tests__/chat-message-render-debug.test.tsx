import { vi, describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { ChatInterface } from '../chat/chat-interface'
import { useChat, useConnection } from '@agentc/realtime-react'
import type { ChatMessage } from '@agentc/realtime-core'

// Mock the hooks
vi.mock('@agentc/realtime-react', () => ({
  useChat: vi.fn(),
  useConnection: vi.fn(),
  useVoice: () => ({
    isListening: false,
    startListening: vi.fn(),
    stopListening: vi.fn(),
    toggleListening: vi.fn(),
    isMuted: false,
    toggleMute: vi.fn(),
    audioLevel: 0,
    error: null,
    permissions: { audio: true, microphone: true }
  })
}))

describe('ChatInterface - Problem Session Rendering Debug', () => {
  const mockUseChat = useChat as jest.MockedFunction<typeof useChat>
  const mockUseConnection = useConnection as jest.MockedFunction<typeof useConnection>

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup connection mock
    mockUseConnection.mockReturnValue({
      isConnected: true,
      connectionState: 'connected',
      connect: vi.fn(),
      disconnect: vi.fn(),
      error: null,
      reconnect: vi.fn(),
      statistics: { latency: 0, packetsLost: 0 }
    })
  })

  it('should render messages with exact problem session structure', async () => {
    // Recreate the exact structure from problem_session.json
    const problemMessages: ChatMessage[] = [
      {
        id: 'msg-1',
        role: 'user',
        content: "Cora, I need you to prepare a document that contains all of the models involved in the MessageParam model",
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'msg-2',
        role: 'assistant',
        content: [
          {
            citations: null,
            text: "I'll help you prepare a comprehensive reference document for the MessageParam model and all its related models.",
            type: 'text'
          }
        ] as any,
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'msg-3',
        role: 'assistant',
        content: [
          {
            id: 'toolu_01AQvxhWsPpzi2NNeocS2feA',
            input: {
              path: '//project/temp/anthropic-sdk-python/src/anthropic/types/message_param.py'
            },
            name: 'workspace_read',
            type: 'tool_use'
          }
        ] as any,
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'msg-4',
        role: 'user',
        content: [
          {
            type: 'tool_result',
            tool_use_id: 'toolu_01AQvxhWsPpzi2NNeocS2feA',
            content: '# File generated from our OpenAPI spec...'
          }
        ] as any,
        timestamp: new Date().toISOString(),
        metadata: {}
      }
    ]

    // Add debug logging
    console.log('=== Test: Exact Problem Session Structure ===')
    console.log('Total messages to render:', problemMessages.length)
    problemMessages.forEach((msg, idx) => {
      console.log(`Message ${idx + 1}:`, {
        id: msg.id,
        role: msg.role,
        contentType: Array.isArray(msg.content) ? 'array' : typeof msg.content,
        content: JSON.stringify(msg.content).substring(0, 100)
      })
    })

    // Setup chat mock
    mockUseChat.mockReturnValue({
      messages: problemMessages,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isLoading: false,
      error: null,
      streamingMessage: null,
      abortStream: vi.fn(),
      editMessage: vi.fn(),
      deleteMessage: vi.fn(),
      resubmitMessage: vi.fn()
    })

    const { container, debug } = render(<ChatInterface />)
    
    // Debug output
    console.log('\n=== Rendered HTML ===')
    debug(container, 20000)
    
    // Wait for rendering
    await waitFor(() => {
      const messageElements = container.querySelectorAll('[data-testid*="message"], [data-message], .message, [class*="message"]')
      console.log('\n=== Found message-like elements:', messageElements.length)
      
      messageElements.forEach((el, idx) => {
        console.log(`Element ${idx + 1}:`, {
          testId: el.getAttribute('data-testid'),
          className: el.className,
          textPreview: el.textContent?.substring(0, 50)
        })
      })
    })

    // Check if messages exist in DOM at all
    const allText = container.textContent || ''
    console.log('\n=== Checking for message content in DOM ===')
    
    const firstMessageExists = allText.includes('Cora, I need you to prepare')
    const secondMessageExists = allText.includes("I'll help you prepare")
    const toolUseExists = allText.includes('workspace_read') || allText.includes('toolu_')
    const fourthMessageExists = allText.includes('File generated')
    
    console.log('First message in DOM:', firstMessageExists)
    console.log('Second message in DOM:', secondMessageExists)
    console.log('Third message (tool use) in DOM:', toolUseExists)
    console.log('Fourth message in DOM:', fourthMessageExists)
    
    // Report findings
    if (!firstMessageExists || !secondMessageExists || !toolUseExists) {
      console.log('\n🔴 CRITICAL: First 3 messages are NOT rendering!')
      console.log('The messages are provided to the component but not appearing in DOM')
    }
    
    expect(firstMessageExists).toBe(false) // Expecting failure to confirm the bug
  })

  it('should test message processing with citations field', async () => {
    // Test specifically the citations field issue
    const messagesWithCitations: ChatMessage[] = [
      {
        id: 'test-1',
        role: 'assistant',
        // Message with citations field (like message 2 in problem session)
        content: [
          {
            citations: null,
            text: 'This message has a citations field',
            type: 'text'
          }
        ] as any,
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'test-2',
        role: 'assistant',
        // Message without citations field
        content: [
          {
            text: 'This message has NO citations field',
            type: 'text'
          }
        ] as any,
        timestamp: new Date().toISOString(),
        metadata: {}
      }
    ]

    console.log('\n=== Test: Citations Field Impact ===')
    
    mockUseChat.mockReturnValue({
      messages: messagesWithCitations,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isLoading: false,
      error: null,
      streamingMessage: null,
      abortStream: vi.fn(),
      editMessage: vi.fn(),
      deleteMessage: vi.fn(),
      resubmitMessage: vi.fn()
    })

    const { container } = render(<ChatInterface />)
    
    await waitFor(() => {
      const allText = container.textContent || ''
      const withCitationsRendered = allText.includes('citations field')
      const withoutCitationsRendered = allText.includes('NO citations field')
      
      console.log('Message WITH citations rendered:', withCitationsRendered)
      console.log('Message WITHOUT citations rendered:', withoutCitationsRendered)
      
      if (!withCitationsRendered && withoutCitationsRendered) {
        console.log('🔴 CONFIRMED: Citations field is causing messages to not render!')
      }
    })
  })

  it('should test different content structures', async () => {
    // Test all the different content structures from the first 3 messages
    const testMessages: ChatMessage[] = [
      {
        id: 'struct-1',
        role: 'user',
        content: 'Simple string content', // Like message 1
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'struct-2',
        role: 'assistant',
        content: [{ type: 'text', text: 'Array with text object' }] as any, // Simplified message 2
        timestamp: new Date().toISOString(),
        metadata: {}
      },
      {
        id: 'struct-3',
        role: 'assistant',
        content: [{ type: 'tool_use', name: 'test_tool', input: {}, id: 'tool-1' }] as any, // Like message 3
        timestamp: new Date().toISOString(),
        metadata: {}
      }
    ]

    console.log('\n=== Test: Different Content Structures ===')
    
    mockUseChat.mockReturnValue({
      messages: testMessages,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      isLoading: false,
      error: null,
      streamingMessage: null,
      abortStream: vi.fn(),
      editMessage: vi.fn(),
      deleteMessage: vi.fn(),
      resubmitMessage: vi.fn()
    })

    const { container } = render(<ChatInterface />)
    
    await waitFor(() => {
      const allText = container.textContent || ''
      
      const results = {
        stringContent: allText.includes('Simple string content'),
        arrayTextContent: allText.includes('Array with text object'),
        toolUseContent: allText.includes('test_tool') || allText.includes('tool-1')
      }
      
      console.log('Results:', results)
      
      // Identify which structures are failing
      Object.entries(results).forEach(([key, rendered]) => {
        if (!rendered) {
          console.log(`🔴 ${key} is NOT rendering`)
        } else {
          console.log(`✅ ${key} is rendering`)
        }
      })
    })
  })
})