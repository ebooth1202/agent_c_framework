/**
 * Tests for EventRegistry
 */

import { describe, it, expect, vi } from 'vitest';
import { EventRegistry } from '../EventRegistry';

describe('EventRegistry', () => {
  describe('isClientEventType', () => {
    it('should identify valid client event types', () => {
      const clientEventTypes = [
        'get_agents',
        'set_agent',
        'get_avatars',
        'set_avatar_session',
        'clear_avatar_session',
        'set_agent_voice',
        'text_input',
        'new_chat_session',
        'resume_chat_session',
        'set_chat_session_name',
        'set_session_metadata',
        'set_session_messages',
        'get_user_sessions',
        'get_voices',
        'get_tool_catalog',
        'ping',
        'delete_chat_session'
      ];

      clientEventTypes.forEach(type => {
        expect(EventRegistry.isClientEventType(type)).toBe(true);
      });
    });

    it('should reject invalid client event types', () => {
      expect(EventRegistry.isClientEventType('invalid_event')).toBe(false);
      expect(EventRegistry.isClientEventType('')).toBe(false);
      expect(EventRegistry.isClientEventType('text_delta')).toBe(false); // Server event
    });
  });

  describe('isServerEventType', () => {
    it('should identify valid server event types', () => {
      const serverEventTypes = [
        'agent_list',
        'agent_configuration_changed',
        'avatar_list',
        'avatar_connection_changed',
        'chat_session_changed',
        'chat_session_name_changed',
        'session_metadata_changed',
        'text_delta',
        'thought_delta',
        'completion',
        'interaction',
        'history',
        'tool_call',
        'system_message',
        'user_turn_start',
        'user_turn_end',
        'agent_voice_changed',
        'error',
        'get_user_sessions_response',
        'chat_user_data',
        'voice_list',
        'tool_catalog',
        'pong',
        'voice_input_supported',
        'server_listening',
        'chat_session_added',
        'chat_session_deleted',
        'tool_select_delta',
        'render_media',
        'history_delta',
        'system_prompt',
        'user_request'
      ];

      serverEventTypes.forEach(type => {
        expect(EventRegistry.isServerEventType(type)).toBe(true);
      });
    });

    it('should reject invalid server event types', () => {
      expect(EventRegistry.isServerEventType('invalid_event')).toBe(false);
      expect(EventRegistry.isServerEventType('')).toBe(false);
      expect(EventRegistry.isServerEventType('text_input')).toBe(false); // Client event
    });
  });

  describe('isValidEventType', () => {
    it('should identify all valid event types', () => {
      // Client events
      expect(EventRegistry.isValidEventType('text_input')).toBe(true);
      expect(EventRegistry.isValidEventType('ping')).toBe(true);
      
      // Server events
      expect(EventRegistry.isValidEventType('text_delta')).toBe(true);
      expect(EventRegistry.isValidEventType('pong')).toBe(true);
      
      // Special events
      expect(EventRegistry.isValidEventType('binary_audio')).toBe(true);
      expect(EventRegistry.isValidEventType('audio:output')).toBe(true);
      expect(EventRegistry.isValidEventType('connected')).toBe(true);
      expect(EventRegistry.isValidEventType('disconnected')).toBe(true);
      expect(EventRegistry.isValidEventType('reconnecting')).toBe(true);
      expect(EventRegistry.isValidEventType('reconnected')).toBe(true);
    });

    it('should reject invalid event types', () => {
      expect(EventRegistry.isValidEventType('not_an_event')).toBe(false);
      expect(EventRegistry.isValidEventType('')).toBe(false);
      expect(EventRegistry.isValidEventType('custom_event')).toBe(false);
    });
  });

  describe('getClientEventTypes', () => {
    it('should return all client event types', () => {
      const types = EventRegistry.getClientEventTypes();
      
      expect(Array.isArray(types)).toBe(true);
      expect(types.length).toBe(17); // 17 client event types
      expect(types).toContain('text_input');
      expect(types).toContain('ping');
      expect(types).toContain('get_agents');
      expect(types).not.toContain('text_delta'); // Server event
    });

    it('should return a new array each time', () => {
      const types1 = EventRegistry.getClientEventTypes();
      const types2 = EventRegistry.getClientEventTypes();
      
      expect(types1).not.toBe(types2); // Different array instances
      expect(types1).toEqual(types2); // Same content
    });
  });

  describe('getServerEventTypes', () => {
    it('should return all server event types', () => {
      const types = EventRegistry.getServerEventTypes();
      
      expect(Array.isArray(types)).toBe(true);
      expect(types.length).toBeGreaterThan(30); // Many server event types
      expect(types).toContain('text_delta');
      expect(types).toContain('pong');
      expect(types).toContain('user_turn_start');
      expect(types).not.toContain('text_input'); // Client event
    });

    it('should return a new array each time', () => {
      const types1 = EventRegistry.getServerEventTypes();
      const types2 = EventRegistry.getServerEventTypes();
      
      expect(types1).not.toBe(types2); // Different array instances
      expect(types1).toEqual(types2); // Same content
    });
  });

  describe('parseEvent', () => {
    it('should parse valid JSON string events', () => {
      const jsonEvent = JSON.stringify({
        type: 'text_input',
        text: 'Hello'
      });

      const parsed = EventRegistry.parseEvent(jsonEvent);
      expect(parsed).toEqual({
        type: 'text_input',
        text: 'Hello'
      });
    });

    it('should parse valid object events', () => {
      const event = {
        type: 'text_delta',
        content: 'World',
        role: 'assistant'
      };

      const parsed = EventRegistry.parseEvent(event);
      expect(parsed).toEqual(event);
    });

    it('should return null for invalid events', () => {
      expect(EventRegistry.parseEvent('not json')).toBeNull();
      expect(EventRegistry.parseEvent({})).toBeNull(); // No type
      expect(EventRegistry.parseEvent({ type: 123 })).toBeNull(); // Wrong type
      expect(EventRegistry.parseEvent({ type: 'invalid_type' })).toBeNull();
      expect(EventRegistry.parseEvent(null)).toBeNull();
      expect(EventRegistry.parseEvent(undefined)).toBeNull();
    });

    it('should handle malformed JSON gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(EventRegistry.parseEvent('{ broken json')).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Failed to parse event:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });

    it('should handle server events', () => {
      const serverEvent = {
        type: 'user_turn_start',
        timestamp: '2024-01-01T00:00:00Z'
      };

      const parsed = EventRegistry.parseEvent(serverEvent);
      expect(parsed).toEqual(serverEvent);
    });

    it('should handle client events', () => {
      const clientEvent = {
        type: 'new_chat_session',
        session_name: 'Test Session'
      };

      const parsed = EventRegistry.parseEvent(clientEvent);
      expect(parsed).toEqual(clientEvent);
    });
  });

  describe('createEvent', () => {
    it('should create typed events with correct structure', () => {
      const textEvent = EventRegistry.createEvent('text_input', {
        text: 'Hello World'
      });

      expect(textEvent).toEqual({
        type: 'text_input',
        text: 'Hello World'
      });
    });

    it('should handle events with multiple properties', () => {
      const sessionEvent = EventRegistry.createEvent('resume_chat_session', {
        session_id: 'session-123',
        start_from_message_id: 'msg-456'
      });

      expect(sessionEvent).toEqual({
        type: 'resume_chat_session',
        session_id: 'session-123',
        start_from_message_id: 'msg-456'
      });
    });

    it('should handle events with no additional data', () => {
      const pingEvent = EventRegistry.createEvent('ping', {});

      expect(pingEvent).toEqual({
        type: 'ping'
      });
    });

    it('should handle events with optional properties', () => {
      const agentEvent = EventRegistry.createEvent('set_agent', {
        agent_key: 'agent-1',
        voice_id: 'voice-1'
      });

      expect(agentEvent).toEqual({
        type: 'set_agent',
        agent_key: 'agent-1',
        voice_id: 'voice-1'
      });
    });

    it('should preserve all properties passed in data', () => {
      const event = EventRegistry.createEvent('text_delta', {
        content: 'Test content',
        role: 'assistant',
        timestamp: '2024-01-01T00:00:00Z',
        metadata: { custom: 'data' }
      });

      expect(event.type).toBe('text_delta');
      expect(event).toHaveProperty('content', 'Test content');
      expect(event).toHaveProperty('role', 'assistant');
      expect(event).toHaveProperty('timestamp');
      expect(event).toHaveProperty('metadata');
    });
  });

  describe('Type safety checks', () => {
    it('should maintain consistency between type checks and lists', () => {
      // All client types should pass isClientEventType
      const clientTypes = EventRegistry.getClientEventTypes();
      clientTypes.forEach(type => {
        expect(EventRegistry.isClientEventType(type)).toBe(true);
        expect(EventRegistry.isValidEventType(type)).toBe(true);
      });

      // All server types should pass isServerEventType
      const serverTypes = EventRegistry.getServerEventTypes();
      serverTypes.forEach(type => {
        expect(EventRegistry.isServerEventType(type)).toBe(true);
        expect(EventRegistry.isValidEventType(type)).toBe(true);
      });
    });

    it('should not have overlapping client and server events', () => {
      const clientTypes = EventRegistry.getClientEventTypes();
      const serverTypes = EventRegistry.getServerEventTypes();

      clientTypes.forEach(type => {
        expect(serverTypes).not.toContain(type);
      });

      serverTypes.forEach(type => {
        expect(clientTypes).not.toContain(type);
      });
    });
  });
});