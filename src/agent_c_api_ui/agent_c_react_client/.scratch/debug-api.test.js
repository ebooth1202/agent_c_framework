import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as debugApi from './debug-api'
import { setupFetchMock, setupNetworkErrorMock } from '../src/test/utils/api-test-utils'

describe('Debug API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  })

  describe('getSessionDebugInfo', () => {
    it('should fetch session debug information successfully', async () => {
      const sessionId = 'test-session-123';
      
      // Mock response data based on API documentation
      const mockData = {
        status: {
          success: true,
          message: "Session debug information retrieved successfully"
        },
        data: {
          session_id: "ui-sess-def456",
          agent_c_session_id: "internal-sess-xyz789",
          agent_name: "Tech Support Agent",
          created_at: "2025-05-04T13:45:22Z",
          backend: "openai",
          model_name: "gpt-4",
          session_manager: {
            exists: true,
            user_id: "user-12345",
            has_chat_session: true
          },
          chat_session: {
            session_id: "chat-sess-abc123",
            has_active_memory: true
          },
          messages: {
            count: 7,
            user_messages: 3,
            assistant_messages: 4,
            latest_message: "I'll analyze that code snippet now..."
          },
          recent_messages: [
            {
              role: "user",
              content_preview: "Can you help me debug my Python code...",
              timestamp: "2025-05-04T14:22:15Z"
            },
            {
              role: "assistant",
              content_preview: "I'd be happy to help with your Python code...",
              timestamp: "2025-05-04T14:22:45Z"
            }
          ],
          current_chat_Log: {
            exists: true,
            count: 12
          },
          tool_chest: {
            exists: true,
            active_tools: ["web_search", "code_interpreter", "file_browser"]
          }
        }
      };

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/debug/sessions/${sessionId}`]: mockData
      });

      // Call the API method
      const result = await debugApi.getSessionDebugInfo(sessionId);

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle API errors', async () => {
      const sessionId = 'invalid-session';
      
      // Setup a server error response
      restoreFetch = setupFetchMock({
        [`/debug/sessions/${sessionId}`]: {
          detail: { message: 'Session not found' },
          status: 404
        }
      });

      // The API call should throw an error
      await expect(debugApi.getSessionDebugInfo(sessionId)).rejects.toThrow('Session not found');
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle network errors', async () => {
      const sessionId = 'test-session-123';
      
      // Setup a network error
      restoreFetch = setupNetworkErrorMock('Network error');

      // The API call should throw an error
      await expect(debugApi.getSessionDebugInfo(sessionId)).rejects.toThrow('Network error');
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })

  describe('getAgentDebugInfo', () => {
    it('should fetch agent debug information successfully', async () => {
      const sessionId = 'test-session-123';
      
      // Mock response data based on API documentation
      const mockData = {
        status: {
          success: true,
          message: "Agent debug information retrieved successfully"
        },
        data: {
          status: "success",
          agent_bridge_params: {
            temperature: 0.7,
            reasoning_effort: "thorough",
            extended_thinking: true,
            budget_tokens: 8000,
            max_tokens: 4000
          },
          internal_agent_params: {
            type: "ReactJSAgent",
            temperature: 0.5,
            reasoning_effort: "thorough",
            budget_tokens: 8000,
            max_tokens: 4000
          }
        }
      };

      // Setup fetch mock for this test
      restoreFetch = setupFetchMock({
        [`/debug/agent/${sessionId}`]: mockData
      });

      // Call the API method
      const result = await debugApi.getAgentDebugInfo(sessionId);

      // Assert the result matches our mock data
      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle API errors when agent not found', async () => {
      const sessionId = 'invalid-session';
      
      // Setup a server error response
      restoreFetch = setupFetchMock({
        [`/debug/agent/${sessionId}`]: {
          detail: { message: 'Agent or session not found' },
          status: 404
        }
      });

      // The API call should throw an error
      await expect(debugApi.getAgentDebugInfo(sessionId)).rejects.toThrow('Agent or session not found');
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle unauthorized access', async () => {
      const sessionId = 'test-session-123';
      
      // Setup an unauthorized error response
      restoreFetch = setupFetchMock({
        [`/debug/agent/${sessionId}`]: {
          detail: { message: 'Unauthorized access to debug endpoints' },
          status: 403
        }
      });

      // The API call should throw an error
      await expect(debugApi.getAgentDebugInfo(sessionId)).rejects.toThrow('Unauthorized access to debug endpoints');
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })
})