/**
 * WebSocket Mock Implementation for Testing
 * Provides a comprehensive mock of the WebSocket API with binary message support
 */

import { vi } from 'vitest';

export class MockWebSocket implements WebSocket {
  // WebSocket states
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  // Instance properties
  readyState: number = MockWebSocket.CONNECTING;
  url: string;
  protocol: string = '';
  extensions: string = '';
  bufferedAmount: number = 0;
  binaryType: BinaryType = 'blob';

  // Event handlers
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  // Mock tracking
  send = vi.fn();
  close = vi.fn((code?: number, reason?: string) => {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      const closeEvent = new CloseEvent('close', {
        code: code || 1000,
        reason: reason || 'Normal closure',
        wasClean: code === 1000
      });
      this.onclose(closeEvent);
    }
  });

  // Event listener tracking
  private eventListeners: Map<string, Set<EventListener>> = new Map();

  constructor(url: string | URL, protocols?: string | string[]) {
    this.url = url.toString();
    if (protocols) {
      this.protocol = Array.isArray(protocols) ? protocols[0] : protocols;
    }
  }

  addEventListener(type: string, listener: EventListener | EventListenerObject): void {
    if (!this.eventListeners.has(type)) {
      this.eventListeners.set(type, new Set());
    }
    const listenerFn = typeof listener === 'function' ? listener : listener.handleEvent;
    this.eventListeners.get(type)!.add(listenerFn);
  }

  removeEventListener(type: string, listener: EventListener | EventListenerObject): void {
    const listeners = this.eventListeners.get(type);
    if (listeners) {
      const listenerFn = typeof listener === 'function' ? listener : listener.handleEvent;
      listeners.delete(listenerFn);
    }
  }

  dispatchEvent(event: Event): boolean {
    const listeners = this.eventListeners.get(event.type);
    if (listeners) {
      listeners.forEach(listener => listener(event));
    }

    // Also trigger on[event] handlers
    const handler = (this as any)[`on${event.type}`];
    if (typeof handler === 'function') {
      handler(event);
    }

    return true;
  }

  // Helper methods for testing
  simulateOpen(): void {
    this.readyState = MockWebSocket.OPEN;
    const event = new Event('open');
    Object.defineProperty(event, 'target', { value: this, writable: false });
    this.dispatchEvent(event);
  }

  simulateClose(code: number = 1000, reason: string = 'Normal closure'): void {
    this.readyState = MockWebSocket.CLOSED;
    const event = new CloseEvent('close', { code, reason, wasClean: code === 1000 });
    Object.defineProperty(event, 'target', { value: this, writable: false });
    this.dispatchEvent(event);
  }

  simulateError(message: string = 'Connection error'): void {
    const event = new Event('error');
    Object.defineProperty(event, 'target', { value: this, writable: false });
    Object.defineProperty(event, 'message', { value: message, writable: false });
    this.dispatchEvent(event);
  }

  simulateMessage(data: string | ArrayBuffer | Blob): void {
    const event = new MessageEvent('message', { data });
    Object.defineProperty(event, 'target', { value: this, writable: false });
    this.dispatchEvent(event);
  }

  // Simulate binary message with proper typing
  simulateBinaryMessage(data: ArrayBuffer): void {
    const event = new MessageEvent('message', { data });
    Object.defineProperty(event, 'target', { value: this, writable: false });
    this.dispatchEvent(event);
  }

  // Simulate text message
  simulateTextMessage(data: string | object): void {
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    const event = new MessageEvent('message', { data: message });
    Object.defineProperty(event, 'target', { value: this, writable: false });
    this.dispatchEvent(event);
  }
}

/**
 * Factory function to create a mock WebSocket constructor
 * Tracks all instances created for testing
 */
export function mockWebSocketConstructor(): jest.Mock<MockWebSocket> {
  const instances: MockWebSocket[] = [];
  
  const MockConstructor = vi.fn((url: string | URL, protocols?: string | string[]) => {
    const instance = new MockWebSocket(url, protocols);
    instances.push(instance);
    return instance;
  }) as any;

  // Attach static properties
  MockConstructor.CONNECTING = MockWebSocket.CONNECTING;
  MockConstructor.OPEN = MockWebSocket.OPEN;
  MockConstructor.CLOSING = MockWebSocket.CLOSING;
  MockConstructor.CLOSED = MockWebSocket.CLOSED;

  // Attach helper to get instances
  MockConstructor.instances = instances;
  MockConstructor.lastInstance = () => instances[instances.length - 1];
  MockConstructor.clearInstances = () => instances.length = 0;

  return MockConstructor;
}

/**
 * WebSocket mock with connection lifecycle helpers
 */
export class WebSocketMock extends MockWebSocket {
  private messageQueue: (string | ArrayBuffer)[] = [];
  private isProcessing = false;

  constructor(url: string | URL, protocols?: string | string[]) {
    super(url, protocols);
  }

  // Queue a message to be sent when connection opens
  queueMessage(data: string | ArrayBuffer): void {
    this.messageQueue.push(data);
    this.processQueue();
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.readyState !== MockWebSocket.OPEN) {
      return;
    }

    this.isProcessing = true;
    while (this.messageQueue.length > 0) {
      const data = this.messageQueue.shift()!;
      this.simulateMessage(data);
      // Small delay to simulate network
      await new Promise(resolve => setTimeout(resolve, 1));
    }
    this.isProcessing = false;
  }

  // Override simulateOpen to process queued messages
  simulateOpen(): void {
    super.simulateOpen();
    this.processQueue();
  }

  // Helper to simulate a complete connection lifecycle
  async simulateConnectionLifecycle(options: {
    connectDelay?: number;
    messageDelay?: number;
    messages?: (string | ArrayBuffer)[];
    closeCode?: number;
    closeReason?: string;
  } = {}): Promise<void> {
    const {
      connectDelay = 10,
      messageDelay = 5,
      messages = [],
      closeCode = 1000,
      closeReason = 'Normal closure'
    } = options;

    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, connectDelay));
    this.simulateOpen();

    // Send messages
    for (const message of messages) {
      await new Promise(resolve => setTimeout(resolve, messageDelay));
      this.simulateMessage(message);
    }

    // Close connection
    this.simulateClose(closeCode, closeReason);
  }
}

/**
 * Create a mock WebSocket with spy capabilities
 */
export function createMockWebSocket(url?: string): WebSocketMock {
  return new WebSocketMock(url || 'ws://localhost:8080/test');
}

/**
 * Setup global WebSocket mock for testing
 */
export function setupWebSocketMock(): {
  MockConstructor: jest.Mock<MockWebSocket>;
  cleanup: () => void;
} {
  const originalWebSocket = global.WebSocket;
  const MockConstructor = mockWebSocketConstructor();
  
  global.WebSocket = MockConstructor as any;

  return {
    MockConstructor,
    cleanup: () => {
      global.WebSocket = originalWebSocket;
      MockConstructor.clearInstances();
    }
  };
}