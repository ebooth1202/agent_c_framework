import { vi } from 'vitest';

// Mock window.prompt for link tests
global.prompt = vi.fn();

// Setup any other global mocks needed for the editor tests