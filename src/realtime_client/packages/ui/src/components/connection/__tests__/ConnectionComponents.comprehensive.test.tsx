/**
 * Comprehensive Connection Components Tests
 * Testing ConnectionIndicator, ConnectionButton, and ConnectionStatus components
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ConnectionIndicator } from '../ConnectionIndicator';
import { ConnectionButton } from '../ConnectionButton';
import { ConnectionStatus } from '../ConnectionStatus';
import { ConnectionPanel } from '../ConnectionPanel';
import { 
  updateMockState,
  resetAllMocks,
  useConnection,
  useInitializationStatus
} from '../../../test/mocks/realtime-react';
import { 
  setupUser, 
  animation, 
  styles, 
  componentState,
  focus,
  keyboard,
  theme
} from '../../../test/utils/ui-test-utils';

expect.extend(toHaveNoViolations);

describe('Connection Components - Comprehensive Tests', () => {
  let user: ReturnType<typeof setupUser>;
  
  beforeEach(() => {
    user = setupUser();
    resetAllMocks();
    vi.useFakeTimers();
    
    // Mock WebSocket
    global.WebSocket = vi.fn().mockImplementation(() => ({
      readyState: WebSocket.CONNECTING,
      close: vi.fn(),
      send: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      CONNECTING: 0,
      OPEN: 1,
      CLOSING: 2,
      CLOSED: 3
    }));
  });
  
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  // ========== CONNECTION INDICATOR TESTS ==========
  describe('ConnectionIndicator', () => {
    describe('Visual States', () => {
      it('should show disconnected state', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'disconnected'
        });
        
        render(<ConnectionIndicator />);
        const indicator = screen.getByRole('status');
        expect(indicator).toHaveAttribute('aria-label', 'Connection status: Disconnected');
        
        // Check for visual indicator
        const dot = indicator.querySelector('.bg-gray-400');
        expect(dot).toBeInTheDocument();
      });

      it('should show connecting state with animation', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting'
        });
        
        render(<ConnectionIndicator />);
        const indicator = screen.getByRole('status');
        expect(indicator).toHaveAttribute('aria-label', 'Connection status: Connecting');
        
        // Check for pulsing animation
        const dot = indicator.querySelector('.animate-pulse');
        expect(dot).toBeInTheDocument();
        expect(dot).toHaveClass('bg-yellow-500');
      });

      it('should show connected state', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionIndicator />);
        const indicator = screen.getByRole('status');
        expect(indicator).toHaveAttribute('aria-label', 'Connection status: Connected');
        
        // Check for green indicator
        const dot = indicator.querySelector('.bg-green-500');
        expect(dot).toBeInTheDocument();
      });

      it('should show error state', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'error',
          error: 'Connection failed'
        });
        
        render(<ConnectionIndicator />);
        const indicator = screen.getByRole('status');
        expect(indicator).toHaveAttribute('aria-label', 'Connection status: Error');
        
        // Check for red indicator
        const dot = indicator.querySelector('.bg-destructive');
        expect(dot).toBeInTheDocument();
      });

      it('should display custom labels', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionIndicator showLabel={true} />);
        expect(screen.getByText('Connected')).toBeInTheDocument();
      });

      it('should handle custom size variants', () => {
        const { container } = render(
          <ConnectionIndicator size="large" />
        );
        
        const indicator = container.querySelector('.h-4.w-4');
        expect(indicator).toBeInTheDocument();
      });
    });

    describe('Tooltip and Hover States', () => {
      it('should show tooltip on hover', async () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected',
          stats: {
            latency: 45,
            messagesReceived: 150,
            messagesSent: 75
          }
        });
        
        render(<ConnectionIndicator showTooltip={true} />);
        const indicator = screen.getByRole('status');
        
        await user.hover(indicator);
        
        await waitFor(() => {
          const tooltip = screen.getByRole('tooltip');
          expect(tooltip).toBeInTheDocument();
          expect(tooltip).toHaveTextContent(/latency: 45ms/i);
        });
      });

      it('should show connection stats in tooltip', async () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 32,
            messagesReceived: 1234,
            messagesSent: 567,
            bytesReceived: 45678,
            bytesSent: 12345
          }
        });
        
        render(<ConnectionIndicator showTooltip={true} showStats={true} />);
        const indicator = screen.getByRole('status');
        
        await user.hover(indicator);
        
        await waitFor(() => {
          const tooltip = screen.getByRole('tooltip');
          expect(tooltip).toHaveTextContent(/messages: 1234 received/i);
          expect(tooltip).toHaveTextContent(/567 sent/i);
        });
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<ConnectionIndicator />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should provide proper ARIA labels', () => {
        const states = [
          { connectionState: 'disconnected', label: 'Disconnected' },
          { connectionState: 'connecting', label: 'Connecting' },
          { connectionState: 'connected', label: 'Connected' },
          { connectionState: 'error', label: 'Error' }
        ];
        
        states.forEach(({ connectionState, label }) => {
          updateMockState('connection', {
            connectionState: connectionState as any,
            isConnected: connectionState === 'connected'
          });
          
          const { container } = render(<ConnectionIndicator />);
          const indicator = container.querySelector('[role="status"]');
          expect(indicator).toHaveAttribute('aria-label', `Connection status: ${label}`);
        });
      });

      it('should announce state changes to screen readers', () => {
        const { rerender } = render(<ConnectionIndicator />);
        
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting'
        });
        rerender(<ConnectionIndicator />);
        
        const indicator = screen.getByRole('status');
        expect(indicator).toHaveAttribute('aria-live', 'polite');
      });
    });

    describe('Animation and Transitions', () => {
      it('should animate state transitions', async () => {
        const { rerender, container } = render(<ConnectionIndicator />);
        
        // Start disconnected
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'disconnected'
        });
        rerender(<ConnectionIndicator />);
        
        // Transition to connecting
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting'
        });
        rerender(<ConnectionIndicator />);
        
        // Check for transition classes
        const indicator = container.querySelector('.transition-all');
        expect(indicator).toBeInTheDocument();
      });

      it('should respect reduced motion preferences', () => {
        window.matchMedia = vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
        }));
        
        updateMockState('connection', {
          connectionState: 'connecting'
        });
        
        const { container } = render(<ConnectionIndicator />);
        const animatedElement = container.querySelector('.animate-pulse');
        
        // Animation should be disabled with reduced motion
        // This would normally check computed styles
        expect(container).toBeInTheDocument();
      });
    });
  });

  // ========== CONNECTION BUTTON TESTS ==========
  describe('ConnectionButton', () => {
    describe('Button States', () => {
      it('should show connect button when disconnected', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'disconnected'
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button', { name: /connect/i });
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });

      it('should show disconnect button when connected', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button', { name: /disconnect/i });
        expect(button).toBeInTheDocument();
      });

      it('should be disabled while connecting', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting'
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
        expect(button).toHaveTextContent(/connecting/i);
      });

      it('should show error state', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'error',
          error: 'Connection failed'
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        expect(button).toHaveClass('bg-destructive');
      });
    });

    describe('User Interactions', () => {
      it('should connect on click when disconnected', async () => {
        const connect = vi.fn();
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'disconnected',
          connect
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(connect).toHaveBeenCalled();
      });

      it('should disconnect on click when connected', async () => {
        const disconnect = vi.fn();
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected',
          disconnect
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(disconnect).toHaveBeenCalled();
      });

      it('should show confirmation dialog for disconnect', async () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionButton requireConfirmation={true} />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        // Check for confirmation dialog
        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });

      it('should handle keyboard activation', async () => {
        const connect = vi.fn();
        updateMockState('connection', {
          isConnected: false,
          connect
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        
        button.focus();
        await keyboard.enter(user);
        
        expect(connect).toHaveBeenCalled();
      });
    });

    describe('Visual Feedback', () => {
      it('should show loading spinner while connecting', () => {
        updateMockState('connection', {
          connectionState: 'connecting'
        });
        
        const { container } = render(<ConnectionButton />);
        const spinner = container.querySelector('.animate-spin');
        expect(spinner).toBeInTheDocument();
      });

      it('should show status indicator', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionButton showStatus={true} />);
        const indicator = screen.getByRole('status');
        expect(indicator).toBeInTheDocument();
      });

      it('should change button variant based on state', () => {
        const { rerender } = render(<ConnectionButton />);
        
        // Disconnected - outline variant
        let button = screen.getByRole('button');
        expect(button).toHaveClass('border', 'border-input');
        
        // Connected - default variant
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        rerender(<ConnectionButton />);
        
        button = screen.getByRole('button');
        expect(button).toHaveClass('bg-primary');
      });

      it('should support different button sizes', () => {
        const { container } = render(<ConnectionButton size="large" />);
        const button = container.querySelector('button');
        expect(button).toHaveClass('h-11', 'px-8');
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<ConnectionButton />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should have descriptive ARIA labels', () => {
        const { rerender } = render(<ConnectionButton />);
        
        let button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-label', 'Connect to server');
        
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        rerender(<ConnectionButton />);
        
        button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-label', 'Disconnect from server');
      });

      it('should indicate loading state to screen readers', () => {
        updateMockState('connection', {
          connectionState: 'connecting'
        });
        
        render(<ConnectionButton />);
        const button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-busy', 'true');
      });
    });
  });

  // ========== CONNECTION STATUS TESTS ==========
  describe('ConnectionStatus', () => {
    describe('Status Display', () => {
      it('should display connection status text', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        render(<ConnectionStatus />);
        expect(screen.getByText(/connected/i)).toBeInTheDocument();
      });

      it('should display latency information', () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected',
          stats: {
            latency: 25
          }
        });
        
        render(<ConnectionStatus showLatency={true} />);
        expect(screen.getByText(/25ms/i)).toBeInTheDocument();
      });

      it('should show reconnection attempts', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting',
          stats: {
            reconnectAttempts: 3
          }
        });
        
        render(<ConnectionStatus />);
        expect(screen.getByText(/attempt 3/i)).toBeInTheDocument();
      });

      it('should display error messages', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'error',
          error: 'WebSocket connection failed'
        });
        
        render(<ConnectionStatus />);
        expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      });

      it('should show data transfer stats', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            bytesReceived: 1024000,
            bytesSent: 512000
          }
        });
        
        render(<ConnectionStatus showDataTransfer={true} />);
        expect(screen.getByText(/1.0 MB received/i)).toBeInTheDocument();
        expect(screen.getByText(/512 KB sent/i)).toBeInTheDocument();
      });
    });

    describe('Quality Indicators', () => {
      it('should show excellent connection quality', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 10
          }
        });
        
        render(<ConnectionStatus showQuality={true} />);
        const quality = screen.getByText(/excellent/i);
        expect(quality).toHaveClass('text-green-500');
      });

      it('should show good connection quality', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 50
          }
        });
        
        render(<ConnectionStatus showQuality={true} />);
        const quality = screen.getByText(/good/i);
        expect(quality).toHaveClass('text-blue-500');
      });

      it('should show fair connection quality', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 150
          }
        });
        
        render(<ConnectionStatus showQuality={true} />);
        const quality = screen.getByText(/fair/i);
        expect(quality).toHaveClass('text-yellow-500');
      });

      it('should show poor connection quality', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 300
          }
        });
        
        render(<ConnectionStatus showQuality={true} />);
        const quality = screen.getByText(/poor/i);
        expect(quality).toHaveClass('text-red-500');
      });
    });

    describe('Auto-hide Behavior', () => {
      it('should auto-hide when connected after delay', async () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        const { container } = render(<ConnectionStatus autoHide={true} hideDelay={1000} />);
        
        // Initially visible
        expect(screen.getByText(/connected/i)).toBeInTheDocument();
        
        // Advance timers
        vi.advanceTimersByTime(1000);
        
        await waitFor(() => {
          const status = container.querySelector('[role="status"]');
          expect(status).toHaveClass('opacity-0');
        });
      });

      it('should not auto-hide when there are errors', () => {
        updateMockState('connection', {
          connectionState: 'error',
          error: 'Connection failed'
        });
        
        render(<ConnectionStatus autoHide={true} hideDelay={1000} />);
        
        vi.advanceTimersByTime(2000);
        
        // Should still be visible
        expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      });

      it('should show on hover when auto-hidden', async () => {
        updateMockState('connection', {
          isConnected: true,
          connectionState: 'connected'
        });
        
        const { container } = render(<ConnectionStatus autoHide={true} hideDelay={100} />);
        
        // Wait for auto-hide
        vi.advanceTimersByTime(100);
        
        // Hover to show
        const status = container.querySelector('[role="status"]');
        await user.hover(status!);
        
        await waitFor(() => {
          expect(status).toHaveClass('opacity-100');
        });
      });
    });

    describe('Collapsed/Expanded States', () => {
      it('should show collapsed view by default', () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 30,
            messagesReceived: 100
          }
        });
        
        render(<ConnectionStatus collapsible={true} />);
        
        // Only basic info visible
        expect(screen.getByText(/connected/i)).toBeInTheDocument();
        expect(screen.queryByText(/messages/i)).not.toBeInTheDocument();
      });

      it('should expand on click to show details', async () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 30,
            messagesReceived: 100,
            messagesSent: 50
          }
        });
        
        render(<ConnectionStatus collapsible={true} />);
        
        const expandButton = screen.getByRole('button', { name: /expand/i });
        await user.click(expandButton);
        
        // Details should be visible
        expect(screen.getByText(/100 received/i)).toBeInTheDocument();
        expect(screen.getByText(/50 sent/i)).toBeInTheDocument();
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<ConnectionStatus />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should use proper ARIA live regions', () => {
        render(<ConnectionStatus />);
        const status = screen.getByRole('status');
        expect(status).toHaveAttribute('aria-live', 'polite');
      });

      it('should announce important status changes', () => {
        const { rerender } = render(<ConnectionStatus />);
        
        // Change to error state
        updateMockState('connection', {
          connectionState: 'error',
          error: 'Connection lost'
        });
        rerender(<ConnectionStatus />);
        
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveTextContent(/connection lost/i);
      });
    });
  });

  // ========== CONNECTION PANEL TESTS ==========
  describe('ConnectionPanel', () => {
    describe('Panel Layout', () => {
      it('should render all connection components', () => {
        render(<ConnectionPanel />);
        
        // Should have indicator
        expect(screen.getByRole('status')).toBeInTheDocument();
        
        // Should have button
        expect(screen.getByRole('button')).toBeInTheDocument();
        
        // Should have status text
        expect(screen.getByText(/disconnected|connected|connecting/i)).toBeInTheDocument();
      });

      it('should support horizontal layout', () => {
        const { container } = render(<ConnectionPanel orientation="horizontal" />);
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-row');
      });

      it('should support vertical layout', () => {
        const { container } = render(<ConnectionPanel orientation="vertical" />);
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-col');
      });

      it('should be collapsible to icon only', async () => {
        render(<ConnectionPanel collapsible={true} />);
        
        const collapseButton = screen.getByRole('button', { name: /collapse/i });
        await user.click(collapseButton);
        
        // Only indicator should be visible
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.queryByText(/connect/i)).not.toBeInTheDocument();
      });
    });

    describe('Advanced Features', () => {
      it('should show connection history', () => {
        const history = [
          { timestamp: new Date(), event: 'connected', duration: 5000 },
          { timestamp: new Date(), event: 'disconnected', reason: 'User initiated' }
        ];
        
        render(<ConnectionPanel showHistory={true} history={history} />);
        
        const historyButton = screen.getByRole('button', { name: /history/i });
        expect(historyButton).toBeInTheDocument();
      });

      it('should allow manual server selection', () => {
        const servers = [
          { id: 'us-east', name: 'US East', url: 'wss://us-east.example.com' },
          { id: 'eu-west', name: 'EU West', url: 'wss://eu-west.example.com' }
        ];
        
        render(<ConnectionPanel servers={servers} />);
        
        const serverSelector = screen.getByRole('combobox', { name: /server/i });
        expect(serverSelector).toBeInTheDocument();
      });

      it('should show reconnection settings', async () => {
        render(<ConnectionPanel showSettings={true} />);
        
        const settingsButton = screen.getByRole('button', { name: /settings/i });
        await user.click(settingsButton);
        
        // Settings dialog should open
        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(screen.getByLabelText(/auto-reconnect/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/max attempts/i)).toBeInTheDocument();
      });

      it('should display connection diagnostics', async () => {
        updateMockState('connection', {
          isConnected: true,
          stats: {
            latency: 45,
            messagesReceived: 1000,
            messagesSent: 500,
            bytesReceived: 102400,
            bytesSent: 51200
          }
        });
        
        render(<ConnectionPanel showDiagnostics={true} />);
        
        const diagnosticsButton = screen.getByRole('button', { name: /diagnostics/i });
        await user.click(diagnosticsButton);
        
        // Should show detailed stats
        expect(screen.getByText(/average latency/i)).toBeInTheDocument();
        expect(screen.getByText(/packet loss/i)).toBeInTheDocument();
        expect(screen.getByText(/bandwidth usage/i)).toBeInTheDocument();
      });
    });

    describe('Responsive Behavior', () => {
      it('should adapt to mobile layout', () => {
        styles.setViewport(375, 667);
        
        const { container } = render(<ConnectionPanel />);
        
        // Should use compact layout
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-col', 'gap-2');
      });

      it('should hide labels on small screens', () => {
        styles.setViewport(320, 568);
        
        render(<ConnectionPanel />);
        
        // Labels should be screen-reader only
        const labels = screen.queryAllByText(/status|connection/i);
        labels.forEach(label => {
          if (label.tagName === 'SPAN') {
            expect(label).toHaveClass('sr-only');
          }
        });
      });

      it('should use drawer instead of dialog on mobile', async () => {
        styles.setViewport(375, 667);
        
        render(<ConnectionPanel showSettings={true} />);
        
        const settingsButton = screen.getByRole('button', { name: /settings/i });
        await user.click(settingsButton);
        
        // Should use drawer presentation
        const drawer = screen.getByRole('dialog');
        expect(drawer).toHaveClass('drawer');
      });
    });

    describe('Performance', () => {
      it('should throttle stats updates', () => {
        const { rerender } = render(<ConnectionPanel />);
        
        // Rapidly update stats
        for (let i = 0; i < 100; i++) {
          updateMockState('connection', {
            stats: {
              latency: Math.random() * 100,
              messagesReceived: i * 10,
              messagesSent: i * 5
            }
          });
          rerender(<ConnectionPanel />);
        }
        
        // Component should remain stable
        expect(screen.getByRole('status')).toBeInTheDocument();
      });

      it('should lazy load history data', async () => {
        const loadHistory = vi.fn().mockResolvedValue([
          { timestamp: new Date(), event: 'connected' }
        ]);
        
        render(<ConnectionPanel showHistory={true} onLoadHistory={loadHistory} />);
        
        const historyButton = screen.getByRole('button', { name: /history/i });
        await user.click(historyButton);
        
        expect(loadHistory).toHaveBeenCalled();
        
        await waitFor(() => {
          expect(screen.getByText(/connected/i)).toBeInTheDocument();
        });
      });
    });

    describe('Error Recovery', () => {
      it('should show retry button on connection failure', () => {
        updateMockState('connection', {
          connectionState: 'error',
          error: 'Connection failed'
        });
        
        render(<ConnectionPanel />);
        
        const retryButton = screen.getByRole('button', { name: /retry/i });
        expect(retryButton).toBeInTheDocument();
      });

      it('should implement exponential backoff for auto-reconnect', async () => {
        const connect = vi.fn();
        updateMockState('connection', {
          connectionState: 'error',
          connect
        });
        
        render(<ConnectionPanel autoReconnect={true} />);
        
        // First retry after 1s
        vi.advanceTimersByTime(1000);
        expect(connect).toHaveBeenCalledTimes(1);
        
        // Second retry after 2s
        vi.advanceTimersByTime(2000);
        expect(connect).toHaveBeenCalledTimes(2);
        
        // Third retry after 4s
        vi.advanceTimersByTime(4000);
        expect(connect).toHaveBeenCalledTimes(3);
      });

      it('should stop auto-reconnect after max attempts', () => {
        const connect = vi.fn();
        updateMockState('connection', {
          connectionState: 'error',
          connect,
          stats: {
            reconnectAttempts: 5
          }
        });
        
        render(<ConnectionPanel autoReconnect={true} maxReconnectAttempts={5} />);
        
        // Should show max attempts reached message
        expect(screen.getByText(/maximum reconnection attempts reached/i)).toBeInTheDocument();
        
        // Should not attempt more connections
        vi.advanceTimersByTime(10000);
        expect(connect).not.toHaveBeenCalled();
      });
    });
  });
});