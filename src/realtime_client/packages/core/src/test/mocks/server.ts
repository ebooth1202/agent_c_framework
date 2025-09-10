/**
 * MSW Server Setup for Core Package
 * Configure Mock Service Worker for testing
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * Setup MSW server with default handlers
 */
export const server = setupServer(...handlers);

/**
 * Server lifecycle management
 */
export const serverLifecycle = {
  /**
   * Start the server before all tests
   */
  start: () => {
    server.listen({
      onUnhandledRequest: 'warn', // Warn on unhandled requests in tests
    });
  },

  /**
   * Reset handlers to defaults after each test
   */
  reset: () => {
    server.resetHandlers();
  },

  /**
   * Close the server after all tests
   */
  close: () => {
    server.close();
  }
};

/**
 * Helper to override handlers for specific tests
 */
export function useHandlers(...customHandlers: any[]) {
  server.use(...customHandlers);
}

/**
 * Helper to temporarily override all handlers
 */
export function replaceAllHandlers(...customHandlers: any[]) {
  server.resetHandlers(...customHandlers);
}

/**
 * Debug helper to log intercepted requests
 */
export function enableRequestLogging() {
  server.events.on('request:start', ({ request }) => {
    console.log('MSW intercepted:', request.method, request.url);
  });

  server.events.on('response:mocked', ({ request, response }) => {
    console.log(
      'MSW responded:',
      request.method,
      request.url,
      'with status',
      response.status
    );
  });
}

/**
 * Test helper to wait for a specific request
 */
export function waitForRequest(
  method: string,
  url: string | RegExp
): Promise<Request> {
  return new Promise((resolve) => {
    const listener = ({ request }: any) => {
      const matches = typeof url === 'string' 
        ? request.url.includes(url)
        : url.test(request.url);
        
      if (request.method === method && matches) {
        server.events.removeListener('request:start', listener);
        resolve(request);
      }
    };
    
    server.events.on('request:start', listener);
  });
}

/**
 * Test helper to assert a request was made
 */
export async function expectRequest(
  method: string,
  url: string | RegExp,
  timeout: number = 1000
): Promise<Request> {
  return Promise.race([
    waitForRequest(method, url),
    new Promise<Request>((_, reject) => 
      setTimeout(() => reject(new Error(`Request ${method} ${url} was not made within ${timeout}ms`)), timeout)
    )
  ]);
}

/**
 * Export server instance and helpers
 */
export default server;