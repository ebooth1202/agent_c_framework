import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConnectionButton } from '../ConnectionButton';
import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

expect.extend(toHaveNoViolations);

// Mock the hook from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useConnection: vi.fn(() => ({
    isConnected: false,
    connectionState: 'disconnected',
    connect: vi.fn(),
    disconnect: vi.fn(),
    error: null,
  })),
}));

describe('ConnectionButton', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render connect button when disconnected', () => {
      render(<ConnectionButton />);
      const button = screen.getByRole('button', { name: /connect/i });
      expect(button).toBeInTheDocument();
    });

    it('should render disconnect button when connected', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: true,
        connectionState: 'connected',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button', { name: /disconnect/i });
      expect(button).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(<ConnectionButton className="custom-button-class" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-button-class');
    });
  });

  describe('Connection States', () => {
    it('should show connecting state', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'connecting',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent(/connecting/i);
      expect(button).toBeDisabled();
    });

    it('should show error state', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'error',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: new Error('Connection failed'),
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-destructive');
    });

    it('should show reconnecting state', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'reconnecting',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      expect(screen.getByText(/reconnecting/i)).toBeInTheDocument();
    });
  });

  describe('Interactivity', () => {
    it('should call connect when clicked while disconnected', async () => {
      const connect = vi.fn();
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'disconnected',
        connect,
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button', { name: /connect/i });
      
      await user.click(button);
      expect(connect).toHaveBeenCalledTimes(1);
    });

    it('should call disconnect when clicked while connected', async () => {
      const disconnect = vi.fn();
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: true,
        connectionState: 'connected',
        connect: vi.fn(),
        disconnect,
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button', { name: /disconnect/i });
      
      await user.click(button);
      expect(disconnect).toHaveBeenCalledTimes(1);
    });

    it('should be disabled during connection attempt', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'connecting',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Status Indicator', () => {
    it('should show status indicator by default', () => {
      render(<ConnectionButton />);
      const statusIndicator = screen.getByRole('img', { name: /connection status/i });
      expect(statusIndicator).toBeInTheDocument();
    });

    it('should hide status indicator when showStatus is false', () => {
      render(<ConnectionButton showStatus={false} />);
      const statusIndicator = screen.queryByRole('img', { name: /connection status/i });
      expect(statusIndicator).not.toBeInTheDocument();
    });

    it('should position status indicator on the left by default', () => {
      const { container } = render(<ConnectionButton />);
      const button = container.querySelector('button');
      const statusIndicator = button?.querySelector('[aria-label*="status"]');
      const buttonText = screen.getByText(/connect/i);
      
      // Status should come before text in DOM
      expect(statusIndicator?.compareDocumentPosition(buttonText.parentElement!))
        .toBe(Node.DOCUMENT_POSITION_FOLLOWING);
    });

    it('should position status indicator on the right when specified', () => {
      const { container } = render(<ConnectionButton statusPosition="right" />);
      const button = container.querySelector('button');
      const statusIndicator = button?.querySelector('[aria-label*="status"]');
      const buttonText = screen.getByText(/connect/i);
      
      // Status should come after text in DOM
      expect(statusIndicator?.compareDocumentPosition(buttonText.parentElement!))
        .toBe(Node.DOCUMENT_POSITION_PRECEDING);
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<ConnectionButton />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have appropriate ARIA labels', () => {
      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Connect');
    });

    it('should update ARIA label based on state', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: true,
        connectionState: 'connected',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Disconnect');
    });

    it('should support keyboard activation', async () => {
      const connect = vi.fn();
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'disconnected',
        connect,
        disconnect: vi.fn(),
        error: null,
      });

      render(<ConnectionButton />);
      const button = screen.getByRole('button');
      
      button.focus();
      await user.keyboard('{Enter}');
      expect(connect).toHaveBeenCalled();
      
      await user.keyboard(' ');
      expect(connect).toHaveBeenCalledTimes(2);
    });

    it('should announce state changes to screen readers', () => {
      const { rerender } = render(<ConnectionButton />);
      
      // Change to connecting state
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'connecting',
        connect: vi.fn(),
        disconnect: vi.fn(),
        error: null,
      });
      
      rerender(<ConnectionButton />);
      
      // Should have live region for status updates
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveTextContent(/connecting/i);
    });
  });

  describe('Button Variants', () => {
    it('should support different visual variants', () => {
      const { rerender } = render(<ConnectionButton variant="default" />);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary');

      rerender(<ConnectionButton variant="outline" />);
      button = screen.getByRole('button');
      expect(button).toHaveClass('border');

      rerender(<ConnectionButton variant="ghost" />);
      button = screen.getByRole('button');
      expect(button).toHaveClass('hover:bg-accent');
    });

    it('should support different sizes', () => {
      const { rerender } = render(<ConnectionButton size="default" />);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('h-10');

      rerender(<ConnectionButton size="sm" />);
      button = screen.getByRole('button');
      expect(button).toHaveClass('h-9');

      rerender(<ConnectionButton size="lg" />);
      button = screen.getByRole('button');
      expect(button).toHaveClass('h-11');
    });
  });
});