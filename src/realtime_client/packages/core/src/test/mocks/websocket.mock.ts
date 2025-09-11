/**
 * WebSocket API mock for unit testing
 * Simple vi.fn() stubs - configure behavior in individual tests
 */
import { vi } from 'vitest';

export const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  
  // Properties that tests can set directly
  readyState: WebSocket.OPEN,
  binaryType: 'arraybuffer' as BinaryType,
  
  // Event handlers that tests can override
  onopen: vi.fn(),
  onclose: vi.fn(),
  onerror: vi.fn(),
  onmessage: vi.fn(),
};

export const MockWebSocketConstructor = Object.assign(
  vi.fn(() => mockWebSocket),
  {
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3,
  }
);

/**
 * Helper to reset WebSocket mock state
 */
export const resetWebSocketMock = () => {
  mockWebSocket.send.mockReset();
  mockWebSocket.close.mockReset();
  mockWebSocket.addEventListener.mockReset();
  mockWebSocket.removeEventListener.mockReset();
  mockWebSocket.onopen.mockReset();
  mockWebSocket.onclose.mockReset();
  mockWebSocket.onerror.mockReset();
  mockWebSocket.onmessage.mockReset();
  mockWebSocket.readyState = WebSocket.OPEN;
  mockWebSocket.binaryType = 'arraybuffer';
  MockWebSocketConstructor.mockClear();
};