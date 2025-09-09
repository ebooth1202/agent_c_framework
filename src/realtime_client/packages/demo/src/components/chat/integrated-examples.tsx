'use client'

import React from 'react'
import { ChatInterface, CompactChatInterface } from './chat-interface'
import { MessageList, Message, TypingIndicator } from '@agentc/realtime-ui'
import { ViewManager } from './view-manager'
import { Card, Tabs, TabsContent, TabsList, TabsTrigger } from '@agentc/realtime-ui'
import { useChat, useAudio, useConnection, useOutputMode } from '@agentc/realtime-react'
import { Button, Alert, AlertDescription } from '@agentc/realtime-ui'
import { MessageSquare, Mic, Volume2, Video, Info } from 'lucide-react'

/**
 * Main example showcasing the fully integrated chat interface
 */
export function IntegratedChatExample() {
  return (
    <div className="container mx-auto p-6 space-y-8 max-w-7xl">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Agent C Realtime SDK - Integrated Chat</h1>
        <p className="text-muted-foreground">
          Full-featured chat interface with voice, text, and avatar modes
        </p>
      </div>

      {/* Main Chat Interface Demo */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Complete Chat Experience</h2>
              <p className="text-muted-foreground">
                Try switching between Text, Voice, and Avatar modes using the controls below
              </p>
            </div>
            <SDKStatusIndicator />
          </div>
          
          <div className="border rounded-lg bg-background" style={{ height: '650px' }}>
            <ChatInterface 
              showViewManager={true}
              showConnectionAlerts={true}
              maxHeight="500px"
            />
          </div>
          
          <FeatureHighlights />
        </div>
      </Card>

      {/* Multiple Integration Examples */}
      <IntegrationExamplesSection />
      
      {/* Code Examples */}
      <CodeExamplesSection />
    </div>
  )
}

/**
 * SDK Status Indicator Component
 */
function SDKStatusIndicator() {
  const { isConnected, connectionState } = useConnection()
  const { canSendInput } = useAudio()
  
  return (
    <div className="flex flex-col gap-2 text-sm">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-muted-foreground">
          {isConnected ? 'Connected' : `Disconnected (${connectionState})`}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${canSendInput ? 'bg-green-500' : 'bg-orange-500'}`} />
        <span className="text-muted-foreground">
          {canSendInput ? 'Can Send Input' : 'Waiting for Turn'}
        </span>
      </div>
    </div>
  )
}

/**
 * Feature Highlights Component
 */
function FeatureHighlights() {
  return (
    <Alert>
      <Info className="h-4 w-4" />
      <AlertDescription>
        <div className="space-y-2">
          <p className="font-semibold">Key Features Active:</p>
          <ul className="grid grid-cols-2 gap-2 text-sm mt-2">
            <li className="flex items-center gap-2">
              <MessageSquare className="h-3 w-3" />
              Real-time text messaging with markdown support
            </li>
            <li className="flex items-center gap-2">
              <Mic className="h-3 w-3" />
              Voice recording with turn management
            </li>
            <li className="flex items-center gap-2">
              <Volume2 className="h-3 w-3" />
              Audio streaming and playback
            </li>
            <li className="flex items-center gap-2">
              <Video className="h-3 w-3" />
              Avatar mode preparation (Phase 6)
            </li>
          </ul>
        </div>
      </AlertDescription>
    </Alert>
  )
}

/**
 * Multiple Integration Examples Section
 */
function IntegrationExamplesSection() {
  const [activeTab, setActiveTab] = React.useState('compact')
  
  return (
    <Card className="p-6">
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Integration Variations</h2>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="compact">Compact</TabsTrigger>
            <TabsTrigger value="voice-focus">Voice Focus</TabsTrigger>
            <TabsTrigger value="custom-empty">Custom Empty</TabsTrigger>
            <TabsTrigger value="widget">Widget</TabsTrigger>
          </TabsList>
          
          <TabsContent value="compact" className="mt-4">
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Compact interface without view manager - ideal for sidebars
              </p>
              <div className="border rounded-lg p-4" style={{ height: '400px' }}>
                <CompactChatInterface 
                  showConnectionAlerts={false}
                  maxHeight="350px"
                />
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="voice-focus" className="mt-4">
            <VoiceFocusedExample />
          </TabsContent>
          
          <TabsContent value="custom-empty" className="mt-4">
            <CustomEmptyStateExample />
          </TabsContent>
          
          <TabsContent value="widget" className="mt-4">
            <WidgetExample />
          </TabsContent>
        </Tabs>
      </div>
    </Card>
  )
}

/**
 * Voice-Focused Example
 */
function VoiceFocusedExample() {
  const { 
    outputMode,
    setOutputMode,
    isVoiceMode 
  } = useOutputMode({ initialMode: 'voice' })
  
  const { 
    isStreaming,
    audioLevel,
    startStreaming,
    stopStreaming,
    canSendInput 
  } = useAudio({ respectTurnState: true })
  
  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">
        Voice-first interface with automatic voice mode activation
      </p>
      <div className="border rounded-lg p-6 bg-background">
        <div className="text-center space-y-6">
          {/* Voice Visualization */}
          <div className="relative mx-auto w-32 h-32">
            <div className={`absolute inset-0 bg-primary/20 rounded-full ${isStreaming ? 'animate-pulse' : ''}`} />
            <div className="relative flex items-center justify-center h-full">
              <Volume2 className={`h-12 w-12 ${isStreaming ? 'text-primary' : 'text-muted-foreground'}`} />
            </div>
          </div>
          
          {/* Audio Level Bars */}
          <div className="flex items-center justify-center gap-1 h-12">
            {[...Array(9)].map((_, i) => {
              const threshold = (i + 1) / 9
              const isActive = audioLevel >= threshold * 0.8
              return (
                <div
                  key={i}
                  className={`w-1 rounded-full transition-all duration-100 ${
                    isActive ? 'bg-primary' : 'bg-primary/20'
                  }`}
                  style={{
                    height: isActive ? `${20 + i * 4}px` : '12px'
                  }}
                />
              )
            })}
          </div>
          
          {/* Control Button */}
          <Button
            size="lg"
            variant={isStreaming ? "destructive" : "default"}
            onClick={isStreaming ? stopStreaming : startStreaming}
            disabled={!canSendInput && !isStreaming}
            className="px-8"
          >
            {isStreaming ? 'Stop Recording' : 'Start Recording'}
          </Button>
          
          {/* Status */}
          <p className="text-sm text-muted-foreground">
            {isStreaming 
              ? canSendInput ? 'Recording your voice...' : 'Listening...'
              : 'Click to start voice conversation'}
          </p>
        </div>
      </div>
    </div>
  )
}

/**
 * Custom Empty State Example
 */
function CustomEmptyStateExample() {
  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">
        Chat interface with custom empty state design
      </p>
      <div className="border rounded-lg" style={{ height: '400px' }}>
        <ChatInterface 
          showViewManager={false}
          showConnectionAlerts={false}
          emptyStateComponent={
            <div className="flex flex-col items-center justify-center h-full p-8">
              <div className="mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-primary/20 to-primary/10 rounded-full flex items-center justify-center">
                  <MessageSquare className="h-10 w-10 text-primary" />
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Welcome to Agent C Chat</h3>
              <p className="text-muted-foreground text-center max-w-md mb-6">
                Start a conversation with our AI assistant. Ask questions about the SDK, 
                get help with integration, or explore our features.
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Text Chat
                </Button>
                <Button variant="outline" size="sm">
                  <Mic className="h-4 w-4 mr-2" />
                  Voice Chat
                </Button>
              </div>
            </div>
          }
          maxHeight="350px"
        />
      </div>
    </div>
  )
}

/**
 * Widget Example
 */
function WidgetExample() {
  const [isOpen, setIsOpen] = React.useState(false)
  
  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">
        Floating chat widget that can be embedded anywhere
      </p>
      <div className="relative h-[500px] border rounded-lg bg-muted/20 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-muted-foreground">Your application content here</p>
        </div>
        
        {/* Chat Widget */}
        {!isOpen ? (
          <button
            onClick={() => setIsOpen(true)}
            className="absolute bottom-4 right-4 w-14 h-14 bg-primary rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform"
          >
            <MessageSquare className="h-6 w-6 text-primary-foreground" />
          </button>
        ) : (
          <div className="absolute bottom-4 right-4 w-96 h-[450px] bg-background border rounded-lg shadow-xl flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold">Agent C Assistant</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <CompactChatInterface 
                showConnectionAlerts={false}
                maxHeight="100%"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Code Examples Section
 */
function CodeExamplesSection() {
  return (
    <Card className="p-6">
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Implementation Code</h2>
        
        <div className="space-y-6">
          {/* Basic Integration */}
          <div>
            <h3 className="text-lg font-semibold mb-2">Basic Integration</h3>
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
              <code className="text-sm">{`import { ChatInterface } from '@/components/chat'
import { AgentCProvider } from '@agentc/realtime-react'

function App() {
  const config = {
    apiKey: process.env.NEXT_PUBLIC_AGENT_C_API_KEY,
    baseURL: process.env.NEXT_PUBLIC_AGENT_C_BASE_URL
  }
  
  return (
    <AgentCProvider config={config}>
      <ChatInterface 
        showViewManager={true}
        showConnectionAlerts={true}
      />
    </AgentCProvider>
  )
}`}</code>
            </pre>
          </div>
          
          {/* Output Mode Management */}
          <div>
            <h3 className="text-lg font-semibold mb-2">Output Mode Management</h3>
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
              <code className="text-sm">{`import { useOutputMode } from '@agentc/realtime-react'

function ChatWithModes() {
  const {
    outputMode,
    setOutputMode,
    isTextMode,
    isVoiceMode,
    isAvatarMode,
    isSwitching
  } = useOutputMode({
    initialMode: 'text',
    defaultVoiceId: 'alloy',
    onModeChange: (mode) => {
      console.log('Switched to:', mode)
    }
  })
  
  return (
    <div>
      <div className="flex gap-2 mb-4">
        <Button 
          onClick={() => setOutputMode('text')}
          variant={isTextMode ? 'default' : 'outline'}
          disabled={isSwitching}
        >
          Text
        </Button>
        <Button 
          onClick={() => setOutputMode('voice')}
          variant={isVoiceMode ? 'default' : 'outline'}
          disabled={isSwitching}
        >
          Voice
        </Button>
        <Button 
          onClick={() => setOutputMode('avatar')}
          variant={isAvatarMode ? 'default' : 'outline'}
          disabled={isSwitching}
        >
          Avatar
        </Button>
      </div>
      
      <ChatInterface />
    </div>
  )
}`}</code>
            </pre>
          </div>
          
          {/* Custom Audio Controls */}
          <div>
            <h3 className="text-lg font-semibold mb-2">Custom Audio Controls</h3>
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
              <code className="text-sm">{`import { useAudio, useTurnState } from '@agentc/realtime-react'

function CustomAudioControls() {
  const { 
    startStreaming,
    stopStreaming,
    isStreaming,
    audioLevel,
    canSendInput,
    hasError,
    errorMessage
  } = useAudio({ respectTurnState: true })
  
  const { canSendInput: turnCanSend } = useTurnState()
  
  const handleToggle = async () => {
    try {
      if (isStreaming) {
        stopStreaming()
      } else {
        await startStreaming()
      }
    } catch (error) {
      console.error('Audio error:', error)
    }
  }
  
  return (
    <div className="space-y-4">
      {hasError && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}
      
      <Button
        onClick={handleToggle}
        disabled={!canSendInput && !isStreaming}
        variant={isStreaming ? 'destructive' : 'default'}
      >
        {isStreaming ? 'Stop' : 'Start'} Recording
      </Button>
      
      {isStreaming && (
        <div className="flex items-center gap-2">
          <span>Level:</span>
          <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-100"
              style={{ width: \`\${audioLevel * 100}%\` }}
            />
          </div>
        </div>
      )}
      
      <p className="text-sm text-muted-foreground">
        Turn State: {turnCanSend ? 'Your turn' : 'Agent speaking'}
      </p>
    </div>
  )
}`}</code>
            </pre>
          </div>
        </div>
      </div>
    </Card>
  )
}