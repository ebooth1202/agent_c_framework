"use client"

import * as React from "react"
import { useState, useCallback, useEffect, useMemo } from "react"
import { cn } from "../../lib/utils"
import { 
  useChat, 
  useAudio, 
  useTurnState, 
  useVoiceModel, 
  useAvatar 
} from "@agentc/realtime-react"
import type { Voice } from "@agentc/realtime-core"
import { InputContainer } from "./InputContainer"
import { RichTextEditor } from "./RichTextEditor"
import { InputToolbar } from "./InputToolbar"
import type { Agent, OutputMode, OutputOption } from "./types"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "../ui/alert"

export interface InputAreaProps {
  // Optional overrides for advanced usage
  className?: string
  maxHeight?: string
  placeholder?: string
  agents?: Agent[]
  voiceOptions?: OutputOption[]
  avatarOptions?: OutputOption[]
  onAgentChange?: (agent: Agent) => void
  onOutputModeChange?: (mode: OutputMode, option?: OutputOption) => void
  // Additional props for test compatibility
  compact?: boolean
  disabled?: boolean
  orientation?: 'horizontal' | 'vertical'
}

const InputArea: React.FC<InputAreaProps> = ({
  className,
  maxHeight = "200px",
  placeholder = "Type a message or click the microphone to speak...",
  agents: propAgents,
  voiceOptions: propVoiceOptions,
  avatarOptions: propAvatarOptions,
  onAgentChange,
  onOutputModeChange,
  compact = false,
  disabled = false,
  orientation = 'horizontal'
}) => {
  // SDK hooks
  const { messages, sendMessage, isAgentTyping } = useChat()
  const { 
    isStreaming,
    startStreaming, 
    stopStreaming,
    audioLevel,
    canSendInput,
    errorMessage: audioError
  } = useAudio({ respectTurnState: true })
  const { canSendInput: turnCanSend } = useTurnState()
  const { availableVoices, currentVoice, setVoice } = useVoiceModel()
  const { 
    isAvatarActive,
    avatarSession,
    setAvatar,
    clearAvatar
  } = useAvatar()

  // Local state
  const [content, setContent] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Default agents if not provided
  const defaultAgents: Agent[] = useMemo(() => [
    {
      id: 'assistant',
      name: 'Assistant',
      description: 'General purpose AI assistant',
      avatar: '🤖',
      tools: [
        { id: 'search', name: 'Search' },
        { id: 'calculate', name: 'Calculate' }
      ],
      capabilities: ['General Q&A', 'Basic reasoning'],
      available: true
    },
    {
      id: 'creative',
      name: 'Creative',
      description: 'Creative writing and ideation',
      avatar: '🎨',
      tools: [
        { id: 'write', name: 'Write' },
        { id: 'edit', name: 'Edit' }
      ],
      capabilities: ['Creative writing', 'Storytelling'],
      available: true
    },
    {
      id: 'technical',
      name: 'Technical',
      description: 'Technical and coding assistance',
      avatar: '💻',
      tools: [
        { id: 'code', name: 'Code' },
        { id: 'debug', name: 'Debug' },
        { id: 'review', name: 'Review' }
      ],
      capabilities: ['Programming', 'Debugging', 'Architecture'],
      available: true
    }
  ], [])

  const agents = propAgents || defaultAgents

  // Map SDK voices to OutputOptions
  const voiceOptions = useMemo(() => {
    if (propVoiceOptions) return propVoiceOptions
    
    // Default voice options if SDK doesn't provide them
    if (!availableVoices || availableVoices.length === 0) {
      return [
        { id: 'alloy', name: 'Alloy', type: 'voice' as const, available: true },
        { id: 'echo', name: 'Echo', type: 'voice' as const, available: true },
        { id: 'fable', name: 'Fable', type: 'voice' as const, available: true },
        { id: 'onyx', name: 'Onyx', type: 'voice' as const, available: true },
        { id: 'nova', name: 'Nova', type: 'voice' as const, available: true },
        { id: 'shimmer', name: 'Shimmer', type: 'voice' as const, available: true }
      ]
    }
    
    return availableVoices
      .filter((v: Voice) => v.voice_id !== 'none' && v.voice_id !== 'avatar')
      .map((v: Voice) => ({
        id: v.voice_id,
        name: v.description,
        type: 'voice' as const,
        available: true,
        metadata: { voiceId: v.voice_id }
      }))
  }, [availableVoices, propVoiceOptions])

  // Map SDK avatars to OutputOptions
  const avatarOptions = useMemo(() => {
    if (propAvatarOptions) return propAvatarOptions
    
    // Default avatar options
    return [
      { 
        id: 'avatar-1', 
        name: 'Professional', 
        type: 'avatar' as const, 
        available: true,
        metadata: { avatarId: 'avatar-1' }
      },
      { 
        id: 'avatar-2', 
        name: 'Friendly', 
        type: 'avatar' as const, 
        available: true,
        metadata: { avatarId: 'avatar-2' }
      }
    ]
  }, [propAvatarOptions])

  // Initialize selected agent
  useEffect(() => {
    if (!selectedAgent && agents.length > 0) {
      setSelectedAgent(agents[0])
    }
  }, [agents, selectedAgent])

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  // Handle text submission
  const handleSendText = useCallback(async () => {
    if (!canSendInput || !content.trim() || disabled) return
    
    try {
      // Stop recording if active
      if (isStreaming) {
        await stopStreaming()
      }
      
      // Send message
      await sendMessage(content)
      
      // Clear editor
      setContent('')
      setError(null)
    } catch (err) {
      console.error('Failed to send message:', err)
      setError('Failed to send message. Please try again.')
      // Keep content for retry
    }
  }, [canSendInput, content, isStreaming, stopStreaming, sendMessage, disabled])

  // Handle recording start
  const handleStartRecording = useCallback(async () => {
    if (!canSendInput || disabled) {
      setError("Can't start recording - wait for your turn")
      return
    }
    
    try {
      setError(null)
      await startStreaming()
    } catch (err) {
      console.error('Failed to start recording:', err)
      if (err instanceof Error) {
        if (err.message.includes('permission')) {
          setError('Microphone permission denied. Please check your browser settings.')
        } else {
          setError('Failed to start recording. Please try again.')
        }
      }
    }
  }, [canSendInput, startStreaming, disabled])

  // Handle recording stop
  const handleStopRecording = useCallback(async () => {
    try {
      await stopStreaming()
      setError(null)
    } catch (err) {
      console.error('Failed to stop recording:', err)
      setError('Failed to stop recording. Please try again.')
    }
  }, [stopStreaming])

  // Handle agent change
  const handleAgentChange = useCallback((agent: Agent) => {
    setSelectedAgent(agent)
    onAgentChange?.(agent)
  }, [onAgentChange])

  // Note: Output option changes are now handled internally by the OutputSelector component
  // which uses SDK hooks directly for state management

  // Stop recording if turn is lost or disabled
  useEffect(() => {
    if (isStreaming && (!canSendInput || disabled)) {
      handleStopRecording()
    }
  }, [isStreaming, canSendInput, disabled, handleStopRecording])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isStreaming) {
        stopStreaming()
      }
    }
  }, [isStreaming, stopStreaming])

  // Determine if input should be disabled
  const isInputDisabled = disabled || !canSendInput || isAgentTyping

  return (
    <div className={cn("w-full", className)}>
      {/* Error display */}
      {(error || audioError) && (
        <Alert variant="destructive" className="mb-2">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || audioError}
          </AlertDescription>
        </Alert>
      )}
      
      {/* Main input area */}
      <InputContainer maxHeight={maxHeight} className={cn(
        orientation === 'horizontal' && !compact && 'gap-2',
        compact && 'py-2'
      )}>
        <RichTextEditor
          value={content}
          onChange={setContent}
          onSubmit={handleSendText}
          disabled={isInputDisabled}
          placeholder={
            isInputDisabled 
              ? (isAgentTyping ? "Agent is typing..." : "Wait for your turn...")
              : placeholder
          }
          className={cn(
            "flex-1",
            compact && "py-2"
          )}
        />
        
        <InputToolbar
          onSend={handleSendText}
          canSend={content.trim().length > 0 && canSendInput && !disabled}
          isRecording={isStreaming}
          onStartRecording={handleStartRecording}
          onStopRecording={handleStopRecording}
          audioLevel={audioLevel}
          agents={agents}
          selectedAgent={selectedAgent || undefined}
          onAgentChange={handleAgentChange}
        />
      </InputContainer>
      
      {/* Status indicators */}
      {(isStreaming || isAgentTyping) && (
        <div className="mt-2 px-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div 
              className={cn(
                "h-2 w-2 rounded-full",
                isStreaming && "bg-green-500 animate-pulse",
                isAgentTyping && "bg-blue-500 animate-pulse"
              )}
            />
            <span>
              {isStreaming && "Recording..."}
              {isAgentTyping && "Agent is typing..."}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

InputArea.displayName = "InputArea"

export { InputArea }