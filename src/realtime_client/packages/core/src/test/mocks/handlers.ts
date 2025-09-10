/**
 * MSW Request Handlers for Core Package
 * Mock API endpoints for testing
 */

import { http, HttpResponse, delay } from 'msw';
import { faker } from '@faker-js/faker';

/**
 * Base API URL for testing
 */
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8080';

/**
 * Mock JWT token generator
 */
function generateMockJWT(): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
  }));
  const signature = faker.string.alphanumeric(43);
  return `${header}.${payload}.${signature}`;
}

/**
 * Mock HeyGen token generator
 */
function generateHeyGenToken(): string {
  return `hg_${faker.string.alphanumeric(32)}`;
}

/**
 * Authentication handlers
 */
export const authHandlers = [
  // POST /api/auth/session - Create new session
  http.post(`${API_BASE_URL}/api/auth/session`, async ({ request }) => {
    await delay(100); // Simulate network delay
    
    const body = await request.json() as any;
    
    // Validate request
    if (!body.username || !body.password) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message: 'Username and password are required',
            details: {
              missing_fields: []
                .concat(!body.username ? ['username'] : [])
                .concat(!body.password ? ['password'] : [])
            }
          }
        },
        { status: 400 }
      );
    }

    // Simulate authentication failure
    if (body.username === 'invalid@example.com' || body.password === 'wrong') {
      return HttpResponse.json(
        {
          error: {
            code: 'AUTHENTICATION_FAILED',
            message: 'Invalid username or password',
            details: {
              attempts_remaining: 3
            }
          }
        },
        { status: 401 }
      );
    }

    // Successful authentication
    const sessionId = `sess_${faker.string.alphanumeric(24)}`;
    const jwt = generateMockJWT();
    const heygenToken = generateHeyGenToken();
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          session_id: sessionId,
          access_token: jwt,
          refresh_token: `refresh_${faker.string.alphanumeric(32)}`,
          heygen_token: heygenToken,
          expires_in: 3600,
          user: {
            id: faker.string.uuid(),
            username: body.username,
            email: body.username,
            name: faker.person.fullName(),
            avatar_url: faker.image.avatar(),
            created_at: faker.date.past().toISOString()
          }
        }
      },
      { 
        status: 200,
        headers: {
          'Set-Cookie': `session=${sessionId}; Path=/; HttpOnly; SameSite=Strict`
        }
      }
    );
  }),

  // POST /api/auth/refresh - Refresh access token
  http.post(`${API_BASE_URL}/api/auth/refresh`, async ({ request }) => {
    await delay(50);
    
    const body = await request.json() as any;
    
    if (!body.refresh_token) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message: 'Refresh token is required',
            details: {}
          }
        },
        { status: 400 }
      );
    }

    // Simulate expired refresh token
    if (body.refresh_token === 'expired_token') {
      return HttpResponse.json(
        {
          error: {
            code: 'TOKEN_EXPIRED',
            message: 'Refresh token has expired',
            details: {
              expired_at: faker.date.recent().toISOString()
            }
          }
        },
        { status: 401 }
      );
    }

    // Successful token refresh
    const newJwt = generateMockJWT();
    const newHeygenToken = generateHeyGenToken();
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          access_token: newJwt,
          heygen_token: newHeygenToken,
          expires_in: 3600,
          refresh_token: body.refresh_token // Return same refresh token
        }
      },
      { status: 200 }
    );
  }),

  // POST /api/auth/logout - End session
  http.post(`${API_BASE_URL}/api/auth/logout`, async () => {
    await delay(50);
    
    return HttpResponse.json(
      {
        success: true,
        message: 'Logged out successfully'
      },
      { 
        status: 200,
        headers: {
          'Set-Cookie': 'session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'
        }
      }
    );
  }),

  // POST /api/auth/validate - Validate token
  http.post(`${API_BASE_URL}/api/auth/validate`, async ({ request }) => {
    await delay(30);
    
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Missing or invalid authorization header',
            details: {}
          }
        },
        { status: 401 }
      );
    }

    const token = authHeader.substring(7);
    
    // Simulate invalid token
    if (token === 'invalid_token') {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_TOKEN',
            message: 'Token validation failed',
            details: {
              reason: 'signature_verification_failed'
            }
          }
        },
        { status: 401 }
      );
    }

    return HttpResponse.json(
      {
        success: true,
        data: {
          valid: true,
          expires_at: faker.date.future().toISOString()
        }
      },
      { status: 200 }
    );
  })
];

/**
 * Session management handlers
 */
export const sessionHandlers = [
  // GET /api/sessions/:id - Get session details
  http.get(`${API_BASE_URL}/api/sessions/:id`, async ({ params }) => {
    await delay(100);
    
    const { id } = params;
    
    // Simulate session not found
    if (id === 'not_found') {
      return HttpResponse.json(
        {
          error: {
            code: 'NOT_FOUND',
            message: 'Session not found',
            details: {
              session_id: id
            }
          }
        },
        { status: 404 }
      );
    }

    // Return session with chat history
    return HttpResponse.json(
      {
        success: true,
        data: {
          session_id: id,
          created_at: faker.date.recent().toISOString(),
          updated_at: faker.date.recent().toISOString(),
          status: 'active',
          metadata: {
            user_id: faker.string.uuid(),
            device_id: faker.string.uuid(),
            location: faker.location.city()
          },
          chat_history: [
            {
              id: faker.string.uuid(),
              role: 'user',
              content: 'Hello, can you help me?',
              timestamp: faker.date.recent().toISOString()
            },
            {
              id: faker.string.uuid(),
              role: 'assistant',
              content: 'Of course! How can I assist you today?',
              timestamp: faker.date.recent().toISOString()
            }
          ],
          statistics: {
            message_count: 2,
            turn_count: 2,
            duration: 120,
            audio_duration: 45
          }
        }
      },
      { status: 200 }
    );
  }),

  // POST /api/sessions/:id/messages - Add message to session
  http.post(`${API_BASE_URL}/api/sessions/:id/messages`, async ({ params, request }) => {
    await delay(50);
    
    const { id } = params;
    const body = await request.json() as any;
    
    if (!body.content || !body.role) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message: 'Content and role are required',
            details: {}
          }
        },
        { status: 400 }
      );
    }

    return HttpResponse.json(
      {
        success: true,
        data: {
          message_id: faker.string.uuid(),
          session_id: id,
          role: body.role,
          content: body.content,
          timestamp: new Date().toISOString()
        }
      },
      { status: 201 }
    );
  }),

  // DELETE /api/sessions/:id - End session
  http.delete(`${API_BASE_URL}/api/sessions/:id`, async ({ params }) => {
    await delay(50);
    
    const { id } = params;
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          session_id: id,
          ended_at: new Date().toISOString()
        }
      },
      { status: 200 }
    );
  })
];

/**
 * User profile handlers
 */
export const userHandlers = [
  // GET /api/user/profile - Get current user profile
  http.get(`${API_BASE_URL}/api/user/profile`, async ({ request }) => {
    await delay(100);
    
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader) {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
            details: {}
          }
        },
        { status: 401 }
      );
    }

    return HttpResponse.json(
      {
        success: true,
        data: {
          id: faker.string.uuid(),
          username: faker.internet.userName(),
          email: faker.internet.email(),
          name: faker.person.fullName(),
          avatar_url: faker.image.avatar(),
          preferences: {
            theme: 'light',
            language: 'en',
            audio_enabled: true,
            notifications: true
          },
          created_at: faker.date.past().toISOString(),
          updated_at: faker.date.recent().toISOString()
        }
      },
      { status: 200 }
    );
  }),

  // PATCH /api/user/profile - Update user profile
  http.patch(`${API_BASE_URL}/api/user/profile`, async ({ request }) => {
    await delay(50);
    
    const body = await request.json() as any;
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          id: faker.string.uuid(),
          ...body,
          updated_at: new Date().toISOString()
        }
      },
      { status: 200 }
    );
  })
];

/**
 * Error simulation handlers
 */
export const errorHandlers = [
  // Simulate rate limiting
  http.all(`${API_BASE_URL}/api/rate-limited/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: 'Too many requests. Please slow down.',
          details: {
            limit: 100,
            remaining: 0,
            reset_at: faker.date.soon().toISOString()
          }
        }
      },
      { status: 429 }
    );
  }),

  // Simulate server error
  http.all(`${API_BASE_URL}/api/error/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'An unexpected error occurred',
          details: {
            request_id: faker.string.uuid(),
            timestamp: new Date().toISOString()
          }
        }
      },
      { status: 500 }
    );
  }),

  // Simulate maintenance mode
  http.all(`${API_BASE_URL}/api/maintenance/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'SERVICE_UNAVAILABLE',
          message: 'Service is under maintenance',
          details: {
            maintenance_until: faker.date.soon().toISOString()
          }
        }
      },
      { status: 503 }
    );
  })
];

/**
 * WebSocket handlers (using MSW's experimental WebSocket support)
 */
export const websocketHandlers = [
  // Note: MSW WebSocket support is experimental
  // These handlers demonstrate the pattern but may need adjustment
  // based on MSW version and WebSocket implementation
];

/**
 * All handlers combined
 */
export const handlers = [
  ...authHandlers,
  ...sessionHandlers,
  ...userHandlers,
  ...errorHandlers,
  ...websocketHandlers
];

/**
 * Handler overrides for specific test scenarios
 */
export const scenarioHandlers = {
  // Network failure scenario
  networkFailure: [
    http.all('*', () => {
      return HttpResponse.error();
    })
  ],

  // Slow network scenario
  slowNetwork: [
    http.all('*', async () => {
      await delay(3000);
      return HttpResponse.json({ success: true });
    })
  ],

  // Unauthorized scenario
  unauthorized: [
    http.all('*', () => {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required'
          }
        },
        { status: 401 }
      );
    })
  ]
};

/**
 * Helper to create custom handlers for testing
 */
export function createCustomHandler(
  method: 'get' | 'post' | 'put' | 'patch' | 'delete',
  path: string,
  response: any,
  status: number = 200,
  delayMs: number = 0
) {
  const handler = http[method](`${API_BASE_URL}${path}`, async () => {
    if (delayMs > 0) {
      await delay(delayMs);
    }
    return HttpResponse.json(response, { status });
  });
  
  return handler;
}