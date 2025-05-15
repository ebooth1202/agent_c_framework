import { http, HttpResponse } from 'msw'

// Base API URL (should match the one used in your API service)
const API_BASE_URL = '/api/v2'

// Add your API endpoint mocks here
export const handlers = [
  // Example handler for a GET request
  http.get(`${API_BASE_URL}/config`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        features: { rag: true, chat: true },
        settings: { maxTokens: 2000 }
      }
    })
  }),
  
  // Example handler for a POST request
  http.post(`${API_BASE_URL}/chat`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: '123',
        message: 'This is a mocked response'
      }
    })
  }),
  
  // Fallback handler for any unhandled requests
  http.get('*', ({ request }) => {
    console.warn(`Unhandled request: ${request.method} ${request.url}`)
    return HttpResponse.json(
      { 
        success: false, 
        detail: { message: 'No handler found for this request' } 
      },
      { status: 404 }
    )
  })
]