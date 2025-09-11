/**
 * WebSocketManager Unit Tests
 * Phase 1 Implementation - Simple behavior testing with Level 1 stubs
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketManager } from '../WebSocketManager';
import { createMockWebSocket } from '../../test/mocks/websocket.mock';
import { useFakeTimers } from '../../test/shared/timer-helpers';

// Import test setup for polyfills
import '../../test/setup';

describe('WebSocketManager', () => {
  let manager: WebSocketManager;
  let mockWS: any;
  let mockConstructor: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Create mock WebSocket instance
    mockWS = createMockWebSocket();
    mockWS.readyState = WebSocket.CONNECTING;
    mockWS.binaryType = 'arraybuffer';
    mockWS.onopen = null;
    mockWS.onclose = null; 
    mockWS.onerror = null;
    mockWS.onmessage = null;
    
    // Mock WebSocket constructor
    mockConstructor = vi.fn(() => mockWS);
    mockConstructor.CONNECTING = 0;
    mockConstructor.OPEN = 1;
    mockConstructor.CLOSING = 2;
    mockConstructor.CLOSED = 3;
    
    // Install globally
    vi.stubGlobal('WebSocket', mockConstructor);
    
    // Create manager with test config
    manager = new WebSocketManager({
      url: 'ws://test.example.com',
      protocols: ['protocol1'],
      pingInterval: 30000,
      pongTimeout: 5000
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
    manager.disconnect();
  });

  describe('Connection lifecycle', () => {
    it('should create WebSocket with correct URL', () => {
      manager.connect();
      
      expect(mockConstructor).toHaveBeenCalledWith('ws://test.example.com', ['protocol1']);
      expect(mockWS.binaryType).toBe('arraybuffer');
    });

    it('should handle connection open event', () => {
      const onOpen = vi.fn();
      manager = new WebSocketManager(
        { url: 'ws://test.example.com' },
        { onOpen }
      );
      
      manager.connect();
      mockWS.readyState = WebSocket.OPEN;
      
      // Trigger open event
      mockWS.onopen?.({} as Event);
      
      expect(onOpen).toHaveBeenCalled();
    });

    it('should handle connection close event', () => {
      const onClose = vi.fn();
      manager = new WebSocketManager(
        { url: 'ws://test.example.com' },
        { onClose }
      );
      
      manager.connect();
      
      // Trigger close event
      const closeEvent = new CloseEvent('close', { code: 1000, reason: 'Normal' });
      mockWS.onclose?.(closeEvent);
      
      expect(onClose).toHaveBeenCalledWith(closeEvent);
    });

    it('should disconnect existing connection before new one', () => {
      manager.connect();
      const firstWS = mockWS;
      firstWS.readyState = WebSocket.OPEN; // Ensure it's open
      
      // Create new mock for second connection
      const secondWS = createMockWebSocket();
      secondWS.readyState = WebSocket.CONNECTING;
      secondWS.binaryType = 'arraybuffer';
      secondWS.onopen = null;
      secondWS.onclose = null;
      secondWS.onerror = null;
      secondWS.onmessage = null;
      mockConstructor.mockReturnValue(secondWS);
      
      manager.connect();
      
      expect(firstWS.close).toHaveBeenCalled();
      expect(mockConstructor).toHaveBeenCalledTimes(2);
    });
  });

  describe('Message sending', () => {
    beforeEach(() => {
      manager.connect();
      mockWS.readyState = WebSocket.OPEN;
    });

    it('should send string messages', () => {
      const message = 'test message';
      manager.send(message);
      
      expect(mockWS.send).toHaveBeenCalledWith(message);
    });

    it('should send binary data', () => {
      const data = new ArrayBuffer(8);
      manager.send(data);
      
      expect(mockWS.send).toHaveBeenCalledWith(data);
    });

    it('should throw when not connected', () => {
      manager.disconnect();
      
      expect(() => manager.send('test')).toThrow('WebSocket is not connected');
    });

    it('should throw when WebSocket is not open', () => {
      mockWS.readyState = WebSocket.CONNECTING;
      
      expect(() => manager.send('test')).toThrow('WebSocket is not open');
    });
  });

  describe('Message receiving', () => {
    it('should handle incoming text messages', () => {
      const onMessage = vi.fn();
      manager = new WebSocketManager(
        { url: 'ws://test.example.com' },
        { onMessage }
      );
      
      manager.connect();
      
      // Simulate text message
      const messageEvent = { data: 'test message' } as MessageEvent;
      mockWS.onmessage?.(messageEvent);
      
      expect(onMessage).toHaveBeenCalledWith('test message');
    });

    it('should handle incoming binary messages', () => {
      const onMessage = vi.fn();
      manager = new WebSocketManager(
        { url: 'ws://test.example.com' },
        { onMessage }
      );
      
      manager.connect();
      
      // Simulate binary message
      const buffer = new ArrayBuffer(8);
      const messageEvent = { data: buffer } as MessageEvent;
      mockWS.onmessage?.(messageEvent);
      
      expect(onMessage).toHaveBeenCalledWith(buffer);
    });
  });

  describe('Heartbeat', () => {
    let timers: ReturnType<typeof useFakeTimers>;
    
    beforeEach(() => {
      timers = useFakeTimers();
      manager.connect();
      mockWS.readyState = WebSocket.OPEN;
    });
    
    afterEach(() => {
      timers.restore();
    });

    it('should send ping at intervals', () => {
      // Trigger connection open
      mockWS.onopen?.({} as Event);
      
      // Advance timer to ping interval
      timers.advance(30000);
      
      expect(mockWS.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }));
      
      // Simulate pong response to reset isAlive flag
      mockWS.onmessage?.({ data: 'pong' } as MessageEvent);
      
      // Clear the mock to check for second ping
      mockWS.send.mockClear();
      
      // Advance again for second ping
      timers.advance(30000);
      expect(mockWS.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }));
    });

    it('should handle pong response', () => {
      // Trigger connection open
      mockWS.onopen?.({} as Event);
      
      // Advance timer to ping interval
      timers.advance(30000);
      expect(mockWS.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }));
      
      // Simulate pong response (any message resets isAlive)
      mockWS.onmessage?.({ data: 'pong' } as MessageEvent);
      
      // Should not disconnect after pong timeout
      timers.advance(5000);
      expect(mockWS.close).not.toHaveBeenCalled();
    });
  });

  describe('State management', () => {
    it('should return correct ready state', () => {
      // Before connection
      expect(manager.getReadyState()).toBe(WebSocket.CLOSED);
      
      // After connection
      manager.connect();
      mockWS.readyState = WebSocket.CONNECTING;
      expect(manager.getReadyState()).toBe(WebSocket.CONNECTING);
      
      // When open
      mockWS.readyState = WebSocket.OPEN;
      expect(manager.getReadyState()).toBe(WebSocket.OPEN);
      
      // After disconnect
      manager.disconnect();
      expect(manager.getReadyState()).toBe(WebSocket.CLOSED);
    });

    it('should report connection status', () => {
      expect(manager.isConnected()).toBe(false);
      
      manager.connect();
      mockWS.readyState = WebSocket.CONNECTING;
      expect(manager.isConnected()).toBe(false);
      
      mockWS.readyState = WebSocket.OPEN;
      expect(manager.isConnected()).toBe(true);
      
      mockWS.readyState = WebSocket.CLOSING;
      expect(manager.isConnected()).toBe(false);
    });
  });
});