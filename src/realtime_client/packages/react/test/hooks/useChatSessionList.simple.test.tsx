/**
 * Simple compilation and export test for useChatSessionList hook
 */

import { describe, it, expect } from 'vitest';
import { useChatSessionList } from '../../src/hooks/useChatSessionList';
import type { UseChatSessionListOptions, UseChatSessionListReturn } from '../../src/hooks/useChatSessionList';

describe('useChatSessionList compilation', () => {
  it('should be exported as a function', () => {
    expect(typeof useChatSessionList).toBe('function');
  });
  
  it('should have proper TypeScript types', () => {
    // This test just verifies that the types compile correctly
    const options: UseChatSessionListOptions = {
      pageSize: 50,
      autoLoad: true,
      searchDebounceMs: 300,
      maxCachedSessions: 500
    };
    
    // Type checks
    const _typeCheck: UseChatSessionListReturn = {
      sessions: [],
      filteredSessions: [],
      searchQuery: '',
      isLoading: false,
      isPaginationLoading: false,
      error: null,
      hasMore: true,
      totalCount: 0,
      currentSessionId: null,
      loadMore: () => {},
      selectSession: (sessionId: string) => {},
      deleteSession: async (sessionId: string) => {},
      searchSessions: (query: string) => {},
      refresh: () => {}
    };
    
    expect(options).toBeDefined();
  });
});