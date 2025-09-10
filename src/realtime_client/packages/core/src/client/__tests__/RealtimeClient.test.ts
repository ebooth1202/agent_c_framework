/**
 * Tests for RealtimeClient
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RealtimeClient } from '../RealtimeClient';
import { MockWebSocket, mockWebSocketConstructor } from '../../test/mocks/mock-websocket';

// Helper functions
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const createMockAgentCEvent = (type: string, data: any) => ({
  type,
  ...data
});

describe('RealtimeClient', () => {
  let client: RealtimeClient;
  let mockWS: ReturnType<typeof mockWebSocketConstructor>;

  beforeEach(() => {
    // Mock WebSocket globally
    mockWS = mockWebSocketConstructor();
    global.WebSocket = mockWS as any;
    
    // Create client instance with proper RealtimeClientConfig
    client = new RealtimeClient({
      apiUrl: 'ws://localhost:8080/realtime',
      authToken: 'test-token',
      autoReconnect: false, // Disable for predictable tests
    });
  });

  afterEach(async () => {
    // Cleanup
    if (client) {
      client.disconnect();
      client.destroy();
    }
    vi.clearAllMocks();
  });

  describe('Connection', () => {
    it('should connect to WebSocket server', async () => {
      const connectPromise = client.connect();
      
      // Get the mock WebSocket instance - includes token in URL
      // WebSocketManager passes protocols parameter (which may be undefined)
      expect(mockWS).toHaveBeenCalled();
      expect(mockWS).toHaveBeenCalledTimes(1);
      
      // Check the arguments passed to the WebSocket constructor
      const wsCall = mockWS.mock.calls[0];
      expect(wsCall[0]).toBe('ws://localhost:8080/realtime/api/rt/ws?token=test-token');
      
      // The WebSocket constructor can be called with 1 or 2 arguments
      // If protocols is undefined, it may only pass 1 argument
      if (wsCall.length === 2) {
        expect(wsCall[1]).toBeUndefined();
      }
      const wsInstance = mockWS.lastInstance();
      
      // Trigger the open event through the onopen handler
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      
      await connectPromise;
      
      expect(client.isConnected()).toBe(true);
    });

    it('should handle connection errors', async () => {
      const connectPromise = client.connect();
      
      // Get the mock WebSocket instance
      const wsInstance = mockWS.lastInstance();
      
      // Trigger error through the onerror handler
      if (wsInstance.onerror) {
        wsInstance.onerror({ type: 'error', target: wsInstance } as Event);
      }
      
      // Then trigger close
      if (wsInstance.onclose) {
        wsInstance.onclose({ 
          type: 'close', 
          target: wsInstance,
          code: 1006,
          reason: 'Connection failed'
        } as CloseEvent);
      }
      
      await expect(connectPromise).rejects.toThrow('Failed to connect');
      expect(client.isConnected()).toBe(false);
    });

    it('should disconnect cleanly', async () => {
      // Connect first
      const connectPromise = client.connect();
      const wsInstance = mockWS.lastInstance();
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      expect(client.isConnected()).toBe(true);
      
      // Now disconnect - this calls wsManager.disconnect which calls ws.close
      client.disconnect();
      
      // Check that client is disconnected
      expect(client.isConnected()).toBe(false);
      // The WebSocketManager should have called close on the WebSocket
      // Note: The actual close call happens, but we verify the state change
    });
  });

  describe('Message Handling', () => {
    let wsInstance: MockWebSocket;

    beforeEach(async () => {
      // Connect the client
      const connectPromise = client.connect();
      wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      
      // Set readyState to OPEN to simulate connected state
      wsInstance.readyState = MockWebSocket.OPEN;
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      // Verify connection is established
      expect(client.isConnected()).toBe(true);
    });

    it('should emit events for received messages', async () => {
      const messageHandler = vi.fn();
      client.on('text_delta', messageHandler);
      
      // Simulate receiving a message through onmessage handler
      const event = createMockAgentCEvent('text_delta', {
        content: 'Hello, world!',
        role: 'assistant',
      });
      
      if (wsInstance.onmessage) {
        wsInstance.onmessage({
          type: 'message',
          target: wsInstance,
          data: JSON.stringify(event)
        } as MessageEvent);
      }
      
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
      client.on('audio:output', binaryHandler);
      
      // Simulate receiving binary data through onmessage handler
      const audioData = new ArrayBuffer(1024);
      
      if (wsInstance.onmessage) {
        wsInstance.onmessage({
          type: 'message',
          target: wsInstance,
          data: audioData
        } as MessageEvent);
      }
      
      // Wait for event processing
      await sleep(10);
      
      expect(binaryHandler).toHaveBeenCalledWith(audioData);
    });

    it('should send text messages', async () => {
      const testMessage = 'Test message';
      
      // Ensure WebSocket is in OPEN state
      expect(wsInstance.readyState).toBe(MockWebSocket.OPEN);
      
      client.sendText(testMessage);
      
      expect(wsInstance.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'text_input',
        text: testMessage
      }));
    });

    it('should send binary data', async () => {
      const audioData = new ArrayBuffer(1024);
      
      // Ensure WebSocket is in OPEN state
      expect(wsInstance.readyState).toBe(MockWebSocket.OPEN);
      
      client.sendBinaryFrame(audioData);
      
      expect(wsInstance.send).toHaveBeenCalledWith(audioData);
    });
  });

  describe('Event Emitter', () => {
    it('should add and remove event listeners', () => {
      const handler = vi.fn();
      
      // Connect to make event emitter work properly
      client.on('connected', handler);
      client.emit('connected', undefined);
      
      expect(handler).toHaveBeenCalledWith(undefined);
      
      client.off('connected', handler);
      handler.mockClear();
      client.emit('connected', undefined);
      
      expect(handler).not.toHaveBeenCalled();
    });

    it('should support once listeners', () => {
      const handler = vi.fn();
      
      client.once('connected', handler);
      client.emit('connected', undefined);
      client.emit('connected', undefined);
      
      expect(handler).toHaveBeenCalledTimes(1);
    });
  });

  describe('Auto Reconnect', () => {
    beforeEach(() => {
      // Create client with auto-reconnect enabled
      client = new RealtimeClient({
        apiUrl: 'ws://localhost:8080/realtime',
        authToken: 'test-token',
        autoReconnect: true,
        reconnection: {
          maxAttempts: 3,
          delay: 100,
          maxDelay: 1000,
          backoffMultiplier: 1.5
        }
      });
    });

    it('should emit reconnecting event on unexpected disconnect', async () => {
      const reconnectingHandler = vi.fn();
      client.on('reconnecting', reconnectingHandler);
      
      // Connect first
      const connectPromise = client.connect();
      const wsInstance = mockWS.lastInstance();
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      // Simulate unexpected disconnect
      if (wsInstance.onclose) {
        wsInstance.onclose({
          type: 'close',
          target: wsInstance,
          code: 1006, // Abnormal closure
          reason: 'Connection lost'
        } as CloseEvent);
      }
      
      // Wait for reconnection logic to trigger
      await sleep(50);
      
      // Should have emitted reconnecting event
      expect(reconnectingHandler).toHaveBeenCalled();
    });

    it('should not reconnect on clean disconnect', async () => {
      const reconnectingHandler = vi.fn();
      client.on('reconnecting', reconnectingHandler);
      
      // Connect first
      const connectPromise = client.connect();
      const wsInstance = mockWS.lastInstance();
      
      // Set readyState to OPEN
      wsInstance.readyState = MockWebSocket.OPEN;
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      expect(client.isConnected()).toBe(true);
      
      // Simulate clean disconnect (code 1000)
      wsInstance.readyState = MockWebSocket.CLOSED;
      if (wsInstance.onclose) {
        wsInstance.onclose({
          type: 'close',
          target: wsInstance,
          code: 1000, // Normal closure
          reason: 'Normal closure'
        } as CloseEvent);
      }
      
      // Wait to ensure no reconnection attempt
      await sleep(200);
      
      // Should NOT have emitted reconnecting event
      expect(reconnectingHandler).not.toHaveBeenCalled();
      expect(client.isConnected()).toBe(false);
    });
  });
});