"use client"

import * as React from "react"
import { MessageSquare, Clock, Hash } from "lucide-react"
import { cn } from "../../lib/utils"
import { ScrollArea } from "../ui/scroll-area"

export interface ChatSessionListProps {
  isCollapsed?: boolean
  className?: string
}

/**
 * ChatSessionList component - STUB implementation
 * Full functionality will be implemented when session management is added
 * Design specifications available in .scratch/design_docs/chat_session_list_design.md
 */
export const ChatSessionList = React.forwardRef<HTMLDivElement, ChatSessionListProps>(
  ({ isCollapsed, className }, ref) => {
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

    // When collapsed, show minimal UI
    if (isCollapsed) {
      return (
        <div
          ref={ref}
          className={cn(
            "flex-1 overflow-hidden",
            className
          )}
        >
          <div className="flex flex-col items-center gap-2">
            {stubSessions.slice(0, 3).map((session) => (
              <button
                key={session.id}
                className={cn(
                  "w-12 h-12 rounded-md flex items-center justify-center transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  session.isActive && "bg-accent text-accent-foreground"
                )}
                disabled
                title={session.name}
                aria-label={`Chat session: ${session.name}`}
              >
                <MessageSquare className="h-5 w-5" />
              </button>
            ))}
          </div>
        </div>
      )
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          "flex-1 overflow-hidden",
          className
        )}
      >
        <ScrollArea className="h-full">
          <div className="space-y-4">
            {/* Section Header */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Today</h3>
            </div>

            {/* Session Items */}
            <div className="space-y-1">
              {stubSessions.map((session) => (
                <button
                  key={session.id}
                  className={cn(
                    "w-full rounded-md p-3 text-left transition-colors",
                    "hover:bg-accent hover:text-accent-foreground",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                    session.isActive && "bg-accent text-accent-foreground"
                  )}
                  disabled // Stub - no functionality yet
                  aria-label={`Chat session: ${session.name}`}
                  aria-current={session.isActive ? "page" : undefined}
                >
                  <div className="flex items-start gap-3">
                    <MessageSquare className="h-4 w-4 mt-0.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-sm font-medium truncate">
                          {session.name}
                        </span>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {session.time}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {session.preview}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Empty State for Other Sections */}
            <div className="mt-6">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Yesterday</h3>
            </div>
            <div className="p-4 text-center">
              <p className="text-sm text-muted-foreground">No previous sessions</p>
            </div>

            {/* Coming Soon Notice */}
            <div className="mt-6 p-4 rounded-md bg-accent/20 border border-border">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Session management coming soon</span>
              </div>
            </div>
          </div>
        </ScrollArea>
      </div>
    )
  }
)
ChatSessionList.displayName = "ChatSessionList"