/**
 * Mock WebSocket implementation for testing
 */

import { vi } from 'vitest';
import { EventEmitter } from 'events';

export class MockWebSocket extends EventEmitter {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  CONNECTING = MockWebSocket.CONNECTING;
  OPEN = MockWebSocket.OPEN;
  CLOSING = MockWebSocket.CLOSING;
  CLOSED = MockWebSocket.CLOSED;

  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  binaryType: 'blob' | 'arraybuffer' = 'blob';
  
  send = vi.fn();
  close = vi.fn();

  private messageQueue: any[] = [];
  private isConnected = false;

  constructor(url: string, protocols?: string | string[]) {
    super();
    this.url = url;
    
    // Simulate connection delay
    setTimeout(() => {
      if (this.readyState === MockWebSocket.CONNECTING) {
        this.connect();
      }
    }, 0);
  }

  connect() {
    this.readyState = MockWebSocket.OPEN;
    this.isConnected = true;
    this.emit('open', { type: 'open', target: this });
    
    // Process any queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.receiveMessage(message);
    }
  }

  disconnect() {
    if (this.readyState === MockWebSocket.OPEN) {
      this.readyState = MockWebSocket.CLOSED;
      this.isConnected = false;
      this.emit('close', { type: 'close', target: this, code: 1000, reason: 'Normal closure' });
    }
  }

  simulateError(error: Error) {
    this.emit('error', { type: 'error', target: this, error });
  }

  receiveMessage(data: any) {
    if (this.isConnected) {
      const event = { type: 'message', target: this, data };
      this.emit('message', event);
    } else {
      this.messageQueue.push(data);
    }
  }

  receiveBinaryMessage(data: ArrayBuffer) {
    if (this.isConnected) {
      const event = { type: 'message', target: this, data };
      this.emit('message', event);
    } else {
      this.messageQueue.push(data);
    }
  }

  addEventListener(event: string, handler: Function) {
    this.on(event, handler as any);
  }

  removeEventListener(event: string, handler: Function) {
    this.off(event, handler as any);
  }
}

export function createMockWebSocket(url?: string) {
  return new MockWebSocket(url || 'ws://localhost:8080');
}

export function mockWebSocketConstructor() {
  const MockWebSocketClass = vi.fn().mockImplementation((url: string) => {
    return createMockWebSocket(url);
  });
  
  // Add static properties
  MockWebSocketClass.CONNECTING = 0;
  MockWebSocketClass.OPEN = 1;
  MockWebSocketClass.CLOSING = 2;
  MockWebSocketClass.CLOSED = 3;
  
  return MockWebSocketClass;
}