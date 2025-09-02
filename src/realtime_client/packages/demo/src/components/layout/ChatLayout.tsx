"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChatSidebar } from "../sidebar/ChatSidebar"
import { ChatHeader } from "./ChatHeader"
import { MainContentArea, OutputMode } from "../content/MainContentArea"
import { InputArea } from "@agentc/realtime-ui"

export interface ChatLayoutProps {
  outputMode?: OutputMode
  sessionName?: string
  className?: string
  children?: React.ReactNode
}

/**
 * ChatLayout component - Main container for the entire chat interface
 * Manages overall layout structure with sidebar, header, content area, and input
 */
export const ChatLayout = React.forwardRef<HTMLDivElement, ChatLayoutProps>(
  ({ outputMode = 'chat', sessionName, className, children }, ref) => {
    const [sidebarOpen, setSidebarOpen] = React.useState(false)
    const [currentOutputMode, setCurrentOutputMode] = React.useState<OutputMode>(outputMode)

    // Note: Output mode is controlled by the InputArea component internally
    // The display mode will update based on the SDK's state
    // For now we'll use a default mode

    return (
      <div
        ref={ref}
        className={cn(
          "min-h-screen bg-background text-foreground flex",
          className
        )}
      >
        {/* Sidebar */}
        <ChatSidebar 
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <ChatHeader 
            onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
            sessionName={sessionName}
          />

          {/* Dynamic Content Area */}
          <MainContentArea outputMode={currentOutputMode} />

          {/* Input Area - Using existing component */}
          <div className="border-t border-border">
            <InputArea 
              className="max-w-4xl mx-auto"
            />
          </div>
        </div>
      </div>
    )
  }
)
ChatLayout.displayName = "ChatLayout"