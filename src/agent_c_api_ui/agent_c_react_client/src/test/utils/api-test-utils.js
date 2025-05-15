import { vi } from 'vitest'

/**
 * Creates a complete mock Response object that mimics the browser's fetch Response
 * @param {Object} data - Response data
 * @param {Object} options - Response options
 * @returns {Object} Mock Response object with all required methods
 */
export const createMockResponse = (data, options = {}) => {
  const { 
    status = 200, 
    statusText = status === 200 ? 'OK' : 'Error',
    headers = { 'content-type': 'application/json' } 
  } = options;
  
  // Convert headers object to Headers-like interface
  const headersObj = {
    get: (name) => headers[name.toLowerCase()],
    has: (name) => name.toLowerCase() in headers,
    forEach: (callback) => Object.entries(headers).forEach(([key, value]) => callback(value, key))
  };
  
  // Create JSON string of data
  const jsonData = JSON.stringify(data);
  // Create a Blob for the blob() method
  const blobData = new Blob([jsonData], { type: 'application/json' });
  
  // Return a mock Response object with all necessary methods
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText,
    headers: headersObj,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(jsonData),
    blob: () => Promise.resolve(blobData),
    arrayBuffer: () => Promise.resolve(new TextEncoder().encode(jsonData).buffer),
    formData: () => { throw new Error('formData() is not implemented in the mock response'); },
    bodyUsed: false,
    redirected: false,
    type: 'basic',
    url: ''
  };
};

/**
 * Creates a mock Response that will cause an error with the expected error message
 * @param {string} errorMessage - The error message to include
 * @param {number} status - HTTP status code
 * @returns {Object} - Mock Response that will trigger the expected error
 */
export const createErrorResponse = (errorMessage, status = 500) => {
  // Format the error response according to the API's error structure
  return createMockResponse(
    { 
      detail: { 
        message: errorMessage,
        error_code: 'TEST_ERROR',
        params: {}
      } 
    },
    { status, statusText: status === 404 ? 'Not Found' : 'Server Error' }
  );
};

/**
 * Sets up fetch mocks for the specified endpoints
 * @param {Object} mockResponses - Map of endpoints to mock responses
 * @returns {Function} - Function to restore original fetch
 */
export const setupFetchMock = (mockResponses = {}) => {
  // Save original fetch
  const originalFetch = global.fetch;
  
  // Create a mock fetch implementation
  global.fetch = vi.fn((url, options = {}) => {
    // Extract the endpoint path from the URL
    let endpoint = url;
    if (url.includes('/api/')) {
      endpoint = url.substring(url.indexOf('/api/') + 4);
    }
    
    // Check if we have a mock for this endpoint
    for (const [mockPath, mockResponse] of Object.entries(mockResponses)) {
      if (endpoint.includes(mockPath)) {
        // For error responses with status code
        if (mockResponse && typeof mockResponse === 'object' && 'status' in mockResponse && mockResponse.status >= 400) {
          return Promise.resolve(createErrorResponse(
            mockResponse.detail?.message || 'Server error',
            mockResponse.status
          ));
        }
        
        // For success responses
        return Promise.resolve(createMockResponse(mockResponse));
      }
    }
    
    // Default response if no match found
    return Promise.resolve(createMockResponse(
      { message: 'Not found' },
      { status: 404 }
    ));
  });
  
  // Return function to restore original fetch
  return () => {
    global.fetch = originalFetch;
  };
};

/**
 * Sets up a fetch mock that will reject with a network error
 * @param {string} errorMessage - The error message
 * @returns {Function} - Function to restore original fetch
 */
export const setupNetworkErrorMock = (errorMessage = 'Network error') => {
  const originalFetch = global.fetch;
  global.fetch = vi.fn().mockRejectedValue(new Error(errorMessage));
  return () => {
    global.fetch = originalFetch;
  };
};