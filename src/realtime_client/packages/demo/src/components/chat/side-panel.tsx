'use client';

import React from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  Search, 
  MessageSquare,
  Clock,
  MoreVertical,
  Trash2
} from 'lucide-react';
import {
  Button,
  Input,
  ScrollArea,
  Separator,
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@agentc/realtime-ui';
import { cn } from '@/lib/utils';

export interface Session {
  id: string;
  title: string;
  timestamp: Date;
  preview?: string;
  messageCount?: number;
}

export interface SidePanelProps {
  isOpen: boolean;
  onToggle: () => void;
  isMobile?: boolean;
  sessions?: Session[];
  activeSessionId?: string;
  onNewSession?: () => void;
  onSelectSession?: (sessionId: string) => void;
  onDeleteSession?: (sessionId: string) => void;
  className?: string;
}

/**
 * Collapsible side panel for session management
 * Adapts to mobile (overlay) and desktop (sidebar) layouts
 */
export function SidePanel({
  isOpen,
  onToggle,
  isMobile = false,
  sessions = [],
  activeSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  className
}: SidePanelProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  
  // Filter sessions based on search
  const filteredSessions = React.useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    
    const query = searchQuery.toLowerCase();
    return sessions.filter(session => 
      session.title.toLowerCase().includes(query) ||
      session.preview?.toLowerCase().includes(query)
    );
  }, [sessions, searchQuery]);

  // Generate placeholder sessions for demo
  const demoSessions: Session[] = React.useMemo(() => {
    if (sessions.length > 0) return sessions;
    
    // Return placeholder sessions
    return [
      {
        id: '1',
        title: 'Getting Started with SDK',
        timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
        preview: 'How do I initialize the Agent C SDK?',
        messageCount: 12
      },
      {
        id: '2',
        title: 'Voice Configuration',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        preview: 'Setting up voice models and avatar...',
        messageCount: 8
      },
      {
        id: '3',
        title: 'WebSocket Connection Issues',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
        preview: 'Debugging connection problems',
        messageCount: 24
      }
    ];
  }, [sessions]);

  const displaySessions = sessions.length > 0 ? filteredSessions : demoSessions;

  // Format timestamp for display
  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  // Panel content component (shared between mobile and desktop)
  const PanelContent = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Sessions</h2>
          {!isMobile && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              aria-label="Toggle sidebar"
              className="h-8 w-8"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* New Session Button */}
        <Button 
          onClick={onNewSession}
          className="w-full justify-start gap-2"
          variant="outline"
        >
          <Plus className="h-4 w-4" />
          New Session
        </Button>

        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Separator />

      {/* Sessions List */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {displaySessions.length > 0 ? (
            <div className="space-y-1">
              {displaySessions.map((session) => (
                <SessionItem
                  key={session.id}
                  session={session}
                  isActive={session.id === activeSessionId}
                  onSelect={() => onSelectSession?.(session.id)}
                  onDelete={() => onDeleteSession?.(session.id)}
                  formatTimestamp={formatTimestamp}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="text-sm">No sessions found</p>
              {searchQuery && (
                <p className="text-xs mt-1">Try a different search term</p>
              )}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer Info */}
      <Separator />
      <div className="flex-shrink-0 p-4">
        <p className="text-xs text-muted-foreground text-center">
          {displaySessions.length} {displaySessions.length === 1 ? 'session' : 'sessions'}
        </p>
      </div>
    </div>
  );

  // Mobile: Render as overlay sheet
  if (isMobile) {
    return (
      <>
        {/* Mobile toggle button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="fixed left-4 top-20 z-40 md:hidden"
          aria-label="Open session menu"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        {/* Mobile overlay */}
        <Sheet open={isOpen} onOpenChange={onToggle}>
          <SheetContent side="left" className="w-80 p-0">
            <PanelContent />
          </SheetContent>
        </Sheet>
      </>
    );
  }

  // Desktop: Render as sidebar
  return (
    <>
      {/* Collapsed state - just show toggle button */}
      {!isOpen && (
        <div className="flex-shrink-0 border-r bg-background p-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            aria-label="Open sidebar"
            className="h-8 w-8"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Expanded sidebar */}
      {isOpen && (
        <aside className={cn(
          'flex-shrink-0 w-80 border-r bg-background',
          className
        )}>
          <PanelContent />
        </aside>
      )}
    </>
  );
}

/**
 * Individual session item component
 */
function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
  formatTimestamp
}: {
  session: Session;
  isActive?: boolean;
  onSelect?: () => void;
  onDelete?: () => void;
  formatTimestamp: (date: Date) => string;
}) {
  return (
    <div
      className={cn(
        'group relative flex items-start gap-3 rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors',
        isActive ? 'bg-secondary' : 'hover:bg-secondary/50'
      )}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect?.();
        }
      }}
    >
      {/* Icon */}
      <MessageSquare className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
      
      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-medium truncate">{session.title}</h3>
          
          {/* Actions dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical className="h-3 w-3" />
                <span className="sr-only">Session options</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={(e) => {
                e.stopPropagation();
                onSelect?.();
              }}>
                Open
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.();
                }}
                className="text-destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        {session.preview && (
          <p className="text-xs text-muted-foreground truncate mt-1">
            {session.preview}
          </p>
        )}
        
        <div className="flex items-center gap-3 mt-1">
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {formatTimestamp(session.timestamp)}
          </span>
          {session.messageCount !== undefined && (
            <span className="text-xs text-muted-foreground">
              {session.messageCount} messages
            </span>
          )}
        </div>
      </div>
    </div>
  );
}