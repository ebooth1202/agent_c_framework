# Chat Streaming Event Sequences - Quick Reference

This document provides a quick reference for the exact event sequences during Agent C chat streaming interactions.

## Basic Agent Turn (10 Events)

1. `interaction` (started: true)
2. `anthropic_user_message` OR `open_ai_user_message`
3. `system_prompt`
4. `completion` (running: true)
5. Multiple `text_delta` / `thought_delta` events
6. `completion` (running: false)
7. `history_delta`
8. `history`
9. `interaction` (started: false)
10. `user_turn_start`

## Tool-Enhanced Turn (Additional Events)

Insert between events 5-6 above:

- Multiple `tool_select_delta` events (agent formulating tool calls)
- `tool_call` (active: true) - execution starts
- `tool_call` (active: false) - execution complete with results
- Additional `text_delta` events (agent using tool results)

## User Turn Management

- **User sends input** → `user_turn_end` → Agent turn sequence → `user_turn_start`
- **Client rule**: Only enable input after `user_turn_start` event

## Critical Client Implementation Points

✅ **DO**
- Wait for `user_turn_start` before enabling input
- Buffer `text_delta` events by role within each interaction  
- Show tool usage from `tool_select_delta` events
- Handle both `anthropic_user_message` and `open_ai_user_message`
- Clear buffers when `interaction.started = false`

❌ **DON'T**
- Enable input before `user_turn_start`
- Mix text deltas across interaction boundaries
- Ignore vendor-specific user message events
- Process tool deltas as regular text content

## Event Type Examples

```javascript
// Basic sequence markers
'interaction'          // Turn boundaries
'user_turn_start'      // Client may send input
'completion'           // LLM processing state

// Content streaming  
'text_delta'           // Agent response text
'thought_delta'        // Agent thinking process

// Tool usage
'tool_select_delta'    // Tool selection in progress
'tool_call'            // Tool execution state

// History management
'history_delta'        // New messages
'history'              // Complete history
```

For complete details, see [Runtime Events Reference](realtime_api_runtime_events.md).