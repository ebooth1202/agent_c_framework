# Tool Call Dropdown Fix

## Problem
The tool call display was hidden when toggled in the assistant message footer because the chat bubble wasn't expanding to accommodate it. The issue was caused by:

1. The `.assistant-message-tool-calls-content` being positioned absolutely, taking it out of the normal document flow
2. Several container elements having `overflow: hidden`, which clipped the dropdown content
3. The positioning of the dropdown not allowing the parent containers to expand properly

## Solution

The following changes were made to fix the issue:

1. Changed `.assistant-message-tool-calls-content` from `position: absolute` to `position: relative` to keep it in the document flow
2. Changed `overflow: hidden` to `overflow: visible` on the following elements:
   - `.assistant-message-card`
   - `.assistant-message-content`
   - `.assistant-message-body`
   - `.assistant-message-footer`
3. Added additional styling to the tool call item content to ensure proper display:
   - Added `max-width: 100%`
   - Added `box-sizing: border-box`
   - Added `overflow-x: auto` to allow horizontal scrolling if needed

## Files Modified

1. `src/styles/components/assistant-message.css`
2. `src/styles/components/tool-call-item.css`

These changes ensure that when the tool calls toggle is clicked, the dropdown content remains visible and doesn't get clipped by the chat bubble. The chat bubble now properly expands to accommodate the dropdown content.