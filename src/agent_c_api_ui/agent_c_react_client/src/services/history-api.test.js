import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as historyApi from './history-api'
import { setupFetchMock, setupNetworkErrorMock, createMockResponse } from '../test/utils/api-test-utils'

describe('History API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  let originalFetch;
  
  beforeEach(() => {
    // Save original fetch before each test
    originalFetch = global.fetch;
  });
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
    
    // Make sure fetch is always restored
    global.fetch = originalFetch;
  })

  describe('listHistories', () => {
    it('should list histories successfully', async () => {
      // Mock response data
      const mockData = {
        success: true,
        data: {
          items: [
            {
              session_id: 'tiger-castle',
              name: 'Task Planning Session',
              created_at: '2025-04-01T14:30:00Z',
              updated_at: '2025-04-01T15:45:00Z',
              message_count: 24,
              duration: 4500
            },
            {
              session_id: 'blue-ocean',
              name: 'Code Review Session',
              created_at: '2025-04-02T09:15:00Z',
              updated_at: '2025-04-02T10:30:00Z',
              message_count: 18,
              duration: 4200
            }
          ],
          total: 42,
          limit: 20,
          offset: 0
        },
        meta: {
          pagination: {
            total: 42,
            limit: 20,
            offset: 0
          }
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        '/history': mockData
      });

      // Call the API method
      const result = await historyApi.listHistories({ limit: 20 })

      // Assert the result matches our expectations
      expect(result.histories).toHaveLength(2)
      expect(result.pagination.total).toBe(42)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle API errors', async () => {
      // Setup a server error response
      restoreFetch = setupFetchMock({
        '/history': {
          detail: { message: 'Server error' },
          status: 500
        }
      });

      // The API call should throw an error
      await expect(historyApi.listHistories()).rejects.toThrow('Server error')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getHistoryDetails', () => {
    it('should fetch history details successfully', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        success: true,
        data: {
          session_id: sessionId,
          name: 'Task Planning Session',
          created_at: '2025-04-01T14:30:00Z',
          updated_at: '2025-04-01T15:45:00Z',
          message_count: 24,
          duration: 4500,
          files: ['events_3fa85f64_1.jsonl', 'events_3fa85f64_2.jsonl'],
          event_types: {
            text_delta: 120,
            tool_call: 15,
            user_request: 12,
            thinking: 30
          },
          metadata: {
            model: 'gpt-4-turbo',
            completion_tokens: 4820,
            prompt_tokens: 1650
          }
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}`]: mockData
      });

      // Call the API method
      const result = await historyApi.getHistoryDetails(sessionId)

      // Assert the result matches our expectations
      expect(result.session_id).toBe(sessionId)
      expect(result.message_count).toBe(24)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle non-existent history', async () => {
      const sessionId = 'non-existent';
      
      // Setup a not found response
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}`]: {
          detail: { message: 'History not found' },
          status: 404
        }
      });

      // The API call should throw an error
      await expect(historyApi.getHistoryDetails(sessionId)).rejects.toThrow('History not found')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getEvents', () => {
    it('should fetch events successfully', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        success: true,
        data: [
          {
            id: 'evt_1234567890',
            timestamp: '2025-04-01T14:32:15Z',
            event: {
              event_type: 'message',
              role: 'user',
              content: 'Can you help me analyze this dataset?',
              message_id: 'msg_abcdef123456'
            }
          },
          {
            id: 'evt_0987654321',
            timestamp: '2025-04-01T14:35:42Z',
            event: {
              event_type: 'tool_call',
              tool_name: 'data_analysis',
              input: {
                file_path: 'data.csv',
                operation: 'summary_statistics'
              },
              call_id: 'call_defabc456789'
            }
          }
        ],
        meta: {
          pagination: {
            page: 1,
            page_size: 50,
            total_items: 120,
            total_pages: 3
          }
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/events`]: mockData
      });

      // Call the API method with options
      const options = {
        event_types: ['message', 'tool_call'],
        limit: 50
      };
      const result = await historyApi.getEvents(sessionId, options)

      // Assert the result matches our expectations
      expect(result.events).toHaveLength(2)
      expect(result.pagination.total_items).toBe(120)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getReplayStatus', () => {
    it('should fetch replay status successfully', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        success: true,
        data: {
          session_id: sessionId,
          is_playing: true,
          current_position: '2025-04-01T14:40:15Z',
          start_time: '2025-04-01T14:30:00Z',
          end_time: '2025-04-01T15:45:00Z'
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/replay`]: mockData
      });

      // Call the API method
      const result = await historyApi.getReplayStatus(sessionId)

      // Assert the result matches our expectations
      expect(result.session_id).toBe(sessionId)
      expect(result.is_playing).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('controlReplay', () => {
    it('should control replay successfully', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        success: true,
        data: true,
        message: "Replay control 'play' successful"
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/replay`]: mockData
      });

      // Call the API method to start playback
      const result = await historyApi.controlReplay(sessionId, 'play', { speed: 2.0 })

      // Assert the result matches our expectations
      expect(result).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle seek operation', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        success: true,
        data: true,
        message: "Replay control 'seek' successful"
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/replay`]: mockData
      });

      // Call the API method to seek to position
      const position = '2025-04-01T14:35:00Z';
      const result = await historyApi.controlReplay(sessionId, 'seek', { position })

      // Assert the result matches our expectations
      expect(result).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle errors', async () => {
      const sessionId = 'tiger-castle';
      
      // Setup an error response
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/replay`]: {
          detail: { message: 'Invalid action' },
          status: 400
        }
      });

      // The API call should throw an error
      await expect(historyApi.controlReplay(sessionId, 'invalid_action')).rejects.toThrow('Invalid action')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('deleteHistory', () => {
    it('should delete history successfully', async () => {
      const sessionId = 'tiger-castle';
      const mockData = {
        status: {
          success: true,
          message: 'Session history deleted successfully',
          error_code: null
        },
        data: {
          status: 'success', 
          message: `Session history tiger-castle deleted successfully`
        }
      }

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}`]: mockData
      });

      // Call the API method
      const result = await historyApi.deleteHistory(sessionId)

      // Assert the result matches our expectations
      expect(result).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle 204 No Content response', async () => {
      const sessionId = 'tiger-castle';
      
      // Mock the global fetch with a 204 No Content response
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
        statusText: 'No Content',
        headers: {
          get: () => null // No content-type for 204 responses
        },
        // No json() method needed for 204 responses
        text: () => Promise.resolve('')
      });
      
      restoreFetch = () => { global.fetch = originalFetch; };
      
      // Call the API method
      const result = await historyApi.deleteHistory(sessionId);

      // Assert the result matches our expectations
      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle errors', async () => {
      const sessionId = 'tiger-castle';
      
      // Setup an error response
      restoreFetch = setupFetchMock({
        [`/history/${sessionId}`]: {
          detail: { message: 'History not found' },
          status: 404
        }
      });

      // The API call should throw an error
      await expect(historyApi.deleteHistory(sessionId)).rejects.toThrow('History not found')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })
})