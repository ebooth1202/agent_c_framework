/**
 * Tests for AgentCProvider
 * Tests provider initialization, context provision, and cleanup
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, renderHook, act, waitFor, screen } from '@testing-library/react';
import React, { useContext } from 'react';
import { AgentCProvider } from '../AgentCProvider';
import { AgentCContext, useRealtimeClient, useAgentCContext, useRealtimeClientSafe, useAgentCData, useInitializationStatus } from '../AgentCContext';
import { createMockClient } from '../../test/utils/react-test-utils';
import type { RealtimeClient } from '@agentc/realtime-core';

describe('AgentCProvider', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockClient = {
      ...createMockClient(),
      initialize: vi.fn().mockResolvedValue(undefined),
      destroy: vi.fn(),
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      isConnected: vi.fn(() => false),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      }),
      emit: vi.fn((event: string, ...args: any[]) => {
        eventHandlers.get(event)?.forEach(handler => handler(...args));
      })
    };

    // Mock RealtimeClient constructor
    vi.mock('@agentc/realtime-core', async () => {
      const actual = await vi.importActual('@agentc/realtime-core');
      return {
        ...actual,
        RealtimeClient: vi.fn(() => mockClient)
      };
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Provider Initialization', () => {
    it('provides context to children', () => {
      const TestComponent = () => {
        const context = useContext(AgentCContext);
        return <div>{context ? 'Context provided' : 'No context'}</div>;
      };

      const { getByText } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws">
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Context provided')).toBeInTheDocument();
    });

    it('initializes with client when provided', () => {
      const TestComponent = () => {
        const context = useAgentCContext();
        return <div>{context.client ? 'Client available' : 'No client'}</div>;
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Client available')).toBeInTheDocument();
    });

    it('creates client when apiUrl provided', async () => {
      const TestComponent = () => {
        const context = useAgentCContext();
        return (
          <div>
            {context.isInitializing ? 'Initializing' : 'Ready'}
            {context.client ? ' with client' : ''}
          </div>
        );
      };

      const { getByText } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws">
          <TestComponent />
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(getByText('Ready with client')).toBeInTheDocument();
      });
    });

    it('initializes with configuration', async () => {
      const config = {
        reconnection: {
          enabled: true,
          maxAttempts: 10,
          initialDelay: 500
        },
        audio: {
          sampleRate: 48000,
          channels: 2
        }
      };

      render(
        <AgentCProvider 
          apiUrl="wss://test.example.com/ws"
          config={config}
        >
          <div>Test</div>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(mockClient.initialize).toHaveBeenCalled();
      });
    });

    it('handles initialization error', async () => {
      mockClient.initialize.mockRejectedValue(new Error('Init failed'));

      const TestComponent = () => {
        const context = useAgentCContext();
        return <div>{context.error?.message || 'No error'}</div>;
      };

      const { getByText } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws">
          <TestComponent />
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(getByText('Init failed')).toBeInTheDocument();
      });
    });

    it('requires either client or apiUrl', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(
          <AgentCProvider>
            <div>Test</div>
          </AgentCProvider>
        );
      }).toThrow('AgentCProvider requires either a client instance or apiUrl');

      consoleSpy.mockRestore();
    });
  });

  describe('Initialization Events', () => {
    it('tracks initialization events', async () => {
      const TestComponent = () => {
        const context = useAgentCContext();
        return (
          <div>
            <div>Initialized: {context.initialization.isInitialized.toString()}</div>
            <div>Events: {context.initialization.receivedEvents.size}</div>
          </div>
        );
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Initialized: false')).toBeInTheDocument();

      // Simulate initialization events
      act(() => {
        eventHandlers.get('chat_user_data')?.forEach(handler => 
          handler({ user: { id: 'user-1', name: 'Test User' } })
        );
        eventHandlers.get('agent_list')?.forEach(handler => 
          handler({ agents: [] })
        );
        eventHandlers.get('avatar_list')?.forEach(handler => 
          handler({ avatars: [] })
        );
        eventHandlers.get('voice_list')?.forEach(handler => 
          handler({ voices: [] })
        );
        eventHandlers.get('tool_catalog')?.forEach(handler => 
          handler({ toolsets: [] })
        );
        eventHandlers.get('chat_session_changed')?.forEach(handler => 
          handler({ session: { id: 'session-1' } })
        );
      });

      await waitFor(() => {
        expect(getByText('Initialized: true')).toBeInTheDocument();
        expect(getByText('Events: 6')).toBeInTheDocument();
      });
    });

    it('provides initialization data through useAgentCData', async () => {
      const TestComponent = () => {
        const { user, agents, avatars, voices, toolsets, currentSession } = useAgentCData();
        return (
          <div>
            <div>User: {user?.name || 'None'}</div>
            <div>Agents: {agents.length}</div>
            <div>Avatars: {avatars.length}</div>
            <div>Voices: {voices.length}</div>
            <div>Toolsets: {toolsets.length}</div>
            <div>Session: {currentSession?.id || 'None'}</div>
          </div>
        );
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      // Simulate initialization events
      act(() => {
        eventHandlers.get('chat_user_data')?.forEach(handler => 
          handler({ 
            user: { id: 'user-1', name: 'John Doe' }
          })
        );
        eventHandlers.get('agent_list')?.forEach(handler => 
          handler({ 
            agents: [
              { id: 'agent-1', name: 'Assistant' }
            ]
          })
        );
        eventHandlers.get('avatar_list')?.forEach(handler => 
          handler({ 
            avatars: [
              { id: 'avatar-1', name: 'Avatar 1' },
              { id: 'avatar-2', name: 'Avatar 2' }
            ]
          })
        );
        eventHandlers.get('voice_list')?.forEach(handler => 
          handler({ 
            voices: [
              { id: 'voice-1', name: 'Voice 1' },
              { id: 'voice-2', name: 'Voice 2' },
              { id: 'voice-3', name: 'Voice 3' }
            ]
          })
        );
        eventHandlers.get('tool_catalog')?.forEach(handler => 
          handler({ 
            toolsets: [
              { id: 'tools-1', name: 'Basic Tools' }
            ]
          })
        );
        eventHandlers.get('chat_session_changed')?.forEach(handler => 
          handler({ 
            session: { id: 'session-123' }
          })
        );
      });

      await waitFor(() => {
        expect(getByText('User: John Doe')).toBeInTheDocument();
        expect(getByText('Agents: 1')).toBeInTheDocument();
        expect(getByText('Avatars: 2')).toBeInTheDocument();
        expect(getByText('Voices: 3')).toBeInTheDocument();
        expect(getByText('Toolsets: 1')).toBeInTheDocument();
        expect(getByText('Session: session-123')).toBeInTheDocument();
      });
    });

    it('tracks pending initialization events', () => {
      const TestComponent = () => {
        const { pendingEvents } = useInitializationStatus();
        return (
          <div>
            <div>Pending: {pendingEvents.length}</div>
            <div>{pendingEvents.join(', ')}</div>
          </div>
        );
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Pending: 6')).toBeInTheDocument();
      expect(getByText(/chat_user_data/)).toBeInTheDocument();
    });
  });

  describe('Hook Integration', () => {
    it('useRealtimeClient returns client when available', () => {
      const TestComponent = () => {
        const client = useRealtimeClient();
        return <div>{client ? 'Client ready' : 'No client'}</div>;
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Client ready')).toBeInTheDocument();
    });

    it('useRealtimeClient throws when used outside provider', () => {
      const TestComponent = () => {
        try {
          useRealtimeClient();
          return <div>Should not render</div>;
        } catch (error) {
          return <div>{(error as Error).message}</div>;
        }
      };

      const { getByText } = render(<TestComponent />);

      expect(getByText(/must be used within an AgentCProvider/)).toBeInTheDocument();
    });

    it('useRealtimeClient throws when client is initializing', () => {
      // Create a mock that simulates initializing state
      const initializingClient = {
        ...mockClient,
        initialize: vi.fn(() => new Promise(() => {})) // Never resolves
      };

      const TestComponent = () => {
        const context = useAgentCContext();
        if (context.isInitializing) {
          try {
            useRealtimeClient();
            return <div>Should not render</div>;
          } catch (error) {
            return <div>{(error as Error).message}</div>;
          }
        }
        return <div>Ready</div>;
      };

      const { getByText } = render(
        <AgentCProvider apiUrl="wss://test.example.com/ws">
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText(/still initializing/)).toBeInTheDocument();
    });

    it('useRealtimeClientSafe returns null when no client', () => {
      const TestComponent = () => {
        const client = useRealtimeClientSafe();
        return <div>{client ? 'Client available' : 'No client'}</div>;
      };

      const { getByText } = render(<TestComponent />);

      expect(getByText('No client')).toBeInTheDocument();
    });

    it('useRealtimeClientSafe returns client when available', () => {
      const TestComponent = () => {
        const client = useRealtimeClientSafe();
        return <div>{client ? 'Client available' : 'No client'}</div>;
      };

      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('Client available')).toBeInTheDocument();
    });
  });

  describe('Auto Connect', () => {
    it('auto connects when enabled', async () => {
      render(
        <AgentCProvider 
          client={mockClient as RealtimeClient}
          autoConnect={true}
        >
          <div>Test</div>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(mockClient.connect).toHaveBeenCalled();
      });
    });

    it('does not auto connect when disabled', async () => {
      render(
        <AgentCProvider 
          client={mockClient as RealtimeClient}
          autoConnect={false}
        >
          <div>Test</div>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(mockClient.connect).not.toHaveBeenCalled();
      });
    });

    it('auto connects by default', async () => {
      render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <div>Test</div>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(mockClient.connect).toHaveBeenCalled();
      });
    });
  });

  describe('Provider Updates', () => {
    it('handles client prop change', () => {
      const client1 = { ...mockClient, id: 'client1' };
      const client2 = { ...mockClient, id: 'client2' };

      const TestComponent = () => {
        const client = useRealtimeClientSafe();
        return <div>{(client as any)?.id || 'No client'}</div>;
      };

      const { rerender, getByText } = render(
        <AgentCProvider client={client1 as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('client1')).toBeInTheDocument();

      rerender(
        <AgentCProvider client={client2 as RealtimeClient}>
          <TestComponent />
        </AgentCProvider>
      );

      expect(getByText('client2')).toBeInTheDocument();
    });

    it('cleans up old client when switching', async () => {
      const client1 = { ...mockClient, destroy: vi.fn() };
      const client2 = { ...mockClient };

      const { rerender } = render(
        <AgentCProvider client={client1 as RealtimeClient}>
          <div>Test</div>
        </AgentCProvider>
      );

      rerender(
        <AgentCProvider client={client2 as RealtimeClient}>
          <div>Test</div>
        </AgentCProvider>
      );

      await waitFor(() => {
        expect(client1.destroy).toHaveBeenCalled();
      });
    });
  });

  describe('Cleanup', () => {
    it('cleans up client on unmount', async () => {
      const { unmount } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <div>Test</div>
        </AgentCProvider>
      );

      unmount();

      await waitFor(() => {
        expect(mockClient.disconnect).toHaveBeenCalled();
        expect(mockClient.destroy).toHaveBeenCalled();
        expect(mockClient.off).toHaveBeenCalled();
      });
    });

    it('removes event listeners on unmount', () => {
      const { unmount } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <div>Test</div>
        </AgentCProvider>
      );

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('chat_user_data', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('agent_list', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('avatar_list', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('voice_list', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('tool_catalog', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('chat_session_changed', expect.any(Function));
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const TestComponent = () => {
        const client = useRealtimeClientSafe();
        return <div>{client ? 'Client available' : 'No client'}</div>;
      };

      const { getByText } = render(
        <React.StrictMode>
          <AgentCProvider client={mockClient as RealtimeClient}>
            <TestComponent />
          </AgentCProvider>
        </React.StrictMode>
      );

      expect(getByText('Client available')).toBeInTheDocument();
      
      // Should not initialize or connect multiple times
      await waitFor(() => {
        expect(mockClient.initialize).toHaveBeenCalledTimes(0); // Client provided, no init needed
        expect(mockClient.connect).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Error Boundaries', () => {
    it('handles errors in child components gracefully', () => {
      const ThrowingComponent = () => {
        throw new Error('Child component error');
      };

      class ErrorBoundary extends React.Component<
        { children: React.ReactNode },
        { hasError: boolean }
      > {
        state = { hasError: false };
        
        static getDerivedStateFromError() {
          return { hasError: true };
        }
        
        render() {
          if (this.state.hasError) {
            return <div>Error caught</div>;
          }
          return this.props.children;
        }
      }

      const { getByText } = render(
        <ErrorBoundary>
          <AgentCProvider client={mockClient as RealtimeClient}>
            <ThrowingComponent />
          </AgentCProvider>
        </ErrorBoundary>
      );

      expect(getByText('Error caught')).toBeInTheDocument();
    });
  });

  describe('Multiple Providers', () => {
    it('warns about nested providers', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <AgentCProvider client={mockClient as RealtimeClient}>
            <div>Nested</div>
          </AgentCProvider>
        </AgentCProvider>
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Nested AgentCProvider detected')
      );

      consoleWarnSpy.mockRestore();
    });
  });

  describe('Edge Cases', () => {
    it('handles null children', () => {
      const { container } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          {null}
        </AgentCProvider>
      );

      expect(container.firstChild).toBeNull();
    });

    it('handles multiple children', () => {
      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <div>Child 1</div>
          <div>Child 2</div>
          <div>Child 3</div>
        </AgentCProvider>
      );

      expect(getByText('Child 1')).toBeInTheDocument();
      expect(getByText('Child 2')).toBeInTheDocument();
      expect(getByText('Child 3')).toBeInTheDocument();
    });

    it('handles fragment children', () => {
      const { getByText } = render(
        <AgentCProvider client={mockClient as RealtimeClient}>
          <>
            <div>Fragment 1</div>
            <div>Fragment 2</div>
          </>
        </AgentCProvider>
      );

      expect(getByText('Fragment 1')).toBeInTheDocument();
      expect(getByText('Fragment 2')).toBeInTheDocument();
    });
  });
});