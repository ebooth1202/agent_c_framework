'use client';

import React from 'react';
import { useChat, useAudio, useTurnState, useConnection } from '@agentc/realtime-react';
import { MessageList } from './message-list';
import { TypingIndicator } from './typing-indicator';
import { InputArea } from '@/components/input/input-area';
import { ViewManager } from './view-manager';
import { useOutputMode, type OutputMode } from '@agentc/realtime-react';
import { cn } from '@/lib/utils';
import { Alert, AlertDescription } from '@agentc/realtime-ui';
import { AlertCircle, WifiOff } from 'lucide-react';

export interface ChatInterfaceProps {
  className?: string;
  /**
   * Whether to show the view manager or just the message list
   */
  showViewManager?: boolean;
  /**
   * Whether to show connection alerts
   */
  showConnectionAlerts?: boolean;
  /**
   * Custom empty state component
   */
  emptyStateComponent?: React.ReactNode;
  /**
   * Maximum height for the message area
   */
  maxHeight?: string;
}

/**
 * Main chat interface component that integrates all SDK functionality
 * Manages the complete chat experience with text, voice, and avatar modes
 */
export function ChatInterface({
  className,
  showViewManager = true,
  showConnectionAlerts = true,
  emptyStateComponent,
  maxHeight = '600px'
}: ChatInterfaceProps) {
  // SDK hooks
  const { 
    messages, 
    sendMessage, 
    isAgentTyping, 
    partialMessage,
    isSending,
    error: chatError 
  } = useChat();
  
  const { 
    startStreaming,
    stopStreaming,
    isStreaming,
    canSendInput,
    audioLevel,
    hasError: audioError,
    errorMessage: audioErrorMessage
  } = useAudio({ respectTurnState: true });
  
  const { canSendInput: turnCanSend } = useTurnState();
  const { isConnected, error: connectionError } = useConnection();
  
  // Output mode management
  const {
    outputMode,
    setOutputMode,
    isTextMode,
    isVoiceMode,
    isAvatarMode,
    error: modeError
  } = useOutputMode({
    initialMode: 'text',
    onModeChange: (mode) => {
      // Stop audio streaming when switching away from voice mode
      if (isStreaming && mode !== 'voice') {
        stopStreaming();
      }
    }
  });
  
  // Handle message sending with mode awareness
  const handleSendMessage = React.useCallback(async (text: string) => {
    if (!isConnected) {
      console.error('Cannot send message: Not connected');
      return;
    }
    
    try {
      await sendMessage(text);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [isConnected, sendMessage]);
  
  // Handle output mode change
  const handleOutputModeChange = React.useCallback((mode: OutputMode) => {
    setOutputMode(mode);
  }, [setOutputMode]);
  
  // Combine errors for display
  const activeError = chatError || audioErrorMessage || modeError || 
    (connectionError instanceof Error ? connectionError.message : connectionError);
  
  // Determine if we should show typing indicator
  const showTypingIndicator = isAgentTyping && !partialMessage;
  
  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Connection alerts */}
      {showConnectionAlerts && !isConnected && (
        <Alert variant="destructive" className="mb-4">
          <WifiOff className="h-4 w-4" />
          <AlertDescription>
            Not connected to server. Messages cannot be sent.
          </AlertDescription>
        </Alert>
      )}
      
      {/* Error display */}
      {activeError && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {typeof activeError === 'string' ? activeError : String(activeError)}
          </AlertDescription>
        </Alert>
      )}
      
      {/* Main content area */}
      <div className="flex-1 overflow-hidden">
        {showViewManager ? (
          <ViewManager 
            outputMode={outputMode}
            messages={messages}
            partialMessage={partialMessage}
            isAgentTyping={showTypingIndicator}
            emptyStateComponent={emptyStateComponent}
            maxHeight={maxHeight}
            audioLevel={audioLevel}
            isStreaming={isStreaming}
          />
        ) : (
          <MessageList
            maxHeight={maxHeight}
            emptyStateComponent={emptyStateComponent}
          />
        )}
      </div>
      
      {/* Input area */}
      <div className="flex-shrink-0 mt-4">
        <InputArea
          outputMode={outputMode}
          onOutputModeChange={handleOutputModeChange}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
}

/**
 * Compact version of ChatInterface for embedded use
 */
export function CompactChatInterface({
  className,
  ...props
}: Omit<ChatInterfaceProps, 'showViewManager'>) {
  return (
    <ChatInterface
      className={className}
      showViewManager={false}
      {...props}
    />
  );
}