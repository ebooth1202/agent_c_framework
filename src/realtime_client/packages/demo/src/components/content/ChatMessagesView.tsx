"use client"

import * as React from "react"
import { MessageSquare } from "lucide-react"
import { cn } from "@/lib/utils"

export interface ChatMessagesViewProps {
  className?: string
}

/**
 * ChatMessagesView component - PLACEHOLDER implementation
 * Complex chat message rendering with rich formatting will be implemented later
 */
export const ChatMessagesView = React.forwardRef<HTMLDivElement, ChatMessagesViewProps>(
  ({ className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex-1 overflow-y-auto",
          "flex items-center justify-center h-full",
          className
        )}
      >
        <div className="text-center space-y-2">
          <MessageSquare className="h-12 w-12 mx-auto opacity-50 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Chat messages will appear here</p>
          <p className="text-xs text-muted-foreground">Complex message rendering coming soon</p>
        </div>
      </div>
    )
  }
)
ChatMessagesView.displayName = "ChatMessagesView"