/**
 * Example usage of Chat Components
 * This file demonstrates how to integrate the chat components into your application
 */

import React from 'react'
import { AgentCProvider } from '@agentc/realtime-react'
import { MessageList } from './message-list'
import { Button, Input } from '@agentc/realtime-ui'
import { useChat } from '@agentc/realtime-react'

/**
 * Basic Chat Interface Example
 * Shows a simple chat UI with message list and input
 */
export function BasicChatExample() {
  return (
    <AgentCProvider>
      <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
        {/* Chat Header */}
        <div className="border-b pb-4 mb-4">
          <h1 className="text-2xl font-bold">Chat Interface</h1>
          <p className="text-muted-foreground">Powered by Agent C Realtime SDK</p>
        </div>
        
        {/* Message List */}
        <div className="flex-1 overflow-hidden">
          <MessageList 
            maxHeight="100%"
            showTimestamps={true}
            className="h-full"
          />
        </div>
        
        {/* Input Area */}
        <ChatInput />
      </div>
    </AgentCProvider>
  )
}

/**
 * Chat Input Component
 * Handles message sending
 */
function ChatInput() {
  const { sendMessage, isSending } = useChat()
  const [input, setInput] = React.useState('')
  
  const handleSend = React.useCallback(async () => {
    if (!input.trim() || isSending) return
    
    try {
      await sendMessage(input)
      setInput('')
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }, [input, isSending, sendMessage])
  
  const handleKeyPress = React.useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])
  
  return (
    <div className="border-t pt-4 mt-4">
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          disabled={isSending}
          className="flex-1"
        />
        <Button 
          onClick={handleSend}
          disabled={!input.trim() || isSending}
        >
          {isSending ? 'Sending...' : 'Send'}
        </Button>
      </div>
    </div>
  )
}

/**
 * Advanced Chat Example with Custom Configuration
 * Shows how to customize the chat components
 */
export function AdvancedChatExample() {
  const { messages } = useChat()
  
  // Custom empty state
  const customEmptyState = (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
        <span className="text-2xl">💬</span>
      </div>
      <h3 className="text-xl font-semibold mb-2">Start a Conversation</h3>
      <p className="text-muted-foreground text-center max-w-md">
        Ask me anything! I&apos;m here to help with your questions about the Agent C Realtime SDK.
      </p>
    </div>
  )
  
  return (
    <div className="h-[600px] bg-background rounded-lg shadow-lg overflow-hidden">
      <MessageList
        maxHeight="100%"
        showTimestamps={true}
        enableVirtualScroll={messages.length > 50}
        emptyStateComponent={customEmptyState}
        className="p-6"
      />
    </div>
  )
}

/**
 * Minimal Chat Widget Example
 * Shows a compact chat interface
 */
export function ChatWidget() {
  const [isOpen, setIsOpen] = React.useState(false)
  
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 w-14 h-14 bg-primary rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform"
        aria-label="Open chat"
      >
        <span className="text-2xl text-primary-foreground">💬</span>
      </button>
    )
  }
  
  return (
    <div className="fixed bottom-4 right-4 w-96 h-[500px] bg-background border rounded-lg shadow-xl flex flex-col">
      {/* Widget Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Chat Assistant</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-muted-foreground hover:text-foreground"
          aria-label="Close chat"
        >
          ✕
        </button>
      </div>
      
      {/* Message Area */}
      <div className="flex-1 overflow-hidden">
        <MessageList 
          maxHeight="100%"
          showTimestamps={false}
          className="h-full"
        />
      </div>
      
      {/* Quick Input */}
      <div className="p-4 border-t">
        <ChatInput />
      </div>
    </div>
  )
}

/**
 * Integration Notes:
 * 
 * 1. Wrap your app with AgentCProvider to provide SDK context
 * 2. MessageList automatically handles message rendering and scrolling
 * 3. Use the useChat() hook to send messages and access chat state
 * 4. Components follow CenSuite design system for consistency
 * 5. All components are fully accessible (WCAG 2.1 AA compliant)
 * 
 * Required Dependencies:
 * - react-markdown (for markdown rendering)
 * - remark-gfm (for GitHub flavored markdown)
 * - react-syntax-highlighter (for code highlighting)
 * 
 * Install with: pnpm add react-markdown remark-gfm react-syntax-highlighter @types/react-syntax-highlighter
 */