/**
 * MSW Server Setup for Demo Application
 * Configure Mock Service Worker for demo app testing
 */

import { setupServer } from 'msw/node';
import { handlers, demoScenarios } from './handlers';

/**
 * Setup MSW server with demo handlers
 */
export const server = setupServer(...handlers);

/**
 * Server lifecycle management for demo app
 */
export const serverLifecycle = {
  /**
   * Start the server with demo-specific configuration
   */
  start: () => {
    server.listen({
      onUnhandledRequest: (request, print) => {
        // Ignore specific requests that are expected to be unhandled
        const ignoredPaths = [
          '/favicon.ico',
          '/manifest.json',
          '/_next/',
          '/static/',
          '/assets/'
        ];
        
        const url = new URL(request.url);
        const shouldIgnore = ignoredPaths.some(path => url.pathname.startsWith(path));
        
        if (!shouldIgnore) {
          print.warning();
        }
      }
    });
  },

  /**
   * Reset handlers and demo data after each test
   */
  reset: () => {
    server.resetHandlers();
    demoScenarios.reset();
  },

  /**
   * Close the server after all tests
   */
  close: () => {
    server.close();
  }
};

/**
 * Demo-specific test helpers
 */

/**
 * Setup demo with pre-authenticated user
 */
export function setupAuthenticatedDemo() {
  const { userId, sessionId } = demoScenarios.loggedInUser();
  
  // Set localStorage to simulate logged in state
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', 'mock_jwt_token');
    localStorage.setItem('session_id', sessionId);
    localStorage.setItem('user_id', userId);
  }
  
  return { userId, sessionId };
}

/**
 * Clear demo authentication
 */
export function clearDemoAuth() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('session_id');
    localStorage.removeItem('user_id');
  }
  demoScenarios.reset();
}

/**
 * Override handlers for specific demo scenarios
 */
export const demoHandlerOverrides = {
  /**
   * Simulate network offline
   */
  offline: () => {
    server.use(
      ...handlers.map(() => {
        return {
          predicate: () => true,
          resolver: () => {
            throw new Error('Network error');
          }
        };
      })
    );
  },

  /**
   * Simulate slow network
   */
  slowNetwork: (delayMs: number = 3000) => {
    const { http, HttpResponse, delay } = require('msw');
    
    server.use(
      http.all('*', async () => {
        await delay(delayMs);
        return HttpResponse.json({ success: true });
      })
    );
  },

  /**
   * Simulate authentication errors
   */
  authError: () => {
    const { http, HttpResponse } = require('msw');
    
    server.use(
      http.all('*/api/*', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'UNAUTHORIZED',
              message: 'Session expired'
            }
          },
          { status: 401 }
        );
      })
    );
  },

  /**
   * Simulate rate limiting
   */
  rateLimited: () => {
    const { http, HttpResponse } = require('msw');
    
    server.use(
      http.all('*/api/*', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'RATE_LIMIT',
              message: 'Rate limit exceeded',
              details: {
                retry_after: 60
              }
            }
          },
          { 
            status: 429,
            headers: {
              'Retry-After': '60'
            }
          }
        );
      })
    );
  }
};

/**
 * Wait for a specific request in demo app
 */
export function waitForDemoRequest(
  method: string,
  pathname: string
): Promise<Request> {
  return new Promise((resolve) => {
    const listener = ({ request }: any) => {
      const url = new URL(request.url);
      
      if (request.method === method && url.pathname === pathname) {
        server.events.removeListener('request:start', listener);
        resolve(request);
      }
    };
    
    server.events.on('request:start', listener);
  });
}

/**
 * Capture all requests made during a test
 */
export class RequestCapture {
  private requests: Request[] = [];
  private listener: any;

  start() {
    this.listener = ({ request }: any) => {
      this.requests.push(request.clone());
    };
    server.events.on('request:start', this.listener);
  }

  stop() {
    if (this.listener) {
      server.events.removeListener('request:start', this.listener);
      this.listener = null;
    }
  }

  getRequests() {
    return [...this.requests];
  }

  findRequest(predicate: (req: Request) => boolean) {
    return this.requests.find(predicate);
  }

  clear() {
    this.requests = [];
  }
}

/**
 * Mock WebSocket connection helper for demo
 */
export class MockWebSocketConnection {
  private messages: any[] = [];
  private isConnected = false;

  connect(sessionId: string) {
    this.isConnected = true;
    this.messages.push({
      type: 'connected',
      session_id: sessionId,
      timestamp: new Date().toISOString()
    });
  }

  sendMessage(message: any) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected');
    }
    this.messages.push(message);
  }

  getMessages() {
    return [...this.messages];
  }

  disconnect() {
    this.isConnected = false;
    this.messages.push({
      type: 'disconnected',
      timestamp: new Date().toISOString()
    });
  }

  clear() {
    this.messages = [];
    this.isConnected = false;
  }
}

/**
 * Export server and helpers
 */
export default server;