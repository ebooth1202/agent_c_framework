import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { EventStreamProcessor } from '../EventStreamProcessor';
import { SessionManager } from '../../session/SessionManager';
import { ChatSessionChangedEvent } from '../types/ServerEvents';
import { Message } from '../types/CommonTypes';
import fs from 'fs';
import path from 'path';

describe('EventStreamProcessor - ChatSessionChangedEvent', () => {
  let processor: EventStreamProcessor;
  let sessionManager: SessionManager;
  let mockEmit: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionManager = new SessionManager();
    mockEmit = vi.fn();
    sessionManager.emit = mockEmit;
    sessionManager.setCurrentSession = vi.fn();
    processor = new EventStreamProcessor(sessionManager);
  });

  afterEach(() => {
    processor.destroy();
    sessionManager.destroy();
  });

  describe('ChatSessionChangedEvent handling', () => {
    it('should handle event with MessageParam[] format and convert to Message[]', () => {
      // Sample session with MessageParam[] format (no timestamps)
      const serverSession = {
        session_id: 'test-session-001',
        messages: [
          {
            role: 'user',
            content: 'Hello, how are you?'
          },
          {
            role: 'assistant',
            content: [
              {
                type: 'text',
                text: 'I am doing well, thank you!'
              }
            ]
          }
        ],
        token_count: 100,
        context_window_size: 10000,
        session_name: 'Test Session',
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {}
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'test-session-001',
        chat_session: serverSession as any
      };

      processor.processEvent(event);

      // Verify SessionManager was called with converted session
      expect(sessionManager.setCurrentSession).toHaveBeenCalledWith(
        expect.objectContaining({
          session_id: 'test-session-001',
          messages: expect.arrayContaining([
            expect.objectContaining({
              role: 'user',
              content: 'Hello, how are you?',
              timestamp: expect.any(String),
              format: 'text'
            }),
            expect.objectContaining({
              role: 'assistant',
              content: expect.arrayContaining([
                expect.objectContaining({
                  type: 'text',
                  text: 'I am doing well, thank you!'
                })
              ]),
              timestamp: expect.any(String),
              format: 'text'
            })
          ])
        })
      );

      // Verify session-messages-loaded event was emitted
      expect(mockEmit).toHaveBeenCalledWith('session-messages-loaded', {
        sessionId: 'test-session-001',
        messages: expect.any(Array)
      });
    });

    it('should handle complex content blocks including images and tool use', () => {
      const serverSession = {
        session_id: 'complex-session',
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/png',
                  data: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
                }
              },
              {
                type: 'text',
                text: 'What is in this image?'
              }
            ]
          },
          {
            role: 'assistant',
            content: [
              {
                type: 'tool_use',
                id: 'tool_001',
                name: 'analyze_image',
                input: { image_data: 'base64...' }
              }
            ]
          },
          {
            role: 'user',
            content: [
              {
                type: 'tool_result',
                tool_use_id: 'tool_001',
                content: 'Image analysis complete',
                is_error: false
              }
            ]
          }
        ],
        token_count: 500,
        context_window_size: 10000,
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {}
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'complex-session',
        chat_session: serverSession as any
      };

      processor.processEvent(event);

      // Verify complex content was normalized
      const setCurrentSessionCall = (sessionManager.setCurrentSession as any).mock.calls[0][0];
      const messages = setCurrentSessionCall.messages as Message[];

      expect(messages).toHaveLength(3);
      
      // Check first message (user with image)
      const firstMessage = messages[0];
      expect(firstMessage.role).toBe('user');
      expect(Array.isArray(firstMessage.content)).toBe(true);
      if (Array.isArray(firstMessage.content)) {
        expect(firstMessage.content).toHaveLength(2);
        expect(firstMessage.content[0]).toEqual({
          type: 'image',
          source: expect.objectContaining({
            type: 'base64',
            media_type: 'image/png'
          })
        });
        expect(firstMessage.content[1]).toEqual({
          type: 'text',
          text: 'What is in this image?'
        });
      }

      // Check second message (assistant with tool use)
      const secondMessage = messages[1];
      expect(secondMessage.role).toBe('assistant');
      if (Array.isArray(secondMessage.content)) {
        expect(secondMessage.content[0]).toEqual({
          type: 'tool_use',
          id: 'tool_001',
          name: 'analyze_image',
          input: { image_data: 'base64...' }
        });
      }

      // Check third message (user with tool result)
      const thirdMessage = messages[2];
      expect(thirdMessage.role).toBe('user');
      if (Array.isArray(thirdMessage.content)) {
        expect(thirdMessage.content[0]).toEqual({
          type: 'tool_result',
          tool_use_id: 'tool_001',
          content: 'Image analysis complete',
          is_error: false
        });
      }
    });

    it('should preserve vendor and display_name fields if present', () => {
      const serverSession = {
        session_id: 'vendor-session',
        messages: [],
        token_count: 0,
        context_window_size: 10000,
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {},
        vendor: 'custom-vendor',
        display_name: 'Custom Display Name'
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'vendor-session',
        chat_session: serverSession as any
      };

      processor.processEvent(event);

      // Verify vendor and display_name were preserved
      expect(sessionManager.setCurrentSession).toHaveBeenCalledWith(
        expect.objectContaining({
          vendor: 'custom-vendor',
          display_name: 'Custom Display Name'
        })
      );
    });

    it('should handle sessions already in Message[] format', () => {
      const runtimeSession = {
        session_id: 'runtime-session',
        messages: [
          {
            role: 'user',
            content: 'Already formatted',
            timestamp: '2025-01-01T00:00:00.000Z',
            format: 'text' as const
          }
        ],
        token_count: 50,
        context_window_size: 10000,
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {}
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'runtime-session',
        chat_session: runtimeSession as any
      };

      processor.processEvent(event);

      // Should pass through without conversion
      expect(sessionManager.setCurrentSession).toHaveBeenCalledWith(runtimeSession);
    });

    it('should handle thinking blocks by converting to text', () => {
      const serverSession = {
        session_id: 'thinking-session',
        messages: [
          {
            role: 'assistant',
            content: [
              {
                type: 'thinking',
                thinking: 'This is my internal thought process...'
              },
              {
                type: 'text',
                text: 'Here is my response.'
              }
            ]
          }
        ],
        token_count: 100,
        context_window_size: 10000,
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {}
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'thinking-session',
        chat_session: serverSession as any
      };

      processor.processEvent(event);

      const setCurrentSessionCall = (sessionManager.setCurrentSession as any).mock.calls[0][0];
      const messages = setCurrentSessionCall.messages as Message[];
      
      expect(messages[0].content).toEqual([
        {
          type: 'text',
          text: '[Thinking] This is my internal thought process...'
        },
        {
          type: 'text',
          text: 'Here is my response.'
        }
      ]);
    });

    it('should handle document blocks', () => {
      const serverSession = {
        session_id: 'document-session',
        messages: [
          {
            role: 'assistant',
            content: [
              {
                type: 'document',
                title: 'Research Paper',
                content: 'Full document content here...'
              }
            ]
          }
        ],
        token_count: 200,
        context_window_size: 10000,
        created_at: '2025-01-01T00:00:00.000Z',
        updated_at: '2025-01-01T00:01:00.000Z',
        user_id: 'test-user',
        metadata: {}
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'document-session',
        chat_session: serverSession as any
      };

      processor.processEvent(event);

      const setCurrentSessionCall = (sessionManager.setCurrentSession as any).mock.calls[0][0];
      const messages = setCurrentSessionCall.messages as Message[];
      
      expect(messages[0].content).toEqual([
        {
          type: 'text',
          text: '[Document: Research Paper]'
        }
      ]);
    });

    it('should handle empty session gracefully', () => {
      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'empty-session',
        chat_session: null as any
      };

      processor.processEvent(event);

      // Should not call setCurrentSession with null
      expect(sessionManager.setCurrentSession).not.toHaveBeenCalled();
    });

    it('should reset message builder on session change', () => {
      const messageBuilderResetSpy = vi.spyOn(processor['messageBuilder'], 'reset');

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: 'reset-test',
        chat_session: {
          session_id: 'reset-test',
          messages: [],
          token_count: 0,
          context_window_size: 10000,
          created_at: '2025-01-01T00:00:00.000Z',
          updated_at: '2025-01-01T00:01:00.000Z',
          user_id: 'test-user',
          metadata: {}
        } as any
      };

      processor.processEvent(event);

      expect(messageBuilderResetSpy).toHaveBeenCalled();
    });
  });

  describe('Integration with real sample data', () => {
    it('should process the example chat session from .scratch without errors', () => {
      // Note: This test would load the actual sample file if it exists
      // For now, we'll use a representative subset
      const sampleSession = {
        version: 1,
        session_id: 'alpine-option-sardine',
        token_count: 48148,
        context_window_size: 10300,
        session_name: null,
        created_at: '2025-09-08T10:26:21.874914',
        updated_at: '2025-09-08T10:26:21.874930',
        deleted_at: null,
        user_id: 'admin',
        metadata: {},
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/png',
                  data: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
                }
              },
              {
                type: 'text',
                text: 'Hello, Could you think about the symbolism in this logo and tell me what you think it represents?'
              }
            ]
          },
          {
            role: 'assistant',
            content: [
              {
                type: 'tool_use',
                id: 'toolu_01FkSXfB8ps8d1EhD7dvQLQR',
                name: 'think',
                input: {
                  thought: 'The user is showing me a logo...'
                }
              }
            ]
          },
          {
            role: 'user',
            content: [
              {
                type: 'tool_result',
                tool_use_id: 'toolu_01FkSXfB8ps8d1EhD7dvQLQR',
                content: ''
              }
            ]
          }
        ],
        agent_config: {
          version: 2,
          name: 'Domo',
          key: 'default',
          model_id: 'claude-sonnet-4-20250514'
        }
      };

      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        session_id: sampleSession.session_id,
        chat_session: sampleSession as any
      };

      // Should not throw
      expect(() => processor.processEvent(event)).not.toThrow();

      // Verify session was set
      expect(sessionManager.setCurrentSession).toHaveBeenCalled();

      // Verify messages were converted
      const setCurrentSessionCall = (sessionManager.setCurrentSession as any).mock.calls[0][0];
      expect(setCurrentSessionCall.messages).toHaveLength(3);
      expect(setCurrentSessionCall.session_id).toBe('alpine-option-sardine');
      expect(setCurrentSessionCall.token_count).toBe(48148);
    });
  });
});