/**
 * Simple Level 1 Fetch API mock - just stubs for testing
 */
import { vi } from 'vitest';

export const createMockFetch = (response = {}) => {
  return vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => response,
    text: async () => JSON.stringify(response),
    headers: new Headers()
  });
};