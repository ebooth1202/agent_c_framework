import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ToolCallManager } from '../ToolCallManager';
import type { ToolSelectDeltaEvent, ToolCallEvent } from '../types/ServerEvents';
import type { ToolCall, ToolResult } from '../types/CommonTypes';

describe('ToolCallManager', () => {
  let manager: ToolCallManager;

  beforeEach(() => {
    manager = new ToolCallManager();
    vi.clearAllMocks();
  });

  describe('onToolSelect', () => {
    it('should create a notification for tool selection', () => {
      const event: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: { param1: 'value1' }
          }
        ]
      };

      const notification = manager.onToolSelect(event);

      expect(notification).toEqual({
        id: 'tool-1',
        toolName: 'test_tool',
        status: 'preparing',
        timestamp: expect.any(Date),
        arguments: JSON.stringify({ param1: 'value1' })
      });
    });

    it('should handle the think tool specially', () => {
      const event: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'think-1',
            type: 'tool_use',
            name: 'think',
            input: {}
          }
        ]
      };

      const notification = manager.onToolSelect(event);

      expect(notification.toolName).toBe('think');
      expect(notification.status).toBe('preparing');
    });

    it('should throw error if no tool calls', () => {
      const event: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: []
      };

      expect(() => manager.onToolSelect(event)).toThrow('ToolSelectDeltaEvent has no tool calls');
    });
  });

  describe('onToolCallActive', () => {
    it('should update existing notification to executing', () => {
      // First select the tool
      const selectEvent: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: { param1: 'value1' }
          }
        ]
      };
      manager.onToolSelect(selectEvent);

      // Then mark it as active
      const activeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: true,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: { param1: 'value1' }
          }
        ]
      };

      const notification = manager.onToolCallActive(activeEvent);

      expect(notification).toEqual({
        id: 'tool-1',
        toolName: 'test_tool',
        status: 'executing',
        timestamp: expect.any(Date),
        arguments: JSON.stringify({ param1: 'value1' })
      });
    });

    it('should create new notification if not previously selected', () => {
      const activeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: true,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-2',
            type: 'tool_use',
            name: 'another_tool',
            input: { key: 'value' }
          }
        ]
      };

      const notification = manager.onToolCallActive(activeEvent);

      expect(notification).toEqual({
        id: 'tool-2',
        toolName: 'another_tool',
        status: 'executing',
        timestamp: expect.any(Date),
        arguments: JSON.stringify({ key: 'value' })
      });
    });

    it('should return null for inactive event', () => {
      const inactiveEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: false,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };

      const notification = manager.onToolCallActive(inactiveEvent);
      expect(notification).toBeNull();
    });
  });

  describe('onToolCallComplete', () => {
    it('should handle tool completion with results', () => {
      // First select and activate the tool
      const selectEvent: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };
      manager.onToolSelect(selectEvent);

      // Complete the tool with results
      const completeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: false,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ],
        tool_results: [
          {
            type: 'tool_result',
            tool_use_id: 'tool-1',
            content: '{"result": "success"}'
          }
        ]
      };

      const completed = manager.onToolCallComplete(completeEvent);

      expect(completed).toHaveLength(1);
      expect(completed[0]).toEqual({
        id: 'tool-1',
        type: 'tool_use',
        name: 'test_tool',
        input: {},
        result: {
          type: 'tool_result',
          tool_use_id: 'tool-1',
          content: '{"result": "success"}'
        }
      });

      // Verify it's removed from active tools
      expect(manager.isToolActive('tool-1')).toBe(false);
    });

    it('should handle completion without results', () => {
      const completeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: false,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-2',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };

      const completed = manager.onToolCallComplete(completeEvent);

      expect(completed).toHaveLength(1);
      expect(completed[0].result).toBeUndefined();
    });

    it('should return empty array for active event', () => {
      const activeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: true,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };

      const completed = manager.onToolCallComplete(activeEvent);
      expect(completed).toEqual([]);
    });
  });

  describe('getActiveNotifications', () => {
    it('should return only active notifications', () => {
      // Add multiple tools
      const event1: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'tool1',
            input: {}
          }
        ]
      };
      const event2: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-2',
            type: 'tool_use',
            name: 'tool2',
            input: {}
          }
        ]
      };

      manager.onToolSelect(event1);
      manager.onToolSelect(event2);

      const notifications = manager.getActiveNotifications();
      expect(notifications).toHaveLength(2);
      expect(notifications.map(n => n.id)).toEqual(['tool-1', 'tool-2']);
    });
  });

  describe('reset', () => {
    it('should clear all state', () => {
      const event: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };

      manager.onToolSelect(event);
      expect(manager.getActiveNotifications()).toHaveLength(1);

      manager.reset();

      expect(manager.getActiveNotifications()).toHaveLength(0);
      expect(manager.getCompletedToolCalls()).toHaveLength(0);
    });
  });

  describe('getStatistics', () => {
    it('should return correct statistics', () => {
      // Add active tool
      const selectEvent: ToolSelectDeltaEvent = {
        type: 'tool_select_delta',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        tool_calls: [
          {
            id: 'tool-1',
            type: 'tool_use',
            name: 'test_tool',
            input: {}
          }
        ]
      };
      manager.onToolSelect(selectEvent);

      // Complete a different tool
      const completeEvent: ToolCallEvent = {
        type: 'tool_call',
        session_id: 'test-session',
        role: 'assistant',
        parent_session_id: null,
        user_session_id: 'test-session',
        active: false,
        vendor: 'anthropic',
        tool_calls: [
          {
            id: 'tool-2',
            type: 'tool_use',
            name: 'another_tool',
            input: {}
          }
        ]
      };
      manager.onToolCallComplete(completeEvent);

      const stats = manager.getStatistics();
      expect(stats).toEqual({
        activeCount: 1,
        completedCount: 1,
        totalCount: 2
      });
    });
  });
});