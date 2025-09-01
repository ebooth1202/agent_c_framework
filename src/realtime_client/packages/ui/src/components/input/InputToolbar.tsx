/**
 * InputToolbar Component
 * 
 * Provides the toolbar for the input area with microphone controls,
 * attachment, agent selection, and send functionality.
 */

import * as React from "react"
import { cn } from "../../lib/utils"
import { Button } from "../ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip"
import { 
  Paperclip, 
  Wrench, 
  Send
} from "lucide-react"

// Import actual components
import { MicrophoneButton } from "./MicrophoneButton"
import type { Agent, OutputMode, OutputOption } from "./types"

export interface InputToolbarProps {
  /** Callback when send button is clicked */
  onSend: () => void
  /** Whether the send button should be enabled */
  canSend: boolean
  /** Whether audio is currently being recorded */
  isRecording: boolean
  /** Callback to start audio recording */
  onStartRecording: () => void
  /** Callback to stop audio recording */
  onStopRecording: () => void
  /** Current audio level (0-100) for visualization */
  audioLevel?: number
  /** Callback for attachment button (optional) */
  onAttachment?: () => void
  /** Callback for tools button (optional, placeholder) */
  onTools?: () => void
  /** Currently selected agent */
  selectedAgent?: Agent
  /** Callback when agent selection changes */
  onAgentChange?: (agent: Agent) => void
  /** Current output mode (how agent responds) */
  outputMode?: OutputMode
  /** Callback when output mode changes */
  onOutputModeChange?: (mode: OutputMode, option?: OutputOption) => void
  /** Additional CSS classes */
  className?: string
}

/**
 * Audio level indicator component
 * Shows 5 bars that light up based on audio level
 */
const AudioLevelIndicator: React.FC<{ level: number; className?: string }> = ({ 
  level, 
  className 
}) => {
  // Calculate how many bars should be active (each bar = 20%)
  const activeBars = Math.ceil((level / 100) * 5)
  
  return (
    <div 
      className={cn("flex items-end gap-0.5 h-5", className)}
      role="img"
      aria-label={`Audio level: ${level}%`}
    >
      {[1, 2, 3, 4, 5].map((bar) => (
        <div
          key={bar}
          className={cn(
            "w-1 rounded-full transition-all duration-150",
            bar <= activeBars 
              ? "bg-primary" 
              : "bg-muted",
            // Variable heights for visual appeal
            bar === 1 && "h-2",
            bar === 2 && "h-3",
            bar === 3 && "h-4",
            bar === 4 && "h-3",
            bar === 5 && "h-2"
          )}
          aria-hidden="true"
        />
      ))}
    </div>
  )
}

/**
 * Attachment button (placeholder)
 */
const AttachmentButton: React.FC<{ onClick?: () => void }> = ({ onClick }) => (
  <Button
    variant="ghost"
    size="icon"
    onClick={onClick}
    aria-label="Add attachment"
    disabled
  >
    <Paperclip className="h-4 w-4" />
  </Button>
)

/**
 * Tools button (placeholder with "Coming Soon" tooltip)
 */
const ToolsButton: React.FC<{ onClick?: () => void }> = ({ onClick }) => (
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClick}
          disabled
          aria-label="Tools (Coming Soon)"
        >
          <Wrench className="h-4 w-4" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>Coming Soon</p>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
)

/**
 * Simple output mode selector
 * For now, just shows the current mode
 */
const OutputModeDisplay: React.FC<{
  mode?: OutputMode
}> = ({ mode = 'text' }) => {
  const modeLabels = {
    'text': 'Text',
    'voice': 'Voice',
    'avatar': 'Avatar'
  }
  
  return (
    <div className="text-sm text-muted-foreground px-2">
      Mode: {modeLabels[mode]}
    </div>
  )
}

/**
 * Simple agent display
 * For now, just shows the agent name
 */
const AgentDisplay: React.FC<{
  selectedAgent?: Agent
}> = ({ selectedAgent }) => {
  if (!selectedAgent) return null
  
  return (
    <div className="text-sm text-muted-foreground px-2">
      {selectedAgent.name}
    </div>
  )
}

/**
 * InputToolbar Component
 * 
 * Main toolbar with three sections:
 * - Left: Attachments, Tools, Output mode
 * - Center: Microphone controls with audio level
 * - Right: Agent selector and Send button
 */
export const InputToolbar = React.forwardRef<HTMLDivElement, InputToolbarProps>(
  ({ 
    onSend,
    canSend,
    isRecording,
    onStartRecording,
    onStopRecording,
    audioLevel = 0,
    onAttachment,
    onTools,
    selectedAgent,
    onAgentChange,
    outputMode,
    onOutputModeChange,
    className,
    ...props 
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center gap-2.5 w-full px-4 py-2 border-t border-border",
          className
        )}
        {...props}
      >
        {/* Left Section - Attachment, Tools, Output */}
        <div className="flex items-center gap-1">
          <AttachmentButton onClick={onAttachment} />
          <ToolsButton onClick={onTools} />
          <div className="w-px h-6 bg-border mx-1" aria-hidden="true" />
          <OutputModeDisplay mode={outputMode} />
        </div>

        {/* Center Section - Microphone Controls (Critical) */}
        <div className="flex-1 flex justify-center items-center gap-2">
          <MicrophoneButton
            isRecording={isRecording}
            onStartRecording={onStartRecording}
            onStopRecording={onStopRecording}
            audioLevel={audioLevel}
            size="default"
            showTooltip={true}
          />
          
          {/* Audio level indicator - only visible when recording */}
          {isRecording && (
            <AudioLevelIndicator 
              level={audioLevel} 
              className="ml-2"
            />
          )}
        </div>

        {/* Right Section - Agent Selector and Send */}
        <div className="flex items-center gap-2">
          <AgentDisplay selectedAgent={selectedAgent} />
          <div className="w-px h-6 bg-border mx-1" aria-hidden="true" />
          <Button
            variant="default"
            size="default"
            onClick={onSend}
            disabled={!canSend}
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
            <span className="ml-1">Send</span>
          </Button>
        </div>
      </div>
    )
  }
)

InputToolbar.displayName = "InputToolbar"