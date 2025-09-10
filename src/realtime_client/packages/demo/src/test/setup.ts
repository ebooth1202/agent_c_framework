/**
 * Test setup for demo package
 */

import { afterEach, afterAll, beforeAll, vi, expect } from 'vitest';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

// Import jest-axe (with type safety)
// @ts-ignore - jest-axe doesn't have TypeScript definitions
import { toHaveNoViolations } from 'jest-axe';

// Extend expect with jest-axe matchers
expect.extend(toHaveNoViolations);

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

// Mock window.prompt for any interactive tests
global.prompt = vi.fn();

// Mock IntersectionObserver for components that use it
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver for components that use it
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Configure Testing Library
import { configure } from '@testing-library/react';

configure({
  testIdAttribute: 'data-testid',
});