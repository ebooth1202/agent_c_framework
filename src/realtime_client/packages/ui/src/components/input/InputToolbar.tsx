/**
 * InputToolbar Component
 * 
 * Provides the toolbar for the input area with microphone controls,
 * attachment, agent selection, and send functionality.
 * 
 * Layout according to design doc:
 * [Attachments] [Tools] [OutputSelector] ... [Microphone] ... [AgentSelector] [Send]
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
import { OutputSelector } from "../controls/OutputSelector"  // Use the fixed version from controls
import { AgentSelector } from "./AgentSelector"
import type { Agent } from "./types"

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
  /** List of available agents */
  agents?: Agent[]
  /** Currently selected agent */
  selectedAgent?: Agent
  /** Callback when agent selection changes */
  onAgentChange?: (agent: Agent) => void
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
 * InputToolbar Component
 * 
 * Main toolbar with three sections:
 * - Left: Attachments, Tools, OutputSelector (controls how AGENT responds)
 * - Center: Microphone controls with audio level
 * - Right: AgentSelector (which agent to talk to) and Send button
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
    agents,
    selectedAgent,
    onAgentChange,
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
        {/* Left Section - Attachment, Tools, OutputSelector */}
        <div className="flex items-center gap-1">
          <AttachmentButton onClick={onAttachment} />
          <ToolsButton onClick={onTools} />
          
          {/* OutputSelector - Controls how AGENT responds (text/voice/avatar) */}
          <OutputSelector className="ml-1" />
        </div>

        {/* Center Section - Microphone Controls (NOT a mode toggle) */}
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
          {/* AgentSelector - Choose which agent to talk to */}
          {onAgentChange && (
            <AgentSelector
              agents={agents}
              selectedAgent={selectedAgent || null}
              onAgentSelect={onAgentChange}
              variant="dropdown"
              className="min-w-[150px] max-w-[200px]"
            />
          )}
          
          {/* Send Button */}
          <Button
            variant="default"
            size="icon"
            onClick={onSend}
            disabled={!canSend}
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }
)

InputToolbar.displayName = "InputToolbar"