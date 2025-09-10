/**
 * Integration Tests for Input Area Components
 * Tests text input, voice input, and mode switching
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { InputArea } from '../input/input-area';
import { VoiceInput } from '../input/voice-input';
import { TextInput } from '../input/text-input';
import { AgentCProvider } from '@agentc/realtime-react';
import { AuthProvider } from '@/contexts/auth-context';
import { storage } from '@/test/utils/demo-test-utils';

describe('Input Area Integration', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;
  let mockMediaStream: MediaStream;

  beforeEach(() => {
    storage.clear();
    eventHandlers = new Map();
    
    // Mock MediaStream for audio input
    mockMediaStream = {
      getTracks: vi.fn(() => [{
        kind: 'audio',
        enabled: true,
        stop: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      }]),
      getAudioTracks: vi.fn(() => [{
        kind: 'audio',
        enabled: true,
        stop: vi.fn()
      }])
    } as any;
    
    // Mock getUserMedia
    navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue(mockMediaStream);
    
    // Setup mock client
    mockClient = {
      isConnected: vi.fn(() => true),
      sendText: vi.fn().mockResolvedValue({ messageId: 'msg-123' }),
      sendBinaryFrame: vi.fn(),
      getAudioStatus: vi.fn(() => ({
        isRecording: false,
        isStreaming: false,
        hasPermission: false,
        currentLevel: 0,
        isAudioEnabled: true,
        isInputEnabled: true
      })),
      startAudioRecording: vi.fn().mockResolvedValue(undefined),
      stopAudioRecording: vi.fn(),
      startAudioStreaming: vi.fn(),
      stopAudioStreaming: vi.fn(),
      getTurnManager: vi.fn(() => ({
        getTurnState: vi.fn(() => ({
          currentTurn: null,
          isUserTurn: false,
          isAssistantTurn: false,
          canSendInput: true
        })),
        on: vi.fn(),
        off: vi.fn()
      })),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn(),
      emit: (event: string, data: any) => {
        eventHandlers.get(event)?.forEach(handler => handler(data));
      }
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Text Input', () => {
    it('handles basic text message sending', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      const sendButton = screen.getByTestId('send-button');
      
      // Type message
      await user.type(input, 'Hello, world!');
      expect(input).toHaveValue('Hello, world!');
      
      // Send message
      await user.click(sendButton);
      
      // Verify callback called
      expect(onSend).toHaveBeenCalledWith('Hello, world!');
      
      // Input should be cleared
      expect(input).toHaveValue('');
    });

    it('handles multi-line text input', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} multiline />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Type multi-line message
      await user.type(input, 'Line 1{Shift>}{Enter}{/Shift}Line 2{Shift>}{Enter}{/Shift}Line 3');
      
      // Verify multi-line content
      expect(input).toHaveValue('Line 1\nLine 2\nLine 3');
      
      // Send with Ctrl+Enter
      await user.keyboard('{Control>}{Enter}{/Control}');
      
      expect(onSend).toHaveBeenCalledWith('Line 1\nLine 2\nLine 3');
    });

    it('handles markdown formatting', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} enableMarkdown />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Type markdown content
      await user.type(input, '**bold** *italic* `code`');
      
      // Should show markdown preview
      const preview = screen.getByTestId('markdown-preview');
      expect(preview).toBeInTheDocument();
      
      // Send message
      await user.keyboard('{Enter}');
      
      expect(onSend).toHaveBeenCalledWith('**bold** *italic* `code`');
    });

    it('handles emoji picker', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} enableEmoji />
        </AgentCProvider>
      );

      // Open emoji picker
      const emojiButton = screen.getByTestId('emoji-button');
      await user.click(emojiButton);
      
      // Select an emoji
      const emojiPicker = screen.getByTestId('emoji-picker');
      const smileEmoji = within(emojiPicker).getByText('😊');
      await user.click(smileEmoji);
      
      // Emoji should be added to input
      const input = screen.getByTestId('text-input');
      expect(input).toHaveValue('😊');
    });

    it('handles character limit', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} maxLength={10} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Try to type more than limit
      await user.type(input, 'This is a very long message');
      
      // Should be truncated to limit
      expect(input).toHaveValue('This is a ');
      
      // Character counter should show limit
      const counter = screen.getByTestId('char-counter');
      expect(counter).toHaveTextContent('10/10');
    });

    it('handles paste events', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Simulate paste event
      const pasteText = 'Pasted content with\nmultiple lines';
      const pasteEvent = new ClipboardEvent('paste', {
        clipboardData: new DataTransfer()
      });
      pasteEvent.clipboardData?.setData('text/plain', pasteText);
      
      fireEvent.paste(input, pasteEvent);
      
      await waitFor(() => {
        expect(input).toHaveValue(pasteText);
      });
    });

    it('prevents sending empty messages', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      const sendButton = screen.getByTestId('send-button');
      
      // Try to send empty message
      await user.click(sendButton);
      
      expect(onSend).not.toHaveBeenCalled();
      
      // Try with only whitespace
      await user.type(input, '   ');
      await user.click(sendButton);
      
      expect(onSend).not.toHaveBeenCalled();
    });

    it('handles typing indicator', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={vi.fn()} sendTypingIndicator />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Start typing
      await user.type(input, 'H');
      
      // Should send typing start event
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'typing_start'
      });
      
      // Wait for typing timeout
      await waitFor(() => {
        expect(mockClient.sendEvent).toHaveBeenCalledWith({
          type: 'typing_stop'
        });
      }, { timeout: 3000 });
    });
  });

  describe('Voice Input', () => {
    it('handles voice recording start and stop', async () => {
      const user = userEvent.setup();
      const onAudioData = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={onAudioData} />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Start recording
      await user.click(voiceButton);
      
      expect(mockClient.startAudioRecording).toHaveBeenCalled();
      
      // Update mock status
      mockClient.getAudioStatus.mockReturnValue({
        isRecording: true,
        isStreaming: true,
        hasPermission: true,
        currentLevel: 0.5,
        isAudioEnabled: true,
        isInputEnabled: true
      });
      
      // Trigger status update
      mockClient.emit('audio_recording_started', {});
      
      // Should show recording indicator
      await waitFor(() => {
        expect(screen.getByTestId('recording-indicator')).toBeInTheDocument();
      });
      
      // Stop recording
      await user.click(voiceButton);
      
      expect(mockClient.stopAudioRecording).toHaveBeenCalled();
    });

    it('handles microphone permission request', async () => {
      const user = userEvent.setup();
      
      // Mock permission denied initially
      navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValueOnce(
        new DOMException('Permission denied', 'NotAllowedError')
      );
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Try to start recording
      await user.click(voiceButton);
      
      // Should show permission error
      await waitFor(() => {
        expect(screen.getByTestId('permission-error')).toBeInTheDocument();
      });
      
      expect(screen.getByText(/microphone permission/i)).toBeInTheDocument();
      
      // Grant permission button
      const grantButton = screen.getByRole('button', { name: /grant permission/i });
      
      // Mock permission granted
      navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue(mockMediaStream);
      
      await user.click(grantButton);
      
      // Error should clear
      await waitFor(() => {
        expect(screen.queryByTestId('permission-error')).not.toBeInTheDocument();
      });
    });

    it('handles audio level visualization', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} showLevelMeter />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Start recording
      await user.click(voiceButton);
      
      mockClient.getAudioStatus.mockReturnValue({
        isRecording: true,
        isStreaming: true,
        hasPermission: true,
        currentLevel: 0,
        isAudioEnabled: true,
        isInputEnabled: true
      });
      
      mockClient.emit('audio_recording_started', {});
      
      // Should show level meter
      await waitFor(() => {
        expect(screen.getByTestId('audio-level-meter')).toBeInTheDocument();
      });
      
      // Simulate audio level changes
      act(() => {
        mockClient.getAudioStatus.mockReturnValue({
          isRecording: true,
          isStreaming: true,
          hasPermission: true,
          currentLevel: 0.7,
          isAudioEnabled: true,
          isInputEnabled: true
        });
        mockClient.emit('audio_level', { level: 0.7 });
      });
      
      // Level meter should update
      const levelMeter = screen.getByTestId('audio-level-meter');
      await waitFor(() => {
        expect(levelMeter).toHaveStyle({ width: '70%' });
      });
    });

    it('handles push-to-talk mode', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} mode="push-to-talk" />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Mouse down to start
      fireEvent.mouseDown(voiceButton);
      
      expect(mockClient.startAudioRecording).toHaveBeenCalled();
      
      // Mouse up to stop
      fireEvent.mouseUp(voiceButton);
      
      expect(mockClient.stopAudioRecording).toHaveBeenCalled();
      
      // Test keyboard push-to-talk
      fireEvent.keyDown(document, { key: ' ', code: 'Space' });
      
      expect(mockClient.startAudioRecording).toHaveBeenCalledTimes(2);
      
      fireEvent.keyUp(document, { key: ' ', code: 'Space' });
      
      expect(mockClient.stopAudioRecording).toHaveBeenCalledTimes(2);
    });

    it('handles voice activity detection', async () => {
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} mode="voice-activity" />
        </AgentCProvider>
      );

      // Should auto-start when voice detected
      act(() => {
        mockClient.emit('voice_activity_start', {});
      });
      
      expect(mockClient.startAudioRecording).toHaveBeenCalled();
      
      // Should auto-stop when voice stops
      act(() => {
        mockClient.emit('voice_activity_end', {});
      });
      
      expect(mockClient.stopAudioRecording).toHaveBeenCalled();
    });

    it('handles recording time limit', async () => {
      vi.useFakeTimers();
      const user = userEvent.setup({ delay: null });
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} maxDuration={5000} />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Start recording
      await user.click(voiceButton);
      
      mockClient.getAudioStatus.mockReturnValue({
        isRecording: true,
        isStreaming: true,
        hasPermission: true,
        currentLevel: 0.5,
        isAudioEnabled: true,
        isInputEnabled: true
      });
      
      mockClient.emit('audio_recording_started', {});
      
      // Should show timer
      await waitFor(() => {
        expect(screen.getByTestId('recording-timer')).toBeInTheDocument();
      });
      
      // Advance time to limit
      act(() => {
        vi.advanceTimersByTime(5000);
      });
      
      // Should auto-stop at limit
      await waitFor(() => {
        expect(mockClient.stopAudioRecording).toHaveBeenCalled();
      });
      
      vi.useRealTimers();
    });
  });

  describe('Input Mode Switching', () => {
    it('switches between text and voice modes', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <InputArea />
        </AgentCProvider>
      );

      // Should start in text mode
      expect(screen.getByTestId('text-input')).toBeInTheDocument();
      expect(screen.queryByTestId('voice-button')).not.toBeInTheDocument();
      
      // Switch to voice mode
      const modeToggle = screen.getByTestId('input-mode-toggle');
      await user.click(modeToggle);
      
      // Should show voice input
      expect(screen.queryByTestId('text-input')).not.toBeInTheDocument();
      expect(screen.getByTestId('voice-button')).toBeInTheDocument();
      
      // Switch back to text
      await user.click(modeToggle);
      
      expect(screen.getByTestId('text-input')).toBeInTheDocument();
      expect(screen.queryByTestId('voice-button')).not.toBeInTheDocument();
    });

    it('preserves text when switching modes', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <InputArea />
        </AgentCProvider>
      );

      const textInput = screen.getByTestId('text-input');
      
      // Type some text
      await user.type(textInput, 'Preserve this text');
      
      // Switch to voice mode
      const modeToggle = screen.getByTestId('input-mode-toggle');
      await user.click(modeToggle);
      
      // Switch back to text
      await user.click(modeToggle);
      
      // Text should be preserved
      expect(screen.getByTestId('text-input')).toHaveValue('Preserve this text');
    });

    it('handles mode preference persistence', async () => {
      const user = userEvent.setup();
      
      const { container, unmount } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <InputArea persistMode />
        </AgentCProvider>
      );

      // Switch to voice mode
      const modeToggle = screen.getByTestId('input-mode-toggle');
      await user.click(modeToggle);
      
      // Verify preference saved
      expect(localStorage.getItem('input-mode')).toBe('voice');
      
      // Unmount and remount
      unmount();
      
      const { container: newContainer } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <InputArea persistMode />
        </AgentCProvider>
      );

      // Should start in voice mode based on preference
      expect(screen.getByTestId('voice-button')).toBeInTheDocument();
    });
  });

  describe('Input Validation', () => {
    it('validates message content before sending', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const validator = (text: string) => {
        if (text.includes('spam')) {
          return 'Spam content not allowed';
        }
        return null;
      };
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} validator={validator} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      const sendButton = screen.getByTestId('send-button');
      
      // Type invalid content
      await user.type(input, 'This is spam content');
      await user.click(sendButton);
      
      // Should show validation error
      expect(screen.getByTestId('validation-error')).toHaveTextContent('Spam content not allowed');
      expect(onSend).not.toHaveBeenCalled();
      
      // Clear and type valid content
      await user.clear(input);
      await user.type(input, 'This is valid content');
      await user.click(sendButton);
      
      // Should send successfully
      expect(onSend).toHaveBeenCalledWith('This is valid content');
      expect(screen.queryByTestId('validation-error')).not.toBeInTheDocument();
    });

    it('handles file attachment validation', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput 
            onSend={vi.fn()} 
            enableAttachments
            maxFileSize={1024 * 1024} // 1MB
            allowedFileTypes={['image/jpeg', 'image/png']}
          />
        </AgentCProvider>
      );

      const fileInput = screen.getByTestId('file-input');
      
      // Try to attach invalid file type
      const invalidFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });
      
      fireEvent.change(fileInput, { target: { files: [invalidFile] } });
      
      await waitFor(() => {
        expect(screen.getByTestId('file-error')).toHaveTextContent(/file type not allowed/i);
      });
      
      // Try to attach oversized file
      const largeContent = new Array(2 * 1024 * 1024).fill('a').join('');
      const largeFile = new File([largeContent], 'large.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [largeFile] } });
      
      await waitFor(() => {
        expect(screen.getByTestId('file-error')).toHaveTextContent(/file too large/i);
      });
      
      // Attach valid file
      const validFile = new File(['valid'], 'image.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [validFile] } });
      
      await waitFor(() => {
        expect(screen.queryByTestId('file-error')).not.toBeInTheDocument();
        expect(screen.getByTestId('attachment-preview')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      const onSend = vi.fn();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <TextInput onSend={onSend} />
        </AgentCProvider>
      );

      const input = screen.getByTestId('text-input');
      
      // Tab to input
      await user.tab();
      expect(input).toHaveFocus();
      
      // Type and send with Enter
      await user.type(input, 'Keyboard test');
      await user.keyboard('{Enter}');
      
      expect(onSend).toHaveBeenCalledWith('Keyboard test');
    });

    it('provides proper ARIA labels', () => {
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <InputArea />
        </AgentCProvider>
      );

      const textInput = screen.getByTestId('text-input');
      expect(textInput).toHaveAttribute('aria-label');
      expect(textInput).toHaveAttribute('aria-describedby');
      
      const sendButton = screen.getByTestId('send-button');
      expect(sendButton).toHaveAttribute('aria-label');
      
      const modeToggle = screen.getByTestId('input-mode-toggle');
      expect(modeToggle).toHaveAttribute('aria-label');
      expect(modeToggle).toHaveAttribute('aria-pressed');
    });

    it('announces recording state to screen readers', async () => {
      const user = userEvent.setup();
      
      const { container } = render(
        <AgentCProvider client={mockClient} apiUrl="ws://test">
          <VoiceInput onAudioData={vi.fn()} />
        </AgentCProvider>
      );

      const voiceButton = screen.getByTestId('voice-button');
      
      // Start recording
      await user.click(voiceButton);
      
      mockClient.getAudioStatus.mockReturnValue({
        isRecording: true,
        isStreaming: true,
        hasPermission: true,
        currentLevel: 0.5,
        isAudioEnabled: true,
        isInputEnabled: true
      });
      
      mockClient.emit('audio_recording_started', {});
      
      // Should have live region for status
      await waitFor(() => {
        const liveRegion = screen.getByRole('status');
        expect(liveRegion).toHaveTextContent(/recording/i);
        expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      });
    });
  });
});