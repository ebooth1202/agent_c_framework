import { describe, it, expect, beforeEach, vi } from 'vitest';
import { EventStreamProcessor } from '../EventStreamProcessor';
import { SessionManager } from '../../session/SessionManager';
import type { ChatSessionChangedEvent } from '../types/ServerEvents';
import type { ChatSession } from '../../types/chat-session';
import type { ContentPart } from '../../types/CommonTypes';

// Sample chat session data from .scratch/chat_session_ref/example_chat_session.json
const sampleChatSession = {
  "version": 1,
  "session_id": "alpine-option-sardine",
  "token_count": 48148,
  "context_window_size": 10300,
  "session_name": null,
  "created_at": "2025-09-08T10:26:21.874914",
  "updated_at": "2025-09-08T10:26:21.874930",
  "deleted_at": null,
  "user_id": "admin",
  "metadata": {},
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "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"
          }
        },
        {
          "type": "text",
          "text": "Hello, Could you think about the symbolism in this logo and tell me what you think it represents?"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "id": "toolu_01FkSXfB8ps8d1EhD7dvQLQR",
          "input": {
            "thought": "The user is showing me a logo for \"CENTRIC\" and asking me to analyze its symbolism. Let me examine the visual elements:\n\n1. The word \"CENTRIC\" is in bold, dark purple/navy lettering\n2. There are yellow/orange curved elements on both sides that look like parentheses or crescents\n3. The curved elements appear to be symmetrical and positioned to \"frame\" or \"embrace\" the word CENTRIC\n\nLet me think about what this might symbolize:\n\n- The word \"centric\" itself means \"having a center\" or \"focused on a central point\"\n- The curved yellow elements could represent:\n  - Parentheses - suggesting inclusion, containment, or emphasis\n  - Arms embracing or protecting the center\n  - Rays of light emanating from or focusing toward the center\n  - Movement or energy flowing around a central point\n  - Sound waves or communication radiating outward\n  - A sense of completeness or wholeness\n\nThe color choices are also meaningful:\n- Purple/navy suggests professionalism, stability, trust, authority\n- Yellow/orange suggests energy, warmth, creativity, optimism\n\nThe overall design creates a sense of balance and focus, with the central text being the stable core and the curved elements suggesting dynamic energy or protective embrace around that center."
          },
          "name": "think",
          "type": "tool_use"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01FkSXfB8ps8d1EhD7dvQLQR",
          "content": ""
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "citations": null,
          "text": "Looking at this \"CENTRIC\" logo, I can see several layers of symbolism that work together quite effectively:",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": "Now could you generate a random number for me?"
    },
    {
      "role": "assistant",
      "content": [
        {
          "id": "toolu_01JT2vYL33LemaPf9ZYTskXa",
          "input": {},
          "name": "rng_generate_random_number",
          "type": "tool_use"
        }
      ]
    }
  ]
};

