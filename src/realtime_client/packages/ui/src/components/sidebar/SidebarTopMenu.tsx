"use client"

import * as React from "react"
import { Plus } from "lucide-react"
import { Button } from "../ui/button"
import { cn } from "../../lib/utils"
import { useRealtimeClientSafe, useAgentCData } from "@agentc/realtime-react"
import type { NewChatSessionEvent } from "@agentc/realtime-core"

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
    const client = useRealtimeClientSafe()
    const { data } = useAgentCData()

    const handleNewChat = React.useCallback(() => {
      // Send the NewChatSessionEvent to the server
      const event: NewChatSessionEvent = {
        type: 'new_chat_session',
        agent_key: data?.currentAgentConfig?.key
      }
      
      // Send the event using the realtime client
      client?.sendEvent(event)
      
      // Call the onNewChat callback after sending the event if provided
      // This maintains backward compatibility
      if (onNewChat) {
        onNewChat()
      }
    }, [client, data?.currentAgentConfig?.key, onNewChat])

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