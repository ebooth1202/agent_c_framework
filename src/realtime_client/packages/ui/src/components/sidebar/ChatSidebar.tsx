"use client"

import * as React from "react"
import { cn } from "../../lib/utils"
import { SidebarTopMenu } from "./SidebarTopMenu"
import { ChatSessionList } from "../session/ChatSessionList"
import { UserDisplay } from "../controls/UserDisplay"
import { X, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "../ui/button"

export interface ChatSidebarProps {
  isOpen?: boolean
  isCollapsed?: boolean
  onClose?: () => void
  onToggleCollapse?: () => void
  className?: string
}

/**
 * ChatSidebar component - Main sidebar container with responsive behavior
 * Desktop: Sticky sidebar always visible (can be collapsed but not hidden)
 * Mobile: Overlay with backdrop (can be fully hidden)
 */
export const ChatSidebar = React.forwardRef<HTMLDivElement, ChatSidebarProps>(
  ({ isOpen = true, isCollapsed = false, onClose, onToggleCollapse, className }, ref) => {
    const [isMobile, setIsMobile] = React.useState(false)

    // Detect mobile viewport
    React.useEffect(() => {
      const checkMobile = () => {
        setIsMobile(window.innerWidth < 1024)
      }
      
      checkMobile()
      window.addEventListener("resize", checkMobile)
      return () => window.removeEventListener("resize", checkMobile)
    }, [])

    // Mobile overlay - only render when mobile AND open
    if (isMobile && isOpen) {
      return (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
            onClick={onClose}
            aria-hidden="true"
          />
          
          {/* Mobile Sidebar */}
          <div
            ref={ref}
            className={cn(
              "fixed inset-y-0 left-0 z-50 w-72 bg-background shadow-lg",
              "flex flex-col",
              "animate-in slide-in-from-left duration-200",
              className
            )}
          >
            {/* Mobile Close Button */}
            <div className="flex items-center justify-between px-2 pt-2">
              <span className="text-sm font-semibold px-2">Navigation</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
                aria-label="Close sidebar"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Sidebar Content */}
            <SidebarTopMenu />
            <ChatSessionList />
            <UserDisplay variant="compact" showMenu={true} />
          </div>
        </>
      )
    }

    // Desktop sidebar - always visible when not mobile
    // Mobile - hidden when closed
    if (!isMobile) {
      return (
        <div
          ref={ref}
          className={cn(
            "border-r border-border bg-muted/30 transition-all duration-300 ease-in-out",
            "sticky top-0 h-screen flex flex-col",
            isCollapsed ? "w-16" : "w-72",
            className
          )}
        >
          {/* Sidebar Header with Title and Collapse Button */}
          <div className="flex items-center justify-between px-2 pt-2 pb-1 border-b border-border mb-4">
            <span className={cn(
              "text-sm font-semibold transition-opacity duration-200 overflow-hidden whitespace-nowrap",
              isCollapsed ? "opacity-0 w-0" : "opacity-100 px-2"
            )}>
              Agent C Realtime
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleCollapse}
              className="h-8 w-8 flex-shrink-0"
              aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          {/* Sidebar Content */}
          <div className={cn(
            "flex flex-col flex-1 overflow-hidden",
            isCollapsed && "items-center"
          )}>
            <SidebarTopMenu isCollapsed={isCollapsed} />
            <ChatSessionList isCollapsed={isCollapsed} />
            <UserDisplay variant="compact" avatarSize={isCollapsed ? "sm" : "md"} showMenu={true} />
          </div>
        </div>
      )
    }

    // Mobile closed state - render nothing
    return null
  }
)
ChatSidebar.displayName = "ChatSidebar"