describe('Chat Session Integration - Sample Data Validation', () => {
  let processor: EventStreamProcessor;
  let sessionManager: SessionManager;

  beforeEach(() => {
    sessionManager = new SessionManager();
    processor = new EventStreamProcessor(sessionManager);
  });

  describe('Phase 5: Real Chat Session Data Processing', () => {
    it('should correctly process the sample chat session with all content types', () => {
      // Create a ChatSessionChangedEvent from the sample data
      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        chat_session: sampleChatSession as any,
        session_id: sampleChatSession.session_id
      };

      // Process the event
      processor.processEvent(event);

      // Get the processed session from SessionManager
      const processedSession = sessionManager.getCurrentSession();

      // Verify the session was processed successfully
      expect(processedSession).toBeDefined();
      expect(processedSession).not.toBeNull();

      // Verify session metadata
      expect(processedSession.session_id).toBe('alpine-option-sardine');
      expect(processedSession.token_count).toBe(48148);
      expect(processedSession.context_window_size).toBe(10300);
      expect(processedSession.user_id).toBe('admin');
      expect(processedSession.created_at).toBe('2025-09-08T10:26:21.874914');
      expect(processedSession.updated_at).toBe('2025-09-08T10:26:21.874930');

      // Verify messages array exists and has correct length
      expect(processedSession.messages).toBeDefined();
      expect(Array.isArray(processedSession.messages)).toBe(true);
      expect(processedSession.messages.length).toBe(6); // Based on sample data

      // Test User Message with Image Content
      const userMessage1 = processedSession.messages[0];
      expect(userMessage1.role).toBe('user');
      expect(userMessage1.content).toBeDefined();
      expect(Array.isArray(userMessage1.content)).toBe(true);
      expect((userMessage1.content as ContentPart[]).length).toBe(2);

      // Verify Image Content Part
      const imageContent = (userMessage1.content as ContentPart[])[0];
      expect(imageContent.type).toBe('image');
      expect((imageContent as any).source).toBeDefined();
      expect((imageContent as any).source.type).toBe('base64');
      expect((imageContent as any).source.media_type).toBe('image/png');
      expect((imageContent as any).source.data).toBeDefined();
      expect((imageContent as any).source.data).toMatch(/^iVBORw0KGgoAAAANSUhEUgAA/); // PNG header

      // Verify Text Content Part
      const textContent = (userMessage1.content as ContentPart[])[1];
      expect(textContent.type).toBe('text');
      expect((textContent as any).text).toBe('Hello, Could you think about the symbolism in this logo and tell me what you think it represents?');

      // Test Assistant Message with Tool Use
      const assistantMessage1 = processedSession.messages[1];
      expect(assistantMessage1.role).toBe('assistant');
      expect(assistantMessage1.content).toBeDefined();
      expect(Array.isArray(assistantMessage1.content)).toBe(true);

      // Verify Tool Use Content Part
      const toolUseContent = (assistantMessage1.content as ContentPart[])[0];
      expect(toolUseContent.type).toBe('tool_use');
      expect((toolUseContent as any).id).toBe('toolu_01FkSXfB8ps8d1EhD7dvQLQR');
      expect((toolUseContent as any).name).toBe('think');
      expect((toolUseContent as any).input).toBeDefined();
      expect((toolUseContent as any).input.thought).toBeDefined();
      expect((toolUseContent as any).input.thought).toContain('The user is showing me a logo');

      // Test User Message with Tool Result
      const userMessage2 = processedSession.messages[2];
      expect(userMessage2.role).toBe('user');
      expect(userMessage2.content).toBeDefined();
      expect(Array.isArray(userMessage2.content)).toBe(true);

      // Verify Tool Result Content Part
      const toolResultContent = (userMessage2.content as ContentPart[])[0];
      expect(toolResultContent.type).toBe('tool_result');
      expect((toolResultContent as any).tool_use_id).toBe('toolu_01FkSXfB8ps8d1EhD7dvQLQR');
      expect((toolResultContent as any).content).toBe('');

      // Test Assistant Message with Text
      const assistantMessage2 = processedSession.messages[3];
      expect(assistantMessage2.role).toBe('assistant');
      expect(assistantMessage2.content).toBeDefined();
      expect(Array.isArray(assistantMessage2.content)).toBe(true);

      // Verify Text Content 
      const assistantTextContent = (assistantMessage2.content as ContentPart[])[0];
      expect(assistantTextContent.type).toBe('text');
      expect((assistantTextContent as any).text).toContain('Looking at this "CENTRIC" logo');

      // Test Simple User Message
      const userMessage3 = processedSession.messages[4];
      expect(userMessage3.role).toBe('user');
      expect(userMessage3.content).toBe('Now could you generate a random number for me?');

      // Test Assistant Message with Tool Use (random number generator)
      const assistantMessage3 = processedSession.messages[5];
      expect(assistantMessage3.role).toBe('assistant');
      expect(assistantMessage3.content).toBeDefined();
      expect(Array.isArray(assistantMessage3.content)).toBe(true);

      const rngToolUse = (assistantMessage3.content as ContentPart[])[0];
      expect(rngToolUse.type).toBe('tool_use');
      expect((rngToolUse as any).id).toBe('toolu_01JT2vYL33LemaPf9ZYTskXa');
      expect((rngToolUse as any).name).toBe('rng_generate_random_number');
      expect((rngToolUse as any).input).toEqual({});
    });

    it('should handle all content types without data loss', () => {
      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        chat_session: sampleChatSession as any,
        session_id: sampleChatSession.session_id
      };

      processor.processEvent(event);
      const processedSession = sessionManager.getCurrentSession()!;

      // Count different content types to ensure nothing was lost
      let imageCount = 0;
      let textCount = 0;
      let toolUseCount = 0;
      let toolResultCount = 0;

      processedSession.messages.forEach(message => {
        if (Array.isArray(message.content)) {
          message.content.forEach((part: ContentPart) => {
            switch (part.type) {
              case 'image':
                imageCount++;
                break;
              case 'text':
                textCount++;
                break;
              case 'tool_use':
                toolUseCount++;
                break;
              case 'tool_result':
                toolResultCount++;
                break;
            }
          });
        } else if (typeof message.content === 'string') {
          textCount++; // Simple string content counts as text
        }
      });

      // Verify counts match expected values from sample data
      expect(imageCount).toBe(1); // 1 image in first user message
      expect(textCount).toBe(3); // Text in user message 1, assistant message 2, and user message 3
      expect(toolUseCount).toBe(2); // Think tool and random number generator
      expect(toolResultCount).toBe(1); // Result for think tool only (sample data cuts off before rng result)
    });

    it('should preserve all message metadata and structure', () => {
      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        chat_session: sampleChatSession as any,
        session_id: sampleChatSession.session_id
      };

      processor.processEvent(event);
      const processedSession = sessionManager.getCurrentSession()!;

      // Verify that optional fields are preserved when present
      expect(processedSession.session_name).toBeNull();
      expect(processedSession.deleted_at).toBeNull();
      expect(processedSession.metadata).toEqual({});

      // Verify message structure integrity
      processedSession.messages.forEach((message, index) => {
        // All messages should have required fields
        expect(message.role).toBeDefined();
        expect(['user', 'assistant', 'system', 'assistant (thought)']).toContain(message.role);
        expect(message.content).toBeDefined();

        // Verify content is properly structured
        if (Array.isArray(message.content)) {
          message.content.forEach((part: ContentPart) => {
            expect(part.type).toBeDefined();
            expect(['text', 'image', 'tool_use', 'tool_result']).toContain(part.type);

            // Type-specific validations
            switch (part.type) {
              case 'text':
                expect(part.text).toBeDefined();
                expect(typeof part.text).toBe('string');
                break;
              case 'image':
                expect(part.source).toBeDefined();
                expect(part.source!.type).toBeDefined();
                expect(part.source!.media_type).toBeDefined();
                expect(part.source!.data).toBeDefined();
                break;
              case 'tool_use':
                expect(part.id).toBeDefined();
                expect(part.name).toBeDefined();
                expect(part.input).toBeDefined();
                break;
              case 'tool_result':
                expect(part.tool_use_id).toBeDefined();
                expect(part.content).toBeDefined();
                break;
            }
          });
        }
      });
    });

    it('should handle edge cases in content normalization', () => {
      const event: ChatSessionChangedEvent = {
        type: 'chat_session_changed',
        chat_session: sampleChatSession as any,
        session_id: sampleChatSession.session_id
      };

      processor.processEvent(event);
      const processedSession = sessionManager.getCurrentSession()!;

      // Test that empty tool input is preserved
      const assistantMessage3 = processedSession.messages[5];
      const rngToolUse = (assistantMessage3.content as ContentPart[])[0];
      expect((rngToolUse as any).input).toEqual({});

      // Test that long base64 image data is preserved intact
      const userMessage1 = processedSession.messages[0];
      const imageContent = (userMessage1.content as ContentPart[])[0];
      expect((imageContent as any).source.data.length).toBeGreaterThan(10000); // Long base64 string

      // Test that complex nested tool input is preserved
      const assistantMessage1 = processedSession.messages[1];
      const thinkTool = (assistantMessage1.content as ContentPart[])[0];
      expect((thinkTool as any).input.thought).toContain('The user is showing me a logo');
      expect((thinkTool as any).input.thought).toContain('Let me think about what this might symbolize');
    });
  });
});