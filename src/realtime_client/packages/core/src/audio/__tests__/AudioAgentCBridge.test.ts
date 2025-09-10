/**
 * Tests for AudioAgentCBridge
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AudioAgentCBridge } from '../AudioAgentCBridge';
import { RealtimeClient } from '../../client/RealtimeClient';
import { mockWebSocketConstructor } from '../../test/mocks/mock-websocket';

describe('AudioAgentCBridge', () => {
  let bridge: AudioAgentCBridge;
  let mockClient: RealtimeClient;
  let mockWS: ReturnType<typeof mockWebSocketConstructor>;

  beforeEach(() => {
    // Mock WebSocket
    mockWS = mockWebSocketConstructor();
    global.WebSocket = mockWS as any;
    
    // Create mock client
    mockClient = new RealtimeClient({
      apiUrl: 'ws://localhost:8080/test',
      authToken: 'test-token',
      autoReconnect: false
    });
    
    // Get singleton instance
    bridge = AudioAgentCBridge.getInstance();
  });

  afterEach(() => {
    bridge.stop();
    AudioAgentCBridge.resetInstance();
    mockClient.destroy();
    vi.clearAllMocks();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = AudioAgentCBridge.getInstance();
      const instance2 = AudioAgentCBridge.getInstance();
      
      expect(instance1).toBe(instance2);
    });

    it('should reset instance properly', () => {
      const instance1 = AudioAgentCBridge.getInstance();
      AudioAgentCBridge.resetInstance();
      const instance2 = AudioAgentCBridge.getInstance();
      
      expect(instance1).not.toBe(instance2);
    });
  });

  describe('Initialization', () => {
    it('should initialize with client and default config', () => {
      bridge.initialize(mockClient);
      
      expect(bridge['client']).toBe(mockClient);
      expect(bridge['config'].respectTurnState).toBe(true);
      expect(bridge['config'].bufferSize).toBe(4096);
    });

    it('should initialize with custom config', () => {
      bridge.initialize(mockClient, {
        respectTurnState: false,
        bufferSize: 8192,
        sendInterval: 50
      });
      
      expect(bridge['config'].respectTurnState).toBe(false);
      expect(bridge['config'].bufferSize).toBe(8192);
      expect(bridge['config'].sendInterval).toBe(50);
    });

    it('should register event listeners on initialization', () => {
      const onSpy = vi.spyOn(mockClient, 'on');
      
      bridge.initialize(mockClient);
      
      expect(onSpy).toHaveBeenCalledWith('user_turn_start', expect.any(Function));
      expect(onSpy).toHaveBeenCalledWith('user_turn_end', expect.any(Function));
      expect(onSpy).toHaveBeenCalledWith('agent_turn_start', expect.any(Function));
      expect(onSpy).toHaveBeenCalledWith('agent_turn_end', expect.any(Function));
    });

    it('should throw error if initialized without client', () => {
      expect(() => bridge.initialize(null as any)).toThrow();
    });
  });

  describe('Turn State Management', () => {
    beforeEach(() => {
      bridge.initialize(mockClient);
    });

    it('should update turn state on user_turn_start', () => {
      expect(bridge['currentUserHasTurn']).toBe(false);
      
      mockClient.emit('user_turn_start', { type: 'user_turn_start' });
      
      expect(bridge['currentUserHasTurn']).toBe(true);
    });

    it('should update turn state on user_turn_end', () => {
      bridge['currentUserHasTurn'] = true;
      
      mockClient.emit('user_turn_end', { type: 'user_turn_end' });
      
      expect(bridge['currentUserHasTurn']).toBe(false);
    });

    it('should update agent turn state on agent_turn_start', () => {
      expect(bridge['agentIsSpeaking']).toBe(false);
      
      mockClient.emit('agent_turn_start', { type: 'agent_turn_start' });
      
      expect(bridge['agentIsSpeaking']).toBe(true);
    });

    it('should update agent turn state on agent_turn_end', () => {
      bridge['agentIsSpeaking'] = true;
      
      mockClient.emit('agent_turn_end', { type: 'agent_turn_end' });
      
      expect(bridge['agentIsSpeaking']).toBe(false);
    });
  });

  describe('Audio Processing', () => {
    beforeEach(async () => {
      bridge.initialize(mockClient);
      
      // Connect client
      const connectPromise = mockClient.connect();
      const wsInstance = mockWS.lastInstance();
      wsInstance.readyState = 1; // OPEN
      wsInstance.simulateOpen();
      await connectPromise;
    });

    it('should process audio data when user has turn', () => {
      bridge['currentUserHasTurn'] = true;
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      
      const audioData = new ArrayBuffer(256);
      bridge.processAudioData(audioData);
      
      // Should accumulate in buffer
      expect(bridge['audioBuffer'].length).toBeGreaterThan(0);
    });

    it('should not process audio when user does not have turn', () => {
      bridge['currentUserHasTurn'] = false;
      bridge['config'].respectTurnState = true;
      
      const audioData = new ArrayBuffer(256);
      bridge.processAudioData(audioData);
      
      // Should not accumulate
      expect(bridge['audioBuffer'].length).toBe(0);
    });

    it('should process audio regardless of turn when respectTurnState is false', () => {
      bridge['currentUserHasTurn'] = false;
      bridge['config'].respectTurnState = false;
      
      const audioData = new ArrayBuffer(256);
      bridge.processAudioData(audioData);
      
      // Should accumulate
      expect(bridge['audioBuffer'].length).toBeGreaterThan(0);
    });

    it('should send buffered audio when buffer is full', () => {
      bridge['currentUserHasTurn'] = true;
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      
      // Fill buffer beyond threshold
      const chunkSize = 1024;
      for (let i = 0; i < 5; i++) {
        const audioData = new ArrayBuffer(chunkSize);
        bridge.processAudioData(audioData);
      }
      
      // Should have sent data
      expect(sendSpy).toHaveBeenCalled();
    });

    it('should clear buffer after sending', () => {
      bridge['currentUserHasTurn'] = true;
      
      // Fill buffer
      const audioData = new ArrayBuffer(bridge['config'].bufferSize + 100);
      bridge.processAudioData(audioData);
      
      // Trigger send
      bridge['sendBufferedAudio']();
      
      // Buffer should be cleared
      expect(bridge['audioBuffer'].length).toBe(0);
    });
  });

  describe('Start/Stop', () => {
    beforeEach(() => {
      bridge.initialize(mockClient);
    });

    it('should start processing', () => {
      bridge.start();
      
      expect(bridge['isProcessing']).toBe(true);
    });

    it('should stop processing', () => {
      bridge.start();
      bridge.stop();
      
      expect(bridge['isProcessing']).toBe(false);
    });

    it('should clear interval on stop', () => {
      bridge.start();
      const intervalId = bridge['sendIntervalId'];
      
      bridge.stop();
      
      expect(bridge['sendIntervalId']).toBeNull();
    });

    it('should send remaining buffer on stop', () => {
      bridge['currentUserHasTurn'] = true;
      bridge.start();
      
      // Add some data to buffer
      const audioData = new ArrayBuffer(256);
      bridge.processAudioData(audioData);
      
      const sendSpy = vi.spyOn(bridge as any, 'sendBufferedAudio');
      
      bridge.stop();
      
      expect(sendSpy).toHaveBeenCalled();
    });

    it('should handle multiple start calls', () => {
      bridge.start();
      const firstIntervalId = bridge['sendIntervalId'];
      
      bridge.start();
      const secondIntervalId = bridge['sendIntervalId'];
      
      // Should not create multiple intervals
      expect(firstIntervalId).toBe(secondIntervalId);
    });
  });

  describe('Buffer Management', () => {
    beforeEach(() => {
      bridge.initialize(mockClient, { bufferSize: 1024 });
      bridge['currentUserHasTurn'] = true;
    });

    it('should accumulate audio in buffer', () => {
      const chunk1 = new ArrayBuffer(256);
      const chunk2 = new ArrayBuffer(256);
      
      bridge.processAudioData(chunk1);
      bridge.processAudioData(chunk2);
      
      expect(bridge['audioBuffer'].length).toBe(512);
    });

    it('should combine buffer into single ArrayBuffer for sending', () => {
      const chunk1 = new Uint8Array([1, 2, 3, 4]);
      const chunk2 = new Uint8Array([5, 6, 7, 8]);
      
      bridge['audioBuffer'].push(...chunk1);
      bridge['audioBuffer'].push(...chunk2);
      
      const combined = bridge['getCombinedBuffer']();
      const view = new Uint8Array(combined);
      
      expect(view.length).toBe(8);
      expect(Array.from(view)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
    });

    it('should respect buffer size limit', () => {
      const sendSpy = vi.spyOn(bridge as any, 'sendBufferedAudio');
      
      // Add data exceeding buffer size
      const largeChunk = new ArrayBuffer(2048);
      bridge.processAudioData(largeChunk);
      
      // Should trigger send
      expect(sendSpy).toHaveBeenCalled();
    });

    it('should handle empty buffer', () => {
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      
      bridge['sendBufferedAudio']();
      
      // Should not send empty buffer
      expect(sendSpy).not.toHaveBeenCalled();
    });
  });

  describe('Connection State Handling', () => {
    beforeEach(() => {
      bridge.initialize(mockClient);
    });

    it('should only send when client is connected', async () => {
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      
      // Try to send while disconnected
      bridge['audioBuffer'] = [1, 2, 3, 4];
      bridge['sendBufferedAudio']();
      
      expect(sendSpy).not.toHaveBeenCalled();
      
      // Connect client
      const connectPromise = mockClient.connect();
      const wsInstance = mockWS.lastInstance();
      wsInstance.readyState = 1; // OPEN
      wsInstance.simulateOpen();
      await connectPromise;
      
      // Now should be able to send
      bridge['audioBuffer'] = [1, 2, 3, 4];
      bridge['sendBufferedAudio']();
      
      expect(sendSpy).toHaveBeenCalled();
    });

    it('should handle disconnection during processing', async () => {
      // Connect first
      const connectPromise = mockClient.connect();
      const wsInstance = mockWS.lastInstance();
      wsInstance.readyState = 1;
      wsInstance.simulateOpen();
      await connectPromise;
      
      bridge.start();
      bridge['currentUserHasTurn'] = true;
      
      // Add audio data
      bridge.processAudioData(new ArrayBuffer(256));
      
      // Disconnect
      mockClient.disconnect();
      
      // Try to send
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      bridge['sendBufferedAudio']();
      
      // Should not send when disconnected
      expect(sendSpy).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    beforeEach(async () => {
      bridge.initialize(mockClient);
      
      // Connect client
      const connectPromise = mockClient.connect();
      const wsInstance = mockWS.lastInstance();
      wsInstance.readyState = 1;
      wsInstance.simulateOpen();
      await connectPromise;
    });

    it('should handle send errors gracefully', () => {
      bridge['currentUserHasTurn'] = true;
      
      // Mock sendBinaryFrame to throw
      vi.spyOn(mockClient, 'sendBinaryFrame').mockImplementation(() => {
        throw new Error('Send failed');
      });
      
      const errorHandler = vi.fn();
      bridge.on('error', errorHandler);
      
      // Add data and try to send
      bridge.processAudioData(new ArrayBuffer(256));
      bridge['sendBufferedAudio']();
      
      expect(errorHandler).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should continue processing after errors', () => {
      bridge['currentUserHasTurn'] = true;
      bridge.start();
      
      // Mock sendBinaryFrame to throw once, then succeed
      const sendSpy = vi.spyOn(mockClient, 'sendBinaryFrame');
      sendSpy.mockImplementationOnce(() => {
        throw new Error('Send failed');
      });
      
      // First send fails
      bridge.processAudioData(new ArrayBuffer(256));
      bridge['sendBufferedAudio']();
      
      // Should clear buffer even on error
      expect(bridge['audioBuffer'].length).toBe(0);
      
      // Second send should work
      bridge.processAudioData(new ArrayBuffer(256));
      bridge['sendBufferedAudio']();
      
      expect(sendSpy).toHaveBeenCalledTimes(2);
    });
  });

  describe('Configuration Options', () => {
    it('should respect custom send interval', () => {
      vi.useFakeTimers();
      
      bridge.initialize(mockClient, { sendInterval: 100 });
      bridge.start();
      
      const sendSpy = vi.spyOn(bridge as any, 'sendBufferedAudio');
      
      vi.advanceTimersByTime(100);
      expect(sendSpy).toHaveBeenCalledTimes(1);
      
      vi.advanceTimersByTime(100);
      expect(sendSpy).toHaveBeenCalledTimes(2);
      
      vi.useRealTimers();
    });

    it('should handle zero send interval', () => {
      bridge.initialize(mockClient, { sendInterval: 0 });
      bridge.start();
      
      // Should still create interval with minimum value
      expect(bridge['sendIntervalId']).not.toBeNull();
    });

    it('should handle negative buffer size', () => {
      bridge.initialize(mockClient, { bufferSize: -1 });
      
      // Should use default or minimum value
      expect(bridge['config'].bufferSize).toBeGreaterThan(0);
    });
  });

  describe('Event Emitter Integration', () => {
    beforeEach(() => {
      bridge.initialize(mockClient);
    });

    it('should emit processing events', () => {
      const startHandler = vi.fn();
      const stopHandler = vi.fn();
      
      bridge.on('processing-started', startHandler);
      bridge.on('processing-stopped', stopHandler);
      
      bridge.start();
      expect(startHandler).toHaveBeenCalled();
      
      bridge.stop();
      expect(stopHandler).toHaveBeenCalled();
    });

    it('should emit data-sent events', async () => {
      const dataSentHandler = vi.fn();
      bridge.on('data-sent', dataSentHandler);
      
      // Connect client
      const connectPromise = mockClient.connect();
      const wsInstance = mockWS.lastInstance();
      wsInstance.readyState = 1;
      wsInstance.simulateOpen();
      await connectPromise;
      
      bridge['currentUserHasTurn'] = true;
      bridge['audioBuffer'] = [1, 2, 3, 4];
      bridge['sendBufferedAudio']();
      
      expect(dataSentHandler).toHaveBeenCalledWith(expect.objectContaining({
        size: 4
      }));
    });
  });

  describe('Cleanup', () => {
    it('should cleanup event listeners on destroy', () => {
      bridge.initialize(mockClient);
      const offSpy = vi.spyOn(mockClient, 'off');
      
      bridge.destroy();
      
      expect(offSpy).toHaveBeenCalledWith('user_turn_start', expect.any(Function));
      expect(offSpy).toHaveBeenCalledWith('user_turn_end', expect.any(Function));
      expect(offSpy).toHaveBeenCalledWith('agent_turn_start', expect.any(Function));
      expect(offSpy).toHaveBeenCalledWith('agent_turn_end', expect.any(Function));
    });

    it('should stop processing on destroy', () => {
      bridge.initialize(mockClient);
      bridge.start();
      
      bridge.destroy();
      
      expect(bridge['isProcessing']).toBe(false);
      expect(bridge['sendIntervalId']).toBeNull();
    });

    it('should clear buffer on destroy', () => {
      bridge.initialize(mockClient);
      bridge['audioBuffer'] = [1, 2, 3, 4];
      
      bridge.destroy();
      
      expect(bridge['audioBuffer'].length).toBe(0);
    });

    it('should reset client reference on destroy', () => {
      bridge.initialize(mockClient);
      
      bridge.destroy();
      
      expect(bridge['client']).toBeNull();
    });
  });
});