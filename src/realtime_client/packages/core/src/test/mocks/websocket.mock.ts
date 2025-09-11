/**
 * Simple Level 1 WebSocket mock - just stubs for testing
 */
import { vi } from 'vitest';

export const createMockWebSocket = () => ({
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: WebSocket.OPEN,
  url: 'ws://test',
  protocol: '',
  binaryType: 'blob' as BinaryType
});