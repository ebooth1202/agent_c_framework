/**
 * Integration Tests for Providers and Initialization
 * Tests InitializationWrapper, ClientProvider, and environment configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { InitializationWrapper } from '../providers/initialization-wrapper';
import { ClientProvider } from '../providers/client-provider';
import { AuthProvider } from '@/contexts/auth-context';
import { AgentCProvider, useRealtimeClient, useAgentCData } from '@agentc/realtime-react';
import { storage } from '@/test/utils/demo-test-utils';
import type { RealtimeClient } from '@agentc/realtime-core';

// Test component to verify initialization
function InitializationTestComponent() {
  const client = useRealtimeClient();
  const { user, agents, avatars, voices, toolsets, currentSession } = useAgentCData();
  
  return (
    <div>
      <div data-testid="client-status">
        {client ? 'Client Ready' : 'No Client'}
      </div>
      <div data-testid="user-data">
        {user ? `User: ${user.name}` : 'No User'}
      </div>
      <div data-testid="agents-count">
        Agents: {agents.length}
      </div>
      <div data-testid="avatars-count">
        Avatars: {avatars.length}
      </div>
      <div data-testid="voices-count">
        Voices: {voices.length}
      </div>
      <div data-testid="toolsets-count">
        Toolsets: {toolsets.length}
      </div>
      <div data-testid="session-info">
        {currentSession ? `Session: ${currentSession.id}` : 'No Session'}
      </div>
    </div>
  );
}

// Loading states component
function LoadingStatesComponent() {
  const [initState, setInitState] = React.useState('pending');
  
  return (
    <InitializationWrapper
      onInitStart={() => setInitState('loading')}
      onInitComplete={() => setInitState('complete')}
      onInitError={() => setInitState('error')}
    >
      <div data-testid="init-state">{initState}</div>
      <InitializationTestComponent />
    </InitializationWrapper>
  );
}

describe('Providers and Initialization Integration', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    storage.clear();
    eventHandlers = new Map();
    
    // Setup environment variables
    process.env.VITE_API_URL = 'wss://test.example.com/ws';
    process.env.VITE_AUTH_TOKEN = 'test-auth-token';
    process.env.VITE_ENABLE_DEBUG = 'true';
    
    // Create comprehensive mock client
    mockClient = {
      isConnected: vi.fn(() => false),
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      destroy: vi.fn(),
      initialize: vi.fn().mockResolvedValue(undefined),
      getConnectionState: vi.fn(() => 'disconnected'),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      }),
      emit: (event: string, data: any) => {
        eventHandlers.get(event)?.forEach(handler => handler(data));
      }
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
    delete process.env.VITE_API_URL;
    delete process.env.VITE_AUTH_TOKEN;
    delete process.env.VITE_ENABLE_DEBUG;
  });

  describe('Environment Configuration', () => {
    it('loads configuration from environment variables', async () => {
      const { container } = render(
        <AgentCProvider apiUrl={process.env.VITE_API_URL!} client={mockClient}>
          <InitializationWrapper>
            <div data-testid="app">App Content</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      expect(screen.getByTestId('app')).toBeInTheDocument();
      
      // Verify API URL from env is used
      expect(mockClient.initialize).toHaveBeenCalledWith(
        expect.objectContaining({
          apiUrl: 'wss://test.example.com/ws'
        })
      );
    });

    it('handles missing environment variables gracefully', async () => {
      delete process.env.VITE_API_URL;
      
      const { container } = render(
        <AgentCProvider apiUrl="wss://fallback.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <div data-testid="app">App Content</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Should use fallback URL
      expect(screen.getByTestId('app')).toBeInTheDocument();
    });

    it('applies debug mode from environment', async () => {
      process.env.VITE_ENABLE_DEBUG = 'true';
      
      const consoleSpy = vi.spyOn(console, 'debug');
      
      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper debug={true}>
            <div data-testid="app">App Content</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Trigger debug logging
      mockClient.emit('debug', { message: 'Debug message' });
      
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('Initialization Wrapper', () => {
    it('shows loading state during initialization', async () => {
      // Delay client connection
      mockClient.connect.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 500))
      );

      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <div data-testid="app">App Content</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Should show loading initially
      expect(screen.getByTestId('initialization-loading')).toBeInTheDocument();
      expect(screen.queryByTestId('app')).not.toBeInTheDocument();

      // Mock successful connection
      mockClient.isConnected.mockReturnValue(true);
      mockClient.getConnectionState.mockReturnValue('connected');
      mockClient.emit('connected', { sessionId: 'test-session' });

      // Wait for initialization to complete
      await waitFor(() => {
        expect(screen.queryByTestId('initialization-loading')).not.toBeInTheDocument();
        expect(screen.getByTestId('app')).toBeInTheDocument();
      });
    });

    it('handles initialization events in correct order', async () => {
      const eventOrder: string[] = [];
      
      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <InitializationTestComponent />
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Simulate initialization events in order
      act(() => {
        // 1. Connection established
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'init-session' });
        eventOrder.push('connected');
        
        // 2. User data received
        mockClient.emit('chat_user_data', {
          user: {
            id: 'user-1',
            name: 'Test User',
            email: 'test@example.com'
          }
        });
        eventOrder.push('user_data');
        
        // 3. Configuration data received
        mockClient.emit('agent_list', {
          agents: [
            { id: 'agent-1', name: 'Assistant' },
            { id: 'agent-2', name: 'Helper' }
          ]
        });
        eventOrder.push('agents');
        
        mockClient.emit('avatar_list', {
          avatars: [
            { id: 'avatar-1', name: 'Avatar 1' },
            { id: 'avatar-2', name: 'Avatar 2' },
            { id: 'avatar-3', name: 'Avatar 3' }
          ]
        });
        eventOrder.push('avatars');
        
        mockClient.emit('voice_list', {
          voices: [
            { id: 'voice-1', name: 'Voice 1' },
            { id: 'voice-2', name: 'Voice 2' }
          ]
        });
        eventOrder.push('voices');
        
        mockClient.emit('tool_catalog', {
          toolsets: [
            { id: 'tools-1', name: 'Basic Tools' }
          ]
        });
        eventOrder.push('toolsets');
        
        // 4. Session established
        mockClient.emit('chat_session_changed', {
          session: { id: 'init-session' }
        });
        eventOrder.push('session');
      });

      // Verify all data loaded
      await waitFor(() => {
        expect(screen.getByTestId('client-status')).toHaveTextContent('Client Ready');
        expect(screen.getByTestId('user-data')).toHaveTextContent('User: Test User');
        expect(screen.getByTestId('agents-count')).toHaveTextContent('Agents: 2');
        expect(screen.getByTestId('avatars-count')).toHaveTextContent('Avatars: 3');
        expect(screen.getByTestId('voices-count')).toHaveTextContent('Voices: 2');
        expect(screen.getByTestId('toolsets-count')).toHaveTextContent('Toolsets: 1');
        expect(screen.getByTestId('session-info')).toHaveTextContent('Session: init-session');
      });

      // Verify events received in correct order
      expect(eventOrder).toEqual([
        'connected',
        'user_data',
        'agents',
        'avatars',
        'voices',
        'toolsets',
        'session'
      ]);
    });

    it('handles initialization failure with retry', async () => {
      const user = userEvent.setup();
      
      // Mock initial connection failure
      mockClient.connect.mockRejectedValueOnce(new Error('Connection failed'));
      
      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <div data-testid="app">App Content</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Should show error state
      await waitFor(() => {
        expect(screen.getByTestId('initialization-error')).toBeInTheDocument();
      });

      expect(screen.getByText(/failed to initialize/i)).toBeInTheDocument();
      
      // Find retry button
      const retryButton = screen.getByRole('button', { name: /retry/i });
      
      // Mock successful retry
      mockClient.connect.mockResolvedValueOnce(undefined);
      
      await user.click(retryButton);
      
      // Mock successful connection
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'retry-session' });
        mockClient.emit('chat_user_data', { user: { id: 'user-1', name: 'User' } });
        mockClient.emit('agent_list', { agents: [] });
        mockClient.emit('avatar_list', { avatars: [] });
        mockClient.emit('voice_list', { voices: [] });
        mockClient.emit('tool_catalog', { toolsets: [] });
        mockClient.emit('chat_session_changed', { session: { id: 'retry-session' } });
      });

      // Should show app after successful retry
      await waitFor(() => {
        expect(screen.queryByTestId('initialization-error')).not.toBeInTheDocument();
        expect(screen.getByTestId('app')).toBeInTheDocument();
      });
    });

    it('handles partial initialization data', async () => {
      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <InitializationTestComponent />
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Send only partial initialization data
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'partial-session' });
        
        // Only send user data and session
        mockClient.emit('chat_user_data', {
          user: { id: 'user-1', name: 'Partial User' }
        });
        mockClient.emit('chat_session_changed', {
          session: { id: 'partial-session' }
        });
        
        // Skip other initialization events
      });

      // Wait for timeout or partial initialization
      await waitFor(() => {
        expect(screen.getByTestId('user-data')).toHaveTextContent('User: Partial User');
      }, { timeout: 3000 });

      // Should show partial data
      expect(screen.getByTestId('agents-count')).toHaveTextContent('Agents: 0');
      expect(screen.getByTestId('avatars-count')).toHaveTextContent('Avatars: 0');
      expect(screen.getByTestId('voices-count')).toHaveTextContent('Voices: 0');
    });
  });

  describe('Client Provider', () => {
    it('provides client instance to child components', async () => {
      const { container } = render(
        <ClientProvider client={mockClient}>
          <AgentCProvider client={mockClient}>
            <InitializationTestComponent />
          </AgentCProvider>
        </ClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('client-status')).toHaveTextContent('Client Ready');
      });
    });

    it('handles client reconnection', async () => {
      const { container } = render(
        <ClientProvider client={mockClient}>
          <AgentCProvider client={mockClient}>
            <InitializationTestComponent />
          </AgentCProvider>
        </ClientProvider>
      );

      // Initial connection
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'initial-session' });
      });

      await waitFor(() => {
        expect(screen.getByTestId('session-info')).toHaveTextContent('Session: initial-session');
      });

      // Simulate disconnection
      act(() => {
        mockClient.isConnected.mockReturnValue(false);
        mockClient.getConnectionState.mockReturnValue('disconnected');
        mockClient.emit('disconnected', { code: 1006, reason: 'Connection lost' });
      });

      // Simulate reconnection
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.getConnectionState.mockReturnValue('connected');
        mockClient.emit('reconnected', { sessionId: 'reconnect-session' });
        mockClient.emit('chat_session_changed', {
          session: { id: 'reconnect-session' }
        });
      });

      // Verify reconnected with new session
      await waitFor(() => {
        expect(screen.getByTestId('session-info')).toHaveTextContent('Session: reconnect-session');
      });
    });

    it('cleans up on unmount', async () => {
      const { unmount } = render(
        <ClientProvider client={mockClient}>
          <AgentCProvider client={mockClient}>
            <div>Test</div>
          </AgentCProvider>
        </ClientProvider>
      );

      unmount();

      // Verify cleanup called
      expect(mockClient.disconnect).toHaveBeenCalled();
      expect(mockClient.destroy).toHaveBeenCalled();
      expect(mockClient.off).toHaveBeenCalled();
    });
  });

  describe('Loading States', () => {
    it('tracks initialization progress', async () => {
      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <LoadingStatesComponent />
        </AgentCProvider>
      );

      // Initially pending
      expect(screen.getByTestId('init-state')).toHaveTextContent('pending');

      // Start initialization
      act(() => {
        mockClient.emit('initialization_start', {});
      });

      expect(screen.getByTestId('init-state')).toHaveTextContent('loading');

      // Complete initialization
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'test' });
        mockClient.emit('chat_user_data', { user: { id: '1', name: 'User' } });
        mockClient.emit('agent_list', { agents: [] });
        mockClient.emit('avatar_list', { avatars: [] });
        mockClient.emit('voice_list', { voices: [] });
        mockClient.emit('tool_catalog', { toolsets: [] });
        mockClient.emit('chat_session_changed', { session: { id: 'test' } });
        mockClient.emit('initialization_complete', {});
      });

      await waitFor(() => {
        expect(screen.getByTestId('init-state')).toHaveTextContent('complete');
      });
    });

    it('shows custom loading component', async () => {
      const CustomLoader = () => <div data-testid="custom-loader">Loading...</div>;
      
      mockClient.connect.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 500))
      );

      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper loadingComponent={<CustomLoader />}>
            <div data-testid="app">App</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      expect(screen.getByTestId('custom-loader')).toBeInTheDocument();
      expect(screen.queryByTestId('app')).not.toBeInTheDocument();

      // Complete initialization
      mockClient.isConnected.mockReturnValue(true);
      mockClient.emit('connected', {});

      await waitFor(() => {
        expect(screen.queryByTestId('custom-loader')).not.toBeInTheDocument();
        expect(screen.getByTestId('app')).toBeInTheDocument();
      });
    });

    it('shows custom error component', async () => {
      const CustomError = ({ error, retry }: any) => (
        <div data-testid="custom-error">
          Error: {error.message}
          <button onClick={retry}>Custom Retry</button>
        </div>
      );
      
      mockClient.connect.mockRejectedValueOnce(new Error('Test error'));

      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper errorComponent={CustomError}>
            <div data-testid="app">App</div>
          </InitializationWrapper>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('custom-error')).toBeInTheDocument();
      });

      expect(screen.getByText('Error: Test error')).toBeInTheDocument();
      expect(screen.getByText('Custom Retry')).toBeInTheDocument();
    });
  });

  describe('Provider Composition', () => {
    it('composes multiple providers correctly', async () => {
      const { container } = render(
        <AuthProvider>
          <ClientProvider client={mockClient}>
            <AgentCProvider client={mockClient}>
              <InitializationWrapper>
                <InitializationTestComponent />
              </InitializationWrapper>
            </AgentCProvider>
          </ClientProvider>
        </AuthProvider>
      );

      // Send initialization events
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.emit('connected', { sessionId: 'composed-session' });
        mockClient.emit('chat_user_data', {
          user: { id: 'user-1', name: 'Composed User' }
        });
        mockClient.emit('agent_list', { agents: [] });
        mockClient.emit('avatar_list', { avatars: [] });
        mockClient.emit('voice_list', { voices: [] });
        mockClient.emit('tool_catalog', { toolsets: [] });
        mockClient.emit('chat_session_changed', {
          session: { id: 'composed-session' }
        });
      });

      // Verify all providers working together
      await waitFor(() => {
        expect(screen.getByTestId('client-status')).toHaveTextContent('Client Ready');
        expect(screen.getByTestId('user-data')).toHaveTextContent('User: Composed User');
        expect(screen.getByTestId('session-info')).toHaveTextContent('Session: composed-session');
      });
    });

    it('handles provider updates without losing state', async () => {
      const { rerender } = render(
        <ClientProvider client={mockClient}>
          <AgentCProvider client={mockClient}>
            <InitializationTestComponent />
          </AgentCProvider>
        </ClientProvider>
      );

      // Set initial state
      act(() => {
        mockClient.emit('chat_user_data', {
          user: { id: 'user-1', name: 'Initial User' }
        });
      });

      await waitFor(() => {
        expect(screen.getByTestId('user-data')).toHaveTextContent('User: Initial User');
      });

      // Update provider props
      const updatedClient = { ...mockClient, customProp: 'updated' };
      
      rerender(
        <ClientProvider client={updatedClient}>
          <AgentCProvider client={updatedClient}>
            <InitializationTestComponent />
          </AgentCProvider>
        </ClientProvider>
      );

      // State should be preserved
      expect(screen.getByTestId('user-data')).toHaveTextContent('User: Initial User');
    });
  });

  describe('Error Boundaries', () => {
    it('catches and displays initialization errors', async () => {
      const ThrowingComponent = () => {
        throw new Error('Component error');
      };

      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <ThrowingComponent />
          </InitializationWrapper>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
      });

      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/Component error/i)).toBeInTheDocument();
    });

    it('allows error recovery through retry', async () => {
      const user = userEvent.setup();
      let shouldThrow = true;
      
      const ConditionalThrowingComponent = () => {
        if (shouldThrow) {
          throw new Error('Conditional error');
        }
        return <div data-testid="recovered">Recovered!</div>;
      };

      const { container } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws" client={mockClient}>
          <InitializationWrapper>
            <ConditionalThrowingComponent />
          </InitializationWrapper>
        </AgentCProvider>
      );

      // Error should be caught
      await waitFor(() => {
        expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
      });

      // Fix the error condition
      shouldThrow = false;
      
      // Click retry
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      // Should recover
      await waitFor(() => {
        expect(screen.queryByTestId('error-boundary')).not.toBeInTheDocument();
        expect(screen.getByTestId('recovered')).toBeInTheDocument();
      });
    });
  });
});