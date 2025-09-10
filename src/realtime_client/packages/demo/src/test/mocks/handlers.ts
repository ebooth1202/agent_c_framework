/**
 * MSW Request Handlers for Demo Application
 * Comprehensive API mocking for the demo app
 */

import { http, HttpResponse, delay, ws } from 'msw';
import { faker } from '@faker-js/faker';
// Mock factories for testing
const ChatMessageFactory = {
  createUserMessage: (content: string) => ({
    id: `msg-${Date.now()}`,
    role: 'user',
    content,
    timestamp: new Date().toISOString(),
    metadata: {}
  }),
  createAssistantMessage: (content: string) => ({
    id: `msg-${Date.now()}`,
    role: 'assistant',
    content,
    timestamp: new Date().toISOString(),
    metadata: {}
  }),
  createConversation: (count: number) => {
    const messages = [];
    for (let i = 0; i < count; i++) {
      messages.push({
        id: `msg-${i}`,
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i + 1}`,
        timestamp: new Date(Date.now() - (count - i) * 60000).toISOString(),
        metadata: {}
      });
    }
    return messages;
  }
};

const TurnEventFactory = {
  create: (data: any) => ({
    type: data.type || 'turn_event',
    turn_id: `turn-${Date.now()}`,
    turn_type: data.turn_type || 'user',
    timestamp: new Date().toISOString(),
    ...data
  })
};

const ConnectionEventFactory = {
  create: (data: any) => ({
    type: data.type || 'connection_event',
    timestamp: new Date().toISOString(),
    ...data
  })
};

/**
 * API configuration
 */
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8080';
const WS_URL = process.env.VITE_WS_URL || 'ws://localhost:8080';

/**
 * Mock user data store (for demo persistence)
 */
const mockUserStore = new Map<string, any>();
const mockSessionStore = new Map<string, any>();

/**
 * Generate mock tokens
 */
function generateTokens() {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600,
  }));
  const signature = faker.string.alphanumeric(43);
  
  return {
    access_token: `${header}.${payload}.${signature}`,
    refresh_token: `refresh_${faker.string.alphanumeric(32)}`,
    heygen_token: `hg_${faker.string.alphanumeric(32)}`,
    expires_in: 3600
  };
}

/**
 * Authentication handlers for demo app
 */
export const authHandlers = [
  // Login endpoint
  http.post(`${API_BASE_URL}/api/auth/login`, async ({ request }) => {
    await delay(200); // Simulate network delay
    
    const body = await request.json() as any;
    
    // Demo validation
    if (!body.email || !body.password) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email and password are required',
            fields: {
              email: !body.email ? 'Email is required' : null,
              password: !body.password ? 'Password is required' : null
            }
          }
        },
        { status: 400 }
      );
    }

    // Demo account check
    if (body.email === 'demo@example.com' && body.password === 'demo123') {
      const userId = 'demo_user_001';
      const tokens = generateTokens();
      const sessionId = `sess_${faker.string.alphanumeric(24)}`;
      
      // Store user data
      mockUserStore.set(userId, {
        id: userId,
        email: body.email,
        name: 'Demo User',
        avatar_url: faker.image.avatar(),
        preferences: {
          theme: 'light',
          language: 'en',
          audio_enabled: true,
          notifications: true
        }
      });
      
      // Create session
      mockSessionStore.set(sessionId, {
        id: sessionId,
        user_id: userId,
        created_at: new Date().toISOString(),
        messages: [],
        is_active: true
      });
      
      return HttpResponse.json(
        {
          success: true,
          data: {
            user: mockUserStore.get(userId),
            session_id: sessionId,
            ...tokens
          }
        },
        { 
          status: 200,
          headers: {
            'Set-Cookie': `session=${sessionId}; Path=/; HttpOnly; SameSite=Lax`
          }
        }
      );
    }

    // Failed login
    return HttpResponse.json(
      {
        error: {
          code: 'INVALID_CREDENTIALS',
          message: 'Invalid email or password',
          details: {
            attempts_remaining: 3
          }
        }
      },
      { status: 401 }
    );
  }),

  // Signup endpoint
  http.post(`${API_BASE_URL}/api/auth/signup`, async ({ request }) => {
    await delay(300);
    
    const body = await request.json() as any;
    
    if (!body.email || !body.password || !body.name) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'All fields are required',
            fields: {
              email: !body.email ? 'Email is required' : null,
              password: !body.password ? 'Password is required' : null,
              name: !body.name ? 'Name is required' : null
            }
          }
        },
        { status: 400 }
      );
    }

    // Check if email already exists
    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        {
          error: {
            code: 'EMAIL_EXISTS',
            message: 'An account with this email already exists'
          }
        },
        { status: 409 }
      );
    }

    const userId = faker.string.uuid();
    const tokens = generateTokens();
    const sessionId = `sess_${faker.string.alphanumeric(24)}`;
    
    const newUser = {
      id: userId,
      email: body.email,
      name: body.name,
      avatar_url: faker.image.avatar(),
      created_at: new Date().toISOString()
    };
    
    mockUserStore.set(userId, newUser);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          user: newUser,
          session_id: sessionId,
          ...tokens
        }
      },
      { status: 201 }
    );
  }),

  // Token refresh
  http.post(`${API_BASE_URL}/api/auth/refresh`, async ({ request }) => {
    await delay(100);
    
    const body = await request.json() as any;
    
    if (!body.refresh_token) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_TOKEN',
            message: 'Refresh token is required'
          }
        },
        { status: 400 }
      );
    }

    const tokens = generateTokens();
    
    return HttpResponse.json(
      {
        success: true,
        data: tokens
      },
      { status: 200 }
    );
  }),

  // Logout
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
          'Set-Cookie': 'session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'
        }
      }
    );
  })
];

/**
 * Chat and session handlers
 */
export const chatHandlers = [
  // Get chat history
  http.get(`${API_BASE_URL}/api/chat/history`, async ({ request }) => {
    await delay(150);
    
    const url = new URL(request.url);
    const sessionId = url.searchParams.get('session_id');
    
    if (!sessionId) {
      return HttpResponse.json(
        {
          error: {
            code: 'MISSING_SESSION',
            message: 'Session ID is required'
          }
        },
        { status: 400 }
      );
    }

    const session = mockSessionStore.get(sessionId);
    
    if (!session) {
      return HttpResponse.json(
        {
          error: {
            code: 'SESSION_NOT_FOUND',
            message: 'Session not found'
          }
        },
        { status: 404 }
      );
    }

    // Generate some demo messages if empty
    if (session.messages.length === 0) {
      session.messages = ChatMessageFactory.createConversation(3);
    }

    return HttpResponse.json(
      {
        success: true,
        data: {
          session_id: sessionId,
          messages: session.messages,
          metadata: {
            total_messages: session.messages.length,
            last_message_at: session.messages[session.messages.length - 1]?.timestamp
          }
        }
      },
      { status: 200 }
    );
  }),

  // Send message
  http.post(`${API_BASE_URL}/api/chat/send`, async ({ request }) => {
    await delay(100);
    
    const body = await request.json() as any;
    
    if (!body.message || !body.session_id) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message: 'Message and session ID are required'
          }
        },
        { status: 400 }
      );
    }

    const session = mockSessionStore.get(body.session_id);
    
    if (!session) {
      return HttpResponse.json(
        {
          error: {
            code: 'SESSION_NOT_FOUND',
            message: 'Session not found'
          }
        },
        { status: 404 }
      );
    }

    const userMessage = ChatMessageFactory.createUserMessage(body.message);
    session.messages.push(userMessage);
    
    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage = ChatMessageFactory.createAssistantMessage(
        `I received your message: "${body.message}". How can I help you further?`
      );
      session.messages.push(assistantMessage);
    }, 500);

    return HttpResponse.json(
      {
        success: true,
        data: {
          message_id: userMessage.id,
          timestamp: userMessage.timestamp
        }
      },
      { status: 200 }
    );
  }),

  // Clear chat history
  http.delete(`${API_BASE_URL}/api/chat/history/:sessionId`, async ({ params }) => {
    await delay(50);
    
    const { sessionId } = params;
    const session = mockSessionStore.get(sessionId as string);
    
    if (session) {
      session.messages = [];
    }

    return HttpResponse.json(
      {
        success: true,
        message: 'Chat history cleared'
      },
      { status: 200 }
    );
  })
];

/**
 * User profile and settings handlers
 */
export const userHandlers = [
  // Get user profile
  http.get(`${API_BASE_URL}/api/user/profile`, async ({ request }) => {
    await delay(100);
    
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader) {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required'
          }
        },
        { status: 401 }
      );
    }

    // Return demo user profile
    const demoUser = mockUserStore.get('demo_user_001') || {
      id: 'demo_user_001',
      email: 'demo@example.com',
      name: 'Demo User',
      avatar_url: faker.image.avatar(),
      preferences: {
        theme: 'light',
        language: 'en',
        audio_enabled: true,
        notifications: true
      },
      created_at: faker.date.past().toISOString()
    };

    return HttpResponse.json(
      {
        success: true,
        data: demoUser
      },
      { status: 200 }
    );
  }),

  // Update user profile
  http.patch(`${API_BASE_URL}/api/user/profile`, async ({ request }) => {
    await delay(100);
    
    const body = await request.json() as any;
    const userId = 'demo_user_001';
    const user = mockUserStore.get(userId);
    
    if (user) {
      Object.assign(user, body);
      user.updated_at = new Date().toISOString();
    }

    return HttpResponse.json(
      {
        success: true,
        data: user || body
      },
      { status: 200 }
    );
  }),

  // Get user settings
  http.get(`${API_BASE_URL}/api/user/settings`, async () => {
    await delay(50);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          theme: 'light',
          language: 'en',
          audio: {
            enabled: true,
            input_device: 'default',
            output_device: 'default',
            echo_cancellation: true,
            noise_suppression: true,
            auto_gain_control: true
          },
          notifications: {
            enabled: true,
            sound: true,
            desktop: false
          },
          privacy: {
            save_history: true,
            analytics: false
          }
        }
      },
      { status: 200 }
    );
  }),

  // Update user settings
  http.put(`${API_BASE_URL}/api/user/settings`, async ({ request }) => {
    await delay(100);
    
    const body = await request.json() as any;
    
    return HttpResponse.json(
      {
        success: true,
        data: body
      },
      { status: 200 }
    );
  })
];

/**
 * WebSocket handlers for real-time communication
 */
export const websocketHandlers = [
  // Main WebSocket connection for chat
  ws.link(`${WS_URL}/ws/:sessionId`).addEventListener('connection', ({ client, params }) => {
    const { sessionId } = params;
    
    // Send connection established event
    client.send(JSON.stringify(
      ConnectionEventFactory.create({
        type: 'connected',
        session_id: sessionId as string
      })
    ));

    // Listen for client messages
    client.addEventListener('message', (event) => {
      const data = event.data;
      
      if (typeof data === 'string') {
        try {
          const message = JSON.parse(data);
          
          // Echo back text messages with assistant response
          if (message.type === 'text_input') {
            // Send user turn start
            client.send(JSON.stringify(
              TurnEventFactory.create({
                type: 'turn_start',
                turn_type: 'user'
              })
            ));

            // Echo user message
            client.send(JSON.stringify(
              ChatMessageFactory.createUserMessage(message.text)
            ));

            // Send user turn end
            setTimeout(() => {
              client.send(JSON.stringify(
                TurnEventFactory.create({
                  type: 'turn_end',
                  turn_type: 'user'
                })
              ));
            }, 100);

            // Send assistant response
            setTimeout(() => {
              // Assistant turn start
              client.send(JSON.stringify(
                TurnEventFactory.create({
                  type: 'turn_start',
                  turn_type: 'assistant'
                })
              ));

              // Assistant message
              client.send(JSON.stringify(
                ChatMessageFactory.createAssistantMessage(
                  `I understand you said: "${message.text}". How can I help you?`
                )
              ));

              // Assistant turn end
              client.send(JSON.stringify(
                TurnEventFactory.create({
                  type: 'turn_end',
                  turn_type: 'assistant'
                })
              ));
            }, 500);
          }
        } catch (error) {
          // Invalid JSON
          client.send(JSON.stringify({
            type: 'error',
            error: {
              code: 'INVALID_MESSAGE',
              message: 'Invalid message format'
            }
          }));
        }
      } else {
        // Handle binary audio data
        // For demo, just acknowledge receipt
        client.send(JSON.stringify({
          type: 'audio_received',
          size: data.byteLength
        }));
      }
    });

    // Handle client close
    client.addEventListener('close', () => {
      console.log(`WebSocket closed for session: ${sessionId}`);
    });
  })
];

/**
 * Analytics and tracking handlers (for demo app analytics)
 */
export const analyticsHandlers = [
  // Track events
  http.post(`${API_BASE_URL}/api/analytics/track`, async ({ request }) => {
    const body = await request.json() as any;
    
    console.log('Analytics event:', body);
    
    return HttpResponse.json(
      {
        success: true,
        event_id: faker.string.uuid()
      },
      { status: 200 }
    );
  }),

  // Page view tracking
  http.post(`${API_BASE_URL}/api/analytics/pageview`, async ({ request }) => {
    const body = await request.json() as any;
    
    console.log('Page view:', body);
    
    return HttpResponse.json(
      {
        success: true
      },
      { status: 200 }
    );
  })
];

/**
 * Error scenario handlers
 */
export const errorHandlers = [
  // Network timeout simulation
  http.get(`${API_BASE_URL}/api/timeout/*`, async () => {
    await delay(30000); // 30 second delay to trigger timeout
    return HttpResponse.json({ success: false });
  }),

  // Rate limiting
  http.all(`${API_BASE_URL}/api/rate-limited/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'RATE_LIMIT',
          message: 'Too many requests',
          details: {
            limit: 60,
            remaining: 0,
            reset_at: faker.date.soon().toISOString()
          }
        }
      },
      { 
        status: 429,
        headers: {
          'X-RateLimit-Limit': '60',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': faker.date.soon().toISOString()
        }
      }
    );
  }),

  // Server error
  http.all(`${API_BASE_URL}/api/error/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'SERVER_ERROR',
          message: 'Internal server error',
          request_id: faker.string.uuid()
        }
      },
      { status: 500 }
    );
  })
];

/**
 * Health check handler
 */
export const healthHandlers = [
  http.get(`${API_BASE_URL}/health`, () => {
    return HttpResponse.json(
      {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      },
      { status: 200 }
    );
  })
];

/**
 * All handlers combined
 */
export const handlers = [
  ...authHandlers,
  ...chatHandlers,
  ...userHandlers,
  ...websocketHandlers,
  ...analyticsHandlers,
  ...errorHandlers,
  ...healthHandlers
];

/**
 * Demo-specific scenario handlers
 */
export const demoScenarios = {
  // Logged in user scenario
  loggedInUser: () => {
    const userId = 'demo_user_001';
    const sessionId = 'demo_session_001';
    
    // Pre-populate stores
    mockUserStore.set(userId, {
      id: userId,
      email: 'demo@example.com',
      name: 'Demo User',
      avatar_url: faker.image.avatar()
    });
    
    mockSessionStore.set(sessionId, {
      id: sessionId,
      user_id: userId,
      messages: ChatMessageFactory.createConversation(5),
      is_active: true
    });
    
    return { userId, sessionId };
  },

  // Clear all data
  reset: () => {
    mockUserStore.clear();
    mockSessionStore.clear();
  }
};