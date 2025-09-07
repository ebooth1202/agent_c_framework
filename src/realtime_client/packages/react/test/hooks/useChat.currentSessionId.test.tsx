/**
 * Test for useChat hook currentSessionId functionality
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChat } from '../../src/hooks/useChat';
import { AgentCProvider } from '../../src/providers/AgentCProvider';
import { RealtimeClient, ConnectionState } from '@agentc/realtime-core';
import type { ChatSession } from '@agentc/realtime-core';
import React from 'react';

// Mock client for testing
const createMockClient = () => {
  const listeners = new Map<string, Set<Function>>();
  
  const mockSession: ChatSession = {
    session_id: 'test-session-123',
    session_name: 'Test Session',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    user_id: 'user-1',
    messages: [],
    meta: {},
    agent_config: {
      key: 'test-agent',
      name: 'Test Agent',
      description: 'Test agent description',
      avatar_id: null,
      voice_id: 'nova',
      tools: []
    }
  };
  
  const mockClient = {
    isConnected: vi.fn(() => true),
    getConnectionState: vi.fn(() => ConnectionState.CONNECTED),
    connect: vi.fn(),
    disconnect: vi.fn(),
    sendText: vi.fn(),
    getSessionManager: vi.fn(() => ({
      getCurrentSession: vi.fn(() => mockSession)
    })),
    on: vi.fn((event: string, handler: Function) => {
      if (!listeners.has(event)) {
        listeners.set(event, new Set());
      }
      listeners.get(event)!.add(handler);
    }),
    off: vi.fn((event: string, handler: Function) => {
      listeners.get(event)?.delete(handler);
    }),
    emit: (event: string, data: any) => {
      listeners.get(event)?.forEach(handler => handler(data));
    },
    destroy: vi.fn()
  };
  
  return { mockClient, mockSession, listeners };
};

describe('useChat - currentSessionId', () => {
  let mockClientData: ReturnType<typeof createMockClient>;
  
  beforeEach(() => {
    mockClientData = createMockClient();
  });
  
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AgentCProvider 
      client={mockClientData.mockClient as any}
      apiUrl="https://test.example.com"
      authToken="test-token"
    >
      {children}
    </AgentCProvider>
  );
  
  it('should expose currentSessionId from the current session', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Should get session ID from SessionManager
    expect(result.current.currentSessionId).toBe('test-session-123');
    expect(result.current.currentSession).toBeDefined();
    expect(result.current.currentSession?.session_id).toBe('test-session-123');
  });
  
  it('should return null when no session is active', () => {
    // Create a client with no session
    const noSessionClient = createMockClient();
    noSessionClient.mockClient.getSessionManager = vi.fn(() => ({
      getCurrentSession: vi.fn(() => null)
    }));
    
    const customWrapper = ({ children }: { children: React.ReactNode }) => (
      <AgentCProvider 
        client={noSessionClient.mockClient as any}
        apiUrl="https://test.example.com"
        authToken="test-token"
      >
        {children}
      </AgentCProvider>
    );
    
    const { result } = renderHook(() => useChat(), { wrapper: customWrapper });
    
    expect(result.current.currentSessionId).toBeNull();
    expect(result.current.currentSession).toBeNull();
  });
  
  it('should update currentSessionId when session changes', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Initial session ID
    expect(result.current.currentSessionId).toBe('test-session-123');
    
    // Emit session change event
    const newSession: ChatSession = {
      session_id: 'new-session-456',
      session_name: 'New Session',
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
      user_id: 'user-1',
      messages: [],
      meta: {},
      agent_config: {
        key: 'test-agent',
        name: 'Test Agent',
        description: 'Test agent description',
        avatar_id: null,
        voice_id: 'nova',
        tools: []
      }
    };
    
    act(() => {
      mockClientData.mockClient.emit('chat_session_changed', {
        chat_session: newSession
      });
    });
    
    // Should update to new session ID
    expect(result.current.currentSessionId).toBe('new-session-456');
    expect(result.current.currentSession?.session_id).toBe('new-session-456');
  });
  
  it('should be consistent between currentSession and currentSessionId', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Both should reference the same session
    expect(result.current.currentSessionId).toBe(result.current.currentSession?.session_id);
    
    // Update to a new session
    const updatedSession: ChatSession = {
      session_id: 'updated-session-789',
      session_name: 'Updated Session',
      created_at: '2024-01-03T00:00:00Z',
      updated_at: '2024-01-03T00:00:00Z',
      user_id: 'user-1',
      messages: [],
      meta: {},
      agent_config: {
        key: 'test-agent',
        name: 'Test Agent',
        description: 'Test agent description',
        avatar_id: null,
        voice_id: 'nova',
        tools: []
      }
    };
    
    act(() => {
      mockClientData.mockClient.emit('chat_session_changed', {
        chat_session: updatedSession
      });
    });
    
    // Should still be consistent
    expect(result.current.currentSessionId).toBe('updated-session-789');
    expect(result.current.currentSessionId).toBe(result.current.currentSession?.session_id);
  });
  
  it('should maintain type safety', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // TypeScript should recognize currentSessionId as string | null
    const sessionId: string | null = result.current.currentSessionId;
    
    // Should be able to use in conditionals
    if (result.current.currentSessionId) {
      const id: string = result.current.currentSessionId;
      expect(id).toBe('test-session-123');
    }
    
    expect(sessionId).toBe('test-session-123');
  });
});