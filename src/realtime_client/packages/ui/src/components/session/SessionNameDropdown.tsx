"use client"

import * as React from "react"
import { ChevronDown, Edit2, Trash2 } from "lucide-react"
import { cn } from "../../lib/utils"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu"

export interface SessionNameDropdownProps {
  sessionName?: string
  className?: string
}

/**
 * SessionNameDropdown component - STUB implementation
 * Displays current session name with dropdown menu for session management
 * Full functionality will be implemented when session management is added
 */
export const SessionNameDropdown = React.forwardRef<HTMLButtonElement, SessionNameDropdownProps>(
  ({ sessionName, className }, ref) => {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            ref={ref}
            className={cn(
              "inline-flex items-center gap-2 px-3 py-1.5 rounded-md",
              "hover:bg-muted transition-colors",
              className
            )}
            aria-label="Session options"
          >
            <span className="text-sm font-medium truncate max-w-[200px]">
              {sessionName || "New Chat"}
            </span>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="center" className="w-56">
          <DropdownMenuItem disabled className="cursor-not-allowed">
            <Edit2 className="mr-2 h-4 w-4" />
            <span>Rename session</span>
            <span className="ml-auto text-xs text-muted-foreground">Coming soon</span>
          </DropdownMenuItem>
          <DropdownMenuItem disabled className="cursor-not-allowed">
            <Trash2 className="mr-2 h-4 w-4" />
            <span>Delete session</span>
            <span className="ml-auto text-xs text-muted-foreground">Coming soon</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }
)
SessionNameDropdown.displayName = "SessionNameDropdown"