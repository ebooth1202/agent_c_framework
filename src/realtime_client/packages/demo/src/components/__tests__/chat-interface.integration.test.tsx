/**
 * Integration Tests for Chat Interface
 * Tests complete chat workflows and SDK integration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ChatInterface } from '../chat/chat-interface';
import { ChatLayout } from '../chat/chat-layout';
import { IntegratedExamples } from '../chat/integrated-examples';
import { AuthProvider } from '@/contexts/auth-context';
import { InitializationWrapper } from '../providers/initialization-wrapper';
import { AgentCProvider } from '@agentc/realtime-react';
import { renderDemo, pages, mockState, storage } from '@/test/utils/demo-test-utils';
import { server, setupAuthenticatedDemo, clearDemoAuth, MockWebSocketConnection } from '@/test/mocks/server';
import { http, HttpResponse, delay } from 'msw';

describe('Chat Interface Integration', () => {
  let mockWebSocket: MockWebSocketConnection;
  let mockClient: any;

  beforeEach(() => {
    // Clear storage and state
    storage.clear();
    clearDemoAuth();
    
    // Setup mock WebSocket
    mockWebSocket = new MockWebSocketConnection();
    
    // Create a more complete mock client
    mockClient = {
      isConnected: vi.fn(() => false),
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      sendText: vi.fn().mockResolvedValue({ messageId: 'msg-123' }),
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
      getConnectionState: vi.fn(() => 'disconnected'),
      getAudioStatus: vi.fn(() => ({
        isRecording: false,
        isStreaming: false,
        hasPermission: false,
        currentLevel: 0
      })),
      getTurnManager: vi.fn(() => ({
        getTurnState: vi.fn(() => ({
          currentTurn: null,
          isUserTurn: false,
          isAssistantTurn: false,
          canSendInput: true
        })),
        on: vi.fn(),
        off: vi.fn()
      }))
    };
  });

  afterEach(() => {
    mockWebSocket.clear();
    vi.clearAllMocks();
  });

  describe('Complete Chat Workflow', () => {
    it('handles new user signup and first chat', async () => {
      const user = userEvent.setup();
      
      // Mock successful authentication
      server.use(
        http.post('/api/auth/login', async () => {
          await delay(100);
          return HttpResponse.json({
            agent_c_token: 'test-jwt-token',
            ui_session_id: 'new-session-123',
            heygen_token: 'heygen-token'
          });
        })
      );

      // Render the complete chat interface with providers
      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <InitializationWrapper>
              <ChatLayout />
            </InitializationWrapper>
          </AgentCProvider>
        </AuthProvider>
      );

      // Initially should show login/connect prompt
      expect(screen.getByText(/connect/i)).toBeInTheDocument();

      // Simulate login
      const connectButton = screen.getByRole('button', { name: /connect/i });
      await user.click(connectButton);

      // Mock connection events
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.getConnectionState.mockReturnValue('connected');
        mockClient.emit('connected', { sessionId: 'new-session-123' });
      });

      // Wait for connection to establish
      await waitFor(() => {
        expect(mockClient.connect).toHaveBeenCalled();
      });

      // Mock initialization events
      act(() => {
        mockClient.emit('chat_user_data', {
          user: {
            id: 'user-new',
            name: 'New User',
            email: 'new@example.com'
          }
        });
        mockClient.emit('agent_list', { agents: [{ id: 'agent-1', name: 'Assistant' }] });
        mockClient.emit('chat_session_changed', { session: { id: 'new-session-123' } });
      });

      // Chat interface should now be ready
      await waitFor(() => {
        expect(screen.getByTestId('chat-input')).toBeInTheDocument();
      });

      // Send first message
      const chatInput = screen.getByTestId('chat-input');
      await user.type(chatInput, 'Hello, this is my first message!');
      
      const sendButton = screen.getByTestId('send-button');
      await user.click(sendButton);

      // Verify message was sent
      expect(mockClient.sendText).toHaveBeenCalledWith('Hello, this is my first message!');

      // Mock receiving assistant response
      act(() => {
        mockClient.emit('message', {
          id: 'msg-response-1',
          role: 'assistant',
          content: 'Welcome! How can I help you today?',
          timestamp: new Date().toISOString()
        });
      });

      // Verify messages appear in chat
      await waitFor(() => {
        expect(screen.getByText('Hello, this is my first message!')).toBeInTheDocument();
        expect(screen.getByText('Welcome! How can I help you today?')).toBeInTheDocument();
      });
    });

    it('handles returning user with existing session', async () => {
      // Setup authenticated state
      const { sessionId } = setupAuthenticatedDemo();
      
      // Mock client to simulate already connected state
      mockClient.isConnected.mockReturnValue(true);
      mockClient.getConnectionState.mockReturnValue('connected');

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <InitializationWrapper>
              <ChatInterface />
            </InitializationWrapper>
          </AgentCProvider>
        </AuthProvider>
      );

      // Mock session restoration
      act(() => {
        mockClient.emit('chat_session_changed', { 
          session: { id: sessionId },
          restored: true
        });
        
        // Load existing messages
        mockClient.emit('message_history', {
          messages: [
            {
              id: 'old-msg-1',
              role: 'user',
              content: 'Previous conversation message',
              timestamp: new Date(Date.now() - 3600000).toISOString()
            },
            {
              id: 'old-msg-2',
              role: 'assistant',
              content: 'Previous response',
              timestamp: new Date(Date.now() - 3500000).toISOString()
            }
          ]
        });
      });

      // Verify previous messages are loaded
      await waitFor(() => {
        expect(screen.getByText('Previous conversation message')).toBeInTheDocument();
        expect(screen.getByText('Previous response')).toBeInTheDocument();
      });

      // Verify session indicator
      expect(screen.getByTestId('session-indicator')).toHaveTextContent(sessionId);
    });

    it('handles voice interaction workflow', async () => {
      const user = userEvent.setup();
      
      // Setup authenticated and connected state
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);
      mockClient.getConnectionState.mockReturnValue('connected');

      // Mock audio permissions granted
      mockClient.getAudioStatus.mockReturnValue({
        isRecording: false,
        isStreaming: false,
        hasPermission: true,
        currentLevel: 0,
        isAudioEnabled: true,
        isInputEnabled: true
      });

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Find and click voice input button
      const voiceButton = screen.getByTestId('voice-input-button');
      expect(voiceButton).toBeInTheDocument();
      
      await user.click(voiceButton);

      // Mock recording started
      act(() => {
        mockClient.getAudioStatus.mockReturnValue({
          isRecording: true,
          isStreaming: true,
          hasPermission: true,
          currentLevel: 0.5,
          isAudioEnabled: true,
          isInputEnabled: true
        });
        mockClient.emit('audio_recording_started', {});
      });

      // Verify recording indicator
      await waitFor(() => {
        expect(screen.getByTestId('recording-indicator')).toBeInTheDocument();
        expect(screen.getByText(/recording/i)).toBeInTheDocument();
      });

      // Simulate audio level changes
      act(() => {
        mockClient.emit('audio_level', { level: 0.7 });
      });

      // Stop recording
      await user.click(voiceButton);

      // Mock turn events for voice interaction
      act(() => {
        mockClient.emit('turn_started', {
          id: 'turn-voice-1',
          type: 'user',
          mode: 'voice'
        });
        
        // Simulate transcription
        mockClient.emit('transcription', {
          text: 'This is a voice message',
          isFinal: true
        });
      });

      // Verify transcribed message appears
      await waitFor(() => {
        expect(screen.getByText('This is a voice message')).toBeInTheDocument();
      });

      // Mock assistant voice response
      act(() => {
        mockClient.emit('turn_started', {
          id: 'turn-voice-2',
          type: 'assistant',
          mode: 'voice'
        });
        
        mockClient.emit('audio_chunk', {
          data: new ArrayBuffer(1024),
          turnId: 'turn-voice-2'
        });
        
        mockClient.emit('turn_ended', {
          id: 'turn-voice-2',
          type: 'assistant'
        });
      });

      // Verify turn indicators
      expect(screen.queryByTestId('assistant-speaking-indicator')).toBeInTheDocument();
    });
  });

  describe('Error Recovery Scenarios', () => {
    it('handles connection failure and retry', async () => {
      const user = userEvent.setup();
      
      // Mock connection failure
      mockClient.connect.mockRejectedValueOnce(new Error('Connection failed'));
      
      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Try to connect
      const connectButton = screen.getByRole('button', { name: /connect/i });
      await user.click(connectButton);

      // Verify error message
      await waitFor(() => {
        expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      });

      // Verify retry button appears
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();

      // Mock successful retry
      mockClient.connect.mockResolvedValueOnce(undefined);
      
      await user.click(retryButton);

      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.getConnectionState.mockReturnValue('connected');
        mockClient.emit('connected', { sessionId: 'retry-session' });
      });

      // Verify connection established
      await waitFor(() => {
        expect(screen.queryByText(/connection failed/i)).not.toBeInTheDocument();
        expect(mockClient.connect).toHaveBeenCalledTimes(2);
      });
    });

    it('handles message send failure with retry', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);
      mockClient.sendText.mockRejectedValueOnce(new Error('Network error'));

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Send a message
      const chatInput = screen.getByTestId('chat-input');
      await user.type(chatInput, 'Test message');
      
      const sendButton = screen.getByTestId('send-button');
      await user.click(sendButton);

      // Verify error state
      await waitFor(() => {
        expect(screen.getByText(/failed to send/i)).toBeInTheDocument();
      });

      // Find failed message and retry
      const failedMessage = screen.getByTestId('failed-message');
      const retryButton = within(failedMessage).getByRole('button', { name: /retry/i });
      
      // Mock successful retry
      mockClient.sendText.mockResolvedValueOnce({ messageId: 'retry-msg' });
      
      await user.click(retryButton);

      // Verify message sent successfully
      await waitFor(() => {
        expect(screen.queryByText(/failed to send/i)).not.toBeInTheDocument();
        expect(mockClient.sendText).toHaveBeenCalledTimes(2);
      });
    });

    it('handles session expiration gracefully', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Simulate session expiration
      act(() => {
        mockClient.emit('error', {
          type: 'session_expired',
          message: 'Your session has expired',
          code: 'SESSION_EXPIRED'
        });
        
        mockClient.isConnected.mockReturnValue(false);
        mockClient.getConnectionState.mockReturnValue('disconnected');
      });

      // Verify session expired message
      await waitFor(() => {
        expect(screen.getByText(/session has expired/i)).toBeInTheDocument();
      });

      // Verify reconnect prompt
      const reconnectButton = screen.getByRole('button', { name: /reconnect/i });
      expect(reconnectButton).toBeInTheDocument();

      // Mock re-authentication
      server.use(
        http.post('/api/auth/refresh', async () => {
          return HttpResponse.json({
            agent_c_token: 'new-jwt-token',
            ui_session_id: 'refreshed-session'
          });
        })
      );

      await user.click(reconnectButton);

      // Mock successful reconnection
      mockClient.connect.mockResolvedValueOnce(undefined);
      
      act(() => {
        mockClient.isConnected.mockReturnValue(true);
        mockClient.getConnectionState.mockReturnValue('connected');
        mockClient.emit('connected', { sessionId: 'refreshed-session' });
      });

      // Verify reconnection
      await waitFor(() => {
        expect(screen.queryByText(/session has expired/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Chat Features Integration', () => {
    it('handles typing indicators correctly', async () => {
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Simulate assistant typing
      act(() => {
        mockClient.emit('typing_start', {
          userId: 'assistant',
          userName: 'AI Assistant'
        });
      });

      // Verify typing indicator appears
      await waitFor(() => {
        expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
        expect(screen.getByText(/AI Assistant is typing/i)).toBeInTheDocument();
      });

      // Simulate typing stop
      act(() => {
        mockClient.emit('typing_stop', {
          userId: 'assistant'
        });
      });

      // Verify typing indicator disappears
      await waitFor(() => {
        expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
      });
    });

    it('handles message editing', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Add a message
      act(() => {
        mockClient.emit('message', {
          id: 'msg-edit-1',
          role: 'user',
          content: 'Original message',
          timestamp: new Date().toISOString()
        });
      });

      await waitFor(() => {
        expect(screen.getByText('Original message')).toBeInTheDocument();
      });

      // Find and click edit button
      const message = screen.getByTestId('chat-message-msg-edit-1');
      const editButton = within(message).getByRole('button', { name: /edit/i });
      
      await user.click(editButton);

      // Edit the message
      const editInput = within(message).getByRole('textbox');
      await user.clear(editInput);
      await user.type(editInput, 'Edited message');
      
      const saveButton = within(message).getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Verify message updated
      await waitFor(() => {
        expect(screen.getByText('Edited message')).toBeInTheDocument();
        expect(screen.queryByText('Original message')).not.toBeInTheDocument();
      });

      // Verify edit indicator
      expect(within(message).getByText(/edited/i)).toBeInTheDocument();
    });

    it('handles message deletion', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <ChatInterface />
          </AgentCProvider>
        </AuthProvider>
      );

      // Add messages
      act(() => {
        mockClient.emit('message', {
          id: 'msg-del-1',
          role: 'user',
          content: 'Message to delete',
          timestamp: new Date().toISOString()
        });
        mockClient.emit('message', {
          id: 'msg-del-2',
          role: 'assistant',
          content: 'Response to keep',
          timestamp: new Date().toISOString()
        });
      });

      await waitFor(() => {
        expect(screen.getByText('Message to delete')).toBeInTheDocument();
        expect(screen.getByText('Response to keep')).toBeInTheDocument();
      });

      // Delete first message
      const message = screen.getByTestId('chat-message-msg-del-1');
      const deleteButton = within(message).getByRole('button', { name: /delete/i });
      
      await user.click(deleteButton);

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await user.click(confirmButton);

      // Verify message deleted
      await waitFor(() => {
        expect(screen.queryByText('Message to delete')).not.toBeInTheDocument();
        expect(screen.getByText('Response to keep')).toBeInTheDocument();
      });
    });
  });

  describe('Integrated Examples', () => {
    it('loads and executes example prompts', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <IntegratedExamples />
          </AgentCProvider>
        </AuthProvider>
      );

      // Find examples section
      const examplesSection = screen.getByTestId('examples-section');
      expect(examplesSection).toBeInTheDocument();

      // Click on an example
      const exampleButton = within(examplesSection).getByText(/Tell me a joke/i);
      await user.click(exampleButton);

      // Verify example prompt is sent
      await waitFor(() => {
        expect(mockClient.sendText).toHaveBeenCalledWith(
          expect.stringContaining('Tell me a joke')
        );
      });

      // Mock response
      act(() => {
        mockClient.emit('message', {
          id: 'msg-joke',
          role: 'assistant',
          content: 'Why did the developer go broke? Because he used up all his cache!',
          timestamp: new Date().toISOString()
        });
      });

      // Verify response appears
      await waitFor(() => {
        expect(screen.getByText(/cache/i)).toBeInTheDocument();
      });
    });

    it('handles code example execution', async () => {
      const user = userEvent.setup();
      
      setupAuthenticatedDemo();
      mockClient.isConnected.mockReturnValue(true);

      const { container } = render(
        <AuthProvider>
          <AgentCProvider apiUrl="ws://localhost:8080/test" client={mockClient}>
            <IntegratedExamples />
          </AgentCProvider>
        </AuthProvider>
      );

      // Find code example
      const codeExample = screen.getByTestId('code-example-python');
      const runButton = within(codeExample).getByRole('button', { name: /run/i });
      
      await user.click(runButton);

      // Verify code is sent with proper formatting
      expect(mockClient.sendText).toHaveBeenCalledWith(
        expect.stringContaining('```python')
      );

      // Mock code execution response
      act(() => {
        mockClient.emit('message', {
          id: 'msg-code',
          role: 'assistant',
          content: '```output\nHello, World!\n```',
          timestamp: new Date().toISOString(),
          metadata: { type: 'code_output' }
        });
      });

      // Verify output appears with proper formatting
      await waitFor(() => {
        const output = screen.getByTestId('code-output');
        expect(output).toBeInTheDocument();
        expect(within(output).getByText('Hello, World!')).toBeInTheDocument();
      });
    });
  });
});