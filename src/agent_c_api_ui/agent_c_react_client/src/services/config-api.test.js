import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as configApi from './config-api'
import { setupFetchMock, setupNetworkErrorMock } from '../test/utils/api-test-utils'

describe('Config API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  })

  describe('getModels', () => {
    it('should fetch models successfully', async () => {
      // Mock response data
      const mockData = {
        success: true,
        data: [
          { id: 'model1', name: 'GPT-4', description: 'Advanced model' },
          { id: 'model2', name: 'Claude 2', description: 'Fast model' }
        ]
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        '/config/models': mockData
      });

      // Call the API method
      const result = await configApi.getModels()

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle API errors', async () => {
      // Setup a server error response
      restoreFetch = setupFetchMock({
        '/config/models': {
          detail: { message: 'Server error' },
          status: 500
        }
      });

      // The API call should throw an error
      await expect(configApi.getModels()).rejects.toThrow('Server error')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle network errors', async () => {
      // Setup a network error
      restoreFetch = setupNetworkErrorMock('Network error');

      // The API call should throw an error
      await expect(configApi.getModels()).rejects.toThrow('Network error')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getSystemConfig', () => {
    it('should fetch system configuration successfully', async () => {
      // Mock response data
      const mockData = {
        success: true,
        data: {
          models: [
            { id: 'model1', name: 'GPT-4' }
          ],
          personas: [
            { id: 'persona1', name: 'Assistant' }
          ],
          tools: [
            { id: 'tool1', name: 'Calculator' }
          ]
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        '/config/system': mockData
      });

      // Call the API method
      const result = await configApi.getSystemConfig()

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getModelDetails', () => {
    it('should fetch model details successfully', async () => {
      const modelId = 'model1';
      const mockData = {
        success: true,
        data: {
          id: modelId,
          name: 'GPT-4',
          description: 'Advanced AI model',
          capabilities: ['chat', 'completion']
        }
      }

      // Setup fetch mock for this test - using specific path
      restoreFetch = setupFetchMock({
        [`/config/models/${modelId}`]: mockData
      });

      // Call the API method
      const result = await configApi.getModelDetails(modelId)

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle non-existent model IDs', async () => {
      const modelId = 'non-existent';
      
      // Setup a not found response with the correct error format
      restoreFetch = setupFetchMock({
        '/config/models/${modelId}': {
          detail: {
            message: 'Not found',
            error_code: 'MODEL_NOT_FOUND',
            params: { model_id: modelId }
          },
          status: 404
        }
      });

      // The API call should throw an error
      await expect(configApi.getModelDetails(modelId)).rejects.toThrow('Not found')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })
})