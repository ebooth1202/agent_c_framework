"use client"

import * as React from "react"
import { ChevronUp, LogOut, User } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { cn } from "@/lib/utils"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export interface UserDisplayProps {
  className?: string
}

/**
 * UserDisplay component - Shows user info and provides logout functionality
 * Located at the bottom of the sidebar with user avatar and details
 */
export const UserDisplay = React.forwardRef<HTMLDivElement, UserDisplayProps>(
  ({ className }, ref) => {
    const router = useRouter()
    const { user, logout } = useAuth()

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

    const displayName = user?.name || user?.id || "User"
    const displayEmail = user?.email || "user@example.com"
    const initials = getInitials(displayName)

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
                {user?.avatar ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img 
                    src={user.avatar} 
                    alt={displayName}
                    className="size-8 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-xs font-semibold text-primary">
                    {initials}
                  </span>
                )}
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