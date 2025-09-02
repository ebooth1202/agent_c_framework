# ChatSessionList Component Design Specification

## Component Overview

The ChatSessionList component displays a user's chat history in the sidebar, organized by time groups with rich session information. It replaces the placeholder stub in the ChatSidebar component and integrates with the authentication API's session data.

## Data Model

```typescript
interface ChatSession {
  session_id: string
  session_name: string | null
  created_at: string | null  // ISO timestamp
  updated_at: string | null  // ISO timestamp
  token_count: number
  messages: Message[]
  agent_config: AgentConfiguration
}

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}
```

## Component Architecture

### Main Component Structure

```tsx
const ChatSessionList: React.FC = () => {
  const { sessions, currentSessionId, loadSession } = useChatSessions()
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  // Group sessions by time periods
  const groupedSessions = useMemo(() => 
    groupSessionsByTime(sessions, searchQuery),
    [sessions, searchQuery]
  )
  
  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Search Bar */}
      <SessionSearch />
      
      {/* Session Groups */}
      <SessionGroups 
        groups={groupedSessions}
        currentSessionId={currentSessionId}
        onSessionClick={loadSession}
        isLoading={isLoading}
      />
      
      {/* Empty State */}
      {sessions.length === 0 && <EmptyState />}
    </div>
  )
}
```

## Visual Design Specifications

### Container Layout

```css
/* Main Container */
className="flex-1 flex flex-col min-h-0 px-2"

/* Scrollable Area */
className="flex-1 overflow-y-auto overflow-x-hidden 
           scrollbar-thin scrollbar-thumb-border 
           scrollbar-track-transparent"
```

### Search Component (Optional Enhancement)

```tsx
<div className="sticky top-0 z-10 pb-2 mb-1 
                bg-gradient-to-b from-background via-background/95 to-transparent">
  <div className="relative">
    <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
    <input
      type="text"
      placeholder="Search conversations..."
      className="w-full h-8 pl-8 pr-2 text-xs rounded-md
                 bg-muted/50 border border-border/50
                 focus:bg-background focus:border-border
                 focus:outline-none focus:ring-1 focus:ring-ring/20
                 placeholder:text-muted-foreground/60
                 transition-colors duration-200"
    />
  </div>
</div>
```

### Time Group Headers

```tsx
const TimeGroupHeader: React.FC<{ label: string }> = ({ label }) => (
  <div className="sticky top-8 z-[5] flex items-center gap-2 
                  pt-3 pb-1.5 px-1
                  bg-gradient-to-b from-background via-background/90 to-transparent">
    <span className="text-[11px] font-medium text-muted-foreground/70 
                     uppercase tracking-wider">
      {label}
    </span>
    <div className="flex-1 h-px bg-border/30" />
  </div>
)

// Time group labels:
- "Today"
- "Yesterday" 
- "This Week"
- "This Month"
- "Older"
```

### Session Item Component

