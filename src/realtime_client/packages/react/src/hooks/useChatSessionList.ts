/**
 * useChatSessionList - React hook for managing chat session list
 * Provides interface for loading, searching, and managing chat sessions
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import type { 
  ChatSessionIndexEntry,
  GetUserSessionsResponseEvent,
  ChatSessionChangedEvent,
  ChatSessionNameChangedEvent,
  ChatSessionAddedEvent,
  ChatSessionDeletedEvent
} from '@agentc/realtime-core';
import { useRealtimeClientSafe } from '../providers/AgentCContext';

/**
 * Simple debounce utility
 */
function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
}

/**
 * Options for the useChatSessionList hook
 */
export interface UseChatSessionListOptions {
  /** Page size for pagination (default: 50) */
  pageSize?: number;
  
  /** Whether to load sessions on mount (default: true) */
  autoLoad?: boolean;
  
  /** Debounce delay for search in ms (default: 300) */
  searchDebounceMs?: number;
  
  /** Maximum number of sessions to cache (default: 500) */
  maxCachedSessions?: number;
}

/**
 * Return type for the useChatSessionList hook
 */
export interface UseChatSessionListReturn {
  /** All loaded sessions */
  sessions: ChatSessionIndexEntry[];
  
  /** Filtered sessions based on search */
  filteredSessions: ChatSessionIndexEntry[];
  
  /** Current search query */
  searchQuery: string;
  
  /** Whether initial load is in progress */
  isLoading: boolean;
  
  /** Whether pagination load is in progress */
  isPaginationLoading: boolean;
  
  /** Error state */
  error: Error | null;
  
  /** Whether more sessions are available */
  hasMore: boolean;
  
  /** Total count of sessions on server */
  totalCount: number;
  
  /** Currently selected session ID */
  currentSessionId: string | null;
  
  /** Load more sessions (pagination) */
  loadMore: () => void;
  
  /** Select and resume a session */
  selectSession: (sessionId: string) => void;
  
  /** Delete a session with optimistic update */
  deleteSession: (sessionId: string) => Promise<void>;
  
  /** Search/filter sessions locally */
  searchSessions: (query: string) => void;
  
  /** Refresh sessions from server */
  refresh: () => void;
}

/**
 * React hook for managing chat session list
 * Provides comprehensive session management with pagination and search
 */
export function useChatSessionList(options: UseChatSessionListOptions = {}): UseChatSessionListReturn {
  const {
    pageSize = 50,
    autoLoad = true,
    searchDebounceMs = 300,
    maxCachedSessions = 500
  } = options;
  
  const client = useRealtimeClientSafe();
  
  // State
  const [sessions, setSessions] = useState<ChatSessionIndexEntry[]>([]);
  const [filteredSessions, setFilteredSessions] = useState<ChatSessionIndexEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPaginationLoading, setIsPaginationLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  // Refs for tracking state
  const offsetRef = useRef(0);
  const isLoadingRef = useRef(false);
  const deletedSessionsRef = useRef<Set<string>>(new Set());
  const rollbackDataRef = useRef<ChatSessionIndexEntry | null>(null);
  
  /**
   * Filter sessions based on search query
   */
  const filterSessions = useCallback((query: string, sessionList: ChatSessionIndexEntry[]) => {
    if (!query.trim()) {
      return sessionList;
    }
    
    const lowerQuery = query.toLowerCase();
    return sessionList.filter(session => {
      const name = (session.session_name || 'Untitled Session').toLowerCase();
      const agentName = (session.agent_name || '').toLowerCase();
      return name.includes(lowerQuery) || agentName.includes(lowerQuery);
    });
  }, []);
  
  /**
   * Load sessions from server
   */
  const loadSessions = useCallback((isInitial: boolean = false) => {
    if (!client || !client.isConnected()) {
      setError(new Error('Not connected to server'));
      return;
    }
    
    if (isLoadingRef.current) {
      return;
    }
    
    isLoadingRef.current = true;
    
    if (isInitial) {
      setIsLoading(true);
      offsetRef.current = 0;
    } else {
      setIsPaginationLoading(true);
    }
    
    setError(null);
    
    // Request sessions from server using sendEvent
    client.sendEvent({
      type: 'get_user_sessions',
      offset: offsetRef.current,
      limit: pageSize
    });
  }, [client, pageSize]);
  
  /**
   * Load more sessions (pagination)
   */
  const loadMore = useCallback(() => {
    if (!hasMore || isLoadingRef.current) {
      return;
    }
    
    loadSessions(false);
  }, [hasMore, loadSessions]);
  
  /**
   * Select and resume a session
   */
  const selectSession = useCallback((sessionId: string) => {
    if (!client || !client.isConnected()) {
      setError(new Error('Not connected to server'));
      return;
    }
    
    setError(null);
    
    try {
      client.resumeChatSession(sessionId);
      setCurrentSessionId(sessionId);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to select session');
      setError(error);
      console.error('Failed to select session:', err);
    }
  }, [client]);
  
  /**
   * Delete a session with optimistic update
   */
  const deleteSession = useCallback(async (sessionId: string): Promise<void> => {
    if (!client || !client.isConnected()) {
      throw new Error('Not connected to server');
    }
    
    // Find the session for potential rollback
    const sessionToDelete = sessions.find(s => s.session_id === sessionId);
    if (!sessionToDelete) {
      throw new Error('Session not found');
    }
    
    // Optimistic update - remove from UI immediately
    rollbackDataRef.current = sessionToDelete;
    setSessions(prev => prev.filter(s => s.session_id !== sessionId));
    setFilteredSessions(prev => prev.filter(s => s.session_id !== sessionId));
    setTotalCount(prev => Math.max(0, prev - 1));
    
    // Mark as deleted to prevent re-adding from events
    deletedSessionsRef.current.add(sessionId);
    
    try {
      // Send delete event to server
      client.sendEvent({
        type: 'delete_chat_session',
        session_id: sessionId
      });
      
      // Clear current session if it was deleted
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
      }
    } catch (err) {
      // Rollback on error
      if (rollbackDataRef.current) {
        setSessions(prev => {
          const newSessions = [...prev, rollbackDataRef.current!];
          // Sort by updated_at descending
          return newSessions.sort((a, b) => {
            const dateA = new Date(a.updated_at || 0).getTime();
            const dateB = new Date(b.updated_at || 0).getTime();
            return dateB - dateA;
          });
        });
        
        // Re-apply filter
        setFilteredSessions(prev => {
          const newSessions = [...prev, rollbackDataRef.current!];
          return filterSessions(searchQuery, newSessions);
        });
        
        setTotalCount(prev => prev + 1);
        deletedSessionsRef.current.delete(sessionId);
      }
      
      const error = err instanceof Error ? err : new Error('Failed to delete session');
      setError(error);
      throw error;
    } finally {
      rollbackDataRef.current = null;
    }
  }, [client, sessions, currentSessionId, searchQuery, filterSessions]);
  
  /**
   * Search sessions with debouncing
   */
  const debouncedSearch = useRef(
    debounce((query: string) => {
      const filtered = filterSessions(query, sessions);
      setFilteredSessions(filtered);
    }, searchDebounceMs)
  ).current;
  
  const searchSessions = useCallback((query: string) => {
    setSearchQuery(query);
    debouncedSearch(query);
  }, [debouncedSearch]);
  
  /**
   * Refresh sessions from server
   */
  const refresh = useCallback(() => {
    setSessions([]);
    setFilteredSessions([]);
    offsetRef.current = 0;
    deletedSessionsRef.current.clear();
    setHasMore(true);
    loadSessions(true);
  }, [loadSessions]);
  
  // Handle server events
  useEffect(() => {
    if (!client) return;
    
    // Handle get_user_sessions_response
    const handleSessionsResponse = (event: GetUserSessionsResponseEvent) => {
      if (!event.sessions) return;
      
      const response = event.sessions;
      const newSessions = response.chat_sessions.filter(
        session => !deletedSessionsRef.current.has(session.session_id)
      );
      
      if (offsetRef.current === 0) {
        // Initial load - replace all sessions
        setSessions(newSessions);
        setFilteredSessions(filterSessions(searchQuery, newSessions));
      } else {
        // Pagination - append new sessions
        setSessions(prev => {
          const combined = [...prev, ...newSessions];
          // Limit cache size
          if (combined.length > maxCachedSessions) {
            return combined.slice(0, maxCachedSessions);
          }
          return combined;
        });
        
        setFilteredSessions(prev => {
          const combined = [...prev, ...filterSessions(searchQuery, newSessions)];
          if (combined.length > maxCachedSessions) {
            return combined.slice(0, maxCachedSessions);
          }
          return combined;
        });
      }
      
      setTotalCount(response.total_sessions);
      offsetRef.current += newSessions.length;
      setHasMore(offsetRef.current < response.total_sessions);
      
      isLoadingRef.current = false;
      setIsLoading(false);
      setIsPaginationLoading(false);
      setError(null);
    };
    
    // Handle chat_session_changed
    const handleSessionChanged = (event: ChatSessionChangedEvent) => {
      if (event.chat_session) {
        setCurrentSessionId(event.chat_session.session_id);
      }
    };
    
    // Handle chat_session_name_changed
    const handleSessionNameChanged = (event: ChatSessionNameChangedEvent) => {
      if (!event.session_name) return;
      
      // Update session name in our list
      setSessions(prev => prev.map(session => {
        if (session.session_id === currentSessionId) {
          return { ...session, session_name: event.session_name };
        }
        return session;
      }));
      
      // Update filtered list too
      setFilteredSessions(prev => prev.map(session => {
        if (session.session_id === currentSessionId) {
          return { ...session, session_name: event.session_name };
        }
        return session;
      }));
    };
    
    // Handle chat_session_added
    const handleSessionAdded = (event: ChatSessionAddedEvent) => {
      if (!event.chat_session) return;
      
      const newSession = event.chat_session;
      
      // Don't add if it was recently deleted
      if (deletedSessionsRef.current.has(newSession.session_id)) {
        return;
      }
      
      // Add to beginning of list (newest first)
      setSessions(prev => {
        const exists = prev.some(s => s.session_id === newSession.session_id);
        if (exists) return prev;
        
        const updated = [newSession, ...prev];
        // Limit cache size
        if (updated.length > maxCachedSessions) {
          return updated.slice(0, maxCachedSessions);
        }
        return updated;
      });
      
      // Update filtered list if it matches search
      if (filterSessions(searchQuery, [newSession]).length > 0) {
        setFilteredSessions(prev => {
          const exists = prev.some(s => s.session_id === newSession.session_id);
          if (exists) return prev;
          
          const updated = [newSession, ...prev];
          if (updated.length > maxCachedSessions) {
            return updated.slice(0, maxCachedSessions);
          }
          return updated;
        });
      }
      
      setTotalCount(prev => prev + 1);
    };
    
    // Handle chat_session_deleted
    const handleSessionDeleted = (event: ChatSessionDeletedEvent) => {
      const sessionId = event.session_id || currentSessionId;
      if (!sessionId) return;
      
      // Remove from our lists
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      setFilteredSessions(prev => prev.filter(s => s.session_id !== sessionId));
      setTotalCount(prev => Math.max(0, prev - 1));
      
      // Mark as deleted
      deletedSessionsRef.current.add(sessionId);
      
      // Clear current session if it was deleted
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
      }
    };
    
    // Handle connection events
    const handleConnected = () => {
      // Load sessions when connected if autoLoad is enabled
      if (autoLoad && sessions.length === 0) {
        loadSessions(true);
      }
    };
    
    const handleDisconnected = () => {
      isLoadingRef.current = false;
      setIsLoading(false);
      setIsPaginationLoading(false);
    };
    
    // Handle errors
    const handleError = (error: unknown) => {
      isLoadingRef.current = false;
      setIsLoading(false);
      setIsPaginationLoading(false);
      
      const err = error instanceof Error ? error : new Error(
        (error as { message?: string })?.message || 'Unknown error'
      );
      setError(err);
    };
    
    // Subscribe to events
    client.on('get_user_sessions_response', handleSessionsResponse);
    client.on('chat_session_changed', handleSessionChanged);
    client.on('chat_session_name_changed', handleSessionNameChanged);
    client.on('chat_session_added', handleSessionAdded);
    client.on('chat_session_deleted', handleSessionDeleted);
    client.on('connected', handleConnected);
    client.on('disconnected', handleDisconnected);
    client.on('error', handleError);
    
    // Cleanup
    return () => {
      client.off('get_user_sessions_response', handleSessionsResponse);
      client.off('chat_session_changed', handleSessionChanged);
      client.off('chat_session_name_changed', handleSessionNameChanged);
      client.off('chat_session_added', handleSessionAdded);
      client.off('chat_session_deleted', handleSessionDeleted);
      client.off('connected', handleConnected);
      client.off('disconnected', handleDisconnected);
      client.off('error', handleError);
    };
  }, [client, autoLoad, searchQuery, currentSessionId, filterSessions, maxCachedSessions, loadSessions]);
  
  // Initial load on mount if autoLoad is enabled
  useEffect(() => {
    if (autoLoad && client && client.isConnected() && sessions.length === 0) {
      loadSessions(true);
    }
  }, [autoLoad, client, sessions.length, loadSessions]);
  
  // Update current session from SessionManager
  useEffect(() => {
    if (!client) return;
    
    const sessionManager = client.getSessionManager();
    if (sessionManager) {
      const currentSession = sessionManager.getCurrentSession();
      if (currentSession) {
        setCurrentSessionId(currentSession.session_id);
      }
    }
  }, [client]);
  
  return {
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
  };
}