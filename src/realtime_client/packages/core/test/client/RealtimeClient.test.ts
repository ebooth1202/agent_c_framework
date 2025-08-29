/**
 * Tests for RealtimeClient
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RealtimeClient } from '../../src/client/RealtimeClient';
import { MockWebSocket, mockWebSocketConstructor } from '@test/utils/mock-websocket';
import { sleep, waitFor, createMockAgentCEvent } from '@test/utils/test-helpers';

describe('RealtimeClient', () => {
  let client: RealtimeClient;
  let mockWS: any;

  beforeEach(() => {
    // Mock WebSocket globally
    mockWS = mockWebSocketConstructor();
    global.WebSocket = mockWS as any;
    
    // Create client instance
    client = new RealtimeClient({
      apiUrl: 'ws://localhost:8080/realtime',
      authToken: 'test-token',
      autoReconnect: false, // Disable for predictable tests
    });
  });

  afterEach(async () => {
    // Cleanup
    if (client) {
      await client.disconnect();
    }
    vi.clearAllMocks();
  });

  describe('Connection', () => {
    it('should connect to WebSocket server', async () => {
      const connectPromise = client.connect();
      
      // Get the mock WebSocket instance
      expect(mockWS).toHaveBeenCalledWith('ws://localhost:8080/realtime');
      const wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      
      // Simulate connection
      wsInstance.connect();
      
      await connectPromise;
      
      expect(client.isConnected()).toBe(true);
    });

    it('should handle connection errors', async () => {
      const connectPromise = client.connect();
      
      // Get the mock WebSocket instance
      const wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      
      // Simulate error
      wsInstance.simulateError(new Error('Connection failed'));
      
      await expect(connectPromise).rejects.toThrow('Connection failed');
      expect(client.isConnected()).toBe(false);
    });

    it('should disconnect cleanly', async () => {
      // Connect first
      const connectPromise = client.connect();
      const wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      wsInstance.connect();
      await connectPromise;
      
      // Now disconnect
      const disconnectPromise = client.disconnect();
      wsInstance.disconnect();
      await disconnectPromise;
      
      expect(client.isConnected()).toBe(false);
      expect(wsInstance.close).toHaveBeenCalled();
    });
  });

  describe('Message Handling', () => {
    let wsInstance: MockWebSocket;

    beforeEach(async () => {
      // Connect the client
      const connectPromise = client.connect();
      wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      wsInstance.connect();
      await connectPromise;
    });

    it('should emit events for received messages', async () => {
      const messageHandler = vi.fn();
      client.on('text_delta', messageHandler);
      
      // Simulate receiving a message
      const event = createMockAgentCEvent('text_delta', {
        content: 'Hello, world!',
        role: 'assistant',
      });
      
      wsInstance.receiveMessage(JSON.stringify(event));
      
      // Wait for event processing
      await sleep(10);
      
      expect(messageHandler).toHaveBeenCalledWith(expect.objectContaining({
        type: 'text_delta',
        content: 'Hello, world!',
        role: 'assistant',
      }));
    });

    it('should handle binary messages', async () => {
      const binaryHandler = vi.fn();
      client.on('audio_delta', binaryHandler);
      
      // Simulate receiving binary data
      const audioData = new ArrayBuffer(1024);
      wsInstance.receiveBinaryMessage(audioData);
      
      // Wait for event processing
      await sleep(10);
      
      expect(binaryHandler).toHaveBeenCalledWith(expect.objectContaining({
        data: audioData,
      }));
    });

    it('should send JSON messages', async () => {
      const message = {
        type: 'text_input',
        content: 'Test message',
      };
      
      await client.send(message);
      
      expect(wsInstance.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('should send binary data', async () => {
      const audioData = new ArrayBuffer(1024);
      
      await client.sendBinary(audioData);
      
      expect(wsInstance.send).toHaveBeenCalledWith(audioData);
    });
  });

  describe('Event Emitter', () => {
    it('should add and remove event listeners', () => {
      const handler = vi.fn();
      
      client.on('test_event', handler);
      client.emit('test_event' as any, { data: 'test' });
      
      expect(handler).toHaveBeenCalledWith({ data: 'test' });
      
      client.off('test_event', handler);
      client.emit('test_event' as any, { data: 'test2' });
      
      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should support once listeners', () => {
      const handler = vi.fn();
      
      client.once('test_event', handler);
      client.emit('test_event' as any, { data: 'test1' });
      client.emit('test_event' as any, { data: 'test2' });
      
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith({ data: 'test1' });
    });
  });

  describe('Auto Reconnect', () => {
    beforeEach(() => {
      // Create client with auto-reconnect enabled
      client = new RealtimeClient({
        apiUrl: 'ws://localhost:8080/realtime',
        authToken: 'test-token',
        autoReconnect: true,
        reconnectInterval: 100,
        maxReconnectAttempts: 3,
      });
    });

    it('should attempt to reconnect on disconnect', async () => {
      // Connect first
      const connectPromise = client.connect();
      const wsInstance1 = mockWS.mock.results[0].value as MockWebSocket;
      wsInstance1.connect();
      await connectPromise;
      
      // Simulate unexpected disconnect
      wsInstance1.disconnect();
      
      // Wait for reconnection attempt
      await sleep(150);
      
      // Should create a new WebSocket
      expect(mockWS).toHaveBeenCalledTimes(2);
      
      // Connect the new instance
      const wsInstance2 = mockWS.mock.results[1].value as MockWebSocket;
      wsInstance2.connect();
      
      await waitFor(() => client.isConnected());
      expect(client.isConnected()).toBe(true);
    });

    it('should stop reconnecting after max attempts', async () => {
      // Connect first
      const connectPromise = client.connect();
      const wsInstance1 = mockWS.mock.results[0].value as MockWebSocket;
      wsInstance1.connect();
      await connectPromise;
      
      // Simulate unexpected disconnect
      wsInstance1.disconnect();
      
      // Wait for all reconnection attempts (3 attempts * 100ms interval + buffer)
      await sleep(500);
      
      // Should have attempted max reconnections + 1 initial connection
      expect(mockWS).toHaveBeenCalledTimes(4); // 1 initial + 3 reconnection attempts
      
      // Should still be disconnected
      expect(client.isConnected()).toBe(false);
    });
  });
});