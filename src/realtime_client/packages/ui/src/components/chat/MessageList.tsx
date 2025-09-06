'use client'

import * as React from 'react'
import { useChat } from '@agentc/realtime-react'
import { cn } from '../../lib/utils'
import { Message } from './Message'
import { ScrollAnchor } from './ScrollAnchor'
import { TypingIndicator } from './TypingIndicator'
import { Loader2, MessageSquare } from 'lucide-react'

export interface MessageListProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Maximum height for the message list
   */
  maxHeight?: string
  /**
   * Show timestamps on messages
   */
  showTimestamps?: boolean
  /**
   * Enable virtual scrolling for performance
   */
  enableVirtualScroll?: boolean
  /**
   * Custom empty state component
   */
  emptyStateComponent?: React.ReactNode
}

const MessageList = React.forwardRef<HTMLDivElement, MessageListProps>(
  ({ 
    className, 
    maxHeight = '600px',
    showTimestamps = true,
    enableVirtualScroll = false,
    emptyStateComponent,
    ...props 
  }, ref) => {
    const { messages, isAgentTyping, partialMessage } = useChat()
    const scrollContainerRef = React.useRef<HTMLDivElement>(null)
    const [isLoading, setIsLoading] = React.useState(false)
    
    // Combine ref forwarding with internal ref
    React.useImperativeHandle(ref, () => scrollContainerRef.current as HTMLDivElement)
    
    // Virtual scrolling logic (simplified for now - can be enhanced with react-window)
    const visibleMessages = React.useMemo(() => {
      if (!enableVirtualScroll) return messages
      // For now, return all messages - in production, implement windowing
      return messages
    }, [messages, enableVirtualScroll])
    
    // Empty state
    const EmptyState = () => {
      if (emptyStateComponent) return <>{emptyStateComponent}</>
      
      return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No messages yet</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Start a conversation to see messages appear here
          </p>
        </div>
      )
    }
    
    // Loading state
    if (isLoading) {
      return (
        <div 
          className={cn(
            "flex items-center justify-center p-8",
            className
          )}
          {...props}
        >
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading messages...</span>
          </div>
        </div>
      )
    }
    
    return (
      <div
        ref={scrollContainerRef}
        className={cn(
          "relative flex flex-col overflow-y-auto",
          className
        )}
        style={{ maxHeight }}
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        {...props}
      >
        {/* Messages container */}
        <div className="flex-1 space-y-4 p-4">
          {visibleMessages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {visibleMessages.map((message, index) => (
                <Message
                  key={`message-${index}-${message.timestamp || index}`}
                  message={{
                    ...message,
                    timestamp: message.timestamp || new Date().toISOString()
                  }}
                  showTimestamp={showTimestamps}
                  className="animate-in slide-in-from-bottom-2 duration-200"
                />
              ))}
              
              {/* Current streaming response */}
              {partialMessage && (
                <Message
                  message={{
                    role: 'assistant',
                    content: partialMessage,
                    timestamp: new Date().toISOString()
                  }}
                  showTimestamp={showTimestamps}
                  isStreaming
                  className="animate-in slide-in-from-bottom-2 duration-200"
                />
              )}
              
              {/* Typing indicator */}
              {isAgentTyping && !partialMessage && (
                <div className="flex items-start gap-3 animate-in slide-in-from-bottom-2 duration-200">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-xs font-medium text-primary">AI</span>
                  </div>
                  <div className="flex-1">
                    <TypingIndicator />
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        
        {/* Scroll anchor for auto-scrolling */}
        <ScrollAnchor 
          scrollContainerRef={scrollContainerRef}
          dependencies={[messages, partialMessage, isAgentTyping]}
        />
      </div>
    )
  }
)

MessageList.displayName = 'MessageList'

export { MessageList }