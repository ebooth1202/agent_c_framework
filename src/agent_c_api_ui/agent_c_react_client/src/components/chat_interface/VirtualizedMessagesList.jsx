import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { ScrollArea } from '../ui/scroll-area';
import MessageItem from './MessageItem';
import { cn } from '../../lib/utils';
import { Button } from '../ui/button';
import { ChevronUp } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

// Import component CSS
import '@/styles/components/messages-list.css';

/**
 * VirtualizedMessagesList component handles rendering a virtualized list of messages 
 * with automatic scrolling and manages the expanded state of tool calls.
 * This is a drop-in replacement for MessagesList with virtualization for performance.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.messages - Array of message objects to display
 * @param {Array} props.expandedToolCallMessages - Array of message indices with expanded tool calls
 * @param {function} props.toggleToolCallExpansion - Function to toggle tool call expansion
 * @param {boolean} props.toolSelectionInProgress - Whether a tool selection is in progress
 * @param {string} props.toolSelectionName - Name of the tool being selected
 * @param {string} props.className - Optional additional CSS classes for the container
 */
const VirtualizedMessagesList = ({
  messages,
  expandedToolCallMessages,
  toggleToolCallExpansion,
  toolSelectionInProgress,
  toolSelectionName,
  className
}) => {
  const parentRef = useRef(null);
  const viewportRef = useRef(null);
  const [showScrollTopButton, setShowScrollTopButton] = useState(false);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const scrollThreshold = 100; // pixels from bottom to consider "at bottom"
  
  // Create virtualizer for messages
  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => viewportRef.current,
    estimateSize: () => 100, // Estimate message height - will be measured dynamically
    overscan: 5, // Render 5 items above and below visible area
  });
  
  // Check if viewport is scrolled near the bottom
  const isNearBottom = useCallback(() => {
    if (!viewportRef.current) return true;
    
    const { scrollTop, scrollHeight, clientHeight } = viewportRef.current;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    
    return distanceFromBottom <= scrollThreshold;
  }, [scrollThreshold]);
  
  // Scroll to bottom when messages change
  const scrollToBottom = useCallback((smooth = true) => {
    if (messages.length > 0) {
      virtualizer.scrollToIndex(messages.length - 1, {
        align: 'end',
        behavior: smooth ? 'smooth' : 'auto'
      });
    }
  }, [messages.length, virtualizer]);
  
  // Scroll to top function
  const scrollToTop = useCallback(() => {
    virtualizer.scrollToOffset(0, { behavior: 'smooth' });
  }, [virtualizer]);
  
  // Track scroll position to show/hide scroll to top button and manage auto-scroll
  const handleScroll = useCallback(() => {
    if (viewportRef.current) {
      const scrollTop = viewportRef.current.scrollTop;
      setShowScrollTopButton(scrollTop > 200); // Show after scrolling 200px
      
      // Update auto-scroll state based on position
      const atBottom = isNearBottom();
      if (atBottom && !shouldAutoScroll) {
        // User scrolled back to bottom, re-enable auto-scroll
        setShouldAutoScroll(true);
      } else if (!atBottom && shouldAutoScroll) {
        // User scrolled up, disable auto-scroll
        setShouldAutoScroll(false);
      }
    }
  }, [isNearBottom, shouldAutoScroll]);
  
  // Add event listener for scroll events
  useEffect(() => {
    const viewport = viewportRef.current;
    if (viewport) {
      viewport.addEventListener('scroll', handleScroll, { passive: true });
      return () => viewport.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);
  
  // Auto-scroll to bottom when messages change, but only if user is already at bottom
  useEffect(() => {
    if (shouldAutoScroll) {
      // Use requestAnimationFrame to ensure DOM is updated
      requestAnimationFrame(() => {
        scrollToBottom(true);
      });
    }
  }, [messages, shouldAutoScroll, scrollToBottom]);
  
  // Auto-scroll when tool selection indicator appears
  useEffect(() => {
    if (toolSelectionInProgress && shouldAutoScroll) {
      scrollToBottom();
    }
  }, [toolSelectionInProgress, shouldAutoScroll, scrollToBottom]);
  
  // Get virtual items to render
  const virtualItems = virtualizer.getVirtualItems();
  
  return (
    <div className={cn(
      "messages-list-container relative flex h-full w-full min-h-0 flex-col overflow-hidden overflow-x-hidden",
      className
    )}>
      <ScrollArea 
        className="flex-1 p-2 pb-3 overflow-hidden"
        type="always"
        scrollHideDelay={100}
        viewportRef={viewportRef}
        aria-label="Chat messages"
      >
        <div className="w-full overflow-x-hidden max-w-full pt-4 pb-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-4 text-center">
              <p>No messages yet. Start a conversation!</p>
            </div>
          ) : (
            <div 
              ref={parentRef}
              style={{
                height: `${virtualizer.getTotalSize()}px`,
                width: '100%',
                position: 'relative',
              }}
            >
              {virtualItems.map((virtualItem) => (
                <div
                  key={virtualItem.key}
                  data-index={virtualItem.index}
                  ref={virtualizer.measureElement}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualItem.start}px)`,
                  }}
                  className="message-item-wrapper w-full"
                >
                  <div className="mb-4">
                    <MessageItem
                      message={messages[virtualItem.index]}
                      index={virtualItem.index}
                      messages={messages}
                      expandedToolCallMessages={expandedToolCallMessages}
                      toggleToolCallExpansion={toggleToolCallExpansion}
                    />
                  </div>
                </div>
              ))}
              
              {/* Tool selection in progress indicator - only show if it would be visible */}
              {toolSelectionInProgress && (
                <div 
                  style={{
                    position: 'absolute',
                    top: `${virtualizer.getTotalSize()}px`,
                    left: 0,
                    width: '100%',
                    transform: 'translateY(0px)',
                  }}
                  className="flex items-center gap-2 text-sm italic ml-8 my-1 text-muted-foreground"
                >
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse"></div>
                  <span>Preparing to use: {toolSelectionName?.replace(/-/g, ' ') || 'tool'}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Scroll to top button with tooltip */}
      {showScrollTopButton && (
        <div className="scroll-indicator">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  onClick={scrollToTop} 
                  size="sm" 
                  variant="secondary" 
                  className="w-10 h-10 rounded-full flex items-center justify-center opacity-80 transition-opacity shadow-md hover:opacity-100"
                  aria-label="Scroll to top"
                >
                  <ChevronUp className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="left">
                <p>Scroll to top</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      )}
    </div>
  );
};

export default VirtualizedMessagesList;
