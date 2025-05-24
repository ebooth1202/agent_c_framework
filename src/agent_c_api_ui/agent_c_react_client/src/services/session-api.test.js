import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as sessionApi from './session-api'
import { setupFetchMock, setupNetworkErrorMock } from '../test/utils/api-test-utils'

describe('Session API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  })

  describe('createSession (v2)', () => {
    it('should create a session successfully', async () => {
      const mockData = {
        data: {
          id: 'session-123',
          model_id: 'gpt-4',
          persona_id: 'default',
          temperature: 0.7,
          name: 'Test Session',
          created_at: '2025-05-23T21:00:00Z'
        }
      }

      restoreFetch = setupFetchMock({
        '/sessions': mockData
      });

      const config = {
        model_id: 'gpt-4',
        persona_id: 'default',
        temperature: 0.7,
        name: 'Test Session'
      };

      const result = await sessionApi.createSession(config)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle API errors', async () => {
      restoreFetch = setupFetchMock({
        '/sessions': {
          detail: { message: 'Invalid model ID' },
          status: 400
        }
      });

      const config = { model_id: 'invalid-model' };
      await expect(sessionApi.createSession(config)).rejects.toThrow('Invalid model ID')
    })
  })

  describe('initialize (v1 compatibility)', () => {
    it('should initialize a session with v1 parameters', async () => {
      const mockData = {
        data: {
          id: 'session-123',
          model_id: 'gpt-4',
          persona_id: 'default',
          temperature: 0.7,
          name: 'Session'
        }
      }

      restoreFetch = setupFetchMock({
        '/sessions': mockData
      });

      const config = {
        model_name: 'gpt-4',
        persona_name: 'default',
        temperature: 0.7
      };

      const result = await sessionApi.initialize(config)

      expect(result).toEqual({
        ui_session_id: 'session-123',
        ...mockData.data
      })
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getSession', () => {
    it('should retrieve a session successfully', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          id: sessionId,
          model_id: 'gpt-4',
          persona_id: 'default',
          temperature: 0.7,
          name: 'Test Session'
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: mockData
      });

      const result = await sessionApi.getSession(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle session not found', async () => {
      const sessionId = 'nonexistent';
      
      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: {
          detail: { message: 'Session not found' },
          status: 404
        }
      });

      await expect(sessionApi.getSession(sessionId)).rejects.toThrow('Session not found')
    })
  })

  describe('verifySession (v1 compatibility)', () => {
    it('should verify an existing session', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          id: sessionId,
          model_id: 'gpt-4',
          valid: true
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: mockData
      });

      const result = await sessionApi.verifySession(sessionId)

      expect(result).toEqual({
        valid: true,
        session: mockData.data
      })
    })

    it('should return invalid for non-existent session', async () => {
      const sessionId = 'nonexistent';
      
      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: {
          detail: { message: 'Session not found' },
          status: 404
        }
      });

      const result = await sessionApi.verifySession(sessionId)

      expect(result).toEqual({ valid: false })
    })
  })

  describe('listSessions', () => {
    it('should list sessions with pagination', async () => {
      const mockData = {
        data: {
          items: [
            { id: 'session-1', name: 'Session 1' },
            { id: 'session-2', name: 'Session 2' }
          ],
          total: 2,
          limit: 10,
          offset: 0
        }
      }

      restoreFetch = setupFetchMock({
        '/sessions': mockData
      });

      const result = await sessionApi.listSessions({ limit: 10, offset: 0 })

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('updateSession', () => {
    it('should update a session successfully', async () => {
      const sessionId = 'session-123';
      const updateData = { name: 'Updated Session' };
      const mockData = {
        data: {
          id: sessionId,
          name: 'Updated Session',
          model_id: 'gpt-4'
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: mockData
      });

      const result = await sessionApi.updateSession(sessionId, updateData)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('deleteSession', () => {
    it('should delete a session successfully', async () => {
      const sessionId = 'session-123';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: { status: 204 }
      });

      const result = await sessionApi.deleteSession(sessionId)

      expect(result).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle deletion errors', async () => {
      const sessionId = 'session-123';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: {
          detail: { message: 'Session not found' },
          status: 404
        }
      });

      await expect(sessionApi.deleteSession(sessionId)).rejects.toThrow('Session not found')
    })
  })

  describe('deleteAllSessions (v1 compatibility)', () => {
    it('should delete all sessions', async () => {
      const mockListData = {
        data: {
          items: [
            { id: 'session-1' },
            { id: 'session-2' }
          ]
        }
      }

      restoreFetch = setupFetchMock({
        '/sessions': mockListData,
        '/sessions/session-1': { status: 204 },
        '/sessions/session-2': { status: 204 }
      });

      const result = await sessionApi.deleteAllSessions()

      expect(result).toEqual({ deleted_count: 2 })
      expect(global.fetch).toHaveBeenCalledTimes(3) // 1 list + 2 deletes
    })
  })

  describe('getAgentConfig', () => {
    it('should retrieve agent configuration', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          persona_id: 'default',
          temperature: 0.7,
          parameters: {}
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/agent`]: mockData
      });

      const result = await sessionApi.getAgentConfig(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('updateAgentConfig', () => {
    it('should update agent configuration', async () => {
      const sessionId = 'session-123';
      const updateData = { temperature: 0.8 };
      const mockData = {
        data: {
          persona_id: 'default',
          temperature: 0.8,
          parameters: {}
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/agent`]: mockData
      });

      const result = await sessionApi.updateAgentConfig(sessionId, updateData)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('updateSettings (v1 compatibility)', () => {
    it('should update settings with v1 parameters', async () => {
      const mockData = {
        data: {
          persona_id: 'assistant',
          temperature: 0.9
        }
      }

      restoreFetch = setupFetchMock({
        '/sessions/session-123/agent': mockData
      });

      const params = {
        ui_session_id: 'session-123',
        persona_name: 'assistant',
        temperature: 0.9
      };

      const result = await sessionApi.updateSettings(params)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getSessionTools', () => {
    it('should retrieve session tools', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          tools: ['calculator', 'web_search']
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/tools`]: mockData
      });

      const result = await sessionApi.getSessionTools(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('updateSessionTools', () => {
    it('should update session tools', async () => {
      const sessionId = 'session-123';
      const tools = ['calculator', 'web_search', 'file_manager'];

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/tools`]: { status: 204 }
      });

      const result = await sessionApi.updateSessionTools(sessionId, tools)

      expect(result).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('updateTools (v1 compatibility)', () => {
    it('should update tools with v1 parameters', async () => {
      restoreFetch = setupFetchMock({
        '/sessions/session-123/tools': { status: 204 }
      });

      const params = {
        ui_session_id: 'session-123',
        tools: ['calculator', 'web_search']
      };

      const result = await sessionApi.updateTools(params)

      expect(result).toEqual({
        success: true,
        tools: ['calculator', 'web_search']
      })
    })
  })

  describe('getAgentTools (v1 compatibility)', () => {
    it('should retrieve agent tools in v1 format', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          tools: ['calculator', 'web_search']
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/tools`]: mockData
      });

      const result = await sessionApi.getAgentTools(sessionId)

      expect(result).toEqual({
        initialized_tools: ['calculator', 'web_search']
      })
    })
  })

  describe('sendMessage', () => {
    it('should send a message successfully', async () => {
      const sessionId = 'session-123';
      const message = {
        role: 'user',
        content: [{ type: 'text', text: 'Hello' }]
      };
      const mockData = {
        data: {
          id: 'message-456',
          content: 'Hello! How can I help you?'
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/chat`]: mockData
      });

      const result = await sessionApi.sendMessage(sessionId, message)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('getMessages', () => {
    it('should retrieve message history', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: [
          { id: 'msg-1', type: 'user_message', content: 'Hello' },
          { id: 'msg-2', type: 'assistant_message', content: 'Hi there!' }
        ]
      }

      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/events`]: mockData
      });

      const result = await sessionApi.getMessages(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('cancelChat', () => {
    it('should cancel chat successfully', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          status: 'cancelled',
          message: 'Chat generation cancelled'
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/chat`]: mockData
      });

      const result = await sessionApi.cancelChat(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('stopGeneration (v1 compatibility)', () => {
    it('should stop generation by cancelling chat', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          status: 'cancelled'
        }
      }

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/chat`]: mockData
      });

      const result = await sessionApi.stopGeneration(sessionId)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      restoreFetch = setupNetworkErrorMock('Network error');

      await expect(sessionApi.createSession({})).rejects.toThrow('Network error')
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle 204 No Content responses', async () => {
      const sessionId = 'session-123';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}`]: { status: 204 }
      });

      const result = await sessionApi.deleteSession(sessionId)
      expect(result).toBe(true)
    })
  })
})