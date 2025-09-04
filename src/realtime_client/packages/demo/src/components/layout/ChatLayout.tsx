"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChatSidebar } from "../sidebar/ChatSidebar"
import { ChatHeader } from "./ChatHeader"
import { MainContentArea, OutputMode } from "../content/MainContentArea"
// Import the SSR-safe wrapper instead of the UI package directly
// This prevents TipTap v3 from breaking the Next.js build
import { InputAreaWrapper } from "../input/InputAreaWrapper"

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
    const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
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
          isCollapsed={sidebarCollapsed}
          onClose={() => setSidebarOpen(false)}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
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

          {/* Input Area - Using SSR-safe wrapper to prevent TipTap build issues */}
          <div className="bg-muted/30">
            <div className="max-w-4xl mx-auto p-4">
              <InputAreaWrapper 
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    )
  }
)
ChatLayout.displayName = "ChatLayout"