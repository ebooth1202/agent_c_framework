"use client"

import * as React from "react"
import { cn } from "../../lib/utils"
import { MessageList } from "./MessageList"
import { ScrollAnchor } from "./ScrollAnchor"
import { TypingIndicator } from "./TypingIndicator"
import { useChat } from "@agentc/realtime-react"

export interface ChatMessagesViewProps {
  className?: string
}

/**
 * ChatMessagesView component - Main chat message display container
 * Integrates MessageList with typing indicators and auto-scrolling
 */
export const ChatMessagesView = React.forwardRef<HTMLDivElement, ChatMessagesViewProps>(
  ({ className }, ref) => {
    const scrollRef = React.useRef<HTMLDivElement>(null)
    const { messages, isAgentTyping } = useChat()

    return (
      <div
        ref={ref}
        className={cn(
          "h-full overflow-hidden",
          className
        )}
      >
        {/* Scrollable message area - takes full height */}
        <div 
          ref={scrollRef}
          className="h-full overflow-y-auto"
        >
          {/* Message list - remove fixed height, let it grow naturally */}
          <MessageList 
            className="px-4 py-4"
            maxHeight="none"
          />
          
          {/* Typing indicator */}
          {isAgentTyping && (
            <div className="px-4 pb-2">
              <TypingIndicator />
            </div>
          )}
          
          {/* Scroll anchor for auto-scrolling */}
          <ScrollAnchor scrollContainerRef={scrollRef} />
        </div>
      </div>
    )
  }
)
ChatMessagesView.displayName = "ChatMessagesView"