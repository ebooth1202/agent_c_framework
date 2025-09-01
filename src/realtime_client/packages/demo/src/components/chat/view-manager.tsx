'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  MessageSquare, 
  Mic, 
  Volume2, 
  Video,
  Activity,
  Loader2,
  User,
  Bot
} from 'lucide-react';
import type { OutputMode } from '@/components/input/input-area';
import type { Message } from '@agentc/realtime-core';
import { MessageList } from './message-list';
import { TypingIndicator } from './typing-indicator';

export interface ViewManagerProps {
  outputMode: OutputMode;
  className?: string;
  messages?: Message[];
  partialMessage?: string;
  isAgentTyping?: boolean;
  emptyStateComponent?: React.ReactNode;
  maxHeight?: string;
  audioLevel?: number;
  isStreaming?: boolean;
}

/**
 * View manager component that renders different views based on output mode
 * Handles chat, voice, and avatar views with smooth transitions
 */
export function ViewManager({ 
  outputMode,
  className,
  messages = [],
  partialMessage,
  isAgentTyping = false,
  emptyStateComponent,
  maxHeight = '600px',
  audioLevel = 0,
  isStreaming = false
}: ViewManagerProps) {
  // Smooth transition between views
  const [transitioning, setTransitioning] = React.useState(false);
  const [currentMode, setCurrentMode] = React.useState(outputMode);

  React.useEffect(() => {
    if (outputMode !== currentMode) {
      setTransitioning(true);
      const timer = setTimeout(() => {
        setCurrentMode(outputMode);
        setTransitioning(false);
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [outputMode, currentMode]);

  return (
    <div className={cn(
      'relative h-full overflow-hidden',
      className
    )}>
      {/* Transition overlay */}
      {transitioning && (
        <div className="absolute inset-0 bg-background/50 z-10 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Render appropriate view based on mode */}
      <div className={cn(
        'h-full transition-opacity duration-150',
        transitioning && 'opacity-50'
      )}>
        {currentMode === 'text' && (
          <ChatView 
            messages={messages}
            partialMessage={partialMessage}
            isAgentTyping={isAgentTyping}
            emptyStateComponent={emptyStateComponent}
            maxHeight={maxHeight}
          />
        )}
        {currentMode === 'voice' && (
          <VoiceView 
            messages={messages}
            partialMessage={partialMessage}
            isAgentTyping={isAgentTyping}
            audioLevel={audioLevel}
            isStreaming={isStreaming}
            maxHeight={maxHeight}
          />
        )}
        {currentMode === 'avatar' && (
          <AvatarView 
            messages={messages}
            partialMessage={partialMessage}
            isAgentTyping={isAgentTyping}
            emptyStateComponent={emptyStateComponent}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Chat view for text-based conversations
 */
function ChatView({ 
  messages = [],
  partialMessage,
  isAgentTyping,
  emptyStateComponent,
  maxHeight
}: {
  messages?: Message[];
  partialMessage?: string;
  isAgentTyping?: boolean;
  emptyStateComponent?: React.ReactNode;
  maxHeight?: string;
}) {
  return (
    <div className="h-full flex flex-col">
      {/* Chat header */}
      <div className="flex-shrink-0 border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">Chat Conversation</h2>
        </div>
      </div>

      {/* Messages area using MessageList component */}
      <div className="flex-1 overflow-hidden">
        <MessageList
          maxHeight={maxHeight}
          emptyStateComponent={emptyStateComponent}
        />
      </div>
    </div>
  );
}

/**
 * Voice view for voice conversations
 */
function VoiceView({ 
  messages = [],
  partialMessage,
  isAgentTyping,
  audioLevel = 0,
  isStreaming = false,
  maxHeight
}: {
  messages?: Message[];
  partialMessage?: string;
  isAgentTyping?: boolean;
  audioLevel?: number;
  isStreaming?: boolean;
  maxHeight?: string;
}) {
  return (
    <div className="h-full flex items-center justify-center">
      <Card className="w-full max-w-md mx-4 p-8">
        <div className="text-center space-y-6">
          {/* Voice icon with animation */}
          <div className="relative mx-auto w-32 h-32">
            <div className="absolute inset-0 bg-primary/20 rounded-full animate-pulse" />
            <div className="absolute inset-4 bg-primary/30 rounded-full animate-pulse animation-delay-200" />
            <div className="absolute inset-8 bg-primary/40 rounded-full animate-pulse animation-delay-400" />
            <div className="relative flex items-center justify-center h-full">
              <Volume2 className="h-12 w-12 text-primary" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-semibold">Voice Mode Active</h2>
            <p className="text-muted-foreground">
              Voice conversation interface will be displayed here
            </p>
          </div>

          {/* Audio visualizer */}
          <div className="flex items-center justify-center gap-1 h-16">
            {[...Array(7)].map((_, i) => {
              // Calculate bar height based on audio level
              const threshold = (i + 1) / 7;
              const isActive = audioLevel >= threshold * 0.8;
              const baseHeight = isStreaming ? 20 : 10;
              const maxHeight = isStreaming ? 50 : 20;
              const height = isActive 
                ? baseHeight + (maxHeight - baseHeight) * audioLevel
                : baseHeight;
              
              return (
                <div
                  key={i}
                  className={cn(
                    'w-1 rounded-full transition-all duration-150',
                    isStreaming && isActive ? 'bg-primary' : 'bg-primary/30'
                  )}
                  style={{
                    height: `${height}px`
                  }}
                />
              );
            })}
          </div>

          {/* Status indicators */}
          <div className="flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Mic className={cn(
                "h-4 w-4",
                isStreaming ? "text-primary" : "text-muted-foreground"
              )} />
              <span className={cn(
                isStreaming ? "text-primary" : "text-muted-foreground"
              )}>
                {isStreaming ? "Listening..." : "Ready to listen"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className={cn(
                "h-4 w-4",
                isAgentTyping ? "text-primary animate-pulse" : "text-muted-foreground"
              )} />
              <span className={cn(
                isAgentTyping ? "text-primary" : "text-muted-foreground"
              )}>
                {isAgentTyping ? "Processing..." : "Idle"}
              </span>
            </div>
          </div>

          {/* Show recent messages below voice visualization */}
          {messages.length > 0 && (
            <div className="mt-6 max-h-40 overflow-y-auto border-t pt-4">
              <div className="space-y-2">
                {messages.slice(-3).map((msg, idx) => (
                  <div key={idx} className="text-sm">
                    <span className="font-medium">
                      {msg.role === 'user' ? 'You: ' : 'Agent: '}
                    </span>
                    <span className="text-muted-foreground">
                      {msg.content.substring(0, 100)}
                      {msg.content.length > 100 && '...'}
                    </span>
                  </div>
                ))}
                {partialMessage && (
                  <div className="text-sm">
                    <span className="font-medium">Agent: </span>
                    <span className="text-muted-foreground">
                      {partialMessage}
                      <span className="inline-block w-1 h-3 ml-0.5 bg-current animate-pulse" />
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

/**
 * Avatar view for video avatar interactions
 */
function AvatarView({ 
  messages = [],
  partialMessage,
  isAgentTyping,
  emptyStateComponent
}: {
  messages?: Message[];
  partialMessage?: string;
  isAgentTyping?: boolean;
  emptyStateComponent?: React.ReactNode;
}) {
  return (
    <div className="h-full flex flex-col">
      {/* Avatar header */}
      <div className="flex-shrink-0 border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Video className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">Avatar Mode</h2>
        </div>
      </div>

      {/* Avatar video area */}
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="w-full max-w-4xl aspect-video bg-black/5 dark:bg-white/5">
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="mx-auto w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center">
                <Video className="h-12 w-12 text-primary/60" />
              </div>
              
              <div className="space-y-2">
                <h3 className="text-xl font-semibold">Avatar Video Stream</h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                  The avatar video stream will appear here when connected.
                  This feature integrates with HeyGen streaming avatars.
                </p>
              </div>

              {/* Placeholder controls */}
              <div className="flex items-center justify-center gap-4 pt-4">
                <div className="px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm">
                  <span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-2" />
                  Not Connected
                </div>
                <div className="text-sm text-muted-foreground">
                  Resolution: 1280x720
                </div>
                <div className="text-sm text-muted-foreground">
                  FPS: 30
                </div>
              </div>

              <p className="text-xs text-muted-foreground italic pt-4">
                Avatar integration will be implemented in Phase 6
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Avatar controls footer with recent messages */}
      <div className="flex-shrink-0 border-t">
        {/* Recent messages */}
        {(messages.length > 0 || partialMessage) && (
          <div className="px-4 py-2 max-h-32 overflow-y-auto bg-muted/20">
            <div className="space-y-1">
              {messages.slice(-2).map((msg, idx) => (
                <div key={idx} className="text-xs">
                  <span className="font-medium">
                    {msg.role === 'user' ? 'You: ' : 'Agent: '}
                  </span>
                  <span className="text-muted-foreground">
                    {msg.content.substring(0, 80)}
                    {msg.content.length > 80 && '...'}
                  </span>
                </div>
              ))}
              {partialMessage && (
                <div className="text-xs">
                  <span className="font-medium">Agent: </span>
                  <span className="text-muted-foreground">
                    {partialMessage}
                    <span className="inline-block w-1 h-2 ml-0.5 bg-current animate-pulse" />
                  </span>
                </div>
              )}
              {isAgentTyping && !partialMessage && (
                <div className="text-xs">
                  <span className="font-medium">Agent: </span>
                  <TypingIndicator className="inline-block" />
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Avatar info */}
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Avatar: Default</span>
              <span>•</span>
              <span>Mode: Avatar</span>
            </div>
            <div className="flex items-center gap-2">
              {/* Placeholder for avatar control buttons */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Removed MessageBubble component as we're using the Message component from message.tsx