"use client"

import * as React from "react"
import { Plus } from "lucide-react"
import { Button } from "../ui/button"
import { cn } from "../../lib/utils"

export interface SidebarTopMenuProps {
  onNewChat?: () => void
  isCollapsed?: boolean
  className?: string
}

/**
 * SidebarTopMenu component - Contains the "New Chat" button
 * Provides session management actions at the top of the sidebar
 */
export const SidebarTopMenu = React.forwardRef<HTMLDivElement, SidebarTopMenuProps>(
  ({ onNewChat, isCollapsed, className }, ref) => {
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
          "w-full",
          className
        )}
      >
        <Button
          onClick={handleNewChat}
          variant="default"
          size="default"
          className={cn(
            "w-full",
            isCollapsed && "px-0"
          )}
          aria-label="Start a new chat"
          title={isCollapsed ? "New Chat" : undefined}
        >
          <Plus className={cn("h-4 w-4", !isCollapsed && "mr-2")} />
          {!isCollapsed && <span className="font-medium">New Chat</span>}
        </Button>
      </div>
    )
  }
)
SidebarTopMenu.displayName = "SidebarTopMenu"