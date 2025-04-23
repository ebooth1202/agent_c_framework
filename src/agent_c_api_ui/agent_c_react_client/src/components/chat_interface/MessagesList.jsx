import React, { useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import MessageItem from './MessageItem';
import { cn } from '@/lib/utils';

// Import component CSS
import '@/styles/components/messages-list.css';

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
 * @param {string} props.className - Optional additional CSS classes for the container
 */
const MessagesList = ({
  messages,
  expandedToolCallMessages,
  toggleToolCallExpansion,
  toolSelectionInProgress,
  toolSelectionName,
  className
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
    <div className={cn("messages-list-container", className)}>
      <ScrollArea 
        className="messages-list-scroll-area"
        type="auto"
      >
        <div className="messages-list-content">
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
            <div className="tool-selection-indicator">
              <div className="tool-selection-indicator-dot"></div>
              <span>Preparing to use: {toolSelectionName?.replace(/-/g, ' ') || 'tool'}</span>
            </div>
          )}
          
          {/* Ref for scrolling to bottom */}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
};

export default MessagesList;