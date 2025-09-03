/**
 * Tests for AudioService
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AudioService } from '../../src/audio/AudioService';
import { AudioProcessor } from '../../src/audio/AudioProcessor';
import {
  AudioServiceStatus,
  AudioServiceState,
  AudioChunkData,
  AudioProcessorError,
  AudioProcessorErrorCode,
  AudioProcessorStatus
} from '../../src/audio/types';
import { 
  MockAudioContext, 
  MockMediaStream, 
  MockMediaStreamTrack,
  setupAudioMocks 
} from '../../../../test/utils/mock-audio';
import { sleep, waitFor } from '../../../../test/utils/test-helpers';

// Mock AudioProcessor module
vi.mock('../../src/audio/AudioProcessor', () => {
  return {
    AudioProcessor: vi.fn().mockImplementation(() => {
      const listeners = new Map<string, Set<Function>>();
      let status: AudioProcessorStatus = {
        state: 'idle',
        audioLevel: 0
      };
      
      return {
        initialize: vi.fn().mockResolvedValue(undefined),
        startProcessing: vi.fn().mockResolvedValue(undefined),
        stopProcessing: vi.fn(),
        cleanup: vi.fn().mockResolvedValue(undefined),
        getStatus: vi.fn(() => status),
        setStatus: (newStatus: AudioProcessorStatus) => { 
          status = newStatus; 
        },
        on: vi.fn((event: string, listener: Function) => {
          if (!listeners.has(event)) {
            listeners.set(event, new Set());
          }
          listeners.get(event)!.add(listener);
          
          // Return unsubscribe function
          return () => {
            listeners.get(event)?.delete(listener);
          };
        }),
        emit: (event: string, ...args: any[]) => {
          const eventListeners = listeners.get(event);
          if (eventListeners) {
            eventListeners.forEach(listener => listener(...args));
          }
        }
      };
    })
  };
});

describe('AudioService', () => {
  let audioService: AudioService;
  let mockProcessor: any;
  let mockGetUserMedia: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    // Setup audio mocks
    setupAudioMocks();
    
    // Reset singleton
    AudioService.resetInstance();
    
    // Get instance
    audioService = AudioService.getInstance({ debug: false });
    
    // Get mock processor instance
    const AudioProcessorMock = AudioProcessor as any;
    mockProcessor = AudioProcessorMock.mock.results[0]?.value;
    
    // Setup getUserMedia mock
    mockGetUserMedia = vi.fn().mockResolvedValue(new MockMediaStream());
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: mockGetUserMedia,
        enumerateDevices: vi.fn().mockResolvedValue([]),
        getSupportedConstraints: vi.fn(() => ({}))
      },
      writable: true,
      configurable: true
    });
  });

  afterEach(() => {
    AudioService.resetInstance();
    vi.clearAllMocks();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = AudioService.getInstance();
      const instance2 = AudioService.getInstance();
      
      expect(instance1).toBe(instance2);
    });

    it('should reset instance properly', () => {
      const instance1 = AudioService.getInstance();
      AudioService.resetInstance();
      const instance2 = AudioService.getInstance();
      
      expect(instance1).not.toBe(instance2);
    });

    it('should pass config to processor', () => {
      AudioService.resetInstance();
      const config = {
        sampleRate: 24000,
        channelCount: 2,
        debug: true
      };
      
      AudioService.getInstance(config);
      
      expect(AudioProcessor).toHaveBeenCalledWith(config);
    });
  });

  describe('Initialization', () => {
    it('should initialize with default status', () => {
      const status = audioService.getStatus();
      
      expect(status.state).toBe('idle');
      expect(status.isRecording).toBe(false);
      expect(status.audioLevel).toBe(0);
      expect(status.frameCount).toBe(0);
      expect(status.sampleRate).toBe(16000);
      expect(status.channelCount).toBe(1);
    });

    it('should setup processor event listeners', () => {
      expect(mockProcessor.on).toHaveBeenCalledWith('audioChunk', expect.any(Function));
      expect(mockProcessor.on).toHaveBeenCalledWith('statusChange', expect.any(Function));
      expect(mockProcessor.on).toHaveBeenCalledWith('levelChange', expect.any(Function));
      expect(mockProcessor.on).toHaveBeenCalledWith('error', expect.any(Function));
    });
  });

  describe('Permission Management', () => {
    it('should request microphone permission', async () => {
      const result = await audioService.requestPermission();
      
      expect(result).toBe(true);
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      expect(audioService.hasPermission()).toBe(true);
    });

    it('should handle permission denial', async () => {
      mockGetUserMedia.mockRejectedValueOnce(new DOMException('Permission denied', 'NotAllowedError'));
      
      const result = await audioService.requestPermission();
      
      expect(result).toBe(false);
      expect(audioService.hasPermission()).toBe(false);
      
      const status = audioService.getStatus();
      expect(status.state).toBe('permission-denied');
      expect(status.error).toContain('Permission denied');
    });

    it('should stop media stream after permission granted', async () => {
      const mockStream = new MockMediaStream();
      const stopSpy = vi.spyOn(mockStream.tracks[0], 'stop');
      mockGetUserMedia.mockResolvedValueOnce(mockStream);
      
      await audioService.requestPermission();
      
      expect(stopSpy).toHaveBeenCalled();
    });

    it('should return true if permission already granted', async () => {
      // First request
      await audioService.requestPermission();
      mockGetUserMedia.mockClear();
      
      // Second request should not call getUserMedia
      const result = await audioService.requestPermission();
      
      expect(result).toBe(true);
      expect(mockGetUserMedia).not.toHaveBeenCalled();
    });
  });

  describe('Recording', () => {
    it('should start recording', async () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      await audioService.startRecording();
      
      expect(mockProcessor.initialize).toHaveBeenCalled();
      expect(mockProcessor.startProcessing).toHaveBeenCalled();
      
      const status = audioService.getStatus();
      expect(status.state).toBe('recording');
      expect(status.isRecording).toBe(true);
      
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'recording',
        isRecording: true
      }));
    });

    it('should not start recording if already recording', async () => {
      await audioService.startRecording();
      mockProcessor.initialize.mockClear();
      mockProcessor.startProcessing.mockClear();
      
      await audioService.startRecording();
      
      expect(mockProcessor.initialize).not.toHaveBeenCalled();
      expect(mockProcessor.startProcessing).not.toHaveBeenCalled();
    });

    it('should initialize processor if not ready', async () => {
      mockProcessor.setStatus({ state: 'idle', audioLevel: 0 });
      
      await audioService.startRecording();
      
      expect(mockProcessor.initialize).toHaveBeenCalled();
      expect(mockProcessor.startProcessing).toHaveBeenCalled();
    });

    it('should not reinitialize if processor is ready', async () => {
      mockProcessor.setStatus({ state: 'ready', audioLevel: 0 });
      
      await audioService.startRecording();
      
      expect(mockProcessor.initialize).not.toHaveBeenCalled();
      expect(mockProcessor.startProcessing).toHaveBeenCalled();
    });

    it('should handle initialization errors', async () => {
      const error = new Error('Failed to initialize');
      mockProcessor.initialize.mockRejectedValueOnce(error);
      
      const errorHandler = vi.fn();
      const statusHandler = vi.fn();
      audioService.on('error', errorHandler);
      audioService.onStatusChange(statusHandler);
      
      await expect(audioService.startRecording()).rejects.toThrow('Failed to initialize');
      
      expect(errorHandler).toHaveBeenCalledWith(error);
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'failed',
        error: 'Failed to initialize'
      }));
    });
  });

  describe('Stop Recording', () => {
    beforeEach(async () => {
      await audioService.startRecording();
    });

    it('should stop recording', () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      audioService.stopRecording();
      
      expect(mockProcessor.stopProcessing).toHaveBeenCalled();
      
      const status = audioService.getStatus();
      expect(status.state).toBe('ready');
      expect(status.isRecording).toBe(false);
      expect(status.audioLevel).toBe(0);
      
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'ready',
        isRecording: false,
        audioLevel: 0
      }));
    });

    it('should not stop if not recording', () => {
      audioService.stopRecording();
      mockProcessor.stopProcessing.mockClear();
      
      audioService.stopRecording();
      
      expect(mockProcessor.stopProcessing).not.toHaveBeenCalled();
    });
  });

  describe('Audio Chunk Handling', () => {
    it('should forward audio chunks with frame count', async () => {
      const chunkHandler = vi.fn();
      audioService.onAudioChunk(chunkHandler);
      
      const mockChunk: AudioChunkData = {
        pcm16: new ArrayBuffer(1024),
        float32: new Float32Array(512)
      };
      
      // Emit chunk from processor
      mockProcessor.emit('audioChunk', mockChunk);
      
      expect(chunkHandler).toHaveBeenCalledWith(expect.objectContaining({
        pcm16: mockChunk.pcm16,
        float32: mockChunk.float32,
        frame_count: 1
      }));
      
      // Emit another chunk
      mockProcessor.emit('audioChunk', mockChunk);
      
      expect(chunkHandler).toHaveBeenCalledWith(expect.objectContaining({
        frame_count: 2
      }));
    });

    it('should increment frame counter for each chunk', async () => {
      const chunks: AudioChunkData[] = [];
      audioService.onAudioChunk(chunk => chunks.push(chunk));
      
      // Emit multiple chunks
      for (let i = 0; i < 5; i++) {
        mockProcessor.emit('audioChunk', {
          pcm16: new ArrayBuffer(1024),
          float32: new Float32Array(512)
        });
      }
      
      // Check frame counts
      expect(chunks[0].frame_count).toBe(1);
      expect(chunks[1].frame_count).toBe(2);
      expect(chunks[2].frame_count).toBe(3);
      expect(chunks[3].frame_count).toBe(4);
      expect(chunks[4].frame_count).toBe(5);
    });
  });

  describe('Processor Status Changes', () => {
    it('should map processor states to service states', () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      // Test state mappings
      const stateMappings = [
        { processor: 'idle', service: 'idle' },
        { processor: 'loading', service: 'initializing' },
        { processor: 'ready', service: 'ready' },
        { processor: 'processing', service: 'recording' },
        { processor: 'error', service: 'failed' }
      ];
      
      stateMappings.forEach(({ processor, service }) => {
        statusHandler.mockClear();
        
        mockProcessor.emit('statusChange', {
          state: processor,
          audioLevel: 0.5
        });
        
        expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
          state: service,
          audioLevel: 0.5
        }));
      });
    });

    it('should detect permission errors', () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      mockProcessor.emit('statusChange', {
        state: 'error',
        audioLevel: 0,
        error: 'Failed to access microphone'
      });
      
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'permission-denied',
        error: 'Failed to access microphone'
      }));
    });

    it('should maintain recording state when processor is ready', async () => {
      await audioService.startRecording();
      
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      // Processor goes to ready state
      mockProcessor.emit('statusChange', {
        state: 'ready',
        audioLevel: 0
      });
      
      // Should maintain recording state
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'recording',
        isRecording: true
      }));
    });
  });

  describe('Audio Level Changes', () => {
    it('should forward audio level changes', () => {
      const levelHandler = vi.fn();
      const statusHandler = vi.fn();
      
      audioService.on('levelChange', levelHandler);
      audioService.onStatusChange(statusHandler);
      
      mockProcessor.emit('levelChange', 0.75);
      
      expect(levelHandler).toHaveBeenCalledWith(0.75);
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        audioLevel: 0.75
      }));
    });
  });

  describe('Error Handling', () => {
    it('should handle processor errors', () => {
      const errorHandler = vi.fn();
      const statusHandler = vi.fn();
      
      audioService.on('error', errorHandler);
      audioService.onStatusChange(statusHandler);
      
      const error = new Error('Processor failed');
      mockProcessor.emit('error', error);
      
      expect(errorHandler).toHaveBeenCalledWith(error);
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'failed',
        error: 'Processor failed'
      }));
    });

    it('should handle AudioProcessorError with microphone access code', () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      const error = new AudioProcessorError(
        'Microphone access denied',
        AudioProcessorErrorCode.MICROPHONE_ACCESS_ERROR
      );
      
      mockProcessor.emit('error', error);
      
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'permission-denied',
        error: 'Microphone access denied'
      }));
      expect(audioService.hasPermission()).toBe(false);
    });

    it('should handle AudioProcessorError with other codes', () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      const error = new AudioProcessorError(
        'Worklet failed',
        AudioProcessorErrorCode.WORKLET_LOAD_ERROR
      );
      
      mockProcessor.emit('error', error);
      
      expect(statusHandler).toHaveBeenCalledWith(expect.objectContaining({
        state: 'failed',
        error: 'Worklet failed'
      }));
    });

    it('should handle errors in event listeners', () => {
      const faultyHandler = vi.fn(() => {
        throw new Error('Handler error');
      });
      const normalHandler = vi.fn();
      
      audioService.on('levelChange', faultyHandler);
      audioService.on('levelChange', normalHandler);
      
      // Console error spy
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // Emit event - should not throw
      expect(() => mockProcessor.emit('levelChange', 0.5)).not.toThrow();
      
      // Normal handler should still be called
      expect(normalHandler).toHaveBeenCalledWith(0.5);
      
      // Error should be logged
      expect(consoleSpy).toHaveBeenCalledWith(
        '[AudioService] Error in event listener for levelChange:',
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('Event Subscription', () => {
    it('should support multiple listeners', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();
      
      audioService.onStatusChange(handler1);
      audioService.onStatusChange(handler2);
      audioService.onAudioChunk(handler3);
      
      // Emit status change
      mockProcessor.emit('statusChange', {
        state: 'ready',
        audioLevel: 0.5
      });
      
      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
      expect(handler3).not.toHaveBeenCalled();
      
      // Emit audio chunk
      mockProcessor.emit('audioChunk', {
        pcm16: new ArrayBuffer(1024),
        float32: new Float32Array(512)
      });
      
      expect(handler3).toHaveBeenCalled();
    });

    it('should support unsubscribing', () => {
      const handler = vi.fn();
      const unsubscribe = audioService.onStatusChange(handler);
      
      // Emit event
      mockProcessor.emit('statusChange', {
        state: 'ready',
        audioLevel: 0.5
      });
      
      expect(handler).toHaveBeenCalledTimes(1);
      
      // Unsubscribe
      unsubscribe();
      handler.mockClear();
      
      // Emit another event
      mockProcessor.emit('statusChange', {
        state: 'idle',
        audioLevel: 0
      });
      
      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('Cleanup', () => {
    it('should cleanup on resetInstance', async () => {
      await audioService.startRecording();
      
      const cleanupSpy = vi.spyOn(mockProcessor, 'cleanup');
      
      AudioService.resetInstance();
      
      expect(cleanupSpy).toHaveBeenCalled();
      expect(mockProcessor.stopProcessing).toHaveBeenCalled();
    });

    it('should reset all state on cleanup', async () => {
      // Setup some state
      await audioService.startRecording();
      mockProcessor.emit('audioChunk', {
        pcm16: new ArrayBuffer(1024),
        float32: new Float32Array(512)
      });
      
      AudioService.resetInstance();
      
      // Get new instance
      const newService = AudioService.getInstance();
      const status = newService.getStatus();
      
      expect(status.state).toBe('idle');
      expect(status.isRecording).toBe(false);
      expect(status.frameCount).toBe(0);
      expect(newService.hasPermission()).toBe(false);
    });

    it('should unsubscribe from processor events', async () => {
      const handler = vi.fn();
      audioService.on('audioChunk', handler);
      
      AudioService.resetInstance();
      
      // Try to emit event from old processor
      mockProcessor.emit('audioChunk', {
        pcm16: new ArrayBuffer(1024),
        float32: new Float32Array(512)
      });
      
      // Handler should not be called after cleanup
      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing navigator.mediaDevices', async () => {
      // Remove mediaDevices
      Object.defineProperty(navigator, 'mediaDevices', {
        value: undefined,
        writable: true,
        configurable: true
      });
      
      const result = await audioService.requestPermission();
      
      expect(result).toBe(false);
      expect(audioService.getStatus().state).toBe('permission-denied');
    });

    it('should update frame count in status when recording starts', async () => {
      // Emit some chunks before recording
      for (let i = 0; i < 3; i++) {
        mockProcessor.emit('audioChunk', {
          pcm16: new ArrayBuffer(1024),
          float32: new Float32Array(512)
        });
      }
      
      await audioService.startRecording();
      
      const status = audioService.getStatus();
      expect(status.frameCount).toBe(3);
    });

    it('should handle rapid state changes', async () => {
      const statusHandler = vi.fn();
      audioService.onStatusChange(statusHandler);
      
      // Rapid state changes
      for (let i = 0; i < 10; i++) {
        await audioService.startRecording();
        audioService.stopRecording();
      }
      
      // Should have handled all state changes
      expect(statusHandler.mock.calls.length).toBeGreaterThan(0);
      
      // Final state should be consistent
      const status = audioService.getStatus();
      expect(status.state).toBe('ready');
      expect(status.isRecording).toBe(false);
    });
  });
});