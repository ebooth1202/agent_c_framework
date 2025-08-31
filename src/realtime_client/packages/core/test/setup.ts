/**
 * Test setup for @agentc/realtime-core package
 */

import { afterEach, afterAll, beforeAll, vi } from 'vitest';

// Track active WebSocket instances for cleanup
const activeWebSockets = new Set<any>();
// Track active AudioContext instances for cleanup
const activeAudioContexts = new Set<any>();

// Setup basic mocks
if (typeof global !== 'undefined') {
  // Mock WebSocket if not available
  if (!global.WebSocket) {
    (global as any).WebSocket = vi.fn().mockImplementation(() => {
      const ws = {
        send: vi.fn(),
        close: vi.fn(() => {
          // Remove from active set when closed
          activeWebSockets.delete(ws);
          ws.readyState = 3; // CLOSED
        }),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        readyState: 0,
        CONNECTING: 0,
        OPEN: 1,
        CLOSING: 2,
        CLOSED: 3,
      };
      
      // Track this WebSocket instance
      activeWebSockets.add(ws);
      
      return ws;
    });
  }

  // Mock AudioContext if not available
  if (!global.AudioContext) {
    (global as any).AudioContext = vi.fn().mockImplementation(() => {
      const ctx = {
        createGain: vi.fn(() => ({
          gain: { value: 1 },
          connect: vi.fn(),
          disconnect: vi.fn(),
        })),
        sampleRate: 48000,
        currentTime: 0,
        state: 'running',
        suspend: vi.fn().mockResolvedValue(undefined),
        resume: vi.fn().mockResolvedValue(undefined),
        close: vi.fn().mockImplementation(() => {
          // Remove from active set when closed
          activeAudioContexts.delete(ctx);
          ctx.state = 'closed';
          return Promise.resolve();
        }),
      };
      
      // Track this AudioContext instance
      activeAudioContexts.add(ctx);
      
      return ctx;
    });
  }

  // Mock fetch if not available
  if (!global.fetch) {
    (global as any).fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({}),
      text: vi.fn().mockResolvedValue(''),
      status: 200,
      statusText: 'OK',
    });
  }
}

// Setup test timeout defaults
beforeAll(() => {
  // Set a reasonable default timeout for async tests
  vi.setConfig({ testTimeout: 10000 });
});

// Clean up after each test
afterEach(async () => {
  // Clear all mock function calls
  vi.clearAllMocks();
  
  // Close any open WebSocket connections
  for (const ws of activeWebSockets) {
    if (ws.readyState !== ws.CLOSED) {
      ws.close();
    }
  }
  activeWebSockets.clear();
  
  // Close any open AudioContexts
  for (const ctx of activeAudioContexts) {
    if (ctx.state !== 'closed') {
      await ctx.close();
    }
  }
  activeAudioContexts.clear();
  
  // Clear any pending timers
  vi.clearAllTimers();
  
  // Restore real timers if they were faked
  if (vi.isFakeTimers()) {
    vi.useRealTimers();
  }
});

// Final cleanup after all tests
afterAll(async () => {
  // Ensure everything is cleaned up
  activeWebSockets.clear();
  activeAudioContexts.clear();
  
  // Reset all mocks
  vi.resetAllMocks();
  
  // Restore all mocked modules
  vi.restoreAllMocks();
});