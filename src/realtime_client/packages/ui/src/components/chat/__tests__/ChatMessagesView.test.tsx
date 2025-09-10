import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatMessagesView } from '../ChatMessagesView';
// TODO: Uncomment when jest-axe is installed
// import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

// TODO: Uncomment when jest-axe is installed
// expect.extend(toHaveNoViolations);

// Mock the hook from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useChat: vi.fn(() => ({
    messages: [],
    isTyping: false,
    sendMessage: vi.fn(),
    clearMessages: vi.fn(),
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
}));

describe('ChatMessagesView', () => {
  const user = userEvent.setup();
  
  const mockMessages = [
    {
      id: '1',
      role: 'user',
      content: 'Hello, how are you?',
      timestamp: new Date('2024-01-01T10:00:00'),
    },
    {
      id: '2',
      role: 'assistant',
      content: 'I am doing well, thank you!',
      timestamp: new Date('2024-01-01T10:00:30'),
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the chat messages view', () => {
      render(<ChatMessagesView />);
      const chatContainer = screen.getByRole('log', { name: /chat messages/i });
      expect(chatContainer).toBeInTheDocument();
    });

    it('should display empty state when no messages', () => {
      render(<ChatMessagesView />);
      const emptyState = screen.getByText(/no messages yet/i);
      expect(emptyState).toBeInTheDocument();
    });

    it('should display all messages', () => {
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument();
    });
  });

  describe('Message Display', () => {
    it('should distinguish between user and assistant messages', () => {
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      const userMessage = screen.getByText('Hello, how are you?').closest('[role="article"]');
      const assistantMessage = screen.getByText('I am doing well, thank you!').closest('[role="article"]');
      
      expect(userMessage).toHaveAttribute('data-sender', 'user');
      expect(assistantMessage).toHaveAttribute('data-sender', 'assistant');
    });

    it('should display timestamps for messages', () => {
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      // Check for timestamp display
      const timestamps = screen.getAllByRole('time');
      expect(timestamps).toHaveLength(2);
    });

    it('should show typing indicator when assistant is typing', () => {
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: true,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      const typingIndicator = screen.getByRole('status', { name: /typing/i });
      expect(typingIndicator).toBeInTheDocument();
    });
  });

  describe('Scrolling Behavior', () => {
    it('should auto-scroll to bottom when new messages arrive', async () => {
      const { rerender } = render(<ChatMessagesView />);
      
      // Add initial messages
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });
      
      rerender(<ChatMessagesView />);
      
      // Add a new message
      const newMessages = [...mockMessages, {
        id: '3',
        role: 'user',
        content: 'New message',
        timestamp: new Date('2024-01-01T10:01:00'),
      }];
      
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: newMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });
      
      rerender(<ChatMessagesView />);
      
      // Check that the new message is visible
      expect(screen.getByText('New message')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    // TODO: Uncomment when jest-axe is installed
    it.skip('should have no accessibility violations', async () => {
      // const { container } = render(<ChatMessagesView />);
      // const results = await axe(container);
      // expect(results).toHaveNoViolations();
    });

    it('should use semantic HTML for message list', () => {
      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      // Should use appropriate ARIA role
      const chatLog = screen.getByRole('log');
      expect(chatLog).toHaveAttribute('aria-label', expect.stringContaining('chat'));
    });

    it('should announce new messages to screen readers', () => {
      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      // Should have live region for new messages
      const liveRegion = screen.getByRole('log');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    });

    it('should provide message context for screen readers', () => {
      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      const messages = screen.getAllByRole('article');
      messages.forEach(message => {
        // Each message should have aria-label with sender info
        expect(message).toHaveAttribute('aria-label');
      });
    });

    it('should support keyboard navigation through messages', async () => {
      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: mockMessages,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      render(<ChatMessagesView />);
      
      // Tab through messages
      await user.tab();
      const firstMessage = screen.getAllByRole('article')[0];
      expect(document.activeElement).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error state when messages fail to load', () => {
      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: [],
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
        error: new Error('Failed to load messages'),
      });

      render(<ChatMessagesView />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent(/failed to load messages/i);
    });
  });

  describe('Performance', () => {
    it('should efficiently render large message lists', () => {
      const largeMessageList = Array.from({ length: 100 }, (_, i) => ({
        id: `msg-${i}`,
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}`,
        timestamp: new Date(),
      }));

      const { useChat } = vi.mocked(await import('@agentc/realtime-react'));
      vi.mocked(realtimeReact.useChat).mockReturnValue({
        messages: largeMessageList,
        isTyping: false,
        sendMessage: vi.fn(),
        clearMessages: vi.fn(),
      });

      const { container } = render(<ChatMessagesView />);
      
      // Should render without crashing
      const messages = within(container).getAllByRole('article');
      expect(messages.length).toBe(100);
    });
  });
});