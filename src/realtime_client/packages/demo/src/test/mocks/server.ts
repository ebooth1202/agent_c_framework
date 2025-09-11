/**
 * MSW Server Mock for Demo App Tests
 * Provides mock server setup for testing
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Define mock handlers
const handlers = [
  // Mock authentication endpoint
  http.post('/api/auth/token', () => {
    return HttpResponse.json({
      access_token: 'mock-access-token',
      token_type: 'Bearer',
      expires_in: 3600
    });
  }),

  // Mock health check
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'ok' });
  })
];

// Create mock server instance
export const server = setupServer(...handlers);

// Server lifecycle management
export const serverLifecycle = {
  start: () => server.listen({ onUnhandledRequest: 'bypass' }),
  close: () => server.close(),
  reset: () => server.resetHandlers()
};

// Export handlers for testing
export { handlers };