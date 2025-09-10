/**
 * Tests for useAudio hook
 * Tests audio recording, playback, and turn-aware streaming
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAudio } from '../useAudio';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';

// Mock MediaRecorder
class MockMediaRecorder {
  state: string = 'inactive';
  ondataavailable: ((event: any) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  
  constructor(public stream: MediaStream) {}
  
  start(timeslice?: number) {
    this.state = 'recording';
    // Simulate data available
    setTimeout(() => {
      if (this.ondataavailable) {
        const blob = new Blob(['audio data'], { type: 'audio/webm' });
        this.ondataavailable({ data: blob });
      }
    }, 100);
  }
  
  stop() {
    this.state = 'inactive';
    if (this.onstop) {
      this.onstop();
    }
  }
  
  pause() {
    this.state = 'paused';
  }
  
  resume() {
    this.state = 'recording';
  }
}

// Mock getUserMedia
const mockGetUserMedia = vi.fn();

describe('useAudio', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;
  let mockMediaStream: MediaStream;
  let mockAudioTrack: MediaStreamTrack;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    // Mock MediaStreamTrack
    mockAudioTrack = {
      kind: 'audio',
      enabled: true,
      stop: vi.fn(),
      getSettings: vi.fn(() => ({ sampleRate: 48000 })),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    } as any;

    // Mock MediaStream
    mockMediaStream = {
      getTracks: vi.fn(() => [mockAudioTrack]),
      getAudioTracks: vi.fn(() => [mockAudioTrack]),
      addTrack: vi.fn(),
      removeTrack: vi.fn()
    } as any;

    // Setup getUserMedia mock
    mockGetUserMedia.mockResolvedValue(mockMediaStream);
    Object.defineProperty(global.navigator, 'mediaDevices', {
      value: { getUserMedia: mockGetUserMedia },
      configurable: true
    });

    // Mock MediaRecorder
    global.MediaRecorder = MockMediaRecorder as any;
    (global.MediaRecorder as any).isTypeSupported = vi.fn(() => true);

    // Mock AudioContext
    global.AudioContext = vi.fn().mockImplementation(() => ({
      createAnalyser: vi.fn(() => ({
        fftSize: 2048,
        frequencyBinCount: 1024,
        getByteFrequencyData: vi.fn((array: Uint8Array) => {
          // Simulate some audio levels
          for (let i = 0; i < array.length; i++) {
            array[i] = Math.random() * 128;
          }
        }),
        connect: vi.fn(),
        disconnect: vi.fn()
      })),
      createMediaStreamSource: vi.fn(() => ({
        connect: vi.fn(),
        disconnect: vi.fn()
      })),
      close: vi.fn(),
      state: 'running'
    })) as any;

    mockClient = {
      ...createMockClient(),
      sendBinaryFrame: vi.fn(),
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
    it('returns initial state correctly', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.isRecording).toBe(false);
      expect(result.current.isPlaying).toBe(false);
      expect(result.current.isMuted).toBe(false);
      expect(result.current.audioLevel).toBe(0);
      expect(result.current.error).toBeNull();
      expect(result.current.recordingDuration).toBe(0);
      expect(result.current.playbackDuration).toBe(0);
    });

    it('provides configuration values', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.config).toEqual({
        sampleRate: 24000,
        channels: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      });
    });

    it('provides device information', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.devices).toEqual({
        input: [],
        output: []
      });
      expect(result.current.selectedInputDevice).toBeNull();
      expect(result.current.selectedOutputDevice).toBeNull();
    });
  });

  describe('Recording Management', () => {
    it('starts recording successfully', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: {
          sampleRate: 24000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      expect(result.current.isRecording).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('stops recording successfully', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start recording first
      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.isRecording).toBe(true);

      // Stop recording
      act(() => {
        result.current.stopRecording();
      });

      await waitFor(() => {
        expect(result.current.isRecording).toBe(false);
        expect(mockAudioTrack.stop).toHaveBeenCalled();
      });
    });

    it('handles permission denied error', async () => {
      mockGetUserMedia.mockRejectedValue(
        new DOMException('Permission denied', 'NotAllowedError')
      );

      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toContain('Permission denied');
      expect(result.current.isRecording).toBe(false);
    });

    it('handles device not found error', async () => {
      mockGetUserMedia.mockRejectedValue(
        new DOMException('Device not found', 'NotFoundError')
      );

      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toContain('Device not found');
    });

    it('sends audio data to client', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      // Wait for audio data to be sent
      await waitFor(() => {
        expect(mockClient.sendBinaryFrame).toHaveBeenCalled();
      }, { timeout: 200 });
    });
  });

  describe('Mute/Unmute', () => {
    it('mutes audio successfully', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start recording first
      await act(async () => {
        await result.current.startRecording();
      });

      act(() => {
        result.current.mute();
      });

      expect(result.current.isMuted).toBe(true);
      expect(mockAudioTrack.enabled).toBe(false);
    });

    it('unmutes audio successfully', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start recording and mute
      await act(async () => {
        await result.current.startRecording();
      });

      act(() => {
        result.current.mute();
      });

      expect(result.current.isMuted).toBe(true);

      act(() => {
        result.current.unmute();
      });

      expect(result.current.isMuted).toBe(false);
      expect(mockAudioTrack.enabled).toBe(true);
    });

    it('toggles mute state', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.isMuted).toBe(false);

      act(() => {
        result.current.toggleMute();
      });

      expect(result.current.isMuted).toBe(true);

      act(() => {
        result.current.toggleMute();
      });

      expect(result.current.isMuted).toBe(false);
    });
  });

  describe('Audio Level Monitoring', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('updates audio levels during recording', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      // Advance timers to trigger audio level updates
      act(() => {
        vi.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(result.current.audioLevel).toBeGreaterThan(0);
      });
    });

    it('resets audio level when recording stops', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      // Get some audio level
      act(() => {
        vi.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(result.current.audioLevel).toBeGreaterThan(0);
      });

      // Stop recording
      act(() => {
        result.current.stopRecording();
      });

      await waitFor(() => {
        expect(result.current.audioLevel).toBe(0);
      });
    });
  });

  describe('Playback Management', () => {
    it('plays audio successfully', async () => {
      const mockAudioBuffer = new ArrayBuffer(1024);
      
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.playAudio(mockAudioBuffer);
      });

      expect(result.current.isPlaying).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('stops playback successfully', async () => {
      const mockAudioBuffer = new ArrayBuffer(1024);
      
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.playAudio(mockAudioBuffer);
      });

      expect(result.current.isPlaying).toBe(true);

      act(() => {
        result.current.stopPlayback();
      });

      expect(result.current.isPlaying).toBe(false);
    });

    it('adjusts playback volume', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        result.current.setVolume(0.5);
      });

      expect(result.current.volume).toBe(0.5);

      // Test clamping
      act(() => {
        result.current.setVolume(1.5);
      });

      expect(result.current.volume).toBe(1);

      act(() => {
        result.current.setVolume(-0.5);
      });

      expect(result.current.volume).toBe(0);
    });
  });

  describe('Turn-aware Audio Streaming', () => {
    it('handles turn_audio_started event', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        eventHandlers.get('turn_audio_started')?.forEach(handler => 
          handler({ turnId: 'turn-123' })
        );
      });

      await waitFor(() => {
        expect(result.current.isTurnAudioActive).toBe(true);
        expect(result.current.currentTurnId).toBe('turn-123');
      });
    });

    it('handles turn_audio_stopped event', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start turn audio first
      act(() => {
        eventHandlers.get('turn_audio_started')?.forEach(handler => 
          handler({ turnId: 'turn-123' })
        );
      });

      expect(result.current.isTurnAudioActive).toBe(true);

      // Stop turn audio
      act(() => {
        eventHandlers.get('turn_audio_stopped')?.forEach(handler => 
          handler({ turnId: 'turn-123' })
        );
      });

      await waitFor(() => {
        expect(result.current.isTurnAudioActive).toBe(false);
        expect(result.current.currentTurnId).toBeNull();
      });
    });

    it('handles audio_chunk event during turn', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const audioData = new ArrayBuffer(1024);

      act(() => {
        eventHandlers.get('audio_chunk')?.forEach(handler => 
          handler({ data: audioData, turnId: 'turn-123' })
        );
      });

      // Should trigger playback
      await waitFor(() => {
        expect(result.current.isPlaying).toBe(true);
      });
    });
  });

  describe('Device Management', () => {
    it('enumerates audio devices', async () => {
      const mockDevices = [
        { 
          deviceId: 'input1', 
          kind: 'audioinput', 
          label: 'Microphone 1',
          groupId: 'group1'
        },
        { 
          deviceId: 'output1', 
          kind: 'audiooutput', 
          label: 'Speaker 1',
          groupId: 'group1'
        }
      ];

      const enumerateDevicesMock = vi.fn().mockResolvedValue(mockDevices);
      Object.defineProperty(navigator.mediaDevices, 'enumerateDevices', {
        value: enumerateDevicesMock,
        configurable: true
      });

      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.refreshDevices();
      });

      expect(result.current.devices.input).toHaveLength(1);
      expect(result.current.devices.output).toHaveLength(1);
      expect(result.current.devices.input[0].label).toBe('Microphone 1');
      expect(result.current.devices.output[0].label).toBe('Speaker 1');
    });

    it('selects input device', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.selectInputDevice('device-id-123');
      });

      expect(result.current.selectedInputDevice).toBe('device-id-123');
    });

    it('selects output device', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.selectOutputDevice('speaker-id-456');
      });

      expect(result.current.selectedOutputDevice).toBe('speaker-id-456');
    });
  });

  describe('Recording Duration Tracking', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('tracks recording duration', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      // Advance time by 3 seconds
      act(() => {
        vi.advanceTimersByTime(3000);
      });

      await waitFor(() => {
        expect(result.current.recordingDuration).toBeGreaterThanOrEqual(3);
      });

      act(() => {
        result.current.stopRecording();
      });

      // Duration should reset
      await waitFor(() => {
        expect(result.current.recordingDuration).toBe(0);
      });
    });
  });

  describe('Cleanup', () => {
    it('cleans up resources on unmount', async () => {
      const { result, unmount } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      // Start recording
      await act(async () => {
        await result.current.startRecording();
      });

      unmount();

      // Verify cleanup
      expect(mockAudioTrack.stop).toHaveBeenCalled();
      expect(mockClient.off).toHaveBeenCalled();
    });

    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('turn_audio_started', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('turn_audio_stopped', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('audio_chunk', expect.any(Function));
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result } = renderHook(() => useAudio(), {
        wrapper: StrictModeWrapper
      });

      // Should handle multiple effect runs without issues
      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.isRecording).toBe(true);
      expect(mockGetUserMedia).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles rapid start/stop recording', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        const startPromise = result.current.startRecording();
        result.current.stopRecording();
        await startPromise;
      });

      // Should handle gracefully
      expect(mockAudioTrack.stop).toHaveBeenCalled();
    });

    it('handles recording when already recording', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.isRecording).toBe(true);

      // Try to start again
      await act(async () => {
        await result.current.startRecording();
      });

      // Should not create multiple recordings
      expect(mockGetUserMedia).toHaveBeenCalledTimes(1);
    });

    it('handles stopping when not recording', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      act(() => {
        result.current.stopRecording();
      });

      // Should not throw error
      expect(result.current.isRecording).toBe(false);
    });
  });
});