```tsx
const SessionItem: React.FC<SessionItemProps> = ({ 
  session, 
  isActive, 
  onClick,
  isLoading 
}) => {
  const sessionName = deriveSessionName(session)
  const preview = getMessagePreview(session.messages)
  const relativeTime = getRelativeTime(session.updated_at)
  const messageCount = session.messages.length
  
  return (
    <button
      onClick={() => onClick(session.session_id)}
      disabled={isLoading}
      className={cn(
        // Base styles
        "group relative w-full text-left rounded-lg px-2.5 py-2 mb-0.5",
        "transition-all duration-200 ease-out",
        
        // Hover state
        "hover:bg-muted/60 hover:shadow-sm",
        
        // Active state
        isActive && "bg-muted shadow-sm ring-1 ring-border/50",
        
        // Loading state
        isLoading && "opacity-60 cursor-wait",
        
        // Focus state
        "focus-visible:outline-none focus-visible:ring-1",
        "focus-visible:ring-ring focus-visible:ring-offset-1"
      )}
      aria-current={isActive ? "true" : undefined}
      aria-label={`Chat: ${sessionName}, ${relativeTime}, ${messageCount} messages`}
    >
      {/* Active Indicator */}
      {isActive && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 
                        w-0.5 h-5 bg-primary rounded-r-full" 
             aria-hidden="true" />
      )}
      
      {/* Content Container */}
      <div className="flex flex-col gap-0.5 min-w-0">
        {/* Session Name and Time */}
        <div className="flex items-baseline justify-between gap-2">
          <span className={cn(
            "text-sm font-medium truncate flex-1",
            isActive ? "text-foreground" : "text-foreground/90"
          )}>
            {sessionName}
          </span>
          <span className="text-[10px] text-muted-foreground/60 flex-shrink-0">
            {relativeTime}
          </span>
        </div>
        
        {/* Message Preview */}
        <p className={cn(
          "text-xs truncate",
          isActive ? "text-muted-foreground/80" : "text-muted-foreground/60"
        )}>
          {preview}
        </p>
        
        {/* Metadata Row */}
        <div className="flex items-center gap-3 mt-0.5">
          <span className="inline-flex items-center gap-1">
            <MessageSquare className="h-2.5 w-2.5 text-muted-foreground/40" />
            <span className="text-[10px] text-muted-foreground/50">
              {messageCount}
            </span>
          </span>
          <span className="inline-flex items-center gap-1">
            <Hash className="h-2.5 w-2.5 text-muted-foreground/40" />
            <span className="text-[10px] text-muted-foreground/50">
              {formatTokenCount(session.token_count)}
            </span>
          </span>
        </div>
      </div>
      
      {/* Hover Actions (Future Enhancement) */}
      <div className={cn(
        "absolute right-2 top-2 opacity-0 group-hover:opacity-100",
        "transition-opacity duration-200",
        "flex items-center gap-1"
      )}>
        <button
          className="p-1 rounded hover:bg-muted"
          onClick={(e) => {
            e.stopPropagation()
            // Archive action
          }}
          aria-label="Archive conversation"
        >
          <Archive className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>
    </button>
  )
}
```

### Empty State

```tsx
const EmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-8 px-4">
    <div className="rounded-full bg-muted/50 p-3 mb-3">
      <MessageSquare className="h-5 w-5 text-muted-foreground/50" />
    </div>
    <p className="text-sm font-medium text-foreground/80 mb-1">
      No conversations yet
    </p>
    <p className="text-xs text-muted-foreground/60 text-center">
      Start a new chat to begin your conversation history
    </p>
  </div>
)
```

### Loading State

```tsx
const LoadingState: React.FC = () => (
  <div className="space-y-2 px-2 py-4">
    {[...Array(3)].map((_, i) => (
      <div key={i} className="animate-pulse">
        <div className="rounded-lg bg-muted/30 p-2.5">
          <div className="h-4 bg-muted/50 rounded w-3/4 mb-2" />
          <div className="h-3 bg-muted/40 rounded w-full mb-1" />
          <div className="flex gap-3">
            <div className="h-2 bg-muted/30 rounded w-12" />
            <div className="h-2 bg-muted/30 rounded w-16" />
          </div>
        </div>
      </div>
    ))}
  </div>
)
```

## Interaction Patterns

### Session Selection

```typescript
const handleSessionClick = async (sessionId: string) => {
  // Prevent double-clicks
  if (isLoading || sessionId === currentSessionId) return
  
  setIsLoading(true)
  
  try {
    // Visual feedback immediately
    await loadSession(sessionId)
    
    // Scroll to top of messages (in main area)
    scrollToTop()
    
    // Mobile: Close sidebar
    if (isMobile) {
      closeSidebar()
    }
  } catch (error) {
    toast.error('Failed to load conversation')
  } finally {
    setIsLoading(false)
  }
}
```

### Keyboard Navigation

```typescript
// Arrow key navigation through sessions
useKeyboardNavigation({
  onArrowUp: () => selectPreviousSession(),
  onArrowDown: () => selectNextSession(),
  onEnter: () => loadSelectedSession(),
  onEscape: () => clearSelection(),
})
```

## Helper Functions

### Session Name Derivation

```typescript
function deriveSessionName(session: ChatSession): string {
  // Priority 1: Explicit session name
  if (session.session_name) {
    return session.session_name
  }
  
  // Priority 2: First user message (truncated)
  const firstUserMessage = session.messages.find(m => m.role === 'user')
  if (firstUserMessage) {
    const text = firstUserMessage.content
    return text.length > 30 ? `${text.substring(0, 30)}...` : text
  }
  
  // Priority 3: Agent name + time
  const agentName = session.agent_config?.name || 'Agent'
  const time = formatDateTime(session.created_at)
  return `${agentName} Chat - ${time}`
}
```

### Message Preview Generation

```typescript
function getMessagePreview(messages: Message[]): string {
  if (!messages.length) return 'No messages yet'
  
  // Get last meaningful message (skip system messages)
  const lastMessage = messages
    .filter(m => m.role !== 'system')
    .slice(-1)[0]
  
  if (!lastMessage) return 'No messages yet'
  
  const prefix = lastMessage.role === 'user' ? 'You: ' : 'Agent: '
  const content = lastMessage.content
    .replace(/\n/g, ' ')  // Remove line breaks
    .substring(0, 60)     // Truncate
  
  return `${prefix}${content}${content.length > 60 ? '...' : ''}`
}
```

### Time Formatting

```typescript
function getRelativeTime(timestamp: string | null): string {
  if (!timestamp) return ''
  
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
  
  // For older dates, show month/day
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric' 
  })
}
```

### Session Grouping

```typescript
function groupSessionsByTime(
  sessions: ChatSession[],
  searchQuery?: string
): GroupedSessions {
  // Filter by search
  let filtered = sessions
  if (searchQuery) {
    filtered = sessions.filter(s => 
      deriveSessionName(s).toLowerCase().includes(searchQuery.toLowerCase()) ||
      getMessagePreview(s.messages).toLowerCase().includes(searchQuery.toLowerCase())
    )
  }
  
  // Sort by updated_at (newest first)
  const sorted = filtered.sort((a, b) => 
    new Date(b.updated_at || b.created_at || 0).getTime() -
    new Date(a.updated_at || a.created_at || 0).getTime()
  )
  
  // Group by time periods
  const groups: GroupedSessions = {
    today: [],
    yesterday: [],
    thisWeek: [],
    thisMonth: [],
    older: []
  }
  
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)
  const monthAgo = new Date(today)
  monthAgo.setMonth(monthAgo.getMonth() - 1)
  
  sorted.forEach(session => {
    const date = new Date(session.updated_at || session.created_at || 0)
    
    if (date >= today) {
      groups.today.push(session)
    } else if (date >= yesterday) {
      groups.yesterday.push(session)
    } else if (date >= weekAgo) {
      groups.thisWeek.push(session)
    } else if (date >= monthAgo) {
      groups.thisMonth.push(session)
    } else {
      groups.older.push(session)
    }
  })
  
  return groups
}
```

### Token Count Formatting

```typescript
function formatTokenCount(count: number): string {
  if (count < 1000) return count.toString()
  if (count < 10000) return `${(count / 1000).toFixed(1)}k`
  return `${Math.floor(count / 1000)}k`
}
```

## Mobile Considerations

### Responsive Behavior

```css
/* Mobile optimizations */
@media (max-width: 768px) {
  /* Larger touch targets */
  .session-item {
    min-height: 56px; /* Increased from 48px */
    padding: 12px;
  }
  
  /* Bigger text for readability */
  .session-name {
    font-size: 14px; /* Up from 13px */
  }
  
  /* Hide metadata on very small screens */
  @media (max-width: 360px) {
    .session-metadata {
      display: none;
    }
  }
}
```

### Touch Interactions

```typescript
// Swipe to delete (mobile only)
const [startX, setStartX] = useState(0)
const [currentX, setCurrentX] = useState(0)
const [isSwiping, setIsSwiping] = useState(false)

const handleTouchStart = (e: TouchEvent) => {
  setStartX(e.touches[0].clientX)
}

const handleTouchMove = (e: TouchEvent) => {
  const x = e.touches[0].clientX
  setCurrentX(x)
  
  if (Math.abs(x - startX) > 10) {
    setIsSwiping(true)
  }
}

const handleTouchEnd = () => {
  if (isSwiping && currentX - startX > 100) {
    // Show delete confirmation
    showDeleteConfirmation()
  }
  
  // Reset
  setStartX(0)
  setCurrentX(0)
  setIsSwiping(false)
}
```

## Performance Optimizations

### Virtualization

```typescript
// Use react-window for large session lists
import { FixedSizeList } from 'react-window'

const VirtualizedSessionList = ({ sessions, height }) => (
  <FixedSizeList
    height={height}
    itemCount={sessions.length}
    itemSize={64} // Height of each session item
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <SessionItem session={sessions[index]} />
      </div>
    )}
  </FixedSizeList>
)
```

### Memoization

```typescript
// Memoize expensive computations
const SessionItem = React.memo(({ session, ...props }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.session.session_id === nextProps.session.session_id &&
         prevProps.isActive === nextProps.isActive &&
         prevProps.session.updated_at === nextProps.session.updated_at
})
```

## Integration with SDK

### Hook Integration

```typescript
// Custom hook for session management
const useChatSessions = () => {
  const { user } = useAuth()
  const { setMessages } = useChat()
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  
  // Load sessions from auth context or API
  useEffect(() => {
    if (user?.sessions) {
      setSessions(user.sessions)
    }
  }, [user])
  
  // Load a specific session
  const loadSession = useCallback(async (sessionId: string) => {
    const session = sessions.find(s => s.session_id === sessionId)
    if (!session) return
    
    // Update chat context with session messages
    setMessages(session.messages)
    setCurrentSessionId(sessionId)
    
    // Optionally update agent config
    // updateAgentConfig(session.agent_config)
  }, [sessions, setMessages])
  
  return {
    sessions,
    currentSessionId,
    loadSession,
    refreshSessions: () => {/* Refresh from API */}
  }
}
```

## ASCII Visual Mockup

```
┌─────────────────────────────────┐
│ 🔍 Search conversations...       │
├─────────────────────────────────┤
│ TODAY                            │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ ▸ Exploring Agent C SDK   2m │ │  <- Active session
│ │   You: How do I integrate... │ │
│ │   💬 15  # 2.3k              │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │   Voice setup questions   1h │ │
│ │   Agent: To enable voice...  │ │
│ │   💬 8   # 1.2k              │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ YESTERDAY                        │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │   Authentication flow     23h│ │
│ │   You: Can you explain the...│ │
│ │   💬 23  # 4.5k              │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ THIS WEEK                        │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │   Initial setup help      3d │ │
│ │   Agent: Welcome! Let's...   │ │
│ │   💬 42  # 8.1k              │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │   API integration test    5d │ │
│ │   You: Testing the new...    │ │
│ │   💬 5   # 0.9k              │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

## Implementation Notes

### Phase 1: Core Functionality
1. Basic session list rendering
2. Time grouping (Today, Yesterday, etc.)
3. Session name derivation
4. Active session highlighting
5. Click to load session

### Phase 2: Enhancements
1. Search functionality
2. Virtual scrolling for performance
3. Swipe actions on mobile
4. Keyboard navigation
5. Session actions (archive, delete)

### Phase 3: Advanced Features
1. Session pinning
2. Custom labels/tags
3. Export conversation
4. Bulk operations
5. Advanced filtering

## Testing Checklist

- [ ] Sessions display correctly with all fields
- [ ] Time grouping works accurately
- [ ] Active session is visually distinct
- [ ] Empty state displays when no sessions
- [ ] Loading state shows during transitions
- [ ] Search filters sessions correctly
- [ ] Mobile touch targets are adequate (44px min)
- [ ] Keyboard navigation works
- [ ] Screen reader announces session details
- [ ] Performance with 100+ sessions
- [ ] Relative timestamps update appropriately
- [ ] Token counts format correctly
- [ ] Message previews truncate properly
- [ ] Session names derive correctly from data

## Accessibility Compliance

- ARIA labels for all interactive elements
- Keyboard navigation support
- Focus management for session switching
- Screen reader announcements for state changes
- Sufficient color contrast (4.5:1 minimum)
- Clear focus indicators
- Semantic HTML structure
- Loading state announcements

## Summary

The ChatSessionList component provides a rich, accessible interface for browsing chat history. It leverages the session data from the authentication API to display organized, searchable conversation history with clear visual hierarchy and smooth interactions. The design follows CenSuite patterns while providing Claude-inspired organization and visual polish.