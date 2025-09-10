/**
 * Integration Tests for Error Boundaries and Recovery
 * Tests error handling, recovery flows, and user experience during failures
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ErrorBoundary } from '../layout/error-boundary';
import { ChatInterface } from '../chat/chat-interface';
import { AuthProvider } from '@/contexts/auth-context';
import { AgentCProvider } from '@agentc/realtime-react';
import { InitializationWrapper } from '../providers/initialization-wrapper';
import { server, demoHandlerOverrides } from '@/test/mocks/server';
import { storage } from '@/test/utils/demo-test-utils';

// Component that throws errors on demand
function ThrowingComponent({ shouldThrow, error }: { shouldThrow: boolean; error?: Error }) {
  if (shouldThrow) {
    throw error || new Error('Test error');
  }
  return <div data-testid="working-component">Component is working</div>;
}

// Component that throws async errors
function AsyncThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  const [isLoading, setIsLoading] = React.useState(true);
  
  React.useEffect(() => {
    const load = async () => {
      if (shouldThrow) {
        throw new Error('Async error');
      }
      setIsLoading(false);
    };
    load().catch(() => {
      // Error should be caught by boundary
    });
  }, [shouldThrow]);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return <div data-testid="async-component">Async component loaded</div>;
}

describe('Error Boundaries and Recovery', () => {
  let mockClient: any;

  beforeEach(() => {
    storage.clear();
    
    mockClient = {
      isConnected: vi.fn(() => true),
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      sendText: vi.fn().mockResolvedValue({ messageId: 'msg-123' }),
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
      getConnectionState: vi.fn(() => 'connected')
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Error Boundary Functionality', () => {
    it('catches and displays component errors', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument();
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/Test error/i)).toBeInTheDocument();
    });

    it('allows recovery through retry button', async () => {
      const user = userEvent.setup();
      let shouldThrow = true;
      
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );

      // Error should be displayed
      expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument();
      
      // Fix the error condition
      shouldThrow = false;
      
      // Click retry
      const retryButton = screen.getByRole('button', { name: /try again/i });
      await user.click(retryButton);
      
      // Rerender with fixed condition
      rerender(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );
      
      // Should recover
      await waitFor(() => {
        expect(screen.queryByTestId('error-boundary-fallback')).not.toBeInTheDocument();
        expect(screen.getByTestId('working-component')).toBeInTheDocument();
      });
    });

    it('provides error details in development mode', () => {
      process.env.NODE_ENV = 'development';
      
      const error = new Error('Detailed error message');
      error.stack = 'Error: Detailed error message\n  at Component.render\n  at ErrorBoundary';
      
      const { container } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} error={error} />
        </ErrorBoundary>
      );

      // Should show stack trace in development
      expect(screen.getByTestId('error-stack-trace')).toBeInTheDocument();
      expect(screen.getByText(/at Component.render/i)).toBeInTheDocument();
      
      process.env.NODE_ENV = 'test';
    });

    it('logs errors to error reporting service', () => {
      const errorReportSpy = vi.fn();
      (global as any).errorReporter = { report: errorReportSpy };
      
      const error = new Error('Error to report');
      
      render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} error={error} />
        </ErrorBoundary>
      );

      expect(errorReportSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          error,
          errorInfo: expect.any(Object),
          timestamp: expect.any(String)
        })
      );
      
      delete (global as any).errorReporter;
    });
  });

  describe('Network Error Recovery', () => {
    it('handles network offline scenario', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Simulate network going offline
      demoHandlerOverrides.offline();
      mockClient.isConnected.mockReturnValue(false);
      mockClient.getConnectionState.mockReturnValue('disconnected');
      mockClient.emit('disconnected', { code: 1006, reason: 'Network error' });

      // Should show offline indicator
      await waitFor(() => {
        expect(screen.getByTestId('offline-indicator')).toBeInTheDocument();
        expect(screen.getByText(/you are offline/i)).toBeInTheDocument();
      });

      // Simulate network recovery
      server.resetHandlers();
      
      const reconnectButton = screen.getByRole('button', { name: /reconnect/i });
      await user.click(reconnectButton);
      
      mockClient.connect.mockResolvedValueOnce(undefined);
      mockClient.isConnected.mockReturnValue(true);
      mockClient.getConnectionState.mockReturnValue('connected');
      mockClient.emit('connected', { sessionId: 'reconnected' });

      // Should recover
      await waitFor(() => {
        expect(screen.queryByTestId('offline-indicator')).not.toBeInTheDocument();
      });
    });

    it('handles slow network with timeout', async () => {
      // Simulate slow network
      demoHandlerOverrides.slowNetwork(5000);
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Try to send a message
      const user = userEvent.setup();
      const input = screen.getByTestId('chat-input');
      const sendButton = screen.getByTestId('send-button');
      
      await user.type(input, 'Test message');
      
      // Mock slow response
      mockClient.sendText.mockImplementation(() => 
        new Promise((resolve) => setTimeout(() => resolve({ messageId: 'slow' }), 5000))
      );
      
      await user.click(sendButton);

      // Should show loading state
      expect(screen.getByTestId('message-sending')).toBeInTheDocument();
      
      // Should show timeout warning after threshold
      await waitFor(() => {
        expect(screen.getByText(/taking longer than usual/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('handles rate limiting gracefully', async () => {
      const user = userEvent.setup();
      
      // Setup rate limiting
      demoHandlerOverrides.rateLimited();
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Try to send multiple messages quickly
      const input = screen.getByTestId('chat-input');
      const sendButton = screen.getByTestId('send-button');
      
      for (let i = 0; i < 5; i++) {
        await user.type(input, `Message ${i}`);
        await user.click(sendButton);
        await user.clear(input);
      }

      // Should show rate limit warning
      await waitFor(() => {
        expect(screen.getByTestId('rate-limit-warning')).toBeInTheDocument();
        expect(screen.getByText(/please slow down/i)).toBeInTheDocument();
      });

      // Should show retry after time
      expect(screen.getByText(/try again in 60 seconds/i)).toBeInTheDocument();
    });
  });

  describe('Authentication Error Recovery', () => {
    it('handles expired session gracefully', async () => {
      const user = userEvent.setup();
      
      // Setup authenticated state
      localStorage.setItem('agentc-auth-token', 'expired-token');
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <InitializationWrapper>
              <ChatInterface />
            </InitializationWrapper>
          </AgentCProvider>
        </AuthProvider>
      );

      // Simulate session expiration
      demoHandlerOverrides.authError();
      mockClient.emit('error', {
        type: 'auth_error',
        code: 'SESSION_EXPIRED',
        message: 'Your session has expired'
      });

      // Should show session expired message
      await waitFor(() => {
        expect(screen.getByTestId('session-expired')).toBeInTheDocument();
      });

      // Should offer to re-authenticate
      const reAuthButton = screen.getByRole('button', { name: /sign in again/i });
      expect(reAuthButton).toBeInTheDocument();
      
      // Click to re-authenticate
      await user.click(reAuthButton);
      
      // Should redirect to login
      expect(screen.getByTestId('login-form')).toBeInTheDocument();
    });

    it('handles invalid token on initialization', async () => {
      // Setup invalid token
      localStorage.setItem('agentc-auth-token', 'invalid-token');
      
      mockClient.connect.mockRejectedValueOnce(new Error('Invalid authentication token'));
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <InitializationWrapper>
              <ChatInterface />
            </InitializationWrapper>
          </AgentCProvider>
        </AuthProvider>
      );

      // Should show auth error
      await waitFor(() => {
        expect(screen.getByTestId('auth-error')).toBeInTheDocument();
        expect(screen.getByText(/invalid authentication/i)).toBeInTheDocument();
      });

      // Should clear invalid token
      expect(localStorage.getItem('agentc-auth-token')).toBeNull();
    });
  });

  describe('Component Error Recovery', () => {
    it('isolates errors to specific components', async () => {
      const { container } = render(
        <div>
          <ErrorBoundary>
            <ThrowingComponent shouldThrow={true} />
          </ErrorBoundary>
          <div data-testid="sibling-component">Sibling is fine</div>
        </div>
      );

      // Error in one component shouldn't affect siblings
      expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument();
      expect(screen.getByTestId('sibling-component')).toBeInTheDocument();
      expect(screen.getByText('Sibling is fine')).toBeInTheDocument();
    });

    it('handles cascading errors', async () => {
      const ParentComponent = () => {
        const [childError, setChildError] = React.useState(false);
        
        return (
          <ErrorBoundary>
            <div>
              <button onClick={() => setChildError(true)}>Trigger Error</button>
              <ErrorBoundary>
                <ThrowingComponent shouldThrow={childError} />
              </ErrorBoundary>
            </div>
          </ErrorBoundary>
        );
      };
      
      const user = userEvent.setup();
      const { container } = render(<ParentComponent />);
      
      // Trigger nested error
      await user.click(screen.getByText('Trigger Error'));
      
      // Inner boundary should catch it
      await waitFor(() => {
        expect(screen.getAllByTestId('error-boundary-fallback')).toHaveLength(1);
      });
    });

    it('recovers from async errors', async () => {
      let shouldThrow = true;
      
      const { rerender } = render(
        <ErrorBoundary>
          <AsyncThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );

      // Wait for async error
      await waitFor(() => {
        expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument();
      });

      // Fix condition and retry
      shouldThrow = false;
      const user = userEvent.setup();
      await user.click(screen.getByRole('button', { name: /try again/i }));
      
      rerender(
        <ErrorBoundary>
          <AsyncThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );
      
      // Should recover
      await waitFor(() => {
        expect(screen.queryByTestId('error-boundary-fallback')).not.toBeInTheDocument();
      });
    });
  });

  describe('User Experience During Errors', () => {
    it('maintains partial functionality during errors', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <div>
              <div data-testid="header">App Header</div>
              <ErrorBoundary>
                <ChatInterface />
              </ErrorBoundary>
              <div data-testid="footer">App Footer</div>
            </div>
          </AgentCProvider>
        </AuthProvider>
      );

      // Cause an error in chat interface
      mockClient.emit('error', { type: 'critical', message: 'Chat system error' });
      
      // Header and footer should still work
      expect(screen.getByTestId('header')).toBeInTheDocument();
      expect(screen.getByTestId('footer')).toBeInTheDocument();
      
      // Should show error in chat area
      await waitFor(() => {
        expect(screen.getByText(/chat system error/i)).toBeInTheDocument();
      });
    });

    it('preserves user data during error recovery', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Add some messages
      const input = screen.getByTestId('chat-input');
      await user.type(input, 'Message before error');
      await user.keyboard('{Enter}');
      
      mockClient.emit('message', {
        id: 'msg-1',
        role: 'user',
        content: 'Message before error',
        timestamp: new Date().toISOString()
      });

      // Cause and recover from error
      mockClient.emit('error', { type: 'temporary', message: 'Temporary error' });
      
      await waitFor(() => {
        expect(screen.getByText(/temporary error/i)).toBeInTheDocument();
      });
      
      // Recover
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);
      
      mockClient.emit('error_cleared', {});
      
      // Messages should still be there
      await waitFor(() => {
        expect(screen.getByText('Message before error')).toBeInTheDocument();
      });
    });

    it('provides helpful error messages', async () => {
      const errorScenarios = [
        {
          error: { code: 'NETWORK_ERROR', message: 'Connection failed' },
          expectedMessage: /check your internet connection/i
        },
        {
          error: { code: 'AUTH_ERROR', message: 'Authentication failed' },
          expectedMessage: /please sign in again/i
        },
        {
          error: { code: 'RATE_LIMIT', message: 'Too many requests' },
          expectedMessage: /please wait a moment/i
        },
        {
          error: { code: 'SERVER_ERROR', message: 'Internal server error' },
          expectedMessage: /temporary issue.*try again/i
        }
      ];

      for (const scenario of errorScenarios) {
        const { container } = render(
          <AuthProvider>
            <AgentCProvider client={mockClient} apiUrl="ws://test">
              <ChatInterface />
            </AgentCProvider>
          </AuthProvider>
        );

        mockClient.emit('error', scenario.error);
        
        await waitFor(() => {
          expect(screen.getByText(scenario.expectedMessage)).toBeInTheDocument();
        });
        
        // Clean up for next iteration
        container.remove();
      }
    });
  });

  describe('Error Reporting and Analytics', () => {
    it('tracks error occurrences', async () => {
      const analyticsSpy = vi.fn();
      (global as any).analytics = { track: analyticsSpy };
      
      const { container } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(analyticsSpy).toHaveBeenCalledWith('error_boundary_triggered', {
        error_message: 'Test error',
        component_stack: expect.any(String),
        timestamp: expect.any(String)
      });
      
      delete (global as any).analytics;
    });

    it('tracks recovery attempts', async () => {
      const user = userEvent.setup();
      const analyticsSpy = vi.fn();
      (global as any).analytics = { track: analyticsSpy };
      
      let shouldThrow = true;
      
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );

      // Attempt recovery
      shouldThrow = false;
      await user.click(screen.getByRole('button', { name: /try again/i }));
      
      rerender(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={shouldThrow} />
        </ErrorBoundary>
      );

      expect(analyticsSpy).toHaveBeenCalledWith('error_recovery_attempted', {
        success: true,
        timestamp: expect.any(String)
      });
      
      delete (global as any).analytics;
    });
  });

  describe('Graceful Degradation', () => {
    it('falls back to basic functionality when advanced features fail', async () => {
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Simulate voice feature failure
      mockClient.emit('feature_error', {
        feature: 'voice',
        message: 'Voice processing unavailable'
      });

      // Voice button should be disabled but text input should work
      await waitFor(() => {
        expect(screen.getByTestId('voice-button')).toBeDisabled();
        expect(screen.getByTestId('chat-input')).not.toBeDisabled();
      });

      // Should show feature unavailable message
      expect(screen.getByText(/voice feature temporarily unavailable/i)).toBeInTheDocument();
    });

    it('provides offline mode with limited functionality', async () => {
      // Start in offline mode
      mockClient.isConnected.mockReturnValue(false);
      mockClient.getConnectionState.mockReturnValue('disconnected');
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider client={mockClient} apiUrl="ws://test">
            <ChatInterface offlineMode={true} />
          </AgentCProvider>
        </AuthProvider>
      );

      // Should show offline mode indicator
      expect(screen.getByTestId('offline-mode')).toBeInTheDocument();
      
      // Can still compose messages (queued for later)
      const user = userEvent.setup();
      const input = screen.getByTestId('chat-input');
      
      await user.type(input, 'Offline message');
      await user.keyboard('{Enter}');
      
      // Message should be queued
      expect(screen.getByText('Offline message')).toBeInTheDocument();
      expect(screen.getByTestId('message-queued')).toBeInTheDocument();
      
      // When connection restored, messages should send
      mockClient.isConnected.mockReturnValue(true);
      mockClient.emit('connected', { sessionId: 'restored' });
      
      await waitFor(() => {
        expect(mockClient.sendText).toHaveBeenCalledWith('Offline message');
        expect(screen.queryByTestId('message-queued')).not.toBeInTheDocument();
      });
    });
  });
});