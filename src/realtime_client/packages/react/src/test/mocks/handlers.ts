/**
 * MSW Request Handlers for React Package
 * Mock API endpoints for React hooks and components testing
 */

import { http, HttpResponse, delay } from 'msw';
import { faker } from '@faker-js/faker';

/**
 * Base API URL
 */
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8080';

/**
 * Mock session data for React components
 */
const mockSessionData = {
  session_id: 'test_session_001',
  user_id: 'test_user_001',
  created_at: new Date().toISOString(),
  is_active: true,
  metadata: {
    client_version: '1.0.0',
    device_type: 'web'
  }
};

/**
 * Session management handlers for React hooks
 */
export const sessionHandlers = [
  // Get current session
  http.get(`${API_BASE_URL}/api/session/current`, async () => {
    await delay(50);
    
    return HttpResponse.json(
      {
        success: true,
        data: mockSessionData
      },
      { status: 200 }
    );
  }),

  // Create new session
  http.post(`${API_BASE_URL}/api/session/create`, async () => {
    await delay(100);
    
    const newSession = {
      ...mockSessionData,
      session_id: `sess_${faker.string.alphanumeric(24)}`,
      created_at: new Date().toISOString()
    };
    
    return HttpResponse.json(
      {
        success: true,
        data: newSession
      },
      { status: 201 }
    );
  }),

  // Update session
  http.patch(`${API_BASE_URL}/api/session/:id`, async ({ params, request }) => {
    await delay(50);
    
    const { id } = params;
    const body = await request.json() as any;
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          ...mockSessionData,
          session_id: id,
          ...body,
          updated_at: new Date().toISOString()
        }
      },
      { status: 200 }
    );
  })
];

/**
 * Audio configuration handlers
 */
export const audioHandlers = [
  // Get audio devices
  http.get(`${API_BASE_URL}/api/audio/devices`, async () => {
    await delay(50);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          input_devices: [
            { id: 'default', label: 'Default Microphone' },
            { id: 'mic_001', label: 'External Microphone' }
          ],
          output_devices: [
            { id: 'default', label: 'Default Speakers' },
            { id: 'headphones_001', label: 'Headphones' }
          ]
        }
      },
      { status: 200 }
    );
  }),

  // Update audio settings
  http.post(`${API_BASE_URL}/api/audio/settings`, async ({ request }) => {
    await delay(50);
    
    const body = await request.json() as any;
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          ...body,
          applied_at: new Date().toISOString()
        }
      },
      { status: 200 }
    );
  })
];

/**
 * Connection status handlers
 */
export const connectionHandlers = [
  // Get connection status
  http.get(`${API_BASE_URL}/api/connection/status`, async () => {
    await delay(30);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          status: 'connected',
          latency: faker.number.int({ min: 10, max: 100 }),
          quality: 'excellent',
          region: 'us-west-2'
        }
      },
      { status: 200 }
    );
  }),

  // Test connection
  http.post(`${API_BASE_URL}/api/connection/test`, async () => {
    await delay(200);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          latency: faker.number.int({ min: 10, max: 100 }),
          packet_loss: faker.number.float({ min: 0, max: 0.05 }),
          jitter: faker.number.float({ min: 0, max: 10 })
        }
      },
      { status: 200 }
    );
  })
];

/**
 * User preferences handlers
 */
export const preferencesHandlers = [
  // Get preferences
  http.get(`${API_BASE_URL}/api/preferences`, async () => {
    await delay(50);
    
    return HttpResponse.json(
      {
        success: true,
        data: {
          theme: 'light',
          language: 'en',
          audio_enabled: true,
          auto_connect: false,
          save_history: true
        }
      },
      { status: 200 }
    );
  }),

  // Update preferences
  http.put(`${API_BASE_URL}/api/preferences`, async ({ request }) => {
    await delay(50);
    
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
 * Error handlers for testing error states
 */
export const errorHandlers = [
  // Unauthorized
  http.get(`${API_BASE_URL}/api/unauthorized/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required'
        }
      },
      { status: 401 }
    );
  }),

  // Not found
  http.get(`${API_BASE_URL}/api/notfound/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'NOT_FOUND',
          message: 'Resource not found'
        }
      },
      { status: 404 }
    );
  }),

  // Server error
  http.all(`${API_BASE_URL}/api/error/*`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Internal server error'
        }
      },
      { status: 500 }
    );
  })
];

/**
 * All handlers combined
 */
export const handlers = [
  ...sessionHandlers,
  ...audioHandlers,
  ...connectionHandlers,
  ...preferencesHandlers,
  ...errorHandlers
];

/**
 * Test scenario handlers
 */
export const testScenarios = {
  // Disconnected state
  disconnected: [
    http.get(`${API_BASE_URL}/api/connection/status`, () => {
      return HttpResponse.json(
        {
          success: true,
          data: {
            status: 'disconnected',
            reason: 'Connection lost'
          }
        },
        { status: 200 }
      );
    })
  ],

  // Poor connection
  poorConnection: [
    http.get(`${API_BASE_URL}/api/connection/status`, () => {
      return HttpResponse.json(
        {
          success: true,
          data: {
            status: 'connected',
            latency: faker.number.int({ min: 200, max: 500 }),
            quality: 'poor',
            packet_loss: 0.15
          }
        },
        { status: 200 }
      );
    })
  ],

  // No audio devices
  noAudioDevices: [
    http.get(`${API_BASE_URL}/api/audio/devices`, () => {
      return HttpResponse.json(
        {
          success: true,
          data: {
            input_devices: [],
            output_devices: []
          }
        },
        { status: 200 }
      );
    })
  ]
};