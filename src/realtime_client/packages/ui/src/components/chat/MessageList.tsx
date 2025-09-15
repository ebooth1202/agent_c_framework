'use client'

import * as React from 'react'
import { useChat, useToolNotifications } from '@agentc/realtime-react'
import { cn } from '../../lib/utils'
import { Message } from './Message'
import { TypingIndicator } from './TypingIndicator'
import { SubsessionDivider } from './SubsessionDivider'
import { ToolNotificationList } from './ToolNotification'
import { Loader2, MessageSquare } from 'lucide-react'
import { Logger } from '../../utils/logger'

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

/**
 * MessageList component with intelligent auto-scrolling behavior:
 * 
 * - Auto-scrolls to bottom when new messages, streaming content, or typing indicators appear
 * - Disables auto-scroll when user manually scrolls up to review older messages
 * - Re-enables auto-scroll when user scrolls back to within 50px of the bottom
 * - Uses smooth scrolling for better UX
 * 
 * The auto-scroll state is managed internally and responds to user interaction patterns
 * common in chat applications.
 */
const MessageList = React.forwardRef<HTMLDivElement, MessageListProps>(
  ({ 
    className, 
    maxHeight = '600px',
    showTimestamps = true,
    enableVirtualScroll = false,
    emptyStateComponent,
    ...props 
  }, ref) => {
    const { messages, isAgentTyping, streamingMessage, isSubSessionMessage } = useChat()
    const { notifications: toolNotifications } = useToolNotifications({
      autoRemoveCompleted: false, // We'll handle removal when tool completes
      maxNotifications: 5
    })
    const scrollContainerRef = React.useRef<HTMLDivElement>(null)
    const scrollSentinelRef = React.useRef<HTMLDivElement>(null)
    const [isLoading, setIsLoading] = React.useState(false)
    const [isAutoScrollEnabled, setIsAutoScrollEnabled] = React.useState(true)
    const [hasCompletedInitialScroll, setHasCompletedInitialScroll] = React.useState(false)
    const isInitialMount = React.useRef(true)
    const scrollThreshold = 50 // pixels from bottom to re-enable auto-scroll
    
    // Debug logging for messages
    React.useEffect(() => {
      Logger.debug('[MessageList] Received messages:', messages.length, 'messages')
      Logger.debug('[MessageList] First 3 messages:', messages.slice(0, 3))
      if (messages.length > 0) {
        Logger.debug('[MessageList] Message roles:', messages.map(m => m.role))
        Logger.debug('[MessageList] Message content types:', messages.map(m => {
          if (typeof m.content === 'string') return 'string';
          if (Array.isArray(m.content)) return `array[${m.content.length}]`;
          return typeof m.content;
        }))
      }
    }, [messages])
    
    // Check if scroll is near bottom
    const isNearBottom = React.useCallback(() => {
      if (!scrollContainerRef.current) return true
      
      const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight
      
      return distanceFromBottom <= scrollThreshold
    }, [scrollThreshold])
    
    // Scroll to bottom function
    const scrollToBottom = React.useCallback((smooth = true) => {
      if (!scrollSentinelRef.current) return
      
      // Use the sentinel element as the scroll target
      scrollSentinelRef.current.scrollIntoView({ 
        behavior: smooth ? 'smooth' : 'auto',
        block: 'end'
      })
    }, [])
    
    // Handle scroll events to detect user scrolling
    const handleScroll = React.useCallback(() => {
      // Ignore scroll events until initial scroll is complete
      if (!hasCompletedInitialScroll) {
        Logger.debug('[MessageList] Ignoring scroll event - initial scroll not complete')
        return
      }
      
      const nearBottom = isNearBottom()
      
      // Re-enable auto-scroll if user scrolls back to bottom
      if (nearBottom && !isAutoScrollEnabled) {
        Logger.debug('[MessageList] Re-enabling auto-scroll - user scrolled to bottom')
        setIsAutoScrollEnabled(true)
      }
      // Disable auto-scroll if user scrolls away from bottom
      else if (!nearBottom && isAutoScrollEnabled) {
        Logger.debug('[MessageList] Disabling auto-scroll - user scrolled up')
        setIsAutoScrollEnabled(false)
      }
    }, [isNearBottom, isAutoScrollEnabled, hasCompletedInitialScroll])
    
    // Set up scroll event listener
    React.useEffect(() => {
      const container = scrollContainerRef.current
      if (!container) return
      
      container.addEventListener('scroll', handleScroll, { passive: true })
      
      return () => {
        container.removeEventListener('scroll', handleScroll)
      }
    }, [handleScroll])
    
    // Handle initial mount scroll for session restoration
    React.useEffect(() => {
      if (isInitialMount.current && messages.length > 0) {
        Logger.debug('[MessageList] Initial mount with existing messages - scrolling after ref attachment')
        // Use requestAnimationFrame to ensure ref is attached before scrolling
        requestAnimationFrame(() => {
          scrollToBottom(false) // Use instant scroll for initial mount
          setHasCompletedInitialScroll(true)
        })
        isInitialMount.current = false
      } else if (isInitialMount.current && messages.length === 0) {
        // No messages on mount, mark initial scroll as complete
        Logger.debug('[MessageList] Initial mount with no messages')
        setHasCompletedInitialScroll(true)
        isInitialMount.current = false
      }
    }, [messages.length, scrollToBottom])
    
    // Auto-scroll when new content arrives (after initial mount)
    React.useEffect(() => {
      // Skip if this is the initial mount or auto-scroll is disabled
      if (!hasCompletedInitialScroll || !isAutoScrollEnabled) {
        return
      }
      
      // Small delay to ensure DOM updates are complete for new messages
      const timeoutId = setTimeout(() => {
        Logger.debug('[MessageList] Auto-scrolling for new content')
        scrollToBottom()
      }, 100)
      
      return () => clearTimeout(timeoutId)
    }, [messages, streamingMessage, isAgentTyping, toolNotifications, isAutoScrollEnabled, scrollToBottom, hasCompletedInitialScroll])
    
    // Combine ref forwarding with internal ref
    React.useImperativeHandle(ref, () => scrollContainerRef.current as HTMLDivElement)
    
    // Virtual scrolling logic (simplified for now - can be enhanced with react-window)
    const visibleMessages = React.useMemo(() => {
      Logger.debug('[MessageList] Computing visible messages');
      Logger.debug('[MessageList] enableVirtualScroll:', enableVirtualScroll);
      Logger.debug('[MessageList] messages length:', messages.length);
      
      if (!enableVirtualScroll) {
        Logger.debug('[MessageList] Returning all messages (no virtual scroll)');
        return messages
      }
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
        style={{ maxHeight: maxHeight === 'none' ? undefined : maxHeight }}
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        {...props}
      >
        {/* Messages container */}
        <div className="space-y-4">
          {visibleMessages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {visibleMessages.map((message, index) => {
                const isSubSession = isSubSessionMessage(message)
                const previousMessage = index > 0 ? visibleMessages[index - 1] : null
                const isPreviousSubSession = previousMessage ? isSubSessionMessage(previousMessage) : false
                
                // Check for subsession transitions
                const isSubSessionStart = isSubSession && !isPreviousSubSession
                const isSubSessionEnd = !isSubSession && isPreviousSubSession
                
                return (
                  <React.Fragment key={`message-${index}-${message.timestamp || index}`}>
                    {/* Subsession start divider */}
                    {isSubSessionStart && (
                      <SubsessionDivider 
                        type="start"
                        timestamp={message.timestamp}
                        className="my-2"
                      />
                    )}
                    
                    {/* Subsession end divider */}
                    {isSubSessionEnd && (
                      <SubsessionDivider 
                        type="end"
                        timestamp={previousMessage?.timestamp}
                        className="my-2"
                      />
                    )}
                    
                    {/* Message */}
                    <Message
                      message={message}
                      showTimestamp={showTimestamps}
                      isSubSession={isSubSession}
                      className="animate-in slide-in-from-bottom-2 duration-200"
                    />
                  </React.Fragment>
                )
              })}
              
              {/* Check if we need an end divider for the last message */}
              {visibleMessages.length > 0 && 
               isSubSessionMessage(visibleMessages[visibleMessages.length - 1]) && 
               !streamingMessage && (
                <SubsessionDivider 
                  type="end"
                  timestamp={visibleMessages[visibleMessages.length - 1].timestamp}
                  className="my-2"
                />
              )}
              
              {/* Current streaming response */}
              {streamingMessage && (
                <Message
                  message={streamingMessage}
                  showTimestamp={showTimestamps}
                  isStreaming
                  isSubSession={streamingMessage.isSubSession}
                  className="animate-in slide-in-from-bottom-2 duration-200"
                />
              )}
              
              {/* Tool notifications */}
              {toolNotifications.length > 0 && (
                <ToolNotificationList
                  notifications={toolNotifications}
                  maxNotifications={3}
                  className="animate-in slide-in-from-bottom-2 duration-200"
                />
              )}
              
              {/* Typing indicator - only show if no streaming message and no active tools */}
              {isAgentTyping && !streamingMessage && toolNotifications.length === 0 && (
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
        
        {/* Sentinel element for scroll targeting */}
        <div
          ref={scrollSentinelRef}
          data-testid="scroll-sentinel"
          style={{ height: '1px', visibility: 'hidden' }}
          aria-hidden="true"
        />
      </div>
    )
  }
)

MessageList.displayName = 'MessageList'

export { MessageList }