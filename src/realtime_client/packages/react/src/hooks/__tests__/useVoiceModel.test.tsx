/**
 * Tests for useVoiceModel hook
 * Tests voice selection and avatar mode management
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useVoiceModel } from '../useVoiceModel';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';
import type { Voice, VoiceConfig } from '@agentc/realtime-core';

describe('useVoiceModel', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;
  let mockVoices: Voice[];

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockVoices = [
      {
        id: 'voice-1',
        name: 'Alloy',
        provider: 'openai',
        language: 'en-US',
        gender: 'neutral',
        style: 'professional',
        previewUrl: 'https://example.com/preview1.mp3',
        metadata: { quality: 'high' }
      },
      {
        id: 'voice-2',
        name: 'Echo',
        provider: 'openai',
        language: 'en-US',
        gender: 'male',
        style: 'friendly',
        previewUrl: 'https://example.com/preview2.mp3',
        metadata: { quality: 'standard' }
      },
      {
        id: 'voice-3',
        name: 'Nova',
        provider: 'openai',
        language: 'en-US',
        gender: 'female',
        style: 'conversational',
        previewUrl: 'https://example.com/preview3.mp3',
        metadata: { quality: 'premium' }
      }
    ];
    
    mockClient = {
      ...createMockClient(),
      getVoiceConfig: vi.fn(() => ({
        currentVoice: mockVoices[0],
        availableVoices: mockVoices,
        isAvatarMode: false,
        avatarVoice: null
      })),
      setVoice: vi.fn().mockResolvedValue(undefined),
      enableAvatarMode: vi.fn().mockResolvedValue(undefined),
      disableAvatarMode: vi.fn().mockResolvedValue(undefined),
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
    it('returns initial voice configuration', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.currentVoice).toEqual(mockVoices[0]);
      expect(result.current.availableVoices).toEqual(mockVoices);
      expect(result.current.isAvatarMode).toBe(false);
      expect(result.current.avatarVoice).toBeNull();
    });

    it('provides voice control methods', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(typeof result.current.setVoice).toBe('function');
      expect(typeof result.current.enableAvatarMode).toBe('function');
      expect(typeof result.current.disableAvatarMode).toBe('function');
      expect(typeof result.current.previewVoice).toBe('function');
      expect(typeof result.current.stopPreview).toBe('function');
    });

    it('provides voice filtering utilities', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(typeof result.current.getVoicesByProvider).toBe('function');
      expect(typeof result.current.getVoicesByLanguage).toBe('function');
      expect(typeof result.current.getVoicesByGender).toBe('function');
    });
  });

  describe('Voice Selection', () => {
    it('sets voice by ID successfully', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setVoice('voice-2');
      });

      expect(mockClient.setVoice).toHaveBeenCalledWith('voice-2');
    });

    it('sets voice with Voice object', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setVoice(mockVoices[1]);
      });

      expect(mockClient.setVoice).toHaveBeenCalledWith('voice-2');
    });

    it('handles invalid voice ID', async () => {
      mockClient.setVoice.mockRejectedValue(new Error('Voice not found'));

      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.setVoice('invalid-voice')).rejects.toThrow('Voice not found');
      });

      expect(result.current.error?.message).toBe('Voice not found');
    });

    it('validates voice before setting', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Try to set voice not in available list
      await act(async () => {
        await expect(result.current.setVoice('unlisted-voice')).rejects.toThrow();
      });

      expect(mockClient.setVoice).not.toHaveBeenCalled();
    });

    it('updates current voice after successful change', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[1],
        availableVoices: mockVoices,
        isAvatarMode: false,
        avatarVoice: null
      });

      await act(async () => {
        await result.current.setVoice('voice-2');
      });

      // Simulate voice changed event
      act(() => {
        eventHandlers.get('voice_changed')?.forEach(handler => 
          handler({ voice: mockVoices[1] })
        );
      });

      await waitFor(() => {
        expect(result.current.currentVoice).toEqual(mockVoices[1]);
      });
    });
  });

  describe('Avatar Mode', () => {
    it('enables avatar mode successfully', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.enableAvatarMode('avatar-voice-id');
      });

      expect(mockClient.enableAvatarMode).toHaveBeenCalledWith('avatar-voice-id');
    });

    it('enables avatar mode with default voice', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.enableAvatarMode();
      });

      expect(mockClient.enableAvatarMode).toHaveBeenCalledWith(undefined);
    });

    it('disables avatar mode successfully', async () => {
      // First enable avatar mode
      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[0],
        availableVoices: mockVoices,
        isAvatarMode: true,
        avatarVoice: mockVoices[0]
      });

      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.isAvatarMode).toBe(true);

      await act(async () => {
        await result.current.disableAvatarMode();
      });

      expect(mockClient.disableAvatarMode).toHaveBeenCalled();
    });

    it('handles avatar mode toggle', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Toggle on
      await act(async () => {
        await result.current.toggleAvatarMode();
      });

      expect(mockClient.enableAvatarMode).toHaveBeenCalled();

      // Update state to reflect avatar mode is on
      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[0],
        availableVoices: mockVoices,
        isAvatarMode: true,
        avatarVoice: mockVoices[0]
      });

      act(() => {
        eventHandlers.get('avatar_mode_changed')?.forEach(handler => 
          handler({ enabled: true, voice: mockVoices[0] })
        );
      });

      // Toggle off
      await act(async () => {
        await result.current.toggleAvatarMode();
      });

      expect(mockClient.disableAvatarMode).toHaveBeenCalled();
    });

    it('updates avatar voice when avatar mode is enabled', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const avatarVoice = mockVoices[2];

      act(() => {
        eventHandlers.get('avatar_mode_changed')?.forEach(handler => 
          handler({ enabled: true, voice: avatarVoice })
        );
      });

      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[0],
        availableVoices: mockVoices,
        isAvatarMode: true,
        avatarVoice
      });

      await waitFor(() => {
        expect(result.current.isAvatarMode).toBe(true);
        expect(result.current.avatarVoice).toEqual(avatarVoice);
      });
    });
  });

  describe('Voice Preview', () => {
    let mockAudio: any;

    beforeEach(() => {
      mockAudio = {
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        load: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        currentTime: 0,
        duration: 10,
        volume: 1
      };

      global.Audio = vi.fn(() => mockAudio) as any;
    });

    it('previews voice successfully', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.previewVoice('voice-1');
      });

      expect(mockAudio.play).toHaveBeenCalled();
      expect(result.current.isPreviewPlaying).toBe(true);
      expect(result.current.previewingVoiceId).toBe('voice-1');
    });

    it('stops preview successfully', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start preview
      await act(async () => {
        await result.current.previewVoice('voice-1');
      });

      expect(result.current.isPreviewPlaying).toBe(true);

      // Stop preview
      act(() => {
        result.current.stopPreview();
      });

      expect(mockAudio.pause).toHaveBeenCalled();
      expect(result.current.isPreviewPlaying).toBe(false);
      expect(result.current.previewingVoiceId).toBeNull();
    });

    it('handles preview error', async () => {
      mockAudio.play.mockRejectedValue(new Error('Playback failed'));

      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.previewVoice('voice-1')).rejects.toThrow('Playback failed');
      });

      expect(result.current.isPreviewPlaying).toBe(false);
      expect(result.current.error?.message).toBe('Playback failed');
    });

    it('stops previous preview when starting new one', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start first preview
      await act(async () => {
        await result.current.previewVoice('voice-1');
      });

      expect(result.current.previewingVoiceId).toBe('voice-1');

      // Start second preview
      await act(async () => {
        await result.current.previewVoice('voice-2');
      });

      expect(mockAudio.pause).toHaveBeenCalled();
      expect(result.current.previewingVoiceId).toBe('voice-2');
    });

    it('handles preview completion', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.previewVoice('voice-1');
      });

      // Simulate audio ended event
      act(() => {
        const endedHandler = mockAudio.addEventListener.mock.calls.find(
          call => call[0] === 'ended'
        )?.[1];
        if (endedHandler) endedHandler();
      });

      await waitFor(() => {
        expect(result.current.isPreviewPlaying).toBe(false);
        expect(result.current.previewingVoiceId).toBeNull();
      });
    });
  });

  describe('Voice Filtering', () => {
    it('filters voices by provider', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const openaiVoices = result.current.getVoicesByProvider('openai');
      expect(openaiVoices).toHaveLength(3);
      expect(openaiVoices.every(v => v.provider === 'openai')).toBe(true);

      const googleVoices = result.current.getVoicesByProvider('google');
      expect(googleVoices).toHaveLength(0);
    });

    it('filters voices by language', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const enVoices = result.current.getVoicesByLanguage('en-US');
      expect(enVoices).toHaveLength(3);

      const frVoices = result.current.getVoicesByLanguage('fr-FR');
      expect(frVoices).toHaveLength(0);
    });

    it('filters voices by gender', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const maleVoices = result.current.getVoicesByGender('male');
      expect(maleVoices).toHaveLength(1);
      expect(maleVoices[0].name).toBe('Echo');

      const femaleVoices = result.current.getVoicesByGender('female');
      expect(femaleVoices).toHaveLength(1);
      expect(femaleVoices[0].name).toBe('Nova');

      const neutralVoices = result.current.getVoicesByGender('neutral');
      expect(neutralVoices).toHaveLength(1);
      expect(neutralVoices[0].name).toBe('Alloy');
    });

    it('filters voices by style', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const professionalVoices = result.current.getVoicesByStyle('professional');
      expect(professionalVoices).toHaveLength(1);
      expect(professionalVoices[0].name).toBe('Alloy');
    });

    it('filters voices by multiple criteria', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const filtered = result.current.filterVoices({
        provider: 'openai',
        gender: 'female',
        language: 'en-US'
      });

      expect(filtered).toHaveLength(1);
      expect(filtered[0].name).toBe('Nova');
    });
  });

  describe('Voice List Updates', () => {
    it('handles voice list update event', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const newVoices = [
        ...mockVoices,
        {
          id: 'voice-4',
          name: 'Sage',
          provider: 'openai',
          language: 'en-GB',
          gender: 'neutral',
          style: 'formal',
          previewUrl: 'https://example.com/preview4.mp3',
          metadata: {}
        }
      ];

      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[0],
        availableVoices: newVoices,
        isAvatarMode: false,
        avatarVoice: null
      });

      act(() => {
        eventHandlers.get('voice_list_updated')?.forEach(handler => 
          handler({ voices: newVoices })
        );
      });

      await waitFor(() => {
        expect(result.current.availableVoices).toHaveLength(4);
        expect(result.current.availableVoices[3].name).toBe('Sage');
      });
    });

    it('handles voice removed from list', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const reducedVoices = mockVoices.slice(0, 2);

      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: mockVoices[0],
        availableVoices: reducedVoices,
        isAvatarMode: false,
        avatarVoice: null
      });

      act(() => {
        eventHandlers.get('voice_list_updated')?.forEach(handler => 
          handler({ voices: reducedVoices })
        );
      });

      await waitFor(() => {
        expect(result.current.availableVoices).toHaveLength(2);
      });
    });
  });

  describe('Voice Configuration', () => {
    it('applies voice configuration settings', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const config: VoiceConfig = {
        speed: 1.2,
        pitch: 0.9,
        volume: 0.8,
        emphasis: 'moderate'
      };

      await act(async () => {
        await result.current.setVoiceConfig(config);
      });

      expect(mockClient.setVoiceConfig).toHaveBeenCalledWith(config);
    });

    it('validates configuration ranges', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const invalidConfig = {
        speed: 3.0, // Too high
        pitch: -2.0, // Too low
        volume: 1.5 // Too high
      };

      await act(async () => {
        await expect(result.current.setVoiceConfig(invalidConfig)).rejects.toThrow();
      });

      expect(mockClient.setVoiceConfig).not.toHaveBeenCalled();
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('voice_changed', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('avatar_mode_changed', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('voice_list_updated', expect.any(Function));
    });

    it('stops preview on unmount', async () => {
      const mockAudio = {
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        load: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      };

      global.Audio = vi.fn(() => mockAudio) as any;

      const { result, unmount } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start preview
      await act(async () => {
        await result.current.previewVoice('voice-1');
      });

      unmount();

      expect(mockAudio.pause).toHaveBeenCalled();
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: StrictModeWrapper
      });

      await act(async () => {
        await result.current.setVoice('voice-2');
      });

      // Should only call once despite double mounting
      expect(mockClient.setVoice).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles missing client gracefully', () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={null}>{children}</TestWrapper>
        )
      });

      expect(result.current.currentVoice).toBeNull();
      expect(result.current.availableVoices).toEqual([]);
      expect(result.current.isAvatarMode).toBe(false);
    });

    it('handles empty voice list', () => {
      mockClient.getVoiceConfig.mockReturnValue({
        currentVoice: null,
        availableVoices: [],
        isAvatarMode: false,
        avatarVoice: null
      });

      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.availableVoices).toEqual([]);
      expect(result.current.currentVoice).toBeNull();
    });

    it('handles rapid voice changes', async () => {
      const { result } = renderHook(() => useVoiceModel(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await Promise.all([
          result.current.setVoice('voice-1'),
          result.current.setVoice('voice-2'),
          result.current.setVoice('voice-3')
        ]);
      });

      // All calls should go through
      expect(mockClient.setVoice).toHaveBeenCalledTimes(3);
    });
  });
});