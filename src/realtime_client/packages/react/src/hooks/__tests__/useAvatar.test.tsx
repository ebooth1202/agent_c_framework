/**
 * Tests for useAvatar hook
 * Tests avatar session lifecycle and management
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAvatar } from '../useAvatar';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';
import type { Avatar, AvatarSession, AvatarState } from '@agentc/realtime-core';

describe('useAvatar', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;
  let mockAvatars: Avatar[];
  let mockAvatarManager: any;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockAvatars = [
      {
        id: 'avatar-1',
        name: 'Professional Avatar',
        provider: 'heygen',
        style: 'professional',
        thumbnailUrl: 'https://example.com/avatar1.jpg',
        previewUrl: 'https://example.com/preview1.mp4',
        metadata: {
          gender: 'female',
          age: 'adult',
          ethnicity: 'diverse'
        }
      },
      {
        id: 'avatar-2',
        name: 'Friendly Avatar',
        provider: 'heygen',
        style: 'casual',
        thumbnailUrl: 'https://example.com/avatar2.jpg',
        previewUrl: 'https://example.com/preview2.mp4',
        metadata: {
          gender: 'male',
          age: 'young-adult',
          ethnicity: 'diverse'
        }
      },
      {
        id: 'avatar-3',
        name: 'Technical Avatar',
        provider: 'synthesia',
        style: 'technical',
        thumbnailUrl: 'https://example.com/avatar3.jpg',
        previewUrl: 'https://example.com/preview3.mp4',
        metadata: {
          gender: 'neutral',
          age: 'adult',
          ethnicity: 'animated'
        }
      }
    ];

    mockAvatarManager = {
      getAvatarState: vi.fn(() => ({
        isEnabled: false,
        currentAvatar: null,
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      })),
      enableAvatar: vi.fn().mockResolvedValue(undefined),
      disableAvatar: vi.fn().mockResolvedValue(undefined),
      startSession: vi.fn().mockResolvedValue({ sessionId: 'session-123' }),
      endSession: vi.fn().mockResolvedValue(undefined),
      switchAvatar: vi.fn().mockResolvedValue(undefined),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      }),
      getAvailableAvatars: vi.fn(() => mockAvatars)
    };
    
    mockClient = {
      ...createMockClient(),
      getAvatarManager: vi.fn(() => mockAvatarManager),
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
    it('returns initial avatar state', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.isEnabled).toBe(false);
      expect(result.current.currentAvatar).toBeNull();
      expect(result.current.session).toBeNull();
      expect(result.current.isConnected).toBe(false);
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('provides available avatars', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.availableAvatars).toEqual(mockAvatars);
    });

    it('provides avatar control methods', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(typeof result.current.enableAvatar).toBe('function');
      expect(typeof result.current.disableAvatar).toBe('function');
      expect(typeof result.current.startSession).toBe('function');
      expect(typeof result.current.endSession).toBe('function');
      expect(typeof result.current.switchAvatar).toBe('function');
    });
  });

  describe('Avatar Enable/Disable', () => {
    it('enables avatar successfully', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.enableAvatar('avatar-1');
      });

      expect(mockAvatarManager.enableAvatar).toHaveBeenCalledWith('avatar-1');
    });

    it('enables avatar with default selection', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.enableAvatar();
      });

      expect(mockAvatarManager.enableAvatar).toHaveBeenCalledWith(undefined);
    });

    it('disables avatar successfully', async () => {
      // First enable avatar
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.disableAvatar();
      });

      expect(mockAvatarManager.disableAvatar).toHaveBeenCalled();
    });

    it('handles enable avatar error', async () => {
      mockAvatarManager.enableAvatar.mockRejectedValue(new Error('Avatar not available'));

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.enableAvatar('invalid-avatar')).rejects.toThrow('Avatar not available');
      });

      expect(result.current.error?.message).toBe('Avatar not available');
    });

    it('updates state after avatar enabled', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.enableAvatar('avatar-1');
      });

      // Simulate avatar enabled event
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-enabled')?.forEach(handler => 
          handler({ avatar: mockAvatars[0] })
        );
      });

      await waitFor(() => {
        expect(result.current.isEnabled).toBe(true);
        expect(result.current.currentAvatar).toEqual(mockAvatars[0]);
      });
    });
  });

  describe('Session Management', () => {
    it('starts session successfully', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startSession();
      });

      expect(mockAvatarManager.startSession).toHaveBeenCalled();
    });

    it('starts session with configuration', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const config = {
        quality: 'high',
        resolution: '1080p',
        frameRate: 30
      };

      await act(async () => {
        await result.current.startSession(config);
      });

      expect(mockAvatarManager.startSession).toHaveBeenCalledWith(config);
    });

    it('prevents starting session when avatar not enabled', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.startSession()).rejects.toThrow('Avatar must be enabled');
      });

      expect(mockAvatarManager.startSession).not.toHaveBeenCalled();
    });

    it('ends session successfully', async () => {
      const session: AvatarSession = {
        sessionId: 'session-123',
        avatarId: 'avatar-1',
        startTime: new Date().toISOString(),
        endTime: null,
        duration: 0,
        metadata: {}
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: true,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.endSession();
      });

      expect(mockAvatarManager.endSession).toHaveBeenCalled();
    });

    it('handles session started event', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const session: AvatarSession = {
        sessionId: 'session-456',
        avatarId: 'avatar-1',
        startTime: new Date().toISOString(),
        endTime: null,
        duration: 0,
        metadata: {}
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: true,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-session-started')?.forEach(handler => 
          handler({ session })
        );
      });

      await waitFor(() => {
        expect(result.current.session).toEqual(session);
        expect(result.current.isConnected).toBe(true);
      });
    });

    it('handles session ended event', async () => {
      const session: AvatarSession = {
        sessionId: 'session-789',
        avatarId: 'avatar-1',
        startTime: '2024-01-01T10:00:00Z',
        endTime: '2024-01-01T10:05:00Z',
        duration: 300,
        metadata: {}
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: true,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // End session
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-session-ended')?.forEach(handler => 
          handler({ session })
        );
      });

      await waitFor(() => {
        expect(result.current.session).toBeNull();
        expect(result.current.isConnected).toBe(false);
      });
    });
  });

  describe('Avatar Switching', () => {
    it('switches avatar successfully', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.switchAvatar('avatar-2');
      });

      expect(mockAvatarManager.switchAvatar).toHaveBeenCalledWith('avatar-2');
    });

    it('prevents switching when session active', async () => {
      const session: AvatarSession = {
        sessionId: 'active-session',
        avatarId: 'avatar-1',
        startTime: new Date().toISOString(),
        endTime: null,
        duration: 0,
        metadata: {}
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: true,
        isStreaming: true,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.switchAvatar('avatar-2')).rejects.toThrow('Cannot switch avatar during active session');
      });

      expect(mockAvatarManager.switchAvatar).not.toHaveBeenCalled();
    });

    it('updates current avatar after switch', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.switchAvatar('avatar-2');
      });

      // Simulate avatar switched event
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[1],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-switched')?.forEach(handler => 
          handler({ avatar: mockAvatars[1] })
        );
      });

      await waitFor(() => {
        expect(result.current.currentAvatar).toEqual(mockAvatars[1]);
      });
    });
  });

  describe('Streaming State', () => {
    it('handles streaming started event', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: { sessionId: 'stream-session' },
        isConnected: true,
        isStreaming: true,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-streaming-started')?.forEach(handler => handler());
      });

      await waitFor(() => {
        expect(result.current.isStreaming).toBe(true);
      });
    });

    it('handles streaming stopped event', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: { sessionId: 'stream-session' },
        isConnected: true,
        isStreaming: true,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Stop streaming
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: { sessionId: 'stream-session' },
        isConnected: true,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-streaming-stopped')?.forEach(handler => handler());
      });

      await waitFor(() => {
        expect(result.current.isStreaming).toBe(false);
      });
    });
  });

  describe('Avatar Filtering', () => {
    it('filters avatars by provider', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const heygenAvatars = result.current.getAvatarsByProvider('heygen');
      expect(heygenAvatars).toHaveLength(2);
      expect(heygenAvatars.every(a => a.provider === 'heygen')).toBe(true);

      const synthesiaAvatars = result.current.getAvatarsByProvider('synthesia');
      expect(synthesiaAvatars).toHaveLength(1);
    });

    it('filters avatars by style', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const professionalAvatars = result.current.getAvatarsByStyle('professional');
      expect(professionalAvatars).toHaveLength(1);
      expect(professionalAvatars[0].name).toBe('Professional Avatar');
    });

    it('filters avatars by metadata', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const femaleAvatars = result.current.filterAvatars({ gender: 'female' });
      expect(femaleAvatars).toHaveLength(1);
      expect(femaleAvatars[0].id).toBe('avatar-1');

      const animatedAvatars = result.current.filterAvatars({ ethnicity: 'animated' });
      expect(animatedAvatars).toHaveLength(1);
      expect(animatedAvatars[0].id).toBe('avatar-3');
    });
  });

  describe('Preview Management', () => {
    let mockVideo: any;

    beforeEach(() => {
      mockVideo = {
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        load: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        currentTime: 0,
        duration: 10,
        volume: 1
      };

      global.HTMLVideoElement = vi.fn(() => mockVideo) as any;
    });

    it('previews avatar successfully', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.previewAvatar('avatar-1');
      });

      expect(mockVideo.play).toHaveBeenCalled();
      expect(result.current.isPreviewPlaying).toBe(true);
      expect(result.current.previewingAvatarId).toBe('avatar-1');
    });

    it('stops preview successfully', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start preview
      await act(async () => {
        await result.current.previewAvatar('avatar-1');
      });

      // Stop preview
      act(() => {
        result.current.stopPreview();
      });

      expect(mockVideo.pause).toHaveBeenCalled();
      expect(result.current.isPreviewPlaying).toBe(false);
      expect(result.current.previewingAvatarId).toBeNull();
    });

    it('handles preview error', async () => {
      mockVideo.play.mockRejectedValue(new Error('Preview failed'));

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.previewAvatar('avatar-1')).rejects.toThrow('Preview failed');
      });

      expect(result.current.isPreviewPlaying).toBe(false);
      expect(result.current.error?.message).toBe('Preview failed');
    });
  });

  describe('Error Handling', () => {
    it('handles connection error', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const error = new Error('Connection failed');

      act(() => {
        eventHandlers.get('avatar-error')?.forEach(handler => 
          handler({ error })
        );
      });

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error
      });

      await waitFor(() => {
        expect(result.current.error).toEqual(error);
      });
    });

    it('clears error on successful action', async () => {
      mockAvatarManager.enableAvatar.mockRejectedValueOnce(new Error('First error'));

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Cause an error
      await act(async () => {
        try {
          await result.current.enableAvatar('invalid');
        } catch (e) {
          // Expected
        }
      });

      expect(result.current.error).toBeDefined();

      // Successful action should clear error
      mockAvatarManager.enableAvatar.mockResolvedValueOnce(undefined);
      
      await act(async () => {
        await result.current.enableAvatar('avatar-1');
      });

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-enabled')?.forEach(handler => 
          handler({ avatar: mockAvatars[0] })
        );
      });

      await waitFor(() => {
        expect(result.current.error).toBeNull();
      });
    });
  });

  describe('Session Statistics', () => {
    it('tracks session statistics', () => {
      const session: AvatarSession = {
        sessionId: 'stats-session',
        avatarId: 'avatar-1',
        startTime: '2024-01-01T10:00:00Z',
        endTime: '2024-01-01T10:30:00Z',
        duration: 1800,
        metadata: {
          messageCount: 42,
          turnCount: 21,
          errors: 2
        }
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const stats = result.current.getSessionStats();
      expect(stats).toEqual({
        duration: 1800,
        messageCount: 42,
        turnCount: 21,
        errors: 2
      });
    });

    it('returns empty stats when no session', () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const stats = result.current.getSessionStats();
      expect(stats).toEqual({
        duration: 0,
        messageCount: 0,
        turnCount: 0,
        errors: 0
      });
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-enabled', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-disabled', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-session-started', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-session-ended', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-switched', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-streaming-started', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-streaming-stopped', expect.any(Function));
      expect(mockAvatarManager.off).toHaveBeenCalledWith('avatar-error', expect.any(Function));
    });

    it('ends session on unmount if active', async () => {
      const session: AvatarSession = {
        sessionId: 'active-unmount',
        avatarId: 'avatar-1',
        startTime: new Date().toISOString(),
        endTime: null,
        duration: 0,
        metadata: {}
      };

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session,
        isConnected: true,
        isStreaming: true,
        error: null
      });

      const { unmount } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockAvatarManager.endSession).toHaveBeenCalled();
    });

    it('stops preview on unmount', async () => {
      const mockVideo = {
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        load: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      };

      global.HTMLVideoElement = vi.fn(() => mockVideo) as any;

      const { result, unmount } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start preview
      await act(async () => {
        await result.current.previewAvatar('avatar-1');
      });

      unmount();

      expect(mockVideo.pause).toHaveBeenCalled();
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result } = renderHook(() => useAvatar(), {
        wrapper: StrictModeWrapper
      });

      await act(async () => {
        await result.current.enableAvatar('avatar-1');
      });

      // Should only call once despite double mounting
      expect(mockAvatarManager.enableAvatar).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles missing avatar manager', () => {
      mockClient.getAvatarManager.mockReturnValue(null);

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.isEnabled).toBe(false);
      expect(result.current.availableAvatars).toEqual([]);
      expect(result.current.currentAvatar).toBeNull();
    });

    it('handles rapid avatar switches', async () => {
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error: null
      });

      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await Promise.all([
          result.current.switchAvatar('avatar-1'),
          result.current.switchAvatar('avatar-2'),
          result.current.switchAvatar('avatar-3')
        ]);
      });

      // All calls should go through
      expect(mockAvatarManager.switchAvatar).toHaveBeenCalledTimes(3);
    });

    it('handles session recovery after error', async () => {
      const { result } = renderHook(() => useAvatar(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Simulate session error
      const error = new Error('Session failed');
      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: null,
        isConnected: false,
        isStreaming: false,
        error
      });

      act(() => {
        eventHandlers.get('avatar-error')?.forEach(handler => 
          handler({ error })
        );
      });

      expect(result.current.error).toEqual(error);

      // Recover session
      mockAvatarManager.startSession.mockResolvedValue({ sessionId: 'recovered-session' });
      
      await act(async () => {
        await result.current.startSession();
      });

      mockAvatarManager.getAvatarState.mockReturnValue({
        isEnabled: true,
        currentAvatar: mockAvatars[0],
        session: { sessionId: 'recovered-session' },
        isConnected: true,
        isStreaming: false,
        error: null
      });

      act(() => {
        eventHandlers.get('avatar-session-started')?.forEach(handler => 
          handler({ session: { sessionId: 'recovered-session' } })
        );
      });

      await waitFor(() => {
        expect(result.current.error).toBeNull();
        expect(result.current.session?.sessionId).toBe('recovered-session');
      });
    });
  });
});