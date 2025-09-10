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

// Mock problem session data for testing
const problemSession = {
  messages: [
    {
      role: 'user',
      content: 'Cora, I need you to prepare a document'
    },
    {
      role: 'assistant',
      content: "I'll help you prepare a comprehensive reference document"
    },
    {
      role: 'assistant',
      content: [{
        type: 'tool_use',
        name: 'document_create',
        input: { title: 'Test Document' }
      }]
    }
  ]
}

describe('ChatInterface - Problem Session Debug', () => {
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

    // Enable debug logging
    console.log('=== Test Starting ===')
    console.log('Problem session has', problemSession.messages.length, 'messages')
    console.log('First 3 messages:')
    problemSession.messages.slice(0, 3).forEach((msg: any, idx: number) => {
      console.log(`Message ${idx + 1}:`, {
        role: msg.role,
        contentType: typeof msg.content,
        content: msg.content
      })
    })
  })

  it('should process and render the first 3 messages from problem session', async () => {
    // Transform the session messages to ChatMessage format
    const transformedMessages: ChatMessage[] = problemSession.messages.map((msg: any, index: number) => {
      console.log(`\n=== Transforming message ${index + 1} ===`)
      console.log('Original message:', JSON.stringify(msg, null, 2))
      
      // Handle different content formats
      let content: any
      if (typeof msg.content === 'string') {
        content = msg.content
      } else if (Array.isArray(msg.content)) {
        // Process content array
        content = msg.content.map((item: any) => {
          if (item.type === 'text') {
            // Remove citations field if it exists
            const { citations, ...textContent } = item
            return textContent
          }
          return item
        })
        
        // If single text item, unwrap to string
        if (content.length === 1 && content[0].type === 'text') {
          content = content[0].text
        }
      } else {
        content = msg.content
      }
      
      const transformed = {
        id: `msg-${index}`,
        role: msg.role,
        content,
        timestamp: new Date().toISOString(),
        metadata: {}
      }
      
      console.log('Transformed message:', JSON.stringify(transformed, null, 2))
      return transformed
    })

    // Setup chat mock with transformed messages
    mockUseChat.mockReturnValue({
      messages: transformedMessages.slice(0, 5), // First 5 messages for testing
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

    console.log('\n=== Rendering ChatInterface component ===')
    const { container } = render(<ChatInterface />)
    
    // Wait for async rendering
    await waitFor(() => {
      const messageElements = container.querySelectorAll('[data-message-id]')
      console.log('Found message elements:', messageElements.length)
      
      messageElements.forEach((el, idx) => {
        console.log(`Element ${idx + 1}:`, {
          id: el.getAttribute('data-message-id'),
          role: el.getAttribute('data-role'),
          text: el.textContent?.substring(0, 100)
        })
      })
    })

    // Check for first user message
    console.log('\n=== Checking for first message (user) ===')
    const firstMessage = await screen.findByText(/Cora, I need you to prepare a document/i, { exact: false })
    expect(firstMessage).toBeInTheDocument()
    console.log('✓ First message found')

    // Check for second message (assistant with text)
    console.log('\n=== Checking for second message (assistant) ===')
    const secondMessage = await screen.findByText(/I'll help you prepare a comprehensive reference document/i, { exact: false })
    expect(secondMessage).toBeInTheDocument()
    console.log('✓ Second message found')

    // Check for third message (assistant with tool_use)
    console.log('\n=== Checking for third message (tool_use) ===')
    const toolUseElements = container.querySelectorAll('[data-tool-use]')
    console.log('Tool use elements found:', toolUseElements.length)
    
    // Debug: Check all rendered content
    console.log('\n=== All rendered text content ===')
    const allText = container.textContent
    console.log(allText?.substring(0, 500))
  })

  it('should trace message processing pipeline', async () => {
    // Create spy functions to trace the pipeline
    const processingPipeline = {
      sdkReceive: vi.fn(),
      hookTransform: vi.fn(),
      componentReceive: vi.fn(),
      componentRender: vi.fn()
    }

    // Transform first 3 messages
    const firstThreeMessages = problemSession.messages.slice(0, 3).map((msg: any, index: number) => {
      const transformed = {
        id: `msg-${index}`,
        role: msg.role,
        content: typeof msg.content === 'string' ? msg.content : msg.content,
        timestamp: new Date().toISOString(),
        metadata: {}
      }
      
      // Simulate SDK receiving message
      processingPipeline.sdkReceive(transformed)
      
      // Simulate hook transformation
      processingPipeline.hookTransform(transformed)
      
      return transformed
    })

    // Setup chat mock
    mockUseChat.mockImplementation(() => {
      // Simulate component receiving messages
      firstThreeMessages.forEach(msg => {
        processingPipeline.componentReceive(msg)
      })
      
      return {
        messages: firstThreeMessages,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
        isLoading: false,
        error: null,
        streamingMessage: null,
        abortStream: vi.fn(),
        editMessage: vi.fn(),
        deleteMessage: vi.fn(),
        resubmitMessage: vi.fn()
      }
    })

    // Render component
    const { container } = render(<ChatInterface />)
    
    // Check pipeline execution
    console.log('\n=== Pipeline Trace ===')
    console.log('SDK Receive calls:', processingPipeline.sdkReceive.mock.calls.length)
    console.log('Hook Transform calls:', processingPipeline.hookTransform.mock.calls.length)
    console.log('Component Receive calls:', processingPipeline.componentReceive.mock.calls.length)
    
    expect(processingPipeline.sdkReceive).toHaveBeenCalledTimes(3)
    expect(processingPipeline.hookTransform).toHaveBeenCalledTimes(3)
    expect(processingPipeline.componentReceive).toHaveBeenCalledTimes(3)
    
    // Check what actually rendered
    await waitFor(() => {
      const messageCount = container.querySelectorAll('[data-message-id]').length
      console.log('Messages rendered:', messageCount)
      
      // Simulate render tracking
      for (let i = 0; i < messageCount; i++) {
        processingPipeline.componentRender({ index: i })
      }
    })
    
    console.log('Component Render calls:', processingPipeline.componentRender.mock.calls.length)
  })

  it('should identify where messages are dropped', async () => {
    const droppedMessages: any[] = []
    const renderedMessages: any[] = []
    
    // Process all messages
    const processedMessages = problemSession.messages.slice(0, 5).map((msg: any, index: number) => {
      const messageId = `msg-${index}`
      
      // Check content structure
      const hasProblematicContent = 
        Array.isArray(msg.content) && 
        msg.content.some((item: any) => item.citations !== undefined)
      
      if (hasProblematicContent) {
        console.log(`\n⚠️ Message ${index + 1} has citations field:`, msg.content)
      }
      
      // Check for tool_use content
      const hasToolUse = 
        Array.isArray(msg.content) && 
        msg.content.some((item: any) => item.type === 'tool_use')
      
      if (hasToolUse) {
        console.log(`\n⚠️ Message ${index + 1} has tool_use content:`, msg.content)
      }
      
      return {
        id: messageId,
        role: msg.role,
        content: msg.content,
        timestamp: new Date().toISOString(),
        metadata: {},
        _debug: {
          originalIndex: index,
          hasProblematicContent,
          hasToolUse
        }
      }
    })
    
    // Setup mock with debug tracking
    mockUseChat.mockReturnValue({
      messages: processedMessages,
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
    
    // Render and track
    const { container } = render(<ChatInterface />)
    
    await waitFor(() => {
      const messageElements = container.querySelectorAll('[data-message-id]')
      
      // Track what rendered
      messageElements.forEach(el => {
        const id = el.getAttribute('data-message-id')
        renderedMessages.push(id)
      })
      
      // Find dropped messages
      processedMessages.forEach(msg => {
        if (!renderedMessages.includes(msg.id)) {
          droppedMessages.push(msg)
        }
      })
    })
    
    console.log('\n=== Message Drop Analysis ===')
    console.log('Total messages processed:', processedMessages.length)
    console.log('Messages rendered:', renderedMessages.length)
    console.log('Messages dropped:', droppedMessages.length)
    
    if (droppedMessages.length > 0) {
      console.log('\n🔴 Dropped messages:')
      droppedMessages.forEach(msg => {
        console.log(`- Message ${msg._debug.originalIndex + 1} (${msg.role}):`, {
          hasProblematicContent: msg._debug.hasProblematicContent,
          hasToolUse: msg._debug.hasToolUse,
          content: JSON.stringify(msg.content).substring(0, 200)
        })
      })
    }
    
    // Assert we found the issue
    expect(droppedMessages.length).toBeGreaterThan(0)
    console.log('\n✓ Successfully identified dropped messages')
  })
})