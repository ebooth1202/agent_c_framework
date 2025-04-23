import React from 'react';
import UserMessage from './UserMessage';
import SystemMessage from './SystemMessage';
import AssistantMessage from './AssistantMessage';
import ThoughtDisplay from './ThoughtDisplay';
import MediaMessage from './MediaMessage';
import ToolCallDisplay from './ToolCallDisplay';

/**
 * MessageItem is a factory component that renders the appropriate message type
 * based on the message object properties.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.message - The message object to render
 * @param {number} props.index - The index of this message in the messages array
 * @param {Array} props.messages - The complete array of messages (needed for context)
 * @param {Array} props.expandedToolCallMessages - Array of message indices with expanded tool calls
 * @param {function} props.toggleToolCallExpansion - Function to toggle tool call expansion
 */
const MessageItem = ({
  message,
  index,
  messages,
  expandedToolCallMessages,
  toggleToolCallExpansion
}) => {
  // User message
  if (message.role === 'user') {
    return (
      <UserMessage 
        content={message.content} 
        files={message.files} 
        isVoiceMessage={message.isVoiceMessage} 
      />
    );
  }
  
  // Assistant text message
  if (message.role === 'assistant' && message.type === 'content') {
    // Find associated tool calls (the next message if it's a tool call)
    const nextMsg = messages[index + 1];
    const hasToolCalls = nextMsg && nextMsg.type === 'tool_calls' && nextMsg.toolCalls && nextMsg.toolCalls.length > 0;
    const isToolCallsExpanded = expandedToolCallMessages.includes(index);
    
    return (
      <AssistantMessage
        content={message.content}
        vendor={message.vendor}
        tokenUsage={message.tokenUsage}
        toolCalls={hasToolCalls ? nextMsg.toolCalls : []}
        isToolCallsExpanded={isToolCallsExpanded}
        onToggleToolCalls={() => toggleToolCallExpansion(index)}
      />
    );
  }
  
  // Tool calls
  if (message.type === 'tool_calls') {
    // If the previous message is an assistant message, skip rendering as a separate component
    // We'll display it inline with the assistant message instead
    const prevMsg = messages[index - 1];
    if (prevMsg && prevMsg.role === 'assistant' && prevMsg.type === 'content') {
      return null;
    }
    
    // Otherwise, render as usual (for standalone tool calls not attached to a message)
    return <ToolCallDisplay toolCalls={message.toolCalls} />;
  }
  
  // Thinking messages
  if (message.role === 'assistant' && message.type === 'thinking') {
    return <ThoughtDisplay content={message.content} vendor={message.vendor} />;
  }
  
  // Media messages
  if (message.type === 'media') {
    return <MediaMessage message={message} />;
  }
  
  // System messages
  if (message.role === 'system') {
    return (
      <SystemMessage 
        content={message.content} 
        isError={message.type === 'error'} 
        isCritical={message.critical} 
      />
    );
  }
  
  // Default fallback
  return null;
};

export default MessageItem;