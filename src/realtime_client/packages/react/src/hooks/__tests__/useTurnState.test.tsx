/**
 * Tests for useTurnState hook
 * Tests conversation flow management and turn tracking
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTurnState } from '../useTurnState';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';
import type { TurnType, TurnState } from '@agentc/realtime-core';

describe('useTurnState', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;
  let mockTurnManager: any;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockTurnManager = {
      getTurnState: vi.fn(() => ({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      })),
      startTurn: vi.fn(),
      endTurn: vi.fn(),
      cancelTurn: vi.fn(),
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
    
    mockClient = {
      ...createMockClient(),
      getTurnManager: vi.fn(() => mockTurnManager),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      })
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns initial turn state', () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.currentTurn).toBeNull();
      expect(result.current.isUserTurn).toBe(false);
      expect(result.current.isAssistantTurn).toBe(false);
      expect(result.current.canSendInput).toBe(true);
      expect(result.current.turnHistory).toEqual([]);
      expect(result.current.pendingTurns).toEqual([]);
    });

    it('provides turn control methods', () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(typeof result.current.startUserTurn).toBe('function');
      expect(typeof result.current.endCurrentTurn).toBe('function');
      expect(typeof result.current.cancelCurrentTurn).toBe('function');
    });

    it('provides turn statistics', () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.stats).toEqual({
        totalTurns: 0,
        userTurns: 0,
        assistantTurns: 0,
        averageTurnDuration: 0,
        currentTurnDuration: 0
      });
    });
  });

  describe('Turn Start Events', () => {
    it('handles user turn start', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turnData = {
        id: 'turn-001',
        type: 'user' as TurnType,
        startTime: new Date().toISOString(),
        metadata: {}
      };

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: turnData,
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
      });

      await waitFor(() => {
        expect(result.current.currentTurn).toEqual(turnData);
        expect(result.current.isUserTurn).toBe(true);
        expect(result.current.isAssistantTurn).toBe(false);
      });
    });

    it('handles assistant turn start', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turnData = {
        id: 'turn-002',
        type: 'assistant' as TurnType,
        startTime: new Date().toISOString(),
        metadata: { model: 'gpt-4' }
      };

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: turnData,
        isUserTurn: false,
        isAssistantTurn: true,
        canSendInput: false,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
      });

      await waitFor(() => {
        expect(result.current.currentTurn).toEqual(turnData);
        expect(result.current.isUserTurn).toBe(false);
        expect(result.current.isAssistantTurn).toBe(true);
        expect(result.current.canSendInput).toBe(false);
      });
    });
  });

  describe('Turn End Events', () => {
    it('handles turn end and updates history', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turnData = {
        id: 'turn-003',
        type: 'user' as TurnType,
        startTime: '2024-01-01T10:00:00Z',
        endTime: '2024-01-01T10:00:05Z',
        duration: 5000,
        metadata: {}
      };

      // Start turn first
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: turnData,
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
      });

      // End turn
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: [turnData]
      });

      act(() => {
        eventHandlers.get('turn-ended')?.forEach(handler => handler(turnData));
      });

      await waitFor(() => {
        expect(result.current.currentTurn).toBeNull();
        expect(result.current.isUserTurn).toBe(false);
        expect(result.current.turnHistory).toHaveLength(1);
        expect(result.current.turnHistory[0]).toEqual(turnData);
      });
    });

    it('updates turn statistics on turn end', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turns = [
        { id: '1', type: 'user' as TurnType, duration: 3000 },
        { id: '2', type: 'assistant' as TurnType, duration: 5000 },
        { id: '3', type: 'user' as TurnType, duration: 2000 }
      ];

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: turns
      });

      act(() => {
        turns.forEach(turn => {
          eventHandlers.get('turn-ended')?.forEach(handler => handler(turn));
        });
      });

      await waitFor(() => {
        expect(result.current.stats.totalTurns).toBe(3);
        expect(result.current.stats.userTurns).toBe(2);
        expect(result.current.stats.assistantTurns).toBe(1);
        expect(result.current.stats.averageTurnDuration).toBeCloseTo(3333.33, 1);
      });
    });
  });

  describe('Turn Control Methods', () => {
    it('starts user turn', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startUserTurn();
      });

      expect(mockTurnManager.startTurn).toHaveBeenCalledWith('user');
    });

    it('starts user turn with metadata', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const metadata = { source: 'voice', confidence: 0.95 };

      await act(async () => {
        await result.current.startUserTurn(metadata);
      });

      expect(mockTurnManager.startTurn).toHaveBeenCalledWith('user', metadata);
    });

    it('ends current turn', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Set up a current turn
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: { id: 'turn-123', type: 'user' },
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      await act(async () => {
        await result.current.endCurrentTurn();
      });

      expect(mockTurnManager.endTurn).toHaveBeenCalledWith('turn-123');
    });

    it('handles end turn when no current turn', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      await act(async () => {
        await result.current.endCurrentTurn();
      });

      expect(consoleWarnSpy).toHaveBeenCalledWith('No current turn to end');
      expect(mockTurnManager.endTurn).not.toHaveBeenCalled();

      consoleWarnSpy.mockRestore();
    });

    it('cancels current turn', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: { id: 'turn-456', type: 'assistant' },
        isUserTurn: false,
        isAssistantTurn: true,
        canSendInput: false,
        pendingTurns: [],
        turnHistory: []
      });

      await act(async () => {
        await result.current.cancelCurrentTurn();
      });

      expect(mockTurnManager.cancelTurn).toHaveBeenCalledWith('turn-456');
    });
  });

  describe('Turn State Changes', () => {
    it('handles turn state change event', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const newState = {
        currentTurn: { id: 'turn-789', type: 'user' as TurnType },
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      };

      mockTurnManager.getTurnState.mockReturnValue(newState);

      act(() => {
        eventHandlers.get('turn-state-changed')?.forEach(handler => handler(newState));
      });

      await waitFor(() => {
        expect(result.current.currentTurn).toEqual(newState.currentTurn);
        expect(result.current.canSendInput).toBe(true);
      });
    });

    it('handles input permission changes', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Initially can send input
      expect(result.current.canSendInput).toBe(true);

      // Change to assistant turn - cannot send input
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: { id: 'turn-assistant', type: 'assistant' },
        isUserTurn: false,
        isAssistantTurn: true,
        canSendInput: false,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-state-changed')?.forEach(handler => 
          handler({ canSendInput: false })
        );
      });

      await waitFor(() => {
        expect(result.current.canSendInput).toBe(false);
      });
    });
  });

  describe('Pending Turns', () => {
    it('tracks pending turns', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const pendingTurns = [
        { id: 'pending-1', type: 'user' as TurnType, queued: true },
        { id: 'pending-2', type: 'assistant' as TurnType, queued: true }
      ];

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns,
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-queued')?.forEach(handler => 
          handler({ pendingTurns })
        );
      });

      await waitFor(() => {
        expect(result.current.pendingTurns).toEqual(pendingTurns);
      });
    });

    it('clears pending turns when processed', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Set pending turns
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [{ id: 'pending-1', type: 'user' }],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-queued')?.forEach(handler => 
          handler({ pendingTurns: [{ id: 'pending-1', type: 'user' }] })
        );
      });

      expect(result.current.pendingTurns).toHaveLength(1);

      // Clear pending turns
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: { id: 'pending-1', type: 'user' },
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => 
          handler({ id: 'pending-1', type: 'user' })
        );
      });

      await waitFor(() => {
        expect(result.current.pendingTurns).toHaveLength(0);
      });
    });
  });

  describe('Turn Duration Tracking', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('tracks current turn duration', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turnData = {
        id: 'turn-duration',
        type: 'user' as TurnType,
        startTime: new Date().toISOString()
      };

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: turnData,
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
      });

      // Advance time by 3 seconds
      act(() => {
        vi.advanceTimersByTime(3000);
      });

      await waitFor(() => {
        expect(result.current.stats.currentTurnDuration).toBeGreaterThanOrEqual(3);
      });
    });

    it('resets duration when turn ends', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start a turn
      const turnData = {
        id: 'turn-reset',
        type: 'user' as TurnType,
        startTime: new Date().toISOString()
      };

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: turnData,
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
      });

      act(() => {
        eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
      });

      // Advance time
      act(() => {
        vi.advanceTimersByTime(2000);
      });

      expect(result.current.stats.currentTurnDuration).toBeGreaterThan(0);

      // End turn
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: [{ ...turnData, endTime: new Date().toISOString(), duration: 2000 }]
      });

      act(() => {
        eventHandlers.get('turn-ended')?.forEach(handler => handler(turnData));
      });

      await waitFor(() => {
        expect(result.current.stats.currentTurnDuration).toBe(0);
      });
    });
  });

  describe('Turn History Management', () => {
    it('maintains turn history limit', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Create many turns
      const turns = Array.from({ length: 150 }, (_, i) => ({
        id: `turn-${i}`,
        type: (i % 2 === 0 ? 'user' : 'assistant') as TurnType,
        duration: 1000
      }));

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: turns.slice(-100) // Keep only last 100
      });

      act(() => {
        eventHandlers.get('turn-history-updated')?.forEach(handler => 
          handler({ history: turns.slice(-100) })
        );
      });

      await waitFor(() => {
        expect(result.current.turnHistory).toHaveLength(100);
        expect(result.current.turnHistory[0].id).toBe('turn-50');
      });
    });

    it('provides turn history filtering', () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const turns = [
        { id: '1', type: 'user' as TurnType },
        { id: '2', type: 'assistant' as TurnType },
        { id: '3', type: 'user' as TurnType },
        { id: '4', type: 'assistant' as TurnType }
      ];

      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: null,
        isUserTurn: false,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: turns
      });

      act(() => {
        eventHandlers.get('turn-history-updated')?.forEach(handler => 
          handler({ history: turns })
        );
      });

      const userTurns = result.current.getUserTurns();
      expect(userTurns).toHaveLength(2);
      expect(userTurns[0].id).toBe('1');

      const assistantTurns = result.current.getAssistantTurns();
      expect(assistantTurns).toHaveLength(2);
      expect(assistantTurns[0].id).toBe('2');
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockTurnManager.off).toHaveBeenCalledWith('turn-started', expect.any(Function));
      expect(mockTurnManager.off).toHaveBeenCalledWith('turn-ended', expect.any(Function));
      expect(mockTurnManager.off).toHaveBeenCalledWith('turn-state-changed', expect.any(Function));
      expect(mockTurnManager.off).toHaveBeenCalledWith('turn-queued', expect.any(Function));
    });

    it('clears intervals on unmount', () => {
      const clearIntervalSpy = vi.spyOn(global, 'clearInterval');

      const { unmount } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start a turn to trigger duration tracking
      mockTurnManager.getTurnState.mockReturnValue({
        currentTurn: { id: 'test', type: 'user' },
        isUserTurn: true,
        isAssistantTurn: false,
        canSendInput: true,
        pendingTurns: [],
        turnHistory: []
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

      const { result } = renderHook(() => useTurnState(), {
        wrapper: StrictModeWrapper
      });

      await act(async () => {
        await result.current.startUserTurn();
      });

      // Should only call once despite double mounting
      expect(mockTurnManager.startTurn).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles missing turn manager', () => {
      mockClient.getTurnManager.mockReturnValue(null);

      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Should return default state
      expect(result.current.currentTurn).toBeNull();
      expect(result.current.canSendInput).toBe(true);
    });

    it('handles rapid turn changes', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Rapid turn changes
      for (let i = 0; i < 10; i++) {
        const turnData = {
          id: `rapid-${i}`,
          type: (i % 2 === 0 ? 'user' : 'assistant') as TurnType
        };

        mockTurnManager.getTurnState.mockReturnValue({
          currentTurn: turnData,
          isUserTurn: i % 2 === 0,
          isAssistantTurn: i % 2 === 1,
          canSendInput: i % 2 === 0,
          pendingTurns: [],
          turnHistory: []
        });

        act(() => {
          eventHandlers.get('turn-started')?.forEach(handler => handler(turnData));
        });
      }

      // Should handle all changes gracefully
      expect(result.current.currentTurn?.id).toBe('rapid-9');
    });

    it('handles turn error events', async () => {
      const { result } = renderHook(() => useTurnState(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const error = new Error('Turn failed');

      act(() => {
        eventHandlers.get('turn-error')?.forEach(handler => 
          handler({ turnId: 'error-turn', error })
        );
      });

      await waitFor(() => {
        expect(result.current.error).toEqual(error);
      });
    });
  });
});