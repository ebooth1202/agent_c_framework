import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import * as chatApi from './chat-api'
import { setupFetchMock, setupNetworkErrorMock } from '../test/utils/api-test-utils'

describe('Chat API Service', () => {
  // Store the cleanup function for each test
  let restoreFetch;
  
  afterEach(() => {
    // Clean up any fetch mocks
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  })

  describe('sendStreamingMessage (v2)', () => {
    it('should send a streaming message successfully', async () => {
      const sessionId = 'session-123';
      const message = {
        role: 'user',
        content: [{ type: 'text', text: 'Hello' }]
      };

      // Mock streaming response
      const mockEvents = [
        JSON.stringify({ type: 'text_delta', content: 'Hello' }),
        JSON.stringify({ type: 'text_delta', content: ' there!' }),
        JSON.stringify({ type: 'completion', status: 'complete' })
      ];

      // Create a mock ReadableStream
      const mockStream = new ReadableStream({
        start(controller) {
          mockEvents.forEach(event => {
            controller.enqueue(new TextEncoder().encode(event + '\n'));
          });
          controller.close();
        }
      });

      const mockResponse = {
        ok: true,
        status: 200,
        body: mockStream
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const events = [];
      const onChunk = (event) => events.push(event);

      const result = await chatApi.sendStreamingMessage(sessionId, message, onChunk);

      expect(result.text_content).toBe('Hello there!');
      expect(result.complete).toBe(true);
      expect(events).toHaveLength(3);
      expect(events[0].type).toBe('text_delta');
      expect(events[2].type).toBe('completion');
    })

    it('should handle streaming errors', async () => {
      const sessionId = 'session-123';
      const message = { role: 'user', content: [{ type: 'text', text: 'Hello' }] };

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400
      });

      await expect(chatApi.sendStreamingMessage(sessionId, message)).rejects.toThrow();
    })
  })

  describe('sendChatMessage (v1 compatibility)', () => {
    it('should send a chat message with v1 format', async () => {
      const sessionId = 'session-123';
      const message = 'Hello world';
      const fileIds = ['file-1', 'file-2'];

      // Mock streaming response
      const mockEvents = [
        JSON.stringify({ type: 'text_delta', content: 'Hello' }),
        JSON.stringify({ type: 'text_delta', content: ' back!' }),
        JSON.stringify({ type: 'completion', status: 'complete' })
      ];

      const mockStream = new ReadableStream({
        start(controller) {
          mockEvents.forEach(event => {
            controller.enqueue(new TextEncoder().encode(event + '\n'));
          });
          controller.close();
        }
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: mockStream
      });

      const chunks = [];
      const onChunk = (chunk) => chunks.push(chunk);

      const result = await chatApi.sendChatMessage(sessionId, message, fileIds, onChunk);

      expect(result).toBe('Hello back!');
      expect(chunks).toEqual(['Hello', ' back!']);
      
      // Verify the request was made with proper v2 format
      const callArgs = global.fetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      expect(requestBody.message.content).toHaveLength(3); // text + 2 files
      expect(requestBody.message.content[0]).toEqual({ type: 'text', text: 'Hello world' });
      expect(requestBody.message.content[1]).toEqual({ type: 'file', file_id: 'file-1' });
    })
  })

  describe('cancelChat', () => {
    it('should cancel chat successfully', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: {
          status: 'cancelled',
          message: 'Chat cancelled successfully'
        }
      };

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/chat`]: mockData
      });

      const result = await chatApi.cancelChat(sessionId);

      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })

  describe('uploadFile (v2)', () => {
    it('should upload a file successfully', async () => {
      const sessionId = 'session-123';
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const mockData = {
        data: {
          file_id: 'file-456',
          filename: 'test.txt',
          content_type: 'text/plain',
          size: 12
        }
      };

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files`]: mockData
      });

      const result = await chatApi.uploadFile(sessionId, mockFile);

      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })

  describe('uploadAttachment (v1 compatibility)', () => {
    it('should upload an attachment with v1 format', async () => {
      const sessionId = 'session-123';
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const mockData = {
        data: {
          file_id: 'file-456',
          filename: 'test.txt',
          content_type: 'text/plain',
          size: 12
        }
      };

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files`]: mockData
      });

      const result = await chatApi.uploadAttachment(sessionId, mockFile);

      expect(result).toEqual({
        id: 'file-456',
        filename: 'test.txt',
        mime_type: 'text/plain',
        size: 12,
        file_id: 'file-456',
        content_type: 'text/plain'
      });
    })
  })

  describe('downloadFile (v2)', () => {
    it('should download a file successfully', async () => {
      const sessionId = 'session-123';
      const fileId = 'file-456';
      const mockBlob = new Blob(['file content'], { type: 'text/plain' });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(mockBlob)
      });

      const result = await chatApi.downloadFile(sessionId, fileId);

      expect(result).toBeInstanceOf(Blob);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sessions/${sessionId}/files/${fileId}/content`),
        expect.any(Object)
      );
    })
  })

  describe('downloadAttachment (v1 compatibility)', () => {
    it('should download an attachment', async () => {
      const sessionId = 'session-123';
      const attachmentId = 'file-456';
      const mockBlob = new Blob(['file content'], { type: 'text/plain' });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(mockBlob)
      });

      const result = await chatApi.downloadAttachment(sessionId, attachmentId);

      expect(result).toBeInstanceOf(Blob);
    })
  })

  describe('getFileMetadata', () => {
    it('should get file metadata successfully', async () => {
      const sessionId = 'session-123';
      const fileId = 'file-456';
      const mockData = {
        data: {
          file_id: fileId,
          filename: 'test.txt',
          content_type: 'text/plain',
          size: 12,
          created_at: '2025-05-23T21:00:00Z'
        }
      };

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files/${fileId}`]: mockData
      });

      const result = await chatApi.getFileMetadata(sessionId, fileId);

      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })

  describe('listFiles', () => {
    it('should list files successfully', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: [
          { file_id: 'file-1', filename: 'test1.txt' },
          { file_id: 'file-2', filename: 'test2.txt' }
        ]
      };

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files`]: mockData
      });

      const result = await chatApi.listFiles(sessionId);

      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })
  })

  describe('deleteFile', () => {
    it('should delete a file successfully', async () => {
      const sessionId = 'session-123';
      const fileId = 'file-456';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files/${fileId}`]: { status: 204 }
      });

      const result = await chatApi.deleteFile(sessionId, fileId);

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should handle deletion errors', async () => {
      const sessionId = 'session-123';
      const fileId = 'file-456';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files/${fileId}`]: {
          detail: { message: 'File not found' },
          status: 404
        }
      });

      await expect(chatApi.deleteFile(sessionId, fileId)).rejects.toThrow('File not found');
    })
  })

  describe('getChatHistory', () => {
    it('should get chat history successfully', async () => {
      const sessionId = 'session-123';
      const mockData = {
        data: [
          { id: 'event-1', type: 'user_message', content: 'Hello' },
          { id: 'event-2', type: 'assistant_message', content: 'Hi there!' }
        ]
      };

      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/events`]: mockData
      });

      const result = await chatApi.getChatHistory(sessionId);

      expect(result).toEqual(mockData.data);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    })

    it('should get chat history with parameters', async () => {
      const sessionId = 'session-123';
      const params = { limit: 10, event_types: 'user_message,assistant_message' };
      const mockData = { data: [] };

      restoreFetch = setupFetchMock({
        [`/history/${sessionId}/events`]: mockData
      });

      await chatApi.getChatHistory(sessionId, params);

      const callArgs = global.fetch.mock.calls[0];
      expect(callArgs[0]).toContain('limit=10');
      expect(callArgs[0]).toContain('event_types=user_message%2Cassistant_message');
    })
  })

  describe('streamChatHistory', () => {
    it('should stream chat history successfully', async () => {
      const sessionId = 'session-123';
      const params = { real_time: true };

      // Mock Server-Sent Events response
      const mockEvents = [
        'data: {"id": "event-1", "type": "user_message", "content": "Hello"}',
        'data: {"id": "event-2", "type": "assistant_message", "content": "Hi!"}'
      ];

      const mockStream = new ReadableStream({
        start(controller) {
          mockEvents.forEach(event => {
            controller.enqueue(new TextEncoder().encode(event + '\n'));
          });
          controller.close();
        }
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: mockStream
      });

      const events = [];
      const onEvent = (event) => events.push(event);

      await chatApi.streamChatHistory(sessionId, params, onEvent);

      expect(events).toHaveLength(2);
      expect(events[0].type).toBe('user_message');
      expect(events[1].type).toBe('assistant_message');
    })

    it('should handle streaming errors', async () => {
      const sessionId = 'session-123';

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400
      });

      await expect(chatApi.streamChatHistory(sessionId)).rejects.toThrow();
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      restoreFetch = setupNetworkErrorMock('Network error');

      await expect(chatApi.uploadFile('session-123', new File([], 'test.txt')))
        .rejects.toThrow('Network error');
    })

    it('should handle 204 No Content responses', async () => {
      const sessionId = 'session-123';
      const fileId = 'file-456';

      restoreFetch = setupFetchMock({
        [`/sessions/${sessionId}/files/${fileId}`]: { status: 204 }
      });

      const result = await chatApi.deleteFile(sessionId, fileId);
      expect(result).toBe(true);
    })

    it('should handle missing ReadableStream support', async () => {
      const sessionId = 'session-123';
      const message = { role: 'user', content: [{ type: 'text', text: 'Hello' }] };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: null // No ReadableStream support
      });

      await expect(chatApi.sendStreamingMessage(sessionId, message))
        .rejects.toThrow('ReadableStream not supported in this browser');
    })
  })
})