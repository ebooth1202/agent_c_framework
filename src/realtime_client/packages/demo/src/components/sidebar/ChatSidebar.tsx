"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { SidebarTopMenu } from "./SidebarTopMenu"
import { ChatSessionList } from "./ChatSessionList"
import { UserDisplay } from "./UserDisplay"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

export interface ChatSidebarProps {
  isOpen?: boolean
  onClose?: () => void
  className?: string
}

/**
 * ChatSidebar component - Main sidebar container with responsive behavior
 * Desktop: Sticky sidebar always visible
 * Mobile: Overlay with backdrop
 */
export const ChatSidebar = React.forwardRef<HTMLDivElement, ChatSidebarProps>(
  ({ isOpen = true, onClose, className }, ref) => {
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

    // Mobile overlay backdrop
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
            <UserDisplay />
          </div>
        </>
      )
    }

    // Desktop sidebar (always visible) or hidden mobile
    if (!isMobile || !isOpen) {
      return (
        <div
          ref={ref}
          className={cn(
            "w-72 border-r border-border bg-muted/30",
            "lg:sticky lg:top-0 lg:h-screen lg:flex lg:flex-col",
            "hidden lg:flex", // Hide on mobile, show on desktop
            className
          )}
        >
          <SidebarTopMenu />
          <ChatSessionList />
          <UserDisplay />
        </div>
      )
    }

    return null
  }
)
ChatSidebar.displayName = "ChatSidebar"