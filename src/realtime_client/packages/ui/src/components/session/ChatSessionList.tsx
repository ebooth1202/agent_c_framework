"use client"

import * as React from "react"
import { 
  MessageSquare, 
  Search,
  Trash2,
  Loader2,
  AlertCircle,
  ChevronRight
} from "lucide-react"
import { cn } from "../../lib/utils"
import { Input } from "../ui/input"
import { Button, buttonVariants } from "../ui/button"
import { Skeleton } from "../ui/skeleton"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog"
import { useChatSessionList } from "@agentc/realtime-react"
import type { ChatSessionIndexEntry } from "@agentc/realtime-core"

/**
 * Props for the ChatSessionList component
 */
export interface ChatSessionListProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Whether the sidebar is collapsed */
  isCollapsed?: boolean
  /** Additional className for styling */
  className?: string
  /** Callback when a session is selected */
  onSessionSelect?: (sessionId: string) => void
  /** Whether to auto-load sessions on mount */
  autoLoad?: boolean
}

/**
 * Format relative time for session timestamps
 */
function getRelativeTime(timestamp: string | null): string {
  if (!timestamp) return 'Unknown'
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m`
  if (diffHours < 24) return `${diffHours}h`
  if (diffDays < 7) return `${diffDays}d`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w`
  
  // Format as month/day for older sessions
  return `${date.getMonth() + 1}/${date.getDate()}`
}

/**
 * Get display name for a session
 */
function getSessionDisplayName(session: ChatSessionIndexEntry): string {
  if (session.session_name) {
    return session.session_name
  }
  
  const date = new Date(session.created_at || 0)
  const hours = date.getHours()
  const minutes = date.getMinutes()
  const ampm = hours >= 12 ? 'PM' : 'AM'
  const displayHours = hours % 12 || 12
  const displayMinutes = minutes.toString().padStart(2, '0')
  
  return `Chat from ${date.getMonth() + 1}/${date.getDate()}, ${displayHours}:${displayMinutes} ${ampm}`
}

/**
 * Search/Filter bar component
 */
const SearchFilterBar: React.FC<{
  value: string
  onChange: (value: string) => void
  onClear?: () => void
  isSearching?: boolean
}> = ({ value, onChange, onClear, isSearching }) => {
  const searchInputRef = React.useRef<HTMLInputElement>(null)
  
  // Handle escape key to clear search
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && value) {
        e.preventDefault()
        onClear?.()
        searchInputRef.current?.focus()
      }
    }
    
    if (searchInputRef.current) {
      searchInputRef.current.addEventListener('keydown', handleKeyDown)
      return () => searchInputRef.current?.removeEventListener('keydown', handleKeyDown)
    }
  }, [value, onClear])
  
  return (
    <div className="bg-background p-2 border-b">
      <div className="relative">
        {isSearching ? (
          <Loader2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        ) : (
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        )}
        <Input
          ref={searchInputRef}
          type="search"
          placeholder="Search sessions..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pl-9 h-9 text-sm"
          aria-label="Search sessions"
        />
      </div>
    </div>
  )
}

/**
 * Session group header component
 */
const SessionGroupHeader: React.FC<{
  label: string
  count: number
  groupId: string
  onHeaderClick?: () => void
}> = ({ label, count, groupId, onHeaderClick }) => (
  <div 
    className={cn(
      "flex items-center gap-2 px-3 py-2",
      "bg-background",
      "border-b border-t",  // Keep borders for visual separation
      "cursor-pointer hover:bg-muted/50 transition-colors"
    )}
    onClick={onHeaderClick}
    role="heading"
    aria-level={3}
    id={`header-${groupId}`}
  >
    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      {label}
    </span>
    <span className="text-xs text-muted-foreground">({count})</span>
    <div className="flex-1 h-px bg-border/50" aria-hidden="true" />
  </div>
)

/**
 * Delete confirmation dialog component
 */
const DeleteSessionDialog: React.FC<{
  session: ChatSessionIndexEntry | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  isDeleting?: boolean
}> = ({ session, open, onOpenChange, onConfirm, isDeleting }) => {
  const sessionName = session ? getSessionDisplayName(session) : ''
  
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Session?</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete '{sessionName}'? This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={isDeleting}
            className={cn(
              buttonVariants({ variant: "destructive" }),
              isDeleting && "opacity-50 cursor-wait"
            )}
          >
            {isDeleting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

/**
 * Individual session item component
 */
const SessionItem: React.FC<{
  session: ChatSessionIndexEntry
  isActive: boolean
  isFocused?: boolean
  onSelect: () => void
  onDelete: () => void
  onFocus?: () => void
  isDeleting?: boolean
  index?: number
  totalCount?: number
}> = ({ session, isActive, isFocused, onSelect, onDelete, onFocus, isDeleting, index, totalCount }) => {
  const displayName = getSessionDisplayName(session)
  const timeAgo = getRelativeTime(session.updated_at || session.created_at)
  const agentDisplay = session.agent_name || session.agent_key || 'Unknown Agent'
  
  return (
    <div
      className={cn(
        "group relative px-3 py-3",
        "transition-all duration-200 cursor-pointer",
        "min-h-[44px]", // 44px touch target
        "hover:bg-muted/60",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
        isActive && "bg-accent",
        isFocused && "ring-2 ring-ring ring-offset-1",
        isDeleting && "opacity-50 pointer-events-none",
        "motion-safe:transition-all motion-reduce:transition-none"
      )}
      onClick={onSelect}
      onFocus={onFocus}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect()
        } else if (e.key === 'Delete') {
          e.preventDefault()
          onDelete()
        }
      }}
      tabIndex={isFocused ? 0 : -1}
      role="option"
      aria-selected={isActive}
      aria-label={`Session ${index !== undefined ? index + 1 : ''} of ${totalCount || ''}: ${displayName} with ${agentDisplay}, last updated ${timeAgo}`}
      aria-posinset={index !== undefined ? index + 1 : undefined}
      aria-setsize={totalCount}
    >
      {/* Active indicator */}
      {isActive && (
        <div 
          className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-primary rounded-r-full" 
          aria-hidden="true" 
        />
      )}
      
      {/* Session content - Two-row layout */}
      <div className="flex flex-col gap-1">
        {/* Row 1: Session name - full width */}
        <p className="font-medium text-sm leading-tight">
          {displayName}
        </p>
        
        {/* Row 2: Agent name on left | Age + Delete button on right */}
        <div className="flex items-center justify-between gap-2">
          {/* Left side: Agent name */}
          <p className="text-xs text-muted-foreground truncate">
            {agentDisplay}
          </p>
          
          {/* Right side: Age + Delete button */}
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {timeAgo}
            </span>
            
            {/* Delete button */}
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-6 w-6 flex-shrink-0 -mr-1",  // Smaller delete button
                "opacity-0 group-hover:opacity-100 group-focus-within:opacity-100",
                "transition-opacity",
                "focus-visible:opacity-100"
              )}
              onClick={(e) => {
                e.stopPropagation()
                onDelete()
              }}
              tabIndex={isFocused ? 0 : -1}
              aria-label={`Delete session: ${displayName}`}
            >
              <Trash2 className="h-3 w-3" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Empty state component
 */
const EmptyState: React.FC<{
  searchQuery?: string
}> = ({ searchQuery }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="rounded-full bg-muted/50 p-4 mb-4">
      <MessageSquare className="h-6 w-6 text-muted-foreground" />
    </div>
    <h3 className="text-base font-semibold text-foreground mb-2">
      {searchQuery ? 'No matching sessions' : 'No conversations yet'}
    </h3>
    <p className="text-sm text-muted-foreground text-center max-w-[200px]">
      {searchQuery 
        ? `No sessions found matching "${searchQuery}"`
        : 'Start a new chat to begin your conversation history'}
    </p>
  </div>
)

/**
 * Loading skeleton component
 */
const LoadingSkeleton: React.FC = () => (
  <div className="space-y-3 p-3">
    {[...Array(5)].map((_, i) => (
      <div key={i} className="space-y-2">
        <Skeleton className="h-16 w-full rounded-lg" />
      </div>
    ))}
  </div>
)

/**
 * Error state component
 */
const ErrorState: React.FC<{
  error: Error
  onRetry: () => void
}> = ({ error, onRetry }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="rounded-full bg-destructive/10 p-4 mb-4">
      <AlertCircle className="h-6 w-6 text-destructive" />
    </div>
    <h3 className="text-base font-semibold text-foreground mb-2">
      Failed to load sessions
    </h3>
    <p className="text-sm text-muted-foreground text-center max-w-[200px] mb-4">
      {error.message || 'An unexpected error occurred'}
    </p>
    <Button 
      variant="outline" 
      size="sm"
      onClick={onRetry}
    >
      Try again
    </Button>
  </div>
)

/**
 * Collapsed view component
 */
const CollapsedView: React.FC<{
  sessions: ChatSessionIndexEntry[]
  currentSessionId: string | null
  onSessionSelect: (sessionId: string) => void
  onExpand?: () => void
}> = ({ sessions, currentSessionId, onSessionSelect, onExpand }) => (
  <div className="flex flex-col items-center gap-2 p-2">
    <TooltipProvider>
      {sessions.slice(0, 5).map(session => (
        <Tooltip key={session.session_id}>
          <TooltipTrigger asChild>
            <Button
              variant={session.session_id === currentSessionId ? "default" : "ghost"}
              size="icon"
              className="h-10 w-10"
              onClick={() => onSessionSelect(session.session_id)}
              aria-label={`Select ${getSessionDisplayName(session)}`}
            >
              <MessageSquare className="h-5 w-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            <p>{getSessionDisplayName(session)}</p>
            <p className="text-xs text-muted-foreground">
              {getRelativeTime(session.updated_at || session.created_at)}
            </p>
          </TooltipContent>
        </Tooltip>
      ))}
      
      {sessions.length > 5 && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-10 w-10"
              onClick={onExpand}
              aria-label="Show all sessions"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            <p>Show all sessions</p>
          </TooltipContent>
        </Tooltip>
      )}
    </TooltipProvider>
  </div>
)

/**
 * ChatSessionList component - Full implementation with session management
 * Displays user's chat session history with search, filtering, and pagination
 */
export const ChatSessionList = React.forwardRef<HTMLDivElement, ChatSessionListProps>(
  ({ isCollapsed, className, onSessionSelect, autoLoad = true, ...props }, ref) => {
    // Use the chat session list hook
    const {
      sessions,
      filteredSessions,
      sessionGroups,  // Using the sessionGroups from the hook
      searchQuery,
      isLoading,
      isPaginationLoading,
      error,
      hasMore,
      totalCount,
      currentSessionId,
      loadMore,
      selectSession,
      deleteSession,
      searchSessions,
      refresh
    } = useChatSessionList({ 
      autoLoad,
      pageSize: 50,
      searchDebounceMs: 300
    })
    
    // State for delete confirmation
    const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
    const [sessionToDelete, setSessionToDelete] = React.useState<ChatSessionIndexEntry | null>(null)
    const [deletingId, setDeletingId] = React.useState<string | null>(null)
    
    // State for keyboard navigation
    const [focusedIndex, setFocusedIndex] = React.useState(-1)
    
    // Announcements for screen readers
    const [announcement, setAnnouncement] = React.useState('')
    
    // Refs
    const scrollContainerRef = React.useRef<HTMLDivElement>(null)
    const loadMoreTriggerRef = React.useRef<HTMLDivElement>(null)
    const searchInputRef = React.useRef<HTMLInputElement>(null)
    
    // Handle session selection
    const handleSessionSelect = React.useCallback((sessionId: string) => {
      selectSession(sessionId)
      onSessionSelect?.(sessionId)
      setAnnouncement('Session selected')
    }, [selectSession, onSessionSelect])
    
    // Handle delete request (opens dialog)
    const handleDeleteRequest = React.useCallback((session: ChatSessionIndexEntry) => {
      setSessionToDelete(session)
      setDeleteDialogOpen(true)
    }, [])
    
    // Handle delete confirmation
    const handleDeleteConfirm = React.useCallback(async () => {
      if (!sessionToDelete) return
      
      setDeletingId(sessionToDelete.session_id)
      setDeleteDialogOpen(false)
      
      try {
        await deleteSession(sessionToDelete.session_id)
        setAnnouncement('Session deleted successfully')
      } catch (error) {
        console.error('Failed to delete session:', error)
        setAnnouncement('Failed to delete session')
      } finally {
        setDeletingId(null)
        setSessionToDelete(null)
      }
    }, [sessionToDelete, deleteSession])
    
    // Handle clear search
    const handleClearSearch = React.useCallback(() => {
      searchSessions('')
      searchInputRef.current?.focus()
    }, [searchSessions])
    
    // Handle header click to scroll UP to section
    const handleHeaderClick = React.useCallback((groupId: string) => {
      const element = document.getElementById(`header-${groupId}`)
      if (element) {
        // Use scrollIntoView with block: 'start' to bring section to TOP of viewport
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start'  // This ensures the section scrolls to the TOP
        })
      }
    }, [])
    
    // Keyboard navigation handler
    const handleKeyboardNavigation = React.useCallback((e: React.KeyboardEvent) => {
      const allSessions = filteredSessions
      
      if (allSessions.length === 0) return
      
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusedIndex(prev => {
            const next = prev < allSessions.length - 1 ? prev + 1 : prev
            // Scroll focused item into view
            const element = scrollContainerRef.current?.querySelectorAll('[role="option"]')[next] as HTMLElement
            element?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
            return next
          })
          break
          
        case 'ArrowUp':
          e.preventDefault()
          setFocusedIndex(prev => {
            const next = prev > 0 ? prev - 1 : 0
            const element = scrollContainerRef.current?.querySelectorAll('[role="option"]')[next] as HTMLElement
            element?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
            return next
          })
          break
          
        case 'Home':
          e.preventDefault()
          setFocusedIndex(0)
          scrollContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
          break
          
        case 'End':
          e.preventDefault()
          setFocusedIndex(allSessions.length - 1)
          scrollContainerRef.current?.scrollTo({ 
            top: scrollContainerRef.current.scrollHeight, 
            behavior: 'smooth' 
          })
          break
          
        case 'Enter':
        case ' ':
          if (focusedIndex >= 0 && focusedIndex < allSessions.length) {
            e.preventDefault()
            handleSessionSelect(allSessions[focusedIndex].session_id)
          }
          break
          
        case 'Delete':
          if (focusedIndex >= 0 && focusedIndex < allSessions.length) {
            e.preventDefault()
            handleDeleteRequest(allSessions[focusedIndex])
          }
          break
      }
    }, [filteredSessions, focusedIndex, handleSessionSelect, handleDeleteRequest])
    
    // Intersection observer for infinite scroll
    React.useEffect(() => {
      const triggerElement = loadMoreTriggerRef.current
      if (!triggerElement) {
        console.debug('No trigger element for infinite scroll')
        return
      }
      
      // Create observer with proper threshold
      const observer = new IntersectionObserver(
        (entries) => {
          const [entry] = entries
          if (entry.isIntersecting) {
            console.debug('Trigger element intersecting, attempting to load more...', { hasMore, isPaginationLoading })
            // Call loadMore directly without checking conditions here
            // The loadMore function handles its own validation
            loadMore()
          }
        },
        { 
          root: scrollContainerRef.current,
          rootMargin: '100px', // Trigger 100px before reaching the element
          threshold: 0.01 // More sensitive threshold
        }
      )
      
      observer.observe(triggerElement)
      
      return () => {
        if (triggerElement) {
          observer.unobserve(triggerElement)
        }
        observer.disconnect()
      }
    }, [loadMore]) // Only depend on loadMore, not on hasMore or isPaginationLoading
    
    // Collapsed view
    if (isCollapsed) {
      return (
        <div
          ref={ref}
          className={cn("flex-1 overflow-hidden", className)}
          {...props}
        >
          <CollapsedView
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSessionSelect={handleSessionSelect}
          />
        </div>
      )
    }
    
    // Main expanded view
    return (
      <div
        ref={ref}
        className={cn("flex flex-col h-full", className)}
        {...props}
      >
        {/* Search bar */}
        <SearchFilterBar
          value={searchQuery}
          onChange={searchSessions}
          onClear={handleClearSearch}
          isSearching={false}
        />
        
        {/* Main scrollable content area */}
        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto"
          role="listbox"
          aria-label="Chat sessions"
          onKeyDown={handleKeyboardNavigation}
          tabIndex={0}
        >
          {/* Loading state */}
          {isLoading && sessions.length === 0 && (
            <LoadingSkeleton />
          )}
          
          {/* Error state */}
          {error && sessions.length === 0 && (
            <ErrorState error={error} onRetry={refresh} />
          )}
          
          {/* Empty state */}
          {!isLoading && !error && filteredSessions.length === 0 && (
            <EmptyState searchQuery={searchQuery} />
          )}
          
          {/* Session groups using sessionGroups from hook */}
          {!isLoading && sessionGroups.length > 0 && (
            <>
              {sessionGroups.map((group, groupIndex) => {
                let globalIndexOffset = 0
                // Calculate the offset for this group
                for (const g of sessionGroups) {
                  if (g.group === group.group) break
                  globalIndexOffset += g.sessions.length
                }
                
                return (
                  <div key={group.group}>
                    {/* Section header */}
                    <SessionGroupHeader
                      label={group.label}
                      count={group.count}
                      groupId={group.group}
                      onHeaderClick={() => handleHeaderClick(group.group)}
                    />
                    
                    {/* Session items */}
                    <div className="pb-2">
                      {group.sessions.map((session, idx) => {
                        const globalIndex = globalIndexOffset + idx
                        return (
                          <SessionItem
                            key={session.session_id}
                            session={session}
                            isActive={session.session_id === currentSessionId}
                            isFocused={focusedIndex === globalIndex}
                            onSelect={() => handleSessionSelect(session.session_id)}
                            onDelete={() => handleDeleteRequest(session)}
                            onFocus={() => setFocusedIndex(globalIndex)}
                            isDeleting={deletingId === session.session_id}
                            index={globalIndex}
                            totalCount={filteredSessions.length}
                          />
                        )
                      })}
                    </div>
                  </div>
                )
              })}
              
              {/* Load more trigger - Always render when hasMore, visibility controls loading */}
              {hasMore && (
                <div
                  ref={loadMoreTriggerRef}
                  className="flex items-center justify-center py-4 min-h-[60px]"
                  aria-label="Load more sessions trigger"
                >
                  {isPaginationLoading ? (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground" role="status" aria-live="polite">
                      <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                      <span>Loading more sessions...</span>
                    </div>
                  ) : (
                    // Invisible element to maintain height and trigger intersection
                    <div className="text-sm text-muted-foreground opacity-50">
                      <span>Scroll for more</span>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
        
        {/* Delete confirmation dialog */}
        <DeleteSessionDialog
          session={sessionToDelete}
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          onConfirm={handleDeleteConfirm}
          isDeleting={!!deletingId}
        />
        
        {/* Screen reader announcements */}
        <div 
          className="sr-only" 
          role="status" 
          aria-live="assertive" 
          aria-atomic="true"
        >
          {announcement}
        </div>
      </div>
    )
  }
)
ChatSessionList.displayName = "ChatSessionList"