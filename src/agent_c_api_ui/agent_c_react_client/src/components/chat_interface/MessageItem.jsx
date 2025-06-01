import React from 'react';
import PropTypes from 'prop-types';
import UserMessage from './UserMessage';
import SystemMessage from './SystemMessage';
import AssistantMessage from './AssistantMessage';
import ThoughtDisplay from './ThoughtDisplay';
import MediaMessage from './MediaMessage';
import ToolCallDisplay from './ToolCallDisplay';
import SystemPromptDisplay from '../replay_interface/SystemPromptDisplay';
import ModelCardDisplay from '../replay_interface/ModelCardDisplay';

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
  // Helper function to check if this message has associated tool calls (excluding 'think')
  const getAssociatedToolCalls = () => {
    // Collect tool calls from all subsequent tool_calls messages until we hit a non-media, non-tool_calls message
    let allToolCalls = [];
    let lookAheadIndex = index + 1;
    const MAX_LOOKAHEAD = 10; // Safety limit to prevent excessive looping
    
    // Look ahead for tool call messages, allowing media messages in between
    for (let i = 0; i < MAX_LOOKAHEAD && lookAheadIndex < messages.length; i++, lookAheadIndex++) {
      const nextMsg = messages[lookAheadIndex];
      
      // If we find a tool_calls message, add its tool calls to our collection
      if (nextMsg && nextMsg.type === 'tool_calls' && nextMsg.toolCalls?.length > 0) {
        // Mark this message as claimed by an assistant message
        nextMsg._claimedByAssistant = true;
        nextMsg._claimedByAssistantIndex = index;
        
        // Add these tool calls to our collection
        allToolCalls = [
          ...allToolCalls, 
          ...nextMsg.toolCalls.filter(tool => tool.name !== 'think' && tool.function?.name !== 'think')
        ];
      } 
      // If it's not a tool_calls message or a media message, stop looking
      else if (!(nextMsg && nextMsg.type === 'media')) {
        break;
      }
    }
    
    return allToolCalls;
  };

  // Helper function to check if tool calls should be expanded
  const isToolCallsExpanded = () => expandedToolCallMessages.includes(index);

  // Render user message
  if (message.role === 'user') {
    return (
      <div role="listitem" className="message-item user-message-container overflow-hidden w-full" aria-label="User message">
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
        className="message-item assistant-message-container overflow-hidden w-full"
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
    // First check if this tool call message was already claimed by an assistant message
    if (message._claimedByAssistant === true) {
      return null; // Skip rendering as it's already been claimed by an assistant message
    }
    
    // If not already claimed, look back through previous messages to find the most recent assistant message,
    // skipping over media events that might have been inserted by tool calls
    let assistantMsgIndex = index - 1;
    let foundAssistantMsg = false;
    const MAX_LOOKBACK = 5; // Maximum number of messages to look back
    
    // Look for assistant message, skipping over media events
    for (let i = 0; i < MAX_LOOKBACK && assistantMsgIndex >= 0; i++, assistantMsgIndex--) {
      const lookbackMsg = messages[assistantMsgIndex];
      
      // If we find an assistant content message, associate this tool call with it
      if (lookbackMsg && lookbackMsg.role === 'assistant' && lookbackMsg.type === 'content') {
        foundAssistantMsg = true;
        // Mark this message as claimed by the assistant message we found
        message._claimedByAssistant = true;
        message._claimedByAssistantIndex = assistantMsgIndex;
        break;
      }
      
      // Only continue looking back if the message is a media message
      // This prevents associating tool calls with unrelated assistant messages
      if (!(lookbackMsg && lookbackMsg.type === 'media')) {
        break;
      }
    }
    
    // Skip rendering if this tool call should be associated with a recent assistant message
    if (foundAssistantMsg) {
      return null;
    }
    
    // Filter out 'think' tool calls
    const displayableToolCalls = message.toolCalls?.filter(
      tool => tool.name !== 'think' && tool.function?.name !== 'think'
    );
    
    // If no displayable tool calls left, don't render anything
    if (!displayableToolCalls || displayableToolCalls.length === 0) {
      return null;
    }
    
    // Otherwise, render as standalone tool calls
    return (
      <div 
        role="listitem" 
        className="message-item tool-call-container"
        aria-label="Tool call results"
      >
        <ToolCallDisplay toolCalls={displayableToolCalls} />
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

  // Order is important here.  Render System prompt and model cards before system messages because they are also system messages
  if (message.role === 'system' && message.type === 'model_card') {
  return (
    <div
      role="listitem"
      className="message-item model-card-container"
      aria-label="Model information"
    >
      <ModelCardDisplay
        modelName={message.modelName}
        modelParameters={message.modelParameters}
        toolNames={message.toolNames}
      />
    </div>
  );
}

  // Render system prompt (before the general system message check)
if (message.role === 'system' && message.type === 'system_prompt') {
  return (
    <div
      role="listitem"
      className="message-item system-prompt-container"
      aria-label="System prompt"
    >
      <SystemPromptDisplay content={message.content} />
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
          severity={message.severity}
        />
      </div>
    );
  }
  
  // Default fallback - render nothing
  return null;
};

// PropTypes validation for runtime type checking
MessageItem.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string,
    content: PropTypes.string,
    type: PropTypes.string,
    vendor: PropTypes.string,
    tokenUsage: PropTypes.object,
    files: PropTypes.array,
    isVoiceMessage: PropTypes.bool,
    toolCalls: PropTypes.array,
    critical: PropTypes.bool,
    modelName: PropTypes.string,
    modelParameters: PropTypes.object,
    toolNames: PropTypes.array
  }).isRequired,
  index: PropTypes.number.isRequired,
  messages: PropTypes.array.isRequired,
  expandedToolCallMessages: PropTypes.array.isRequired,
  toggleToolCallExpansion: PropTypes.func.isRequired
};

export default MessageItem;