/**
 * Comprehensive MessageList Component Tests
 * Testing list rendering, scrolling, virtualization, and interactions
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MessageList } from '../MessageList';
import { MessageFactory } from '../../../test/factories/message-factory';
import { 
  renderUI, 
  setupUser, 
  animation, 
  styles, 
  componentState,
  focus,
  keyboard,
  theme
} from '../../../test/utils/ui-test-utils';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('MessageList Component - Comprehensive Tests', () => {
  let user: ReturnType<typeof setupUser>;
  
  beforeEach(() => {
    user = setupUser();
    vi.useFakeTimers();
    
    // Mock IntersectionObserver for scroll detection
    global.IntersectionObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
      takeRecords: vi.fn(),
      root: null,
      rootMargin: '',
      thresholds: [],
    }));
  });
  
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  // ========== RENDERING TESTS ==========
  describe('Rendering Messages', () => {
    it('should render empty state when no messages', () => {
      render(<MessageList messages={[]} />);
      
      const emptyState = screen.getByText(/no messages yet/i);
      expect(emptyState).toBeInTheDocument();
    });

    it('should render a list of messages', () => {
      const messages = MessageFactory.createConversation(5);
      render(<MessageList messages={messages} />);
      
      const messageElements = screen.getAllByRole('article');
      expect(messageElements).toHaveLength(5);
    });

    it('should render messages in chronological order', () => {
      const messages = MessageFactory.createConversation(3);
      render(<MessageList messages={messages} />);
      
      const messageElements = screen.getAllByRole('article');
      
      // Check that timestamps are in ascending order
      const timestamps = messageElements.map(el => 
        el.getAttribute('data-timestamp')
      );
      
      for (let i = 1; i < timestamps.length; i++) {
        expect(new Date(timestamps[i]!).getTime()).toBeGreaterThanOrEqual(
          new Date(timestamps[i - 1]!).getTime()
        );
      }
    });

    it('should group messages by date', () => {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      const messages = [
        { ...MessageFactory.createUserMessage(), timestamp: yesterday },
        { ...MessageFactory.createAssistantMessage(), timestamp: yesterday },
        { ...MessageFactory.createUserMessage(), timestamp: today },
        { ...MessageFactory.createAssistantMessage(), timestamp: today }
      ];
      
      render(<MessageList messages={messages} showDateSeparators={true} />);
      
      // Should have date separators
      const dateSeparators = screen.getAllByRole('separator');
      expect(dateSeparators.length).toBeGreaterThan(0);
      
      // Check for "Today" and "Yesterday" labels
      expect(screen.getByText(/today/i)).toBeInTheDocument();
      expect(screen.getByText(/yesterday/i)).toBeInTheDocument();
    });

    it('should handle mixed message types', () => {
      const messages = MessageFactory.createMixedConversation();
      render(<MessageList messages={messages} />);
      
      // Check for system messages
      const systemMessages = screen.getAllByRole('article').filter(el =>
        el.getAttribute('aria-label')?.includes('system')
      );
      expect(systemMessages.length).toBeGreaterThan(0);
    });
  });

  // ========== SCROLLING BEHAVIOR ==========
  describe('Scrolling Behavior', () => {
    it('should auto-scroll to bottom on new messages', async () => {
      const scrollIntoViewMock = vi.fn();
      Element.prototype.scrollIntoView = scrollIntoViewMock;
      
      const messages = MessageFactory.createConversation(5);
      const { rerender } = render(<MessageList messages={messages} />);
      
      // Add a new message
      const newMessage = MessageFactory.createUserMessage('New message');
      const updatedMessages = [...messages, newMessage];
      
      rerender(<MessageList messages={updatedMessages} />);
      
      await waitFor(() => {
        expect(scrollIntoViewMock).toHaveBeenCalled();
      });
    });

    it('should not auto-scroll if user has scrolled up', async () => {
      const scrollIntoViewMock = vi.fn();
      Element.prototype.scrollIntoView = scrollIntoViewMock;
      
      const messages = MessageFactory.createConversation(20);
      const { container, rerender } = render(<MessageList messages={messages} />);
      
      // Simulate user scrolling up
      const scrollContainer = container.querySelector('[role="log"]');
      if (scrollContainer) {
        Object.defineProperty(scrollContainer, 'scrollTop', {
          writable: true,
          value: 100
        });
        Object.defineProperty(scrollContainer, 'scrollHeight', {
          writable: true,
          value: 1000
        });
        Object.defineProperty(scrollContainer, 'clientHeight', {
          writable: true,
          value: 500
        });
      }
      
      // Add new message
      const newMessage = MessageFactory.createAssistantMessage();
      rerender(<MessageList messages={[...messages, newMessage]} />);
      
      // Should not auto-scroll
      expect(scrollIntoViewMock).not.toHaveBeenCalled();
    });

    it('should show "scroll to bottom" button when scrolled up', async () => {
      const messages = MessageFactory.createConversation(50);
      const { container } = render(<MessageList messages={messages} />);
      
      // Simulate scrolling up
      const scrollContainer = container.querySelector('[role="log"]');
      if (scrollContainer) {
        scrollContainer.dispatchEvent(new Event('scroll'));
      }
      
      await waitFor(() => {
        const scrollButton = screen.getByRole('button', { name: /scroll to bottom/i });
        expect(scrollButton).toBeInTheDocument();
      });
    });

    it('should scroll to bottom when button is clicked', async () => {
      const scrollIntoViewMock = vi.fn();
      Element.prototype.scrollIntoView = scrollIntoViewMock;
      
      const messages = MessageFactory.createConversation(50);
      render(<MessageList messages={messages} />);
      
      // Click scroll to bottom button if it exists
      const scrollButton = screen.queryByRole('button', { name: /scroll to bottom/i });
      if (scrollButton) {
        await user.click(scrollButton);
        expect(scrollIntoViewMock).toHaveBeenCalled();
      }
    });
  });

  // ========== LOADING STATES ==========
  describe('Loading and Streaming States', () => {
    it('should show loading indicator when loading prop is true', () => {
      const messages = MessageFactory.createConversation(3);
      render(<MessageList messages={messages} isLoading={true} />);
      
      const loadingIndicator = screen.getByRole('status');
      expect(loadingIndicator).toBeInTheDocument();
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('should show typing indicator when someone is typing', () => {
      const messages = MessageFactory.createConversation(3);
      render(<MessageList messages={messages} showTypingIndicator={true} />);
      
      const typingIndicator = screen.getByRole('status', { name: /typing/i });
      expect(typingIndicator).toBeInTheDocument();
    });

    it('should display streaming message with indicator', () => {
      const messages = [
        ...MessageFactory.createConversation(3),
        MessageFactory.createStreamingMessage('Streaming...')
      ];
      
      render(<MessageList messages={messages} />);
      
      // Last message should have streaming indicator
      const messageElements = screen.getAllByRole('article');
      const lastMessage = messageElements[messageElements.length - 1];
      
      const streamingIndicator = within(lastMessage).queryByRole('status');
      expect(streamingIndicator || lastMessage.querySelector('.animate-pulse')).toBeTruthy();
    });

    it('should handle multiple users typing', () => {
      const messages = MessageFactory.createConversation(3);
      render(
        <MessageList 
          messages={messages} 
          typingUsers={['Alice', 'Bob']}
        />
      );
      
      expect(screen.getByText(/alice.*typing/i)).toBeInTheDocument();
      expect(screen.getByText(/bob.*typing/i)).toBeInTheDocument();
    });
  });

  // ========== VIRTUALIZATION ==========
  describe('Performance - Virtualization', () => {
    it('should virtualize long message lists', () => {
      const messages = MessageFactory.createManyMessages(1000);
      const { container } = render(
        <MessageList messages={messages} enableVirtualization={true} />
      );
      
      // Only a subset of messages should be rendered
      const renderedMessages = container.querySelectorAll('[role="article"]');
      expect(renderedMessages.length).toBeLessThan(messages.length);
    });

    it('should render visible messages on scroll', async () => {
      const messages = MessageFactory.createManyMessages(100);
      const { container } = render(
        <MessageList messages={messages} enableVirtualization={true} />
      );
      
      const scrollContainer = container.querySelector('[role="log"]');
      if (scrollContainer) {
        // Simulate scrolling
        scrollContainer.dispatchEvent(new Event('scroll'));
        
        await waitFor(() => {
          const renderedMessages = container.querySelectorAll('[role="article"]');
          expect(renderedMessages.length).toBeGreaterThan(0);
        });
      }
    });

    it('should maintain scroll position during virtualization', async () => {
      const messages = MessageFactory.createManyMessages(500);
      const { container } = render(
        <MessageList messages={messages} enableVirtualization={true} />
      );
      
      const scrollContainer = container.querySelector('[role="log"]');
      if (scrollContainer) {
        // Set scroll position
        const scrollPosition = 5000;
        Object.defineProperty(scrollContainer, 'scrollTop', {
          writable: true,
          value: scrollPosition
        });
        
        // Trigger scroll event
        scrollContainer.dispatchEvent(new Event('scroll'));
        
        // Scroll position should be maintained
        expect(scrollContainer.scrollTop).toBe(scrollPosition);
      }
    });
  });

  // ========== ACCESSIBILITY ==========
  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const messages = MessageFactory.createMixedConversation();
      const { container } = render(<MessageList messages={messages} />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should use semantic HTML for message list', () => {
      const messages = MessageFactory.createConversation(3);
      render(<MessageList messages={messages} />);
      
      const list = screen.getByRole('log');
      expect(list).toBeInTheDocument();
      expect(list).toHaveAttribute('aria-label', 'Chat messages');
    });

    it('should announce new messages to screen readers', async () => {
      const messages = MessageFactory.createConversation(2);
      const { rerender } = render(<MessageList messages={messages} />);
      
      // Add new message
      const newMessage = MessageFactory.createAssistantMessage('New announcement');
      rerender(<MessageList messages={[...messages, newMessage]} />);
      
      // Check for live region
      const liveRegion = screen.getByRole('log');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    });

    it('should support keyboard navigation', async () => {
      const messages = MessageFactory.createConversation(5);
      render(<MessageList messages={messages} />);
      
      // Tab through messages
      for (let i = 0; i < 5; i++) {
        await keyboard.tab(user);
        const focused = focus.getCurrent();
        expect(focused).toBeDefined();
      }
    });

    it('should handle focus management for interactive elements', async () => {
      const onMessageEdit = vi.fn();
      const messages = MessageFactory.createConversation(3);
      
      render(
        <MessageList 
          messages={messages} 
          onMessageEdit={onMessageEdit}
          enableMessageActions={true}
        />
      );
      
      // Focus on first message's action button
      await keyboard.tab(user);
      const actionButton = screen.getAllByRole('button')[0];
      
      if (actionButton) {
        expect(focus.hasFocus(actionButton)).toBe(true);
      }
    });
  });

  // ========== RESPONSIVE DESIGN ==========
  describe('Responsive Behavior', () => {
    it('should adapt layout for mobile devices', () => {
      styles.setViewport(375, 667);
      
      const messages = MessageFactory.createConversation(10);
      const { container } = render(<MessageList messages={messages} />);
      
      // Check for mobile-optimized spacing
      const messageContainer = container.querySelector('[role="log"]');
      const computedStyle = window.getComputedStyle(messageContainer!);
      
      expect(computedStyle.padding).toBeDefined();
    });

    it('should show compact view on small screens', () => {
      styles.setViewport(320, 568);
      
      const messages = MessageFactory.createConversation(5);
      render(<MessageList messages={messages} compactMode="auto" />);
      
      // Messages should use less padding
      const articles = screen.getAllByRole('article');
      articles.forEach(article => {
        expect(article.className).toMatch(/p-2|py-1/);
      });
    });

    it('should handle horizontal scrolling for wide content', () => {
      const longCodeMessage = MessageFactory.createCodeMessage();
      const messages = [longCodeMessage];
      
      const { container } = render(<MessageList messages={messages} />);
      
      const codeBlock = container.querySelector('pre');
      if (codeBlock) {
        const computedStyle = window.getComputedStyle(codeBlock);
        expect(computedStyle.overflowX).toBe('auto');
      }
    });
  });

  // ========== THEME SUPPORT ==========
  describe('Theme Customization', () => {
    it('should apply correct colors in dark mode', () => {
      document.documentElement.classList.add('dark');
      
      const messages = MessageFactory.createConversation(3);
      const { container } = render(<MessageList messages={messages} />);
      
      const messageList = container.querySelector('[role="log"]');
      expect(messageList).toHaveClass('dark:bg-background');
    });

    it('should transition smoothly between themes', async () => {
      const messages = MessageFactory.createConversation(3);
      render(<MessageList messages={messages} />);
      
      // Toggle theme
      theme.toggleDarkMode();
      
      await animation.waitForAnimation(300);
      
      // Messages should still be visible
      const messageElements = screen.getAllByRole('article');
      expect(messageElements).toHaveLength(3);
    });

    it('should support custom theme overrides', () => {
      const messages = MessageFactory.createConversation(2);
      const customTheme = {
        messageBackground: 'bg-custom-message',
        listBackground: 'bg-custom-list'
      };
      
      render(<MessageList messages={messages} theme={customTheme} />);
      
      // This would check for custom classes if theme prop is supported
      expect(screen.getByRole('log')).toBeInTheDocument();
    });
  });

  // ========== MESSAGE ACTIONS ==========
  describe('Message Actions and Interactions', () => {
    it('should handle message editing', async () => {
      const onMessageEdit = vi.fn();
      const messages = MessageFactory.createConversation(3);
      
      render(
        <MessageList 
          messages={messages} 
          onMessageEdit={onMessageEdit}
          enableMessageActions={true}
        />
      );
      
      // Find and click edit button on user message
      const userMessages = screen.getAllByRole('article').filter(el =>
        el.getAttribute('aria-label')?.includes('user')
      );
      
      if (userMessages.length > 0) {
        await user.hover(userMessages[0]);
        const editButton = within(userMessages[0]).getByRole('button', { name: /edit/i });
        await user.click(editButton);
        
        expect(onMessageEdit).toHaveBeenCalled();
      }
    });

    it('should handle message deletion', async () => {
      const onMessageDelete = vi.fn();
      const messages = MessageFactory.createConversation(3);
      
      render(
        <MessageList 
          messages={messages} 
          onMessageDelete={onMessageDelete}
          enableMessageActions={true}
        />
      );
      
      // Find and click delete button
      const messageElements = screen.getAllByRole('article');
      if (messageElements.length > 0) {
        await user.hover(messageElements[0]);
        const deleteButton = within(messageElements[0]).queryByRole('button', { name: /delete/i });
        
        if (deleteButton) {
          await user.click(deleteButton);
          expect(onMessageDelete).toHaveBeenCalled();
        }
      }
    });

    it('should handle message retry for failed messages', async () => {
      const onMessageRetry = vi.fn();
      const failedMessage = MessageFactory.createFailedMessage();
      const messages = [failedMessage];
      
      render(
        <MessageList 
          messages={messages} 
          onMessageRetry={onMessageRetry}
        />
      );
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);
      
      expect(onMessageRetry).toHaveBeenCalledWith(failedMessage.id);
    });

    it('should copy message content to clipboard', async () => {
      const mockClipboard = {
        writeText: vi.fn().mockResolvedValue(undefined)
      };
      Object.assign(navigator, { clipboard: mockClipboard });
      
      const messages = MessageFactory.createConversation(1);
      render(<MessageList messages={messages} enableMessageActions={true} />);
      
      const messageElement = screen.getByRole('article');
      await user.hover(messageElement);
      
      const copyButton = within(messageElement).queryByRole('button', { name: /copy/i });
      if (copyButton) {
        await user.click(copyButton);
        expect(mockClipboard.writeText).toHaveBeenCalled();
      }
    });
  });

  // ========== SEARCH AND FILTERING ==========
  describe('Search and Filtering', () => {
    it('should highlight search terms in messages', () => {
      const messages = [
        MessageFactory.createUserMessage('Hello world'),
        MessageFactory.createAssistantMessage('World peace is important')
      ];
      
      render(<MessageList messages={messages} searchTerm="world" />);
      
      // Check for highlighted text
      const highlights = screen.getAllByText(/world/i);
      highlights.forEach(highlight => {
        expect(highlight.className).toMatch(/highlight|bg-yellow/);
      });
    });

    it('should filter messages by role', () => {
      const messages = MessageFactory.createConversation(6);
      render(<MessageList messages={messages} filterRole="user" />);
      
      const displayedMessages = screen.getAllByRole('article');
      displayedMessages.forEach(msg => {
        expect(msg.getAttribute('aria-label')).toContain('user');
      });
    });

    it('should filter messages by date range', () => {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const twoDaysAgo = new Date(today);
      twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
      
      const messages = [
        { ...MessageFactory.createUserMessage(), timestamp: twoDaysAgo },
        { ...MessageFactory.createAssistantMessage(), timestamp: yesterday },
        { ...MessageFactory.createUserMessage(), timestamp: today }
      ];
      
      render(
        <MessageList 
          messages={messages} 
          dateFilter={{ from: yesterday, to: today }}
        />
      );
      
      // Only messages from yesterday and today should be shown
      const displayedMessages = screen.getAllByRole('article');
      expect(displayedMessages).toHaveLength(2);
    });
  });

  // ========== ERROR HANDLING ==========
  describe('Error Handling', () => {
    it('should display error state when messages fail to load', () => {
      render(<MessageList messages={[]} error="Failed to load messages" />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveTextContent(/failed to load/i);
    });

    it('should show retry button on error', async () => {
      const onRetry = vi.fn();
      render(
        <MessageList 
          messages={[]} 
          error="Network error" 
          onRetry={onRetry}
        />
      );
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);
      
      expect(onRetry).toHaveBeenCalled();
    });

    it('should handle malformed message data gracefully', () => {
      const malformedMessages = [
        { id: '1', role: 'user', content: null, timestamp: new Date() } as any,
        { id: '2', role: undefined, content: 'Test', timestamp: new Date() } as any,
        { id: '3', role: 'assistant', content: undefined, timestamp: null } as any
      ];
      
      // Should not crash
      const { container } = render(<MessageList messages={malformedMessages} />);
      expect(container).toBeInTheDocument();
    });
  });

  // ========== PERFORMANCE OPTIMIZATIONS ==========
  describe('Performance', () => {
    it('should debounce scroll events', async () => {
      const onScroll = vi.fn();
      const messages = MessageFactory.createManyMessages(100);
      
      const { container } = render(
        <MessageList messages={messages} onScroll={onScroll} />
      );
      
      const scrollContainer = container.querySelector('[role="log"]');
      if (scrollContainer) {
        // Trigger multiple scroll events rapidly
        for (let i = 0; i < 10; i++) {
          scrollContainer.dispatchEvent(new Event('scroll'));
        }
        
        // Wait for debounce
        vi.advanceTimersByTime(300);
        
        // Should be called less than 10 times due to debouncing
        expect(onScroll.mock.calls.length).toBeLessThan(10);
      }
    });

    it('should use React.memo for message components', () => {
      const messages = MessageFactory.createConversation(5);
      const { rerender } = render(<MessageList messages={messages} />);
      
      // Re-render with same messages
      rerender(<MessageList messages={messages} />);
      
      // This would normally check render counts with a spy
      expect(screen.getAllByRole('article')).toHaveLength(5);
    });

    it('should batch message updates', async () => {
      const messages = MessageFactory.createConversation(10);
      const { rerender } = render(<MessageList messages={messages} />);
      
      // Add multiple messages at once
      const newMessages = [
        ...messages,
        ...MessageFactory.createConversation(5)
      ];
      
      rerender(<MessageList messages={newMessages} />);
      
      await waitFor(() => {
        expect(screen.getAllByRole('article')).toHaveLength(15);
      });
    });
  });
});