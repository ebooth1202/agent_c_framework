/**
 * Test setup for @agentc/realtime-react package
 */

import { beforeAll, afterEach, afterAll, vi } from 'vitest';
import '@testing-library/jest-dom';

// Re-export testing utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';

// Mock Web APIs that might not be available in happy-dom
beforeAll(() => {
  // Mock WebSocket if not available
  if (!global.WebSocket) {
    global.WebSocket = vi.fn().mockImplementation(() => ({
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      readyState: 0,
      CONNECTING: 0,
      OPEN: 1,
      CLOSING: 2,
      CLOSED: 3,
    })) as any;
  }

  // Mock Audio APIs if not available
  if (!global.AudioContext) {
    global.AudioContext = vi.fn().mockImplementation(() => ({
      createGain: vi.fn(() => ({
        gain: { value: 1 },
        connect: vi.fn(),
        disconnect: vi.fn(),
      })),
      createBufferSource: vi.fn(() => ({
        buffer: null,
        connect: vi.fn(),
        disconnect: vi.fn(),
        start: vi.fn(),
        stop: vi.fn(),
      })),
      createMediaStreamSource: vi.fn(() => ({
        connect: vi.fn(),
        disconnect: vi.fn(),
      })),
      sampleRate: 48000,
      currentTime: 0,
      state: 'running',
      suspend: vi.fn(),
      resume: vi.fn(),
      close: vi.fn(),
    })) as any;
  }

  // Mock navigator.mediaDevices if not available
  if (!navigator.mediaDevices) {
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: vi.fn().mockResolvedValue({
          getTracks: () => [],
          getAudioTracks: () => [{
            stop: vi.fn(),
            enabled: true,
          }],
          getVideoTracks: () => [],
        }),
        enumerateDevices: vi.fn().mockResolvedValue([]),
      },
      writable: true,
    });
  }
});

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks();
});

// Restore all mocks after all tests
afterAll(() => {
  vi.restoreAllMocks();
});