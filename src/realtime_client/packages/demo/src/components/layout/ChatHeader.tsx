"use client"

import * as React from "react"
import { Menu } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { SessionNameDropdown } from "./SessionNameDropdown"
import { 
  ConnectionButton, 
  AudioControls,
  OutputSelector,
  AgentSelector 
} from "@agentc/realtime-ui"
import { toast } from "sonner"

export interface ChatHeaderProps {
  onMenuToggle?: () => void
  sessionName?: string
  className?: string
}

/**
 * ChatHeader component - Main header for the chat interface
 * Contains menu toggle (mobile), session name, selectors, and connection/audio controls
 */
export const ChatHeader = React.forwardRef<HTMLDivElement, ChatHeaderProps>(
  ({ onMenuToggle, sessionName, className }, ref) => {
    // Set up effect to monitor avatar selections
    React.useEffect(() => {
      // Monitor for avatar selection attempts by checking console logs
      const originalWarn = console.warn
      console.warn = function(...args) {
        if (args[0] && args[0].includes('Avatar selection requires HeyGen SDK integration')) {
          toast.info('Avatar integration coming soon!', {
            description: 'HeyGen avatar support will be available in the next release.',
            duration: 5000,
          })
        }
        originalWarn.apply(console, args)
      }
      
      return () => {
        console.warn = originalWarn
      }
    }, [])

    return (
      <header
        ref={ref}
        className={cn(
          "sticky top-0 z-40",
          "bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
          className
        )}
      >
        <div className="h-14 px-4 flex items-center justify-between gap-2">
          {/* Left side: Menu toggle (mobile) and session name dropdown */}
          <div className="flex items-center gap-2 min-w-0">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden shrink-0"
              onClick={onMenuToggle}
              aria-label="Toggle sidebar"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <SessionNameDropdown sessionName={sessionName} />
          </div>

          {/* Center: Agent and Output selectors */}
          <div className="flex items-center gap-2 flex-1 justify-center max-w-md">
            <div className="hidden sm:flex items-center gap-2">
              <AgentSelector className="w-[200px]" />
              <OutputSelector className="w-[180px]" />
            </div>
          </div>

          {/* Right side: Connection status and audio controls */}
          <div className="flex items-center gap-2 shrink-0">
            <AudioControls size="sm" showLabel={false} />
            <ConnectionButton size="sm" showStatus={true} />
          </div>
        </div>

        {/* Mobile selectors - shown below header on small screens */}
        <div className="sm:hidden px-4 pb-2 flex items-center justify-center gap-2 border-b">
          <AgentSelector className="flex-1" />
          <OutputSelector className="flex-1" />
        </div>
      </header>
    )
  }
)
ChatHeader.displayName = "ChatHeader"