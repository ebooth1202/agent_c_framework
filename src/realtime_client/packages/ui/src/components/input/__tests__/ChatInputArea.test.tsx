import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInputArea } from '../ChatInputArea';
import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

expect.extend(toHaveNoViolations);

// Mock the hooks from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useChat: vi.fn(() => ({
    sendMessage: vi.fn(),
    isTyping: false,
    canSend: true,
  })),
  useAudio: vi.fn(() => ({
    isRecording: false,
    startRecording: vi.fn(),
    stopRecording: vi.fn(),
    canRecord: true,
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
}));

describe('ChatInputArea', () => {
  const user = userEvent.setup();
  
  const defaultProps = {
    onSendMessage: vi.fn(),
    placeholder: 'Type a message...',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the input area', () => {
      render(<ChatInputArea {...defaultProps} />);
      const input = screen.getByRole('textbox');
      expect(input).toBeInTheDocument();
    });

    it('should display placeholder text', () => {
      render(<ChatInputArea {...defaultProps} />);
      expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    });

    it('should render send button', () => {
      render(<ChatInputArea {...defaultProps} />);
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeInTheDocument();
    });

    it('should render microphone button', () => {
      render(<ChatInputArea {...defaultProps} />);
      const micButton = screen.getByRole('button', { name: /microphone/i });
      expect(micButton).toBeInTheDocument();
    });
  });

  describe('Text Input', () => {
    it('should handle text input', async () => {
      render(<ChatInputArea {...defaultProps} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Hello world');
      
      expect(input).toHaveValue('Hello world');
    });

    it('should send message on Enter key', async () => {
      const onSendMessage = vi.fn();
      render(<ChatInputArea {...defaultProps} onSendMessage={onSendMessage} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Test message');
      await user.keyboard('{Enter}');
      
      expect(onSendMessage).toHaveBeenCalledWith('Test message');
    });

    it('should support multiline with Shift+Enter', async () => {
      render(<ChatInputArea {...defaultProps} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Line 1');
      await user.keyboard('{Shift>}{Enter}{/Shift}');
      await user.type(input, 'Line 2');
      
      expect(input).toHaveValue('Line 1\nLine 2');
    });

    it('should clear input after sending', async () => {
      const onSendMessage = vi.fn();
      render(<ChatInputArea {...defaultProps} onSendMessage={onSendMessage} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Message to send');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(input).toHaveValue('');
    });

    it('should not send empty messages', async () => {
      const onSendMessage = vi.fn();
      render(<ChatInputArea {...defaultProps} onSendMessage={onSendMessage} />);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(onSendMessage).not.toHaveBeenCalled();
    });
  });

  describe('Voice Input', () => {
    it('should start recording on microphone click', async () => {
      const startRecording = vi.fn();
      vi.mocked(realtimeReact.useAudio).mockReturnValue({
        isRecording: false,
        startRecording,
        stopRecording: vi.fn(),
        canRecord: true,
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const micButton = screen.getByRole('button', { name: /microphone/i });
      await user.click(micButton);
      
      expect(startRecording).toHaveBeenCalled();
    });

    it('should stop recording when already recording', async () => {
      const stopRecording = vi.fn();
      vi.mocked(realtimeReact.useAudio).mockReturnValue({
        isRecording: true,
        startRecording: vi.fn(),
        stopRecording,
        canRecord: true,
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const micButton = screen.getByRole('button', { name: /stop recording/i });
      await user.click(micButton);
      
      expect(stopRecording).toHaveBeenCalled();
    });

    it('should show recording indicator when recording', () => {
      vi.mocked(realtimeReact.useAudio).mockReturnValue({
        isRecording: true,
        startRecording: vi.fn(),
        stopRecording: vi.fn(),
        canRecord: true,
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const recordingIndicator = screen.getByRole('status', { name: /recording/i });
      expect(recordingIndicator).toBeInTheDocument();
      expect(recordingIndicator).toHaveClass('animate-pulse');
    });

    it('should disable microphone when cannot record', () => {
      vi.mocked(realtimeReact.useAudio).mockReturnValue({
        isRecording: false,
        startRecording: vi.fn(),
        stopRecording: vi.fn(),
        canRecord: false,
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const micButton = screen.getByRole('button', { name: /microphone/i });
      expect(micButton).toBeDisabled();
    });
  });

  describe('Connection State', () => {
    it('should disable input when disconnected', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'disconnected',
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const input = screen.getByRole('textbox');
      expect(input).toBeDisabled();
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeDisabled();
    });

    it('should show connection status message', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'disconnected',
      });

      render(<ChatInputArea {...defaultProps} />);
      
      expect(screen.getByText(/not connected/i)).toBeInTheDocument();
    });
  });

  describe('Typing Indicator', () => {
    it('should trigger typing indicator on input', async () => {
      const onTyping = vi.fn();
      render(<ChatInputArea {...defaultProps} onTyping={onTyping} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'H');
      
      await waitFor(() => {
        expect(onTyping).toHaveBeenCalledWith(true);
      });
    });

    it('should stop typing indicator after pause', async () => {
      vi.useFakeTimers();
      const onTyping = vi.fn();
      render(<ChatInputArea {...defaultProps} onTyping={onTyping} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Hello');
      
      // Fast-forward time to trigger typing stop
      vi.advanceTimersByTime(1000);
      
      await waitFor(() => {
        expect(onTyping).toHaveBeenCalledWith(false);
      });
      
      vi.useRealTimers();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<ChatInputArea {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels', () => {
      render(<ChatInputArea {...defaultProps} />);
      
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-label', 'Message input');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toHaveAttribute('aria-label');
      
      const micButton = screen.getByRole('button', { name: /microphone/i });
      expect(micButton).toHaveAttribute('aria-label');
    });

    it('should announce recording state to screen readers', () => {
      vi.mocked(realtimeReact.useAudio).mockReturnValue({
        isRecording: true,
        startRecording: vi.fn(),
        stopRecording: vi.fn(),
        canRecord: true,
      });

      render(<ChatInputArea {...defaultProps} />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-live', 'polite');
      expect(status).toHaveTextContent(/recording/i);
    });

    it('should support keyboard shortcuts', async () => {
      const onSendMessage = vi.fn();
      render(<ChatInputArea {...defaultProps} onSendMessage={onSendMessage} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Test message');
      
      // Ctrl+Enter to send
      await user.keyboard('{Control>}{Enter}{/Control}');
      expect(onSendMessage).toHaveBeenCalledWith('Test message');
    });

    it('should manage focus properly', async () => {
      render(<ChatInputArea {...defaultProps} />);
      
      // Tab navigation
      await user.tab();
      const input = screen.getByRole('textbox');
      expect(input).toHaveFocus();
      
      await user.tab();
      const micButton = screen.getByRole('button', { name: /microphone/i });
      expect(micButton).toHaveFocus();
      
      await user.tab();
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toHaveFocus();
    });
  });

  describe('Character Limit', () => {
    it('should enforce character limit', async () => {
      render(<ChatInputArea {...defaultProps} maxLength={10} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'This is a very long message');
      
      expect(input).toHaveValue('This is a ');
    });

    it('should display character count', () => {
      render(<ChatInputArea {...defaultProps} maxLength={100} />);
      
      expect(screen.getByText('0 / 100')).toBeInTheDocument();
    });

    it('should update character count as typing', async () => {
      render(<ChatInputArea {...defaultProps} maxLength={100} />);
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'Hello');
      
      expect(screen.getByText('5 / 100')).toBeInTheDocument();
    });
  });

  describe('File Attachment', () => {
    it('should show attachment button when enabled', () => {
      render(<ChatInputArea {...defaultProps} allowAttachments />);
      
      const attachButton = screen.getByRole('button', { name: /attach/i });
      expect(attachButton).toBeInTheDocument();
    });

    it('should handle file selection', async () => {
      const onAttachment = vi.fn();
      render(
        <ChatInputArea 
          {...defaultProps} 
          allowAttachments 
          onAttachment={onAttachment} 
        />
      );
      
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const input = screen.getByLabelText(/attach file/i);
      
      await user.upload(input, file);
      
      expect(onAttachment).toHaveBeenCalledWith(file);
    });

    it('should display attached files', async () => {
      render(<ChatInputArea {...defaultProps} allowAttachments />);
      
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const input = screen.getByLabelText(/attach file/i);
      
      await user.upload(input, file);
      
      expect(screen.getByText('test.txt')).toBeInTheDocument();
    });
  });
});