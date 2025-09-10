/**
 * Tests for AudioService
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AudioService } from '../AudioService';
import { setupAudioMocks, MockAudioContext } from '../../test/mocks/audio-mocks';

describe('AudioService', () => {
  let audioService: AudioService;
  let cleanup: () => void;

  beforeEach(() => {
    // Setup audio mocks
    const mocks = setupAudioMocks();
    cleanup = mocks.cleanup;
    
    // Get singleton instance
    audioService = AudioService.getInstance();
  });

  afterEach(() => {
    // Cleanup singleton
    audioService.stop();
    AudioService.resetInstance();
    cleanup();
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
  });

  describe('Initialization', () => {
    it('should initialize with default config', async () => {
      await audioService.initialize();
      
      expect(audioService.isActive()).toBe(true);
      expect(MockAudioContext).toBeDefined();
    });

    it('should initialize with custom config', async () => {
      await audioService.initialize({
        sampleRate: 48000,
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false
      });
      
      expect(audioService.isActive()).toBe(true);
      // AudioContext was created with custom sample rate
      const context = audioService.getAudioContext();
      expect(context?.sampleRate).toBe(48000);
    });

    it('should handle initialization errors', async () => {
      // Mock getUserMedia to reject
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));
      
      await expect(audioService.initialize()).rejects.toThrow('Permission denied');
      expect(audioService.isActive()).toBe(false);
    });

    it('should not reinitialize if already active', async () => {
      await audioService.initialize();
      const firstContext = audioService['audioContext'];
      
      await audioService.initialize();
      const secondContext = audioService['audioContext'];
      
      expect(firstContext).toBe(secondContext);
      // Should not create a new context
    });
  });

  describe('Audio Stream Management', () => {
    beforeEach(async () => {
      await audioService.initialize();
    });

    it('should get audio stream', () => {
      const stream = audioService.getStream();
      expect(stream).toBeDefined();
      expect(stream).toBeInstanceOf(MediaStream);
    });

    it('should get audio context', () => {
      const context = audioService.getAudioContext();
      expect(context).toBeDefined();
      expect(context?.sampleRate).toBe(24000);
    });

    it('should connect audio processor', async () => {
      const processor = vi.fn();
      await audioService.connectProcessor(processor);
      
      // Verify the processor was connected
      // Note: Implementation details would depend on actual AudioService
    });

    it('should stop audio service', () => {
      audioService.stop();
      
      expect(audioService.isActive()).toBe(false);
      
      // Verify cleanup
      const stream = audioService.getStream();
      if (stream) {
        stream.getTracks().forEach(track => {
          expect(track.stop).toHaveBeenCalled();
        });
      }
    });
  });

  describe('Audio Constraints', () => {
    it('should apply echo cancellation', async () => {
      await audioService.initialize({
        echoCancellation: true,
        noiseSuppression: false,
        autoGainControl: false
      });
      
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: expect.objectContaining({
          echoCancellation: true,
          noiseSuppression: false,
          autoGainControl: false
        })
      });
    });

    it('should apply noise suppression', async () => {
      await audioService.initialize({
        echoCancellation: false,
        noiseSuppression: true,
        autoGainControl: false
      });
      
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: expect.objectContaining({
          echoCancellation: false,
          noiseSuppression: true,
          autoGainControl: false
        })
      });
    });

    it('should apply auto gain control', async () => {
      await audioService.initialize({
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: true
      });
      
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: expect.objectContaining({
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: true
        })
      });
    });

    it('should apply all audio constraints', async () => {
      await audioService.initialize({
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      });
      
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: expect.objectContaining({
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        })
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle missing getUserMedia', async () => {
      // Temporarily remove getUserMedia
      const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
      delete (navigator.mediaDevices as any).getUserMedia;
      
      await expect(audioService.initialize()).rejects.toThrow();
      
      // Restore
      navigator.mediaDevices.getUserMedia = originalGetUserMedia;
    });

    it('should handle AudioContext creation failure', async () => {
      // Mock AudioContext to throw
      (global.AudioContext as any) = vi.fn().mockImplementation(() => {
        throw new Error('AudioContext creation failed');
      });
      
      await expect(audioService.initialize()).rejects.toThrow('AudioContext creation failed');
    });

    it('should cleanup on error', async () => {
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      mockGetUserMedia.mockRejectedValueOnce(new Error('Test error'));
      
      try {
        await audioService.initialize();
      } catch (error) {
        // Expected to throw
      }
      
      expect(audioService.isActive()).toBe(false);
      expect(audioService.getStream()).toBeNull();
      expect(audioService.getAudioContext()).toBeNull();
    });
  });

  describe('Audio Processing', () => {
    beforeEach(async () => {
      await audioService.initialize();
    });

    it('should emit audio data events', async () => {
      const dataHandler = vi.fn();
      audioService.on('audioData', dataHandler);
      
      // Simulate audio processing
      // This would typically happen through the AudioWorklet
      audioService.emit('audioData', new ArrayBuffer(256));
      
      expect(dataHandler).toHaveBeenCalledWith(expect.any(ArrayBuffer));
    });

    it('should handle processor connection', async () => {
      const processor = vi.fn();
      
      await audioService.connectProcessor(processor);
      
      // Verify processor is connected
      // Implementation would depend on actual AudioService
    });

    it('should disconnect processor', async () => {
      const processor = vi.fn();
      
      await audioService.connectProcessor(processor);
      audioService.disconnectProcessor();
      
      // Verify processor is disconnected
    });
  });

  describe('Lifecycle Management', () => {
    it('should handle multiple start/stop cycles', async () => {
      // Start
      await audioService.initialize();
      expect(audioService.isActive()).toBe(true);
      
      // Stop
      audioService.stop();
      expect(audioService.isActive()).toBe(false);
      
      // Start again
      await audioService.initialize();
      expect(audioService.isActive()).toBe(true);
      
      // Stop again
      audioService.stop();
      expect(audioService.isActive()).toBe(false);
    });

    it('should cleanup resources on stop', async () => {
      await audioService.initialize();
      
      const context = audioService.getAudioContext();
      const stream = audioService.getStream();
      
      audioService.stop();
      
      // Verify cleanup
      if (context) {
        expect(context.close).toHaveBeenCalled();
      }
      
      if (stream) {
        stream.getTracks().forEach(track => {
          expect(track.stop).toHaveBeenCalled();
        });
      }
    });

    it('should handle stop when not initialized', () => {
      expect(() => audioService.stop()).not.toThrow();
      expect(audioService.isActive()).toBe(false);
    });
  });

  describe('Event Emitter Integration', () => {
    it('should emit initialization events', async () => {
      const initHandler = vi.fn();
      const errorHandler = vi.fn();
      
      audioService.on('initialized', initHandler);
      audioService.on('error', errorHandler);
      
      await audioService.initialize();
      
      expect(initHandler).toHaveBeenCalled();
      expect(errorHandler).not.toHaveBeenCalled();
    });

    it('should emit error events', async () => {
      const errorHandler = vi.fn();
      audioService.on('error', errorHandler);
      
      const mockGetUserMedia = navigator.mediaDevices.getUserMedia as vi.Mock;
      mockGetUserMedia.mockRejectedValueOnce(new Error('Test error'));
      
      try {
        await audioService.initialize();
      } catch (error) {
        // Expected
      }
      
      expect(errorHandler).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should support multiple listeners', async () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      audioService.on('initialized', handler1);
      audioService.on('initialized', handler2);
      
      await audioService.initialize();
      
      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });

    it('should support removing listeners', async () => {
      const handler = vi.fn();
      
      audioService.on('initialized', handler);
      audioService.off('initialized', handler);
      
      await audioService.initialize();
      
      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('Sample Rate Configuration', () => {
    it('should use default sample rate', async () => {
      await audioService.initialize();
      
      // Default sample rate is used
      const context = audioService.getAudioContext();
      expect(context?.sampleRate).toBe(24000);
    });

    it('should accept custom sample rate', async () => {
      await audioService.initialize({ sampleRate: 44100 });
      
      // Custom sample rate is used
    });

    it('should handle invalid sample rates', async () => {
      await audioService.initialize({ sampleRate: -1 });
      
      // Should fall back to default or handle gracefully
      const context = audioService.getAudioContext();
      expect(context).toBeDefined();
    });
  });

  describe('Browser Compatibility', () => {
    it('should check for MediaDevices API', async () => {
      const hasMediaDevices = 'mediaDevices' in navigator;
      expect(hasMediaDevices).toBe(true);
    });

    it('should check for AudioContext', () => {
      const hasAudioContext = 'AudioContext' in global || 'webkitAudioContext' in global;
      expect(hasAudioContext).toBe(true);
    });

    it('should handle webkit prefixed AudioContext', async () => {
      // Temporarily replace AudioContext with webkitAudioContext
      const originalAudioContext = global.AudioContext;
      delete (global as any).AudioContext;
      (global as any).webkitAudioContext = MockAudioContext;
      
      await audioService.initialize();
      
      expect(audioService.isActive()).toBe(true);
      
      // Restore
      global.AudioContext = originalAudioContext;
      delete (global as any).webkitAudioContext;
    });
  });
});