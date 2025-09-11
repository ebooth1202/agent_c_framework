/**
 * Example test file showing how to use the mocks
 * This file demonstrates best practices for using our simple mocks
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  mockWebSocket,
  MockWebSocketConstructor,
  mockAudioContext,
  MockAudioContextConstructor,
  mockNavigator,
  MockAbortControllerConstructor,
  resetAllMocks,
} from './index';

describe('Mock Usage Examples', () => {
  beforeEach(() => {
    // Setup global mocks
    global.WebSocket = MockWebSocketConstructor as unknown as typeof WebSocket;
    global.AudioContext = MockAudioContextConstructor as unknown as typeof AudioContext;
    global.navigator = mockNavigator as unknown as Navigator;
    global.AbortController = MockAbortControllerConstructor as unknown as typeof AbortController;
  });

  afterEach(() => {
    // Reset all mocks after each test
    resetAllMocks();
    vi.restoreAllMocks();
  });

  describe('WebSocket Mock', () => {
    it('should track WebSocket instantiation', () => {
      const ws = new WebSocket('ws://test.example.com');
      expect(MockWebSocketConstructor).toHaveBeenCalledWith('ws://test.example.com');
      expect(ws).toBe(mockWebSocket);
    });

    it('should track send calls', () => {
      const ws = new WebSocket('ws://test.example.com');
      const message = JSON.stringify({ type: 'test', data: 'hello' });
      
      ws.send(message);
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(message);
      expect(mockWebSocket.send).toHaveBeenCalledTimes(1);
    });

    it('should allow simulating events', () => {
      const ws = new WebSocket('ws://test.example.com');
      const onMessage = vi.fn();
      
      // Set up event handler
      ws.onmessage = onMessage;
      
      // Simulate receiving a message
      const messageEvent = { data: JSON.stringify({ type: 'response' }) };
      mockWebSocket.onmessage(messageEvent);
      
      expect(onMessage).toHaveBeenCalledWith(messageEvent);
    });

    it('should track connection state', () => {
      const ws = new WebSocket('ws://test.example.com');
      
      // Check initial state
      expect(ws.readyState).toBe(WebSocket.OPEN);
      
      // Simulate closing
      mockWebSocket.readyState = WebSocket.CLOSED;
      expect(ws.readyState).toBe(WebSocket.CLOSED);
    });
  });

  describe('AudioContext Mock', () => {
    it('should track AudioContext creation', () => {
      const ctx = new AudioContext();
      expect(MockAudioContextConstructor).toHaveBeenCalled();
      expect(ctx).toBe(mockAudioContext);
    });

    it('should track node creation', () => {
      const ctx = new AudioContext();
      
      const gain = ctx.createGain();
      const buffer = ctx.createBuffer(2, 44100, 44100);
      const source = ctx.createBufferSource();
      
      expect(mockAudioContext.createGain).toHaveBeenCalled();
      expect(mockAudioContext.createBuffer).toHaveBeenCalledWith(2, 44100, 44100);
      expect(mockAudioContext.createBufferSource).toHaveBeenCalled();
      
      // Nodes can be used
      expect(gain.connect).toBeDefined();
      expect(source.start).toBeDefined();
    });

    it('should handle async operations', async () => {
      const ctx = new AudioContext();
      
      // Configure mock response
      mockAudioContext.resume.mockResolvedValue(undefined);
      
      await ctx.resume();
      
      expect(mockAudioContext.resume).toHaveBeenCalled();
    });
  });

  describe('MediaStream Mock', () => {
    it('should mock getUserMedia', async () => {
      const constraints = { audio: true, video: false };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      expect(mockNavigator.mediaDevices.getUserMedia).toHaveBeenCalledWith(constraints);
      expect(stream.getTracks()).toHaveLength(1);
      expect(stream.getAudioTracks()).toHaveLength(1);
    });

    it('should allow track manipulation', () => {
      const stream = mockNavigator.mediaDevices.getUserMedia({ audio: true });
      const tracks = stream.getTracks();
      
      tracks[0].stop();
      
      expect(tracks[0].stop).toHaveBeenCalled();
    });

    it('should handle getUserMedia rejection', async () => {
      // Configure mock to reject
      mockNavigator.mediaDevices.getUserMedia.mockRejectedValue(
        new Error('Permission denied')
      );
      
      await expect(
        navigator.mediaDevices.getUserMedia({ audio: true })
      ).rejects.toThrow('Permission denied');
    });
  });

  describe('AbortController Mock', () => {
    it('should track abort signals', () => {
      const controller = new AbortController();
      
      expect(controller.signal.aborted).toBe(false);
      
      controller.abort('User cancelled');
      
      expect(controller.signal.aborted).toBe(true);
      expect(controller.signal.reason).toBe('User cancelled');
    });
  });

  describe('Combined Usage', () => {
    it('should work with multiple mocks together', async () => {
      // Create audio context
      const ctx = new AudioContext();
      
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create source from stream
      const source = ctx.createMediaStreamSource(stream);
      
      // Create WebSocket
      const ws = new WebSocket('ws://audio.test');
      
      // Verify all mocks were called
      expect(MockAudioContextConstructor).toHaveBeenCalled();
      expect(mockNavigator.mediaDevices.getUserMedia).toHaveBeenCalled();
      expect(mockAudioContext.createMediaStreamSource).toHaveBeenCalledWith(stream);
      expect(MockWebSocketConstructor).toHaveBeenCalled();
      
      // All objects are mocked
      expect(source.connect).toBeDefined();
      expect(ws.send).toBeDefined();
    });
  });
});