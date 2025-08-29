/**
 * Test setup for @agentc/realtime-core package
 */

import { beforeAll, afterEach, afterAll, vi } from 'vitest';

// Mock Web APIs that aren't available in Node
beforeAll(() => {
  // Mock WebSocket
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

  // Mock Audio APIs
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
    createScriptProcessor: vi.fn(() => ({
      connect: vi.fn(),
      disconnect: vi.fn(),
      onaudioprocess: null,
    })),
    createAnalyser: vi.fn(() => ({
      fftSize: 2048,
      connect: vi.fn(),
      disconnect: vi.fn(),
      getByteTimeDomainData: vi.fn(),
    })),
    decodeAudioData: vi.fn(),
    sampleRate: 48000,
    currentTime: 0,
    state: 'running',
    suspend: vi.fn(),
    resume: vi.fn(),
    close: vi.fn(),
  })) as any;

  // Mock MediaStream and related APIs
  global.MediaStream = vi.fn() as any;
  global.MediaStreamTrack = vi.fn() as any;
  
  // Mock navigator.mediaDevices
  Object.defineProperty(global.navigator, 'mediaDevices', {
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

  // Mock localStorage for browser-like environments
  global.localStorage = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  } as any;

  // Mock fetch
  global.fetch = vi.fn();
});

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks();
});

// Restore all mocks after all tests
afterAll(() => {
  vi.restoreAllMocks();
});