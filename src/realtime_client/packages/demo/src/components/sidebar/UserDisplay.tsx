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
  isCollapsed?: boolean
  className?: string
}

/**
 * UserDisplay component - Shows user info and provides logout functionality
 * Located at the bottom of the sidebar with user avatar and details
 */
export const UserDisplay = React.forwardRef<HTMLDivElement, UserDisplayProps>(
  ({ isCollapsed, className }, ref) => {
    const router = useRouter()
    const { user, logout } = useAuth()

    // DEBUG: Log what we're receiving from auth context
    React.useEffect(() => {
      console.log('%c[UserDisplay] Component mounted/updated', 'color: magenta; font-weight: bold');
      console.log('[UserDisplay] User object received from auth:', user);
      
      if (!user) {
        console.error('%c[UserDisplay] 🚨 USER IS NULL!', 'color: red; font-size: 14px; font-weight: bold');
        console.error('[UserDisplay] This will cause fallback values to be displayed!');
      } else {
        console.log('[UserDisplay] User data breakdown:', {
          hasUserId: !!user.user_id,
          userId: user.user_id,
          hasEmail: !!user.email,
          email: user.email,
          hasUserName: !!user.user_name,
          userName: user.user_name,
          hasFirstName: !!user.first_name,
          firstName: user.first_name,
          hasLastName: !!user.last_name,
          lastName: user.last_name,
          hasId: !!user.id,
          id: user.id,
          allKeys: Object.keys(user)
        });
        
        // CRITICAL: Check for missing fields
        const missingFields = [];
        if (!user.email) missingFields.push('email');
        if (!user.user_name) missingFields.push('user_name');
        if (!user.user_id && !user.id) missingFields.push('user_id/id');
        
        if (missingFields.length > 0) {
          console.error(`%c[UserDisplay] 🚨 MISSING CRITICAL FIELDS: ${missingFields.join(', ')}`, 'color: red; font-weight: bold');
        }
      }
    }, [user]);

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

    // Display the user_name ONLY - this is what the user wants to see
    const getDisplayName = () => {
      if (user?.user_name) {
        return user.user_name;
      }
      // NO FALLBACK TO "User" - if there's no user_name, that's a critical error
      console.error('🚨 CRITICAL: No user_name available in user object:', user);
      return "ERROR: No Username";
    }

    const displayName = getDisplayName()
    const userId = user?.user_id || "unknown"
    const displayEmail = user?.email || "user@example.com"
    const initials = getInitials(displayName)
    
    // Log what will be displayed
    React.useEffect(() => {
      console.log('[UserDisplay] Rendering with values:', {
        displayName,
        displayEmail,
        userId,
        initials,
        isFallback: displayName === "User" || displayEmail === "user@example.com"
      });
      
      if (displayName === "User" || displayEmail === "user@example.com") {
        console.error('%c[UserDisplay] 🚨 USING FALLBACK VALUES!', 'color: red; font-size: 14px; font-weight: bold');
      }
    }, [displayName, displayEmail, userId, initials]);

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