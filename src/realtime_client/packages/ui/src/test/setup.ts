import { vi } from 'vitest';
// TODO: Uncomment when @testing-library/jest-dom is installed
// import '@testing-library/jest-dom';

// Mock window.prompt for link tests
global.prompt = vi.fn();

// Setup any other global mocks needed for the editor tests

// Configure Testing Library
import { configure } from '@testing-library/react';

configure({
  testIdAttribute: 'data-testid',
});

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