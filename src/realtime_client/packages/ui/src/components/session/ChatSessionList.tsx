"use client"

import * as React from "react"
import { 
  MessageSquare, 
  Search,
  Trash2,
  Loader2,
  AlertCircle,
  Clock,
  ChevronRight
} from "lucide-react"
import { cn } from "../../lib/utils"
import { ScrollArea } from "../ui/scroll-area"
import { Input } from "../ui/input"
import { Button } from "../ui/button"
import { Skeleton } from "../ui/skeleton"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip"
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
 * Internal type for grouped sessions
 */
interface GroupedSessions {
  today: ChatSessionIndexEntry[]
  recent: ChatSessionIndexEntry[]  // Past 14 days
  past: ChatSessionIndexEntry[]     // Older than 14 days
}

/**
 * Group sessions by time periods
 */
function groupSessionsByTime(sessions: ChatSessionIndexEntry[]): GroupedSessions {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const twoWeeksAgo = new Date(today.getTime() - (14 * 24 * 60 * 60 * 1000))
  
  const groups: GroupedSessions = {
    today: [],
    recent: [],
    past: []
  }
  
  sessions.forEach(session => {
    const sessionDate = new Date(session.updated_at || session.created_at || 0)
    
    if (sessionDate >= today) {
      groups.today.push(session)
    } else if (sessionDate >= twoWeeksAgo) {
      groups.recent.push(session)
    } else {
      groups.past.push(session)
    }
  })
  
  return groups
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
  isSearching?: boolean
}> = ({ value, onChange, isSearching }) => (
  <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm p-2 border-b">
    <div className="relative">
      {isSearching ? (
        <Loader2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
      ) : (
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      )}
      <Input
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

/**
 * Session group header component
 */
const SessionGroupHeader: React.FC<{
  label: string
  count?: number
}> = ({ label, count }) => (
  <div className="sticky top-[53px] z-[5] flex items-center gap-2 px-3 py-2 bg-background/90 backdrop-blur-sm">
    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      {label}
    </span>
    {count !== undefined && count > 0 && (
      <span className="text-xs text-muted-foreground">({count})</span>
    )}
    <div className="flex-1 h-px bg-border/50" />
  </div>
)

/**
 * Individual session item component
 */
const SessionItem: React.FC<{
  session: ChatSessionIndexEntry
  isActive: boolean
  onSelect: () => void
  onDelete: () => void
  isDeleting?: boolean
}> = ({ session, isActive, onSelect, onDelete, isDeleting }) => {
  const displayName = getSessionDisplayName(session)
  const timeAgo = getRelativeTime(session.updated_at || session.created_at)
  const agentDisplay = session.agent_name || session.agent_key || 'Unknown Agent'
  
  return (
    <div
      className={cn(
        "group relative flex items-start gap-3 rounded-lg px-3 py-3",
        "transition-all duration-200 cursor-pointer",
        "hover:bg-muted/60 hover:shadow-sm",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        isActive && "bg-accent shadow-sm ring-1 ring-border/50",
        isDeleting && "opacity-50 pointer-events-none"
      )}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect()
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`Select session: ${displayName} with ${agentDisplay}`}
      aria-current={isActive ? "true" : undefined}
    >
      {/* Active indicator */}
      {isActive && (
        <div 
          className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-primary rounded-r-full" 
          aria-hidden="true" 
        />
      )}
      
      {/* Session icon */}
      <MessageSquare className="h-4 w-4 mt-0.5 shrink-0 text-muted-foreground" />
      
      {/* Session content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm truncate">
              {displayName}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {agentDisplay}
            </p>
          </div>
          
          <div className="flex items-center gap-1">
            <span className="text-xs text-muted-foreground">
              {timeAgo}
            </span>
            
            {/* Delete button */}
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={(e) => {
                e.stopPropagation()
                onDelete()
              }}
              aria-label={`Delete session: ${displayName}`}
            >
              <Trash2 className="h-3 w-3" />
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
    const [deleteConfirmId, setDeleteConfirmId] = React.useState<string | null>(null)
    const [deletingId, setDeletingId] = React.useState<string | null>(null)
    
    // Ref for scroll area
    const scrollAreaRef = React.useRef<HTMLDivElement>(null)
    const loadMoreTriggerRef = React.useRef<HTMLDivElement>(null)
    
    // Group sessions by time
    const groupedSessions = React.useMemo(
      () => groupSessionsByTime(filteredSessions),
      [filteredSessions]
    )
    
    // Handle session selection
    const handleSessionSelect = React.useCallback((sessionId: string) => {
      selectSession(sessionId)
      onSessionSelect?.(sessionId)
    }, [selectSession, onSessionSelect])
    
    // Handle delete with confirmation
    const handleDeleteSession = React.useCallback(async (sessionId: string) => {
      setDeletingId(sessionId)
      try {
        await deleteSession(sessionId)
      } catch (error) {
        console.error('Failed to delete session:', error)
      } finally {
        setDeletingId(null)
      }
    }, [deleteSession])
    
    // Intersection observer for infinite scroll
    React.useEffect(() => {
      if (!loadMoreTriggerRef.current || !hasMore || isPaginationLoading) return
      
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting) {
            loadMore()
          }
        },
        { threshold: 0.1 }
      )
      
      observer.observe(loadMoreTriggerRef.current)
      
      return () => observer.disconnect()
    }, [hasMore, isPaginationLoading, loadMore])
    
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
          isSearching={false}
        />
        
        {/* Session count indicator */}
        {totalCount > 0 && (
          <div className="px-3 py-2 text-xs text-muted-foreground border-b">
            Showing {filteredSessions.length} of {totalCount} sessions
          </div>
        )}
        
        {/* Main content area */}
        <ScrollArea className="flex-1" ref={scrollAreaRef}>
          <div className="pb-4">
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
            
            {/* Session groups */}
            {!isLoading && filteredSessions.length > 0 && (
              <>
                {/* Today's sessions */}
                {groupedSessions.today.length > 0 && (
                  <>
                    <SessionGroupHeader label="Today" count={groupedSessions.today.length} />
                    <div className="px-2 py-2 space-y-1">
                      {groupedSessions.today.map(session => (
                        <SessionItem
                          key={session.session_id}
                          session={session}
                          isActive={session.session_id === currentSessionId}
                          onSelect={() => handleSessionSelect(session.session_id)}
                          onDelete={() => handleDeleteSession(session.session_id)}
                          isDeleting={deletingId === session.session_id}
                        />
                      ))}
                    </div>
                  </>
                )}
                
                {/* Recent sessions (past 14 days) */}
                {groupedSessions.recent.length > 0 && (
                  <>
                    <SessionGroupHeader label="Recent" count={groupedSessions.recent.length} />
                    <div className="px-2 py-2 space-y-1">
                      {groupedSessions.recent.map(session => (
                        <SessionItem
                          key={session.session_id}
                          session={session}
                          isActive={session.session_id === currentSessionId}
                          onSelect={() => handleSessionSelect(session.session_id)}
                          onDelete={() => handleDeleteSession(session.session_id)}
                          isDeleting={deletingId === session.session_id}
                        />
                      ))}
                    </div>
                  </>
                )}
                
                {/* Past sessions (older than 14 days) */}
                {groupedSessions.past.length > 0 && (
                  <>
                    <SessionGroupHeader label="Past Sessions" count={groupedSessions.past.length} />
                    <div className="px-2 py-2 space-y-1">
                      {groupedSessions.past.map(session => (
                        <SessionItem
                          key={session.session_id}
                          session={session}
                          isActive={session.session_id === currentSessionId}
                          onSelect={() => handleSessionSelect(session.session_id)}
                          onDelete={() => handleDeleteSession(session.session_id)}
                          isDeleting={deletingId === session.session_id}
                        />
                      ))}
                    </div>
                  </>
                )}
                
                {/* Load more trigger */}
                {hasMore && (
                  <div
                    ref={loadMoreTriggerRef}
                    className="flex items-center justify-center py-4"
                  >
                    {isPaginationLoading && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Loading more sessions...</span>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </ScrollArea>
      </div>
    )
  }
)
ChatSessionList.displayName = "ChatSessionList"