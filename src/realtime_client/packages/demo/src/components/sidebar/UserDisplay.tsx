"use client"

import * as React from "react"
import { ChevronUp, LogOut, User } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { useUserData } from "@agentc/realtime-react"
import { cn } from "@/lib/utils"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export interface UserDisplayProps {
  isCollapsed?: boolean
  className?: string
}

/**
 * UserDisplay component - Shows user info and provides logout functionality
 * 
 * This component now gets user data from the WebSocket connection via
 * the useUserData hook, not from the auth context. The auth context only
 * manages authentication state and tokens.
 */
export const UserDisplay = React.forwardRef<HTMLDivElement, UserDisplayProps>(
  ({ isCollapsed, className }, ref) => {
    const router = useRouter()
    const { logout } = useAuth()
    const { user, isLoading: isUserLoading } = useUserData()

    const handleLogout = React.useCallback(() => {
      logout()
      router.push("/login")
    }, [logout, router])

    // Get user initials for avatar
    const getInitials = (name?: string) => {
      if (!name) return "U"
      const parts = name.split(" ")
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
      }
      return name[0].toUpperCase()
    }

    // Display the user_name from WebSocket data
    const getDisplayName = () => {
      if (user?.user_name) {
        return user.user_name;
      }
      // Show loading state while waiting for WebSocket data
      if (isUserLoading) {
        return "Loading...";
      }
      // This should rarely happen - only if WebSocket fails to send user data
      return "Unknown User";
    }

    const displayName = getDisplayName()
    const userId = user?.user_id || "unknown"
    const displayEmail = user?.email || (isUserLoading ? "loading..." : "no-email@example.com")
    const initials = getInitials(displayName)
    
    // When collapsed, show only avatar
    if (isCollapsed) {
      return (
        <div
          ref={ref}
          className={cn(
            "px-2 pb-2 border-t border-border mt-auto",
            className
          )}
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className={cn(
                  "flex items-center justify-center w-full py-4",
                  "hover:bg-muted rounded-lg transition-colors"
                )}
                aria-label="User menu"
                title={displayName}
              >
                <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden">
                  <span className="text-xs font-semibold text-primary">
                    {initials}
                  </span>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              className="w-56" 
              align="end" 
              side="right"
              sideOffset={8}
            >
              <div className="px-2 py-1.5 text-sm font-medium">{displayName}</div>
              <div className="px-2 pb-2 text-xs text-muted-foreground">{displayEmail}</div>
              <DropdownMenuItem 
                onClick={handleLogout}
                className="cursor-pointer"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          "px-2 pb-1 border-t border-border mt-auto",
          className
        )}
      >
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className={cn(
                "flex flex-row flex-grow items-center !px-1.5 py-6 gap-3 w-full",
                "hover:bg-muted rounded-lg transition-colors"
              )}
              aria-label="User menu"
            >
              <div className="flex-shrink-0 size-8 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden">
                <span className="text-xs font-semibold text-primary">
                  {initials}
                </span>
              </div>
              <div className="flex flex-col items-start overflow-hidden pr-4">
                <span className="truncate text-sm font-medium">
                  {displayName}
                </span>
                <span className="text-xs text-muted-foreground truncate">
                  {displayEmail}
                </span>
              </div>
              <ChevronUp className="h-4 w-4 text-muted-foreground ml-auto" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent 
            className="w-56" 
            align="end" 
            side="top"
            sideOffset={8}
          >
            <DropdownMenuItem 
              onClick={handleLogout}
              className="cursor-pointer"
            >
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    )
  }
)
UserDisplay.displayName = "UserDisplay"