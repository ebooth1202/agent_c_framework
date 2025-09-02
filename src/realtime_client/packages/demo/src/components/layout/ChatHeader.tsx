"use client"

import * as React from "react"
import { Menu } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { SessionNameDropdown } from "./SessionNameDropdown"
import { ConnectionButton, AudioControls } from "@agentc/realtime-ui"

export interface ChatHeaderProps {
  onMenuToggle?: () => void
  sessionName?: string
  className?: string
}

/**
 * ChatHeader component - Main header for the chat interface
 * Contains menu toggle (mobile), session name, and connection/audio controls
 */
export const ChatHeader = React.forwardRef<HTMLDivElement, ChatHeaderProps>(
  ({ onMenuToggle, sessionName, className }, ref) => {
    return (
      <header
        ref={ref}
        className={cn(
          "sticky top-0 z-40 border-b border-border",
          "bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
          className
        )}
      >
        <div className="h-14 px-4 flex items-center justify-between">
          {/* Left side: Menu toggle (mobile) and agent name */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onMenuToggle}
              aria-label="Toggle sidebar"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <span className="text-sm font-medium hidden sm:inline">
              Agent C Realtime
            </span>
          </div>

          {/* Center: Session name dropdown */}
          <div className="flex-1 flex justify-center">
            <SessionNameDropdown sessionName={sessionName} />
          </div>

          {/* Right side: Connection status and audio controls */}
          <div className="flex items-center gap-2">
            <AudioControls size="sm" showLabel={false} />
            <ConnectionButton size="sm" showStatus={true} />
          </div>
        </div>
      </header>
    )
  }
)
ChatHeader.displayName = "ChatHeader"