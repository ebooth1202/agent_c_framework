import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Message } from '../Message';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Message', () => {
  const user = userEvent.setup();

  const defaultProps = {
    id: 'msg-1',
    role: 'user' as const,
    content: 'Hello, this is a test message',
    timestamp: new Date('2024-01-01T10:00:00'),
  };

  describe('Rendering', () => {
    it('should render message content', () => {
      render(<Message {...defaultProps} />);
      expect(screen.getByText('Hello, this is a test message')).toBeInTheDocument();
    });

    it('should display user messages with correct styling', () => {
      render(<Message {...defaultProps} />);
      const message = screen.getByRole('article');
      expect(message).toHaveAttribute('data-sender', 'user');
      expect(message.className).toMatch(/justify-end/);
    });

    it('should display assistant messages with correct styling', () => {
      render(<Message {...defaultProps} role="assistant" />);
      const message = screen.getByRole('article');
      expect(message).toHaveAttribute('data-sender', 'assistant');
      expect(message.className).toMatch(/justify-start/);
    });

    it('should display system messages with correct styling', () => {
      render(<Message {...defaultProps} role="system" />);
      const message = screen.getByRole('article');
      expect(message).toHaveAttribute('data-sender', 'system');
      expect(message.className).toMatch(/justify-center/);
    });
  });

  describe('Content Types', () => {
    it('should render plain text content', () => {
      render(<Message {...defaultProps} />);
      expect(screen.getByText('Hello, this is a test message')).toBeInTheDocument();
    });

    it('should render markdown content', () => {
      const markdownContent = '**Bold text** and *italic text*';
      render(<Message {...defaultProps} content={markdownContent} />);
      
      const boldText = screen.getByText(/Bold text/);
      const italicText = screen.getByText(/italic text/);
      
      expect(boldText.tagName).toBe('STRONG');
      expect(italicText.tagName).toBe('EM');
    });

    it('should render code blocks with syntax highlighting', () => {
      const codeContent = '```javascript\nconst hello = "world";\n```';
      render(<Message {...defaultProps} content={codeContent} />);
      
      const codeBlock = screen.getByRole('code');
      expect(codeBlock).toBeInTheDocument();
      expect(codeBlock).toHaveClass('language-javascript');
    });

    it('should render links as clickable', () => {
      const linkContent = 'Visit [OpenAI](https://openai.com)';
      render(<Message {...defaultProps} content={linkContent} />);
      
      const link = screen.getByRole('link', { name: 'OpenAI' });
      expect(link).toHaveAttribute('href', 'https://openai.com');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('Timestamp Display', () => {
    it('should display formatted timestamp', () => {
      render(<Message {...defaultProps} />);
      const timestamp = screen.getByRole('time');
      expect(timestamp).toBeInTheDocument();
      expect(timestamp).toHaveAttribute('datetime', '2024-01-01T10:00:00.000Z');
    });

    it('should display relative time for recent messages', () => {
      const recentTime = new Date(Date.now() - 60000); // 1 minute ago
      render(<Message {...defaultProps} timestamp={recentTime} />);
      
      const timestamp = screen.getByRole('time');
      expect(timestamp.textContent).toMatch(/1 minute ago|just now/i);
    });
  });

  describe('Interactive Features', () => {
    it('should handle copy to clipboard', async () => {
      render(<Message {...defaultProps} />);
      
      const copyButton = screen.getByRole('button', { name: /copy/i });
      await user.click(copyButton);
      
      // Check for success feedback
      expect(screen.getByText(/copied/i)).toBeInTheDocument();
    });

    it('should handle message actions menu', async () => {
      render(<Message {...defaultProps} showActions />);
      
      const actionsButton = screen.getByRole('button', { name: /message actions/i });
      await user.click(actionsButton);
      
      // Check that menu opens
      expect(screen.getByRole('menu')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<Message {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels', () => {
      render(<Message {...defaultProps} />);
      const message = screen.getByRole('article');
      expect(message).toHaveAttribute('aria-label', expect.stringContaining('Message from user'));
    });

    it('should announce message sender to screen readers', () => {
      render(<Message {...defaultProps} />);
      const message = screen.getByRole('article');
      expect(message).toHaveAttribute('aria-label');
      expect(message.getAttribute('aria-label')).toMatch(/user/i);
    });

    it('should make timestamp accessible', () => {
      render(<Message {...defaultProps} />);
      const timestamp = screen.getByRole('time');
      expect(timestamp).toHaveAttribute('datetime');
      expect(timestamp).toHaveAccessibleName();
    });

    it('should support keyboard navigation for actions', async () => {
      render(<Message {...defaultProps} showActions />);
      
      // Tab to copy button
      await user.tab();
      const copyButton = screen.getByRole('button', { name: /copy/i });
      expect(copyButton).toHaveFocus();
      
      // Activate with Enter
      await user.keyboard('{Enter}');
      expect(screen.getByText(/copied/i)).toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    it('should display error state for failed messages', () => {
      render(<Message {...defaultProps} status="error" />);
      
      const errorIndicator = screen.getByRole('alert');
      expect(errorIndicator).toBeInTheDocument();
      expect(errorIndicator).toHaveTextContent(/failed to send/i);
    });

    it('should show retry option for failed messages', () => {
      const onRetry = vi.fn();
      render(<Message {...defaultProps} status="error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should display sending indicator', () => {
      render(<Message {...defaultProps} status="sending" />);
      
      const sendingIndicator = screen.getByRole('status');
      expect(sendingIndicator).toHaveTextContent(/sending/i);
    });
  });
});