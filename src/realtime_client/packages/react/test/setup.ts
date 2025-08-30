/**
 * Test setup for @agentc/realtime-react package
 */

import { afterEach, afterAll, beforeAll, vi } from 'vitest';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

// Re-export testing utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';

// Track active resources for cleanup
const activeTimers = new Set<any>();
const activePromises = new Set<Promise<any>>();

// Setup test timeout defaults
beforeAll(() => {
  // Set a reasonable default timeout for async tests
  vi.setConfig({ testTimeout: 10000 });
});

// Clean up after each test
afterEach(async () => {
  // Clean up React Testing Library
  cleanup();
  
  // Clear all mock function calls
  vi.clearAllMocks();
  
  // Wait for any pending promises to resolve
  if (activePromises.size > 0) {
    await Promise.allSettled(Array.from(activePromises));
    activePromises.clear();
  }
  
  // Clear any pending timers
  vi.clearAllTimers();
  
  // Restore real timers if they were faked
  if (vi.isFakeTimers()) {
    vi.useRealTimers();
  }
  
  // Clear tracked timers
  activeTimers.clear();
});

// Final cleanup after all tests
afterAll(async () => {
  // Ensure everything is cleaned up
  cleanup();
  activeTimers.clear();
  activePromises.clear();
  
  // Reset all mocks
  vi.resetAllMocks();
  
  // Restore all mocked modules
  vi.restoreAllMocks();
});