# MessageItem Component Standardization Plan

## Component Overview
The MessageItem component acts as a factory component that renders different message types based on the message properties. It doesn't have its own styles but delegates to specialized components for rendering different message types (user, assistant, system, thinking, media, tool calls).

## Current State
- Factory pattern that determines which message component to render
- Handles logic for associating tool calls with assistant messages
- No specific CSS file as it delegates rendering to specialized components
- Good component structure but could benefit from documentation and type safety

## Standardization Goals
1. Improve code organization and readability
2. Add better PropTypes or TypeScript type definitions
3. Enhance documentation and comments
4. Add appropriate ARIA roles and accessibility attributes
5. Refactor the tool call association logic for clarity
6. Consider adding shadcn/ui components where appropriate

## Implementation Details

### 1. Code Organization
- Reorder the message type checks for better readability
- Extract complex condition logic into named functions
- Use early returns for cleaner code flow

### 2. PropTypes/Type Definitions
- Add comprehensive PropTypes for better type safety
- Document all props with JSDoc comments

### 3. Accessibility Improvements
- Add appropriate ARIA roles to the message container
- Add a11y attributes for better screen reader support

### 4. Tool Call Logic Refactoring
- Extract tool call association logic into a separate function
- Make the relationship between messages and tool calls more explicit

### 5. Component Enhancement
- Consider adding shadcn/ui Tooltip for message metadata
- Add transition effects for message rendering

## Code Changes

### Updated Component Definition
```jsx
import React from 'react';
import PropTypes from 'prop-types';
import UserMessage from './UserMessage';
import SystemMessage from './SystemMessage';
import AssistantMessage from './AssistantMessage';
import ThoughtDisplay from './ThoughtDisplay';
import MediaMessage from './MediaMessage';
import ToolCallDisplay from './ToolCallDisplay';
import { cn } from '../../lib/utils';

/**
 * MessageItem is a factory component that renders the appropriate message type
 * based on the message object properties.
 */
const MessageItem = ({
  message,
  index,
  messages,
  expandedToolCallMessages,
  toggleToolCallExpansion
}) => {
  // Helper function to check if this message has associated tool calls
  const getAssociatedToolCalls = () => {
    const nextMsg = messages[index + 1];
    if (nextMsg && nextMsg.type === 'tool_calls' && nextMsg.toolCalls?.length > 0) {
      return nextMsg.toolCalls;
    }
    return [];
  };

  // Helper function to check if tool calls should be expanded
  const isToolCallsExpanded = () => expandedToolCallMessages.includes(index);

  // Render user message
  if (message.role === 'user') {
    return (
      <div role="listitem" className="message-item user-message-container" aria-label="User message">
        <UserMessage 
          content={message.content} 
          files={message.files} 
          isVoiceMessage={message.isVoiceMessage} 
        />
      </div>
    );
  }
  
  // Render assistant text message
  if (message.role === 'assistant' && message.type === 'content') {
    const toolCalls = getAssociatedToolCalls();
    const hasToolCalls = toolCalls.length > 0;
    
    return (
      <div 
        role="listitem" 
        className="message-item assistant-message-container"
        aria-label="Assistant message"
      >
        <AssistantMessage
          content={message.content}
          vendor={message.vendor}
          tokenUsage={message.tokenUsage}
          toolCalls={toolCalls}
          isToolCallsExpanded={isToolCallsExpanded()}
          onToggleToolCalls={() => toggleToolCallExpansion(index)}
        />
      </div>
    );
  }
  
  // Handle tool calls rendering
  if (message.type === 'tool_calls') {
    // Skip rendering if this is associated with a previous assistant message
    const prevMsg = messages[index - 1];
    if (prevMsg && prevMsg.role === 'assistant' && prevMsg.type === 'content') {
      return null;
    }
    
    // Otherwise, render as standalone tool calls
    return (
      <div 
        role="listitem" 
        className="message-item tool-call-container"
        aria-label="Tool call results"
      >
        <ToolCallDisplay toolCalls={message.toolCalls} />
      </div>
    );
  }
  
  // Render thinking messages
  if (message.role === 'assistant' && message.type === 'thinking') {
    return (
      <div 
        role="listitem" 
        className="message-item thinking-container"
        aria-label="Assistant thinking process"
      >
        <ThoughtDisplay content={message.content} vendor={message.vendor} />
      </div>
    );
  }
  
  // Render media messages
  if (message.type === 'media') {
    return (
      <div 
        role="listitem" 
        className="message-item media-container"
        aria-label="Media message"
      >
        <MediaMessage message={message} />
      </div>
    );
  }
  
  // Render system messages
  if (message.role === 'system') {
    return (
      <div 
        role="listitem" 
        className="message-item system-message-container"
        aria-label={message.type === 'error' ? 'System error message' : 'System message'}
      >
        <SystemMessage 
          content={message.content} 
          isError={message.type === 'error'} 
          isCritical={message.critical} 
        />
      </div>
    );
  }
  
  // Default fallback - render nothing
  return null;
};

// PropTypes for type safety
MessageItem.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string.isRequired,
    type: PropTypes.string,
    content: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
    files: PropTypes.array,
    isVoiceMessage: PropTypes.bool,
    vendor: PropTypes.string,
    tokenUsage: PropTypes.object,
    toolCalls: PropTypes.array,
    critical: PropTypes.bool
  }).isRequired,
  index: PropTypes.number.isRequired,
  messages: PropTypes.array.isRequired,
  expandedToolCallMessages: PropTypes.array.isRequired,
  toggleToolCallExpansion: PropTypes.func.isRequired
};

export default MessageItem;
```

### CSS Updates
Since this is a factory component that delegates rendering, we don't need a dedicated CSS file. The component-specific styling will be handled by the individual message components.

## Implementation Steps
1. Update the MessageItem.jsx file with the new code
2. Add PropTypes dependency if not already present
3. Test rendering of each message type
4. Verify that tool call association logic works correctly
5. Test with screen readers for accessibility

## Testing Checklist
- [ ] All message types render correctly
- [ ] Tool call expansion/collapse works properly
- [ ] Accessibility features work with screen readers
- [ ] Component works in both light and dark modes
- [ ] No regressions in functionality