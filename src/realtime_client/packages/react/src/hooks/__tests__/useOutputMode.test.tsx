/**
 * Tests for useOutputMode hook
 * Tests output mode switching between audio and text
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useOutputMode } from '../useOutputMode';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';

describe('useOutputMode', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockClient = {
      ...createMockClient(),
      getOutputMode: vi.fn(() => 'audio'),
      setOutputMode: vi.fn().mockResolvedValue(undefined),
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
    it('returns initial output mode', () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.mode).toBe('audio');
      expect(result.current.isAudioMode).toBe(true);
      expect(result.current.isTextMode).toBe(false);
    });

    it('returns text mode when configured', () => {
      mockClient.getOutputMode.mockReturnValue('text');

      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.mode).toBe('text');
      expect(result.current.isAudioMode).toBe(false);
      expect(result.current.isTextMode).toBe(true);
    });
  });

  describe('Mode Switching', () => {
    it('switches to text mode', async () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setTextMode();
      });

      expect(mockClient.setOutputMode).toHaveBeenCalledWith('text');
    });

    it('switches to audio mode', async () => {
      mockClient.getOutputMode.mockReturnValue('text');

      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setAudioMode();
      });

      expect(mockClient.setOutputMode).toHaveBeenCalledWith('audio');
    });

    it('toggles output mode', async () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Currently audio, should toggle to text
      await act(async () => {
        await result.current.toggleMode();
      });

      expect(mockClient.setOutputMode).toHaveBeenCalledWith('text');

      // Update mock to return text mode
      mockClient.getOutputMode.mockReturnValue('text');

      // Now text, should toggle to audio
      await act(async () => {
        await result.current.toggleMode();
      });

      expect(mockClient.setOutputMode).toHaveBeenCalledWith('audio');
    });

    it('sets mode directly', async () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setMode('text');
      });

      expect(mockClient.setOutputMode).toHaveBeenCalledWith('text');
    });
  });

  describe('Event Handling', () => {
    it('handles output mode changed event', async () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      mockClient.getOutputMode.mockReturnValue('text');

      act(() => {
        eventHandlers.get('output_mode_changed')?.forEach(handler => 
          handler({ mode: 'text' })
        );
      });

      await waitFor(() => {
        expect(result.current.mode).toBe('text');
        expect(result.current.isTextMode).toBe(true);
      });
    });
  });

  describe('Error Handling', () => {
    it('handles mode change error', async () => {
      mockClient.setOutputMode.mockRejectedValue(new Error('Mode change failed'));

      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.setTextMode()).rejects.toThrow('Mode change failed');
      });
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('output_mode_changed', expect.any(Function));
    });
  });

  describe('Edge Cases', () => {
    it('handles missing client', () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={null}>{children}</TestWrapper>
        )
      });

      expect(result.current.mode).toBe('audio');
      expect(result.current.isAudioMode).toBe(true);
    });

    it('prevents setting same mode', async () => {
      const { result } = renderHook(() => useOutputMode(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Already in audio mode
      await act(async () => {
        await result.current.setAudioMode();
      });

      // Should still call setOutputMode (let client handle no-op)
      expect(mockClient.setOutputMode).toHaveBeenCalledWith('audio');
    });
  });
});