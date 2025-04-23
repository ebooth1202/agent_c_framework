import React, { useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import MessageItem from './MessageItem';

/**
 * MessagesList component handles rendering a list of messages with automatic scrolling
 * and manages the expanded state of tool calls.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.messages - Array of message objects to display
 * @param {Array} props.expandedToolCallMessages - Array of message indices with expanded tool calls
 * @param {function} props.toggleToolCallExpansion - Function to toggle tool call expansion
 * @param {boolean} props.toolSelectionInProgress - Whether a tool selection is in progress
 * @param {string} props.toolSelectionName - Name of the tool being selected
 */
const MessagesList = ({
  messages,
  expandedToolCallMessages,
  toggleToolCallExpansion,
  toolSelectionInProgress,
  toolSelectionName
}) => {
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  return (
    <ScrollArea className="flex-1 px-4 py-3" type="auto">
      <div className="space-y-4 w-full overflow-x-hidden">
        {messages.map((message, index) => (
          <MessageItem
            key={index}
            message={message}
            index={index}
            messages={messages}
            expandedToolCallMessages={expandedToolCallMessages}
            toggleToolCallExpansion={toggleToolCallExpansion}
          />
        ))}
        
        {/* Tool selection in progress indicator */}
        {toolSelectionInProgress && (
          <div className="flex items-center gap-2 text-sm text-gray-500 italic my-1 ml-8">
            <div className="animate-pulse h-2 w-2 bg-purple-400 rounded-full"></div>
            <span>Preparing to use: {toolSelectionName?.replace(/-/g, ' ') || 'tool'}</span>
          </div>
        )}
        
        {/* Ref for scrolling to bottom */}
        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
};

export default MessagesList;