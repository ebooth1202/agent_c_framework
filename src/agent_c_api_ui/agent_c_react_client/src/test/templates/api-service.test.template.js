import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as apiService from '../../services/your-api-service' // Update this import
import { setupFetchMock, setupNetworkErrorMock } from '../utils/api-test-utils'

describe('Your API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  })

  describe('yourApiMethod', () => {
    it('should fetch data successfully', async () => {
      // Mock response data
      const mockData = {
        success: true,
        data: {
          id: '123',
          name: 'Test Item',
          properties: ['a', 'b', 'c']
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        '/your/endpoint': mockData
      });

      // Call the API method
      const result = await apiService.yourApiMethod()

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle API errors', async () => {
      // Setup a server error response
      restoreFetch = setupFetchMock({
        '/your/endpoint': {
          detail: { message: 'Server error' },
          status: 500
        }
      });

      // The API call should throw an error
      await expect(apiService.yourApiMethod()).rejects.toThrow('Server error')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should send correct parameters', async () => {
      // Mock response data
      const mockData = {
        success: true,
        data: { result: 'success' }
      }

      // Capture the request options
      let capturedUrl;
      let capturedOptions;
      
      // Setup a custom mock to capture the request
      const originalFetch = global.fetch;
      global.fetch = vi.fn((url, options) => {
        capturedUrl = url;
        capturedOptions = options;
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockData),
          headers: {
            get: () => 'application/json'
          }
        });
      });
      
      restoreFetch = () => { global.fetch = originalFetch; };

      // Test parameters
      const params = { id: '123', value: 'test' };
      
      // Call the API method with parameters
      await apiService.yourApiMethod(params);

      // Verify the URL and parameters were correct
      expect(capturedUrl).toContain('/your/endpoint');
      // If it's a POST request with JSON body:
      if (capturedOptions?.body) {
        const parsedBody = JSON.parse(capturedOptions.body);
        expect(parsedBody).toEqual(params);
      }
      
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })
})