"use client"

import * as React from "react"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export interface SidebarTopMenuProps {
  onNewChat?: () => void
  className?: string
}

/**
 * SidebarTopMenu component - Contains the "New Chat" button
 * Provides session management actions at the top of the sidebar
 */
export const SidebarTopMenu = React.forwardRef<HTMLDivElement, SidebarTopMenuProps>(
  ({ onNewChat, className }, ref) => {
    const handleNewChat = React.useCallback(() => {
      // Clear current session
      // For now, we'll just refresh - actual implementation will come with session management
      if (onNewChat) {
        onNewChat()
      } else {
        // Default behavior: Clear messages and reset
        // This will be connected to the actual chat context later
        window.location.reload()
      }
    }, [onNewChat])

    return (
      <div
        ref={ref}
        className={cn(
          "px-2 pt-1 gap-px mb-6",
          className
        )}
      >
        <Button
          onClick={handleNewChat}
          className={cn(
            "inline-flex items-center justify-center h-9 px-4 py-2 rounded-lg w-full",
            "bg-primary text-primary-foreground hover:bg-primary/90",
            "transition duration-300"
          )}
          aria-label="Start a new chat"
        >
          <Plus className="h-4 w-4 mr-2" />
          <span>New Chat</span>
        </Button>
      </div>
    )
  }
)
SidebarTopMenu.displayName = "SidebarTopMenu"