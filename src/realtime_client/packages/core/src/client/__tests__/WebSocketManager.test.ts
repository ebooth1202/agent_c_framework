/**
 * Comprehensive tests for WebSocketManager
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { WebSocketManager } from '../WebSocketManager';
import { MockWebSocket, mockWebSocketConstructor } from '../../test/mocks/mock-websocket';

// Helper functions
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

describe('WebSocketManager', () => {
  let manager: WebSocketManager;
  let mockWS: ReturnType<typeof mockWebSocketConstructor>;
  let wsInstance: MockWebSocket;
  let callbacks: any;

  beforeEach(() => {
    // Mock WebSocket globally
    mockWS = mockWebSocketConstructor();
    global.WebSocket = mockWS as any;
    
    // Create callbacks
    callbacks = {
      onOpen: vi.fn(),
      onClose: vi.fn(),
      onError: vi.fn(),
      onMessage: vi.fn()
    };
    
    // Create manager instance
    manager = new WebSocketManager({
      url: 'ws://localhost:8080/test',
      protocols: undefined,
      binaryType: 'arraybuffer'
    }, callbacks);
  });

  afterEach(() => {
    manager.disconnect();
    vi.clearAllMocks();
  });

  describe('Connection Management', () => {
    it('should create WebSocket with correct parameters', () => {
      manager.connect();
      
      expect(mockWS).toHaveBeenCalledWith('ws://localhost:8080/test', undefined);
      expect(mockWS).toHaveBeenCalledTimes(1);
    });

    it('should set binaryType on connection', () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      expect(wsInstance.binaryType).toBe('arraybuffer');
    });

    it('should handle connection with protocols', () => {
      const managerWithProtocols = new WebSocketManager({
        url: 'ws://localhost:8080/test',
        protocols: ['protocol1', 'protocol2'],
        binaryType: 'blob'
      });

      managerWithProtocols.connect();
      
      expect(mockWS).toHaveBeenCalledWith('ws://localhost:8080/test', ['protocol1', 'protocol2']);
      
      const instance = mockWS.lastInstance();
      expect(instance.binaryType).toBe('blob');
      
      managerWithProtocols.disconnect();
    });

    it('should call onOpen callback when WebSocket opens', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      // Simulate open event
      wsInstance.simulateOpen();
      
      await sleep(10);
      
      expect(callbacks.onOpen).toHaveBeenCalled();
    });

    it('should call onClose callback when WebSocket closes', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      // Simulate close event
      wsInstance.simulateClose(1000, 'Normal closure');
      
      await sleep(10);
      
      expect(callbacks.onClose).toHaveBeenCalled();
    });

    it('should call onError callback on WebSocket error', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      // Simulate error event
      wsInstance.simulateError('Connection failed');
      
      await sleep(10);
      
      expect(callbacks.onError).toHaveBeenCalled();
    });

    it('should handle multiple connections correctly', () => {
      // First connection
      manager.connect();
      const firstInstance = mockWS.lastInstance();
      
      // Second connection should close first
      manager.connect();
      const secondInstance = mockWS.lastInstance();
      
      expect(firstInstance.close).toHaveBeenCalled();
      expect(secondInstance).not.toBe(firstInstance);
    });

    it('should handle disconnect when not connected', () => {
      expect(() => manager.disconnect()).not.toThrow();
    });

    it('should close WebSocket on disconnect', () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      manager.disconnect();
      
      expect(wsInstance.close).toHaveBeenCalled();
    });

    it('should check connection state correctly', () => {
      expect(manager.isConnected()).toBe(false);
      
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      expect(manager.isConnected()).toBe(false); // Still connecting
      
      wsInstance.readyState = MockWebSocket.OPEN;
      expect(manager.isConnected()).toBe(true);
      
      wsInstance.readyState = MockWebSocket.CLOSING;
      expect(manager.isConnected()).toBe(false);
      
      wsInstance.readyState = MockWebSocket.CLOSED;
      expect(manager.isConnected()).toBe(false);
    });
  });

  describe('Message Handling', () => {
    beforeEach(() => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      wsInstance.readyState = MockWebSocket.OPEN;
    });

    it('should call onMessage callback for text messages', async () => {
      const testData = { type: 'test', data: 'hello' };
      wsInstance.simulateTextMessage(testData);
      
      await sleep(10);
      
      expect(callbacks.onMessage).toHaveBeenCalledWith(JSON.stringify(testData));
    });

    it('should call onMessage callback for binary messages', async () => {
      const binaryData = new ArrayBuffer(256);
      wsInstance.simulateBinaryMessage(binaryData);
      
      await sleep(10);
      
      expect(callbacks.onMessage).toHaveBeenCalledWith(binaryData);
    });

    it('should send text messages', () => {
      const message = JSON.stringify({ type: 'test', content: 'hello' });
      
      manager.send(message);
      
      expect(wsInstance.send).toHaveBeenCalledWith(message);
    });

    it('should send binary messages', () => {
      const binaryData = new ArrayBuffer(128);
      
      manager.send(binaryData);
      
      expect(wsInstance.send).toHaveBeenCalledWith(binaryData);
    });

    it('should throw error when sending without connection', () => {
      manager.disconnect();
      
      expect(() => manager.send('test')).toThrow('WebSocket is not connected');
    });

    it('should handle send errors gracefully', () => {
      wsInstance.send = vi.fn().mockImplementation(() => {
        throw new Error('Send failed');
      });
      
      expect(() => manager.send('test')).toThrow('Send failed');
    });
  });

  describe('Reconnection Support', () => {
    it('should handle unexpected disconnect', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      wsInstance.simulateOpen();
      
      // Simulate unexpected disconnect
      wsInstance.simulateClose(1006, 'Connection lost');
      
      await sleep(10);
      
      // Should call onClose callback with error code
      expect(callbacks.onClose).toHaveBeenCalled();
      const closeCall = callbacks.onClose.mock.calls[0][0];
      expect(closeCall.code).toBe(1006);
    });

    it('should handle clean disconnect', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      wsInstance.simulateOpen();
      
      // Simulate clean disconnect
      wsInstance.simulateClose(1000, 'Normal closure');
      
      await sleep(10);
      
      // Should call onClose callback with normal code
      expect(callbacks.onClose).toHaveBeenCalled();
      const closeCall = callbacks.onClose.mock.calls[0][0];
      expect(closeCall.code).toBe(1000);
    });
  });

  describe('Callback System', () => {
    it('should handle multiple callbacks', () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      // Test all callbacks
      wsInstance.simulateOpen();
      expect(callbacks.onOpen).toHaveBeenCalled();
      
      wsInstance.simulateTextMessage('test');
      expect(callbacks.onMessage).toHaveBeenCalledWith('test');
      
      wsInstance.simulateError('error');
      expect(callbacks.onError).toHaveBeenCalled();
      
      wsInstance.simulateClose(1000, 'Normal');
      expect(callbacks.onClose).toHaveBeenCalled();
    });

    it('should work without callbacks', () => {
      // Create manager without callbacks
      const managerNoCallbacks = new WebSocketManager({
        url: 'ws://localhost:8080/test',
        protocols: undefined,
        binaryType: 'arraybuffer'
      });
      
      managerNoCallbacks.connect();
      const instance = mockWS.lastInstance();
      
      // Should not throw when events occur
      expect(() => {
        instance.simulateOpen();
        instance.simulateTextMessage('test');
        instance.simulateClose(1000, 'Normal');
      }).not.toThrow();
      
      managerNoCallbacks.disconnect();
    });
  });

  describe('Binary Protocol Support', () => {
    beforeEach(() => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      wsInstance.readyState = MockWebSocket.OPEN;
    });

    it('should handle ArrayBuffer messages', async () => {
      const binaryHandler = vi.fn();
      manager.on('message', binaryHandler);
      
      const buffer = new ArrayBuffer(1024);
      const view = new Uint8Array(buffer);
      for (let i = 0; i < view.length; i++) {
        view[i] = i % 256;
      }
      
      wsInstance.simulateBinaryMessage(buffer);
      
      await sleep(10);
      
      expect(binaryHandler).toHaveBeenCalledWith(buffer);
    });

    it('should send ArrayBuffer data', () => {
      const buffer = new ArrayBuffer(512);
      
      manager.send(buffer);
      
      expect(wsInstance.send).toHaveBeenCalledWith(buffer);
    });

    it('should handle Blob messages if binaryType is blob', async () => {
      manager.disconnect();
      
      const blobManager = new WebSocketManager({
        url: 'ws://localhost:8080/test',
        protocols: undefined,
        binaryType: 'blob'
      });
      
      blobManager.connect();
      const blobWsInstance = mockWS.lastInstance();
      blobWsInstance.readyState = MockWebSocket.OPEN;
      
      expect(blobWsInstance.binaryType).toBe('blob');
      
      const messageHandler = vi.fn();
      blobManager.on('message', messageHandler);
      
      const blob = new Blob(['test data']);
      blobWsInstance.simulateMessage(blob);
      
      await sleep(10);
      
      expect(messageHandler).toHaveBeenCalledWith(blob);
      
      blobManager.disconnect();
    });
  });

  describe('WebSocket State Management', () => {
    it('should track WebSocket state transitions', () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      // Initially connecting
      expect(wsInstance.readyState).toBe(MockWebSocket.CONNECTING);
      
      // Open
      wsInstance.readyState = MockWebSocket.OPEN;
      wsInstance.simulateOpen();
      expect(manager.isConnected()).toBe(true);
      
      // Closing
      wsInstance.readyState = MockWebSocket.CLOSING;
      expect(manager.isConnected()).toBe(false);
      
      // Closed
      wsInstance.readyState = MockWebSocket.CLOSED;
      wsInstance.simulateClose();
      expect(manager.isConnected()).toBe(false);
    });

    it('should handle rapid connect/disconnect cycles', () => {
      for (let i = 0; i < 5; i++) {
        manager.connect();
        const instance = mockWS.lastInstance();
        manager.disconnect();
        expect(instance.close).toHaveBeenCalled();
      }
      
      expect(mockWS).toHaveBeenCalledTimes(5);
    });
  });

  describe('Error Handling', () => {
    it('should handle connection failures', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      
      wsInstance.simulateError('Network error');
      
      await sleep(10);
      
      expect(callbacks.onError).toHaveBeenCalled();
    });

    it('should handle WebSocket constructor errors', () => {
      // Mock WebSocket to throw on construction
      const throwingMock = vi.fn().mockImplementation(() => {
        throw new Error('WebSocket construction failed');
      });
      global.WebSocket = throwingMock as any;
      
      expect(() => manager.connect()).toThrow('WebSocket construction failed');
    });

    it('should handle abnormal closures', async () => {
      manager.connect();
      wsInstance = mockWS.lastInstance();
      wsInstance.simulateOpen();
      
      // Abnormal closure
      wsInstance.simulateClose(1006, 'Abnormal closure');
      
      await sleep(10);
      
      expect(callbacks.onClose).toHaveBeenCalled();
      const closeCall = callbacks.onClose.mock.calls[0][0];
      expect(closeCall.code).toBe(1006);
      expect(closeCall.reason).toBe('Abnormal closure');
    });
  });

  describe('Configuration Options', () => {
    it('should handle different URL formats', () => {
      const urls = [
        'ws://localhost:8080',
        'wss://example.com/ws',
        'ws://192.168.1.1:3000/socket',
        'wss://api.example.com/v1/ws'
      ];
      
      urls.forEach(url => {
        const testManager = new WebSocketManager({
          url,
          protocols: undefined,
          binaryType: 'arraybuffer'
        });
        
        testManager.connect();
        expect(mockWS).toHaveBeenCalledWith(url, undefined);
        testManager.disconnect();
      });
    });

    it('should handle different protocol configurations', () => {
      const configs = [
        { protocols: undefined },
        { protocols: 'chat' },
        { protocols: ['chat', 'v1'] },
        { protocols: [] }
      ];
      
      configs.forEach(({ protocols }) => {
        const testManager = new WebSocketManager({
          url: 'ws://test',
          protocols,
          binaryType: 'arraybuffer'
        });
        
        testManager.connect();
        expect(mockWS).toHaveBeenCalledWith('ws://test', protocols);
        testManager.disconnect();
      });
    });
  });
});