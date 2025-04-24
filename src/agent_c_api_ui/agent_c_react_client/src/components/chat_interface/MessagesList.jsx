import React, { useRef, useEffect, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import MessageItem from './MessageItem';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChevronUp } from 'lucide-react';

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
  const viewportRef = useRef(null);
  const [showScrollTopButton, setShowScrollTopButton] = useState(false);
  
  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Scroll to top function
  const scrollToTop = () => {
    viewportRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  // Track scroll position to show/hide scroll to top button
  const handleScroll = () => {
    if (viewportRef.current) {
      const scrollTop = viewportRef.current.scrollTop;
      setShowScrollTopButton(scrollTop > 200); // Show after scrolling 200px
    }
  };
  
  // Add event listener for scroll events
  useEffect(() => {
    const viewport = viewportRef.current;
    if (viewport) {
      viewport.addEventListener('scroll', handleScroll);
      return () => viewport.removeEventListener('scroll', handleScroll);
    }
  }, []);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Auto-scroll when tool selection indicator appears
  useEffect(() => {
    if (toolSelectionInProgress) {
      scrollToBottom();
    }
  }, [toolSelectionInProgress]);
  
  return (
    <div className={cn("messages-list-container", className)}>
      <ScrollArea 
        className="messages-list-scroll-area"
        type="always"
        scrollHideDelay={100}
        viewportRef={viewportRef}
      >
        <div className="messages-list-content">
          <div className="messages-list-inner">
            {messages.map((message, index) => (
              <div key={index} className="message-item-wrapper">
                <MessageItem
                  message={message}
                  index={index}
                  messages={messages}
                  expandedToolCallMessages={expandedToolCallMessages}
                  toggleToolCallExpansion={toggleToolCallExpansion}
                />
              </div>
            ))}
            
            {/* Tool selection in progress indicator */}
            {toolSelectionInProgress && (
              <div className="tool-selection-indicator">
                <div className="tool-selection-indicator-dot"></div>
                <span>Preparing to use: {toolSelectionName?.replace(/-/g, ' ') || 'tool'}</span>
              </div>
            )}
            
            {/* Ref for scrolling to bottom - placed after tool indicator to ensure it scrolls into view */}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </ScrollArea>
      
      {/* Scroll to top button */}
      {showScrollTopButton && (
        <Button 
          onClick={scrollToTop} 
          size="sm" 
          variant="secondary" 
          className="scroll-to-top-button"
          aria-label="Scroll to top"
        >
          <ChevronUp className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
};

export default MessagesList;