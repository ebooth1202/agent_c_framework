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
          "flex flex-col h-full overflow-hidden",
          className
        )}
      >
        {/* Scrollable message area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto"
        >
          {/* Message list */}
          <MessageList 
            className="px-4 py-4"
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