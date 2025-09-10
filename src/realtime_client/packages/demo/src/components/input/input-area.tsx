'use client';

import React from 'react';
import { Send, Mic, Type, Volume2, Video } from 'lucide-react';
import { Logger } from '@/utils/logger';
import { 
  Button,
  Textarea,
  Card,
  ToggleGroup,
  ToggleGroupItem,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from '@agentc/realtime-ui';
import { useAudio, useChat, type OutputMode } from '@agentc/realtime-react';

// Re-export OutputMode for other components
export type { OutputMode };
import { cn } from '@/lib/utils';

export interface InputAreaProps {
  className?: string;
  outputMode: OutputMode;
  onOutputModeChange: (mode: OutputMode) => void;
  onSendMessage?: (text: string) => void;
}

/**
 * Input area component with text input and output mode selector
 * Handles both text input and voice recording controls
 */
export function InputArea({ 
  className,
  outputMode,
  onOutputModeChange,
  onSendMessage
}: InputAreaProps) {
  const [message, setMessage] = React.useState('');
  const [isComposing, setIsComposing] = React.useState(false);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  
  const { sendMessage: sdkSendMessage } = useChat();
  const { 
    isStreaming,
    startStreaming,
    stopStreaming,
    audioLevel,
    canSendInput,
    isRecording
  } = useAudio({ respectTurnState: true });

  // Handle text message submission
  const handleSubmit = React.useCallback(() => {
    if (!message.trim()) return;
    
    // Use custom handler if provided, otherwise use SDK
    if (onSendMessage) {
      onSendMessage(message.trim());
    } else {
      sdkSendMessage(message.trim());
    }
    setMessage('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [message, sdkSendMessage, onSendMessage]);

  // Handle Enter key (submit on Enter, newline on Shift+Enter)
  const handleKeyDown = React.useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit, isComposing]);

  // Auto-resize textarea as user types
  const handleTextareaChange = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, []);

  // Handle voice recording toggle
  const handleVoiceToggle = React.useCallback(async () => {
    try {
      if (isStreaming) {
        stopStreaming();
      } else {
        await startStreaming();
      }
    } catch (error) {
      Logger.error('Failed to toggle audio streaming:', error);
    }
  }, [isStreaming, startStreaming, stopStreaming]);

  return (
    <Card className={cn('p-4', className)}>
      <div className="space-y-4">
        {/* Output Mode Selector */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Output Mode</span>
          <ToggleGroup 
            type="single" 
            value={outputMode}
            onValueChange={(value) => value && onOutputModeChange(value as OutputMode)}
            className="justify-start"
          >
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <ToggleGroupItem value="text" aria-label="Text mode">
                    <Type className="h-4 w-4" />
                  </ToggleGroupItem>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Text Chat</p>
                </TooltipContent>
              </Tooltip>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <ToggleGroupItem value="voice" aria-label="Voice mode">
                    <Volume2 className="h-4 w-4" />
                  </ToggleGroupItem>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Voice Conversation</p>
                </TooltipContent>
              </Tooltip>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <ToggleGroupItem value="avatar" aria-label="Avatar mode">
                    <Video className="h-4 w-4" />
                  </ToggleGroupItem>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Avatar Video</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </ToggleGroup>
        </div>

        {/* Input Controls */}
        <div className="flex gap-2">
          {/* Text Input Area */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={message}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              placeholder="Type a message..."
              className="min-h-[44px] max-h-[200px] resize-none pr-12"
              rows={1}
            />
            
            {/* Send Button (inside textarea) */}
            <Button
              size="icon"
              variant="ghost"
              onClick={handleSubmit}
              disabled={!message.trim()}
              className="absolute bottom-1 right-1 h-8 w-8"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>

          {/* Voice Controls */}
          <div className="flex gap-2">
            <TooltipProvider>
              {/* Recording Button */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="icon"
                    variant={isStreaming ? "destructive" : "default"}
                    onClick={handleVoiceToggle}
                    disabled={!canSendInput && !isStreaming}
                    aria-label={isStreaming ? "Stop recording" : "Start recording"}
                  >
                    <Mic className={cn(
                      "h-4 w-4",
                      isStreaming && "animate-pulse"
                    )} />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isRecording ? "Stop Recording" : "Start Recording"}</p>
                </TooltipContent>
              </Tooltip>

              {/* Audio Level Indicator */}
              {isStreaming && audioLevel > 0 && (
                <div className="flex items-center justify-center px-2">
                  <div className="flex gap-0.5 h-8 items-center">
                    {[0.2, 0.4, 0.6, 0.8, 1.0].map((threshold, i) => (
                      <div
                        key={i}
                        className={cn(
                          "w-1 transition-all duration-75",
                          audioLevel >= threshold 
                            ? "bg-primary" 
                            : "bg-primary/20",
                          audioLevel >= threshold
                            ? threshold >= 0.8 ? "h-8" : threshold >= 0.6 ? "h-6" : "h-4"
                            : "h-2"
                        )}
                      />
                    ))}
                  </div>
                </div>
              )}
            </TooltipProvider>
          </div>
        </div>

        {/* Recording Indicator */}
        {isStreaming && (
          <div className="flex items-center gap-2 text-sm text-destructive">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive"></span>
            </span>
            {canSendInput ? 'Recording...' : 'Listening...'}
          </div>
        )}
        
        {/* Turn state indicator */}
        {!canSendInput && !isStreaming && outputMode === 'voice' && (
          <div className="text-xs text-muted-foreground">
            Agent is speaking...
          </div>
        )}
      </div>
    </Card>
  );
}

/**
 * Output mode selector component (can be used separately)
 */
export function OutputSelector({ 
  value, 
  onChange,
  className 
}: { 
  value: OutputMode;
  onChange: (mode: OutputMode) => void;
  className?: string;
}) {
  return (
    <ToggleGroup 
      type="single" 
      value={value}
      onValueChange={(v) => v && onChange(v as OutputMode)}
      className={cn("justify-start", className)}
    >
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <ToggleGroupItem value="text" aria-label="Text mode">
              <Type className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Text</span>
            </ToggleGroupItem>
          </TooltipTrigger>
          <TooltipContent>
            <p>Text Chat Mode</p>
          </TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <ToggleGroupItem value="voice" aria-label="Voice mode">
              <Volume2 className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Voice</span>
            </ToggleGroupItem>
          </TooltipTrigger>
          <TooltipContent>
            <p>Voice Conversation Mode</p>
          </TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <ToggleGroupItem value="avatar" aria-label="Avatar mode">
              <Video className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Avatar</span>
            </ToggleGroupItem>
          </TooltipTrigger>
          <TooltipContent>
            <p>Avatar Video Mode</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </ToggleGroup>
  );
}