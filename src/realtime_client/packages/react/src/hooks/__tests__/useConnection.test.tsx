/**
 * Tests for useConnection hook
 * Tests connection management, state transitions, and event handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useConnection } from '../useConnection';
import { ConnectionState } from '@agentc/realtime-core';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';

describe('useConnection', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockClient = {
      ...createMockClient(),
      isConnected: vi.fn(() => false),
      getConnectionState: vi.fn(() => ConnectionState.DISCONNECTED),
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      }),
      emit: vi.fn((event: string, ...args: any[]) => {
        eventHandlers.get(event)?.forEach(handler => handler(...args));
      })
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns disconnected state initially', () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
      expect(result.current.isConnected).toBe(false);
      expect(result.current.isConnecting).toBe(false);
      expect(result.current.isDisconnected).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('initializes with correct statistics', () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.stats).toEqual({
        connectionAttempts: 0,
        successfulConnections: 0,
        failedConnections: 0,
        lastConnectedAt: null,
        lastDisconnectedAt: null,
        sessionDuration: 0
      });
    });

    it('provides configuration values', () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.autoReconnectEnabled).toBe(true);
      expect(result.current.maxReconnectAttempts).toBe(5);
      expect(result.current.reconnectAttempt).toBe(0);
    });
  });

  describe('Connection Management', () => {
    it('connects successfully when connect is called', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.connect();
      });

      expect(mockClient.connect).toHaveBeenCalledTimes(1);
      expect(result.current.stats.connectionAttempts).toBe(1);
      expect(result.current.stats.successfulConnections).toBe(1);
      expect(result.current.error).toBeNull();
    });

    it('handles connection when already connected', async () => {
      mockClient.isConnected.mockReturnValue(true);
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.connect();
      });

      expect(consoleWarnSpy).toHaveBeenCalledWith('Already connected');
      expect(mockClient.connect).not.toHaveBeenCalled();

      consoleWarnSpy.mockRestore();
    });

    it('handles connection failure', async () => {
      const error = new Error('Connection failed');
      mockClient.connect.mockRejectedValue(error);

      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.connect()).rejects.toThrow('Connection failed');
      });

      expect(result.current.error).toEqual(error);
      expect(result.current.stats.failedConnections).toBe(1);
      expect(result.current.stats.connectionAttempts).toBe(1);
      expect(result.current.stats.successfulConnections).toBe(0);
    });

    it('disconnects successfully', () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        result.current.disconnect();
      });

      expect(mockClient.disconnect).toHaveBeenCalledTimes(1);
      expect(result.current.stats.lastDisconnectedAt).toBeInstanceOf(Date);
    });

    it('handles disconnect when client not available', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={null}>{children}</TestWrapper>
        )
      });

      act(() => {
        result.current.disconnect();
      });

      expect(consoleWarnSpy).toHaveBeenCalledWith('Client not available');
      consoleWarnSpy.mockRestore();
    });

    it('reconnects successfully', async () => {
      mockClient.isConnected.mockReturnValueOnce(true).mockReturnValueOnce(false);

      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.reconnect();
      });

      expect(mockClient.disconnect).toHaveBeenCalledTimes(1);
      expect(mockClient.connect).toHaveBeenCalledTimes(1);
    });
  });

  describe('Event Handling', () => {
    it('handles connected event', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        // Simulate connected event
        eventHandlers.get('connected')?.forEach(handler => handler());
      });

      await waitFor(() => {
        expect(result.current.connectionState).toBe(ConnectionState.CONNECTED);
        expect(result.current.error).toBeNull();
        expect(result.current.stats.lastConnectedAt).toBeInstanceOf(Date);
      });
    });

    it('handles disconnected event with normal closure', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        // Simulate disconnected event with normal closure
        eventHandlers.get('disconnected')?.forEach(handler => 
          handler({ code: 1000, reason: 'Normal closure' })
        );
      });

      await waitFor(() => {
        expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
        expect(result.current.error).toBeNull();
        expect(result.current.stats.lastDisconnectedAt).toBeInstanceOf(Date);
      });
    });

    it('handles disconnected event with error', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        // Simulate disconnected event with error
        eventHandlers.get('disconnected')?.forEach(handler => 
          handler({ code: 1006, reason: 'Connection lost' })
        );
      });

      await waitFor(() => {
        expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
        expect(result.current.error).toBeInstanceOf(Error);
        expect(result.current.error?.message).toContain('Disconnected: Connection lost');
      });
    });

    it('handles reconnecting event', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        // Simulate reconnecting event
        eventHandlers.get('reconnecting')?.forEach(handler => 
          handler({ attempt: 3 })
        );
      });

      await waitFor(() => {
        expect(result.current.connectionState).toBe(ConnectionState.RECONNECTING);
        expect(result.current.reconnectAttempt).toBe(3);
      });
    });

    it('handles error event', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const error = new Error('WebSocket error');

      act(() => {
        // Simulate error event
        eventHandlers.get('error')?.forEach(handler => handler(error));
      });

      await waitFor(() => {
        expect(result.current.error).toEqual(error);
        expect(result.current.stats.failedConnections).toBe(1);
      });
    });

    it('handles error event with non-Error object', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        // Simulate error event with custom error object
        eventHandlers.get('error')?.forEach(handler => 
          handler({ message: 'Custom error' })
        );
      });

      await waitFor(() => {
        expect(result.current.error).toBeInstanceOf(Error);
        expect(result.current.error?.message).toBe('Custom error');
      });
    });
  });

  describe('Session Duration Tracking', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('tracks session duration when connected', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Connect and trigger connected event
      act(() => {
        eventHandlers.get('connected')?.forEach(handler => handler());
      });

      // Advance time by 5 seconds
      act(() => {
        vi.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(result.current.stats.sessionDuration).toBeGreaterThanOrEqual(5000);
      });
    });

    it('stops tracking session duration when disconnected', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Connect
      act(() => {
        eventHandlers.get('connected')?.forEach(handler => handler());
      });

      // Advance time
      act(() => {
        vi.advanceTimersByTime(3000);
      });

      // Disconnect
      act(() => {
        eventHandlers.get('disconnected')?.forEach(handler => 
          handler({ code: 1000, reason: 'Normal' })
        );
      });

      const durationAtDisconnect = result.current.stats.sessionDuration;

      // Advance time after disconnect
      act(() => {
        vi.advanceTimersByTime(2000);
      });

      // Duration should not change after disconnect
      expect(result.current.stats.sessionDuration).toBe(durationAtDisconnect);
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Verify listeners are added
      expect(mockClient.on).toHaveBeenCalledWith('connected', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('disconnected', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('reconnecting', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('error', expect.any(Function));

      unmount();

      // Verify listeners are removed
      expect(mockClient.off).toHaveBeenCalledWith('connected', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('disconnected', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('reconnecting', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('error', expect.any(Function));
    });

    it('clears interval on unmount', () => {
      const clearIntervalSpy = vi.spyOn(global, 'clearInterval');

      const { unmount } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start a session to trigger interval
      act(() => {
        eventHandlers.get('connected')?.forEach(handler => handler());
      });

      unmount();

      expect(clearIntervalSpy).toHaveBeenCalled();
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result, unmount } = renderHook(() => useConnection(), {
        wrapper: StrictModeWrapper
      });

      // Should handle multiple effect runs without issues
      expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
      
      // Connect should work correctly
      await act(async () => {
        await result.current.connect();
      });

      expect(mockClient.connect).toHaveBeenCalledTimes(1);
      
      unmount();
      
      // Cleanup should be handled properly
      expect(mockClient.off).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('handles missing client gracefully', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={null}>{children}</TestWrapper>
        )
      });

      expect(result.current.connectionState).toBe(ConnectionState.DISCONNECTED);
      
      await act(async () => {
        await expect(result.current.connect()).rejects.toThrow('Client not available');
      });
    });

    it('handles rapid connect/disconnect calls', async () => {
      const { result } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        // Rapid calls
        const connectPromise = result.current.connect();
        result.current.disconnect();
        await connectPromise;
      });

      expect(mockClient.connect).toHaveBeenCalledTimes(1);
      expect(mockClient.disconnect).toHaveBeenCalledTimes(1);
    });

    it('handles state updates after unmount', async () => {
      const { result, unmount } = renderHook(() => useConnection(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start a connection
      const connectPromise = act(async () => {
        await result.current.connect();
      });

      // Unmount immediately
      unmount();

      // Complete the connection (should not cause errors)
      await connectPromise;

      // No errors should be thrown
      expect(true).toBe(true);
    });
  });
});