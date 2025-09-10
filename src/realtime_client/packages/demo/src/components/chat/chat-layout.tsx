'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { ConnectionStatus } from '@agentc/realtime-ui';
import { SidePanel } from './side-panel';
import { ViewManager } from './view-manager';
import { ChatInputArea, type OutputMode } from '@agentc/realtime-ui';
import { Card, Separator } from '@agentc/realtime-ui';
import { Logger } from '@/utils/logger';

export interface ChatLayoutProps {
  className?: string;
  defaultOutputMode?: OutputMode;
}

/**
 * Main chat layout component
 * Provides the overall structure for the chat interface with header, sidebar, content, and footer
 */
export function ChatLayout({ 
  className,
  defaultOutputMode = 'text'
}: ChatLayoutProps) {
  const [outputMode, setOutputMode] = React.useState<OutputMode>(defaultOutputMode);
  const [isSidePanelOpen, setIsSidePanelOpen] = React.useState(true);
  const [isMobile, setIsMobile] = React.useState(false);

  // Detect mobile screen size
  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      // Auto-close sidebar on mobile
      if (window.innerWidth < 768) {
        setIsSidePanelOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className={cn(
      'flex flex-col h-screen bg-background',
      className
    )}>
      {/* Header */}
      <header className="flex-shrink-0 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold">Agent C Realtime</h1>
            <ConnectionStatus compact showDetails={false} />
          </div>
          
          {/* Mobile menu button could go here if needed */}
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Side Panel */}
        <SidePanel 
          isOpen={isSidePanelOpen}
          onToggle={() => setIsSidePanelOpen(!isSidePanelOpen)}
          isMobile={isMobile}
          onNewSession={() => {
            // Placeholder for new session logic
            Logger.debug('New session requested');
          }}
        />

        {/* Main Chat Area */}
        <main className={cn(
          'flex-1 flex flex-col overflow-hidden',
          isMobile && isSidePanelOpen && 'hidden' // Hide main content on mobile when sidebar is open
        )}>
          {/* View Manager - Main content area */}
          <div className="flex-1 overflow-hidden">
            <ViewManager 
              outputMode={outputMode}
              className="h-full"
            />
          </div>

          {/* Input Area - Footer */}
          <footer className="flex-shrink-0 border-t bg-background">
            <div className="p-4">
              <ChatInputArea 
                outputMode={outputMode}
                onOutputModeChange={setOutputMode}
              />
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}

/**
 * Alternative compact layout for embedding
 */
export function CompactChatLayout({ 
  className,
  defaultOutputMode = 'text'
}: ChatLayoutProps) {
  const [outputMode, setOutputMode] = React.useState<OutputMode>(defaultOutputMode);

  return (
    <Card className={cn(
      'flex flex-col h-full min-h-[400px]',
      className
    )}>
      {/* Compact Header */}
      <div className="flex-shrink-0 p-3 border-b">
        <ConnectionStatus compact />
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        <ViewManager 
          outputMode={outputMode}
          className="h-full"
        />
      </div>

      <Separator />

      {/* Input Footer */}
      <div className="flex-shrink-0 p-3">
        <ChatInputArea 
          outputMode={outputMode}
          onOutputModeChange={setOutputMode}
        />
      </div>
    </Card>
  );
}

/**
 * Layout with split view for development/debugging
 */
export function DebugChatLayout({ 
  className,
  defaultOutputMode = 'text'
}: ChatLayoutProps & {
  showDebugPanel?: boolean;
}) {
  const [outputMode, setOutputMode] = React.useState<OutputMode>(defaultOutputMode);
  const [showDebug, setShowDebug] = React.useState(false);

  return (
    <div className={cn(
      'flex flex-col h-screen bg-background',
      className
    )}>
      {/* Header with debug toggle */}
      <header className="flex-shrink-0 border-b">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold">Agent C Realtime (Debug)</h1>
            <ConnectionStatus compact showDetails={false} />
          </div>
          
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {showDebug ? 'Hide' : 'Show'} Debug
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-hidden">
            <ViewManager 
              outputMode={outputMode}
              className="h-full"
            />
          </div>
          
          <div className="flex-shrink-0 border-t p-4">
            <ChatInputArea 
              outputMode={outputMode}
              onOutputModeChange={setOutputMode}
            />
          </div>
        </div>

        {/* Debug Panel */}
        {showDebug && (
          <>
            <Separator orientation="vertical" />
            <div className="w-96 overflow-auto p-4 bg-muted/30">
              <h2 className="text-lg font-semibold mb-4">Debug Information</h2>
              <div className="space-y-4">
                <Card className="p-3">
                  <h3 className="text-sm font-medium mb-2">Connection Details</h3>
                  <ConnectionStatus showDetails compact={false} />
                </Card>
                
                <Card className="p-3">
                  <h3 className="text-sm font-medium mb-2">Current Mode</h3>
                  <p className="text-sm text-muted-foreground">Output: {outputMode}</p>
                </Card>
                
                {/* Additional debug info can be added here */}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}