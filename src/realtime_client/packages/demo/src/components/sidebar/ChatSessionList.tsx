"use client"

import * as React from "react"
import { MessageSquare, Clock, Hash } from "lucide-react"
import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"

export interface ChatSessionListProps {
  className?: string
}

/**
 * ChatSessionList component - STUB implementation
 * Full functionality will be implemented when session management is added
 * Design specifications available in .scratch/design_docs/chat_session_list_design.md
 */
export const ChatSessionList = React.forwardRef<HTMLDivElement, ChatSessionListProps>(
  ({ className }, ref) => {
    // Stub data for visual representation
    const stubSessions = [
      {
        id: "current",
        name: "Current Session",
        time: "Now",
        preview: "This is your active chat session",
        isActive: true,
      },
      {
        id: "1",
        name: "Previous Chat",
        time: "2 hours ago",
        preview: "Session history will appear here",
        isActive: false,
      },
    ]

    return (
      <div
        ref={ref}
        className={cn(
          "flex-grow overflow-hidden px-2",
          className
        )}
      >
        <ScrollArea className="h-full">
          <div className="space-y-1">
            {/* Section Header */}
            <div className="px-2 py-1">
              <h3 className="text-xs font-medium text-muted-foreground">Today</h3>
            </div>

            {/* Session Items */}
            {stubSessions.map((session) => (
              <button
                key={session.id}
                className={cn(
                  "w-full rounded-lg px-2 py-2 text-left transition-colors",
                  "hover:bg-muted",
                  session.isActive && "bg-muted"
                )}
                disabled // Stub - no functionality yet
                aria-label={`Chat session: ${session.name}`}
                aria-current={session.isActive ? "page" : undefined}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                  <div className="flex-1 overflow-hidden">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium truncate">
                        {session.name}
                      </span>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {session.time}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground truncate mt-0.5">
                      {session.preview}
                    </p>
                  </div>
                </div>
              </button>
            ))}

            {/* Empty State for Other Sections */}
            <div className="px-2 py-1 mt-4">
              <h3 className="text-xs font-medium text-muted-foreground">Yesterday</h3>
            </div>
            <div className="px-2 py-3 text-center">
              <p className="text-xs text-muted-foreground">No previous sessions</p>
            </div>

            {/* Coming Soon Notice */}
            <div className="mt-6 mx-2 p-3 rounded-lg border border-dashed border-border">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span className="text-xs">Session management coming soon</span>
              </div>
            </div>
          </div>
        </ScrollArea>
      </div>
    )
  }
)
ChatSessionList.displayName = "ChatSessionList"