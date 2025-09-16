'use client'

import * as React from 'react'
import { cn } from '../../lib/utils'
import { 
  Copy, Check, Hash, ArrowRight, Wrench, 
  ChevronDown, RefreshCw, Edit2, Clock,
  FileInput, FileOutput, Equal
} from 'lucide-react'
import { Button } from '../ui/button'
import { motion, AnimatePresence } from 'framer-motion'
import type { MessageData } from './Message'
import type { MessageContent } from '@agentc/realtime-core'

export interface MessageFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * The message data
   */
  message: MessageData
  /**
   * Callback for editing message
   */
  onEdit?: () => void
  /**
   * Callback for regenerating message
   */
  onRegenerate?: () => void
  /**
   * Whether to show timestamp
   */
  showTimestamp?: boolean
}

interface ToolCallDisplayProps {
  toolCalls: NonNullable<MessageData['toolCalls']>
  className?: string
}

const ToolCallDisplay: React.FC<ToolCallDisplayProps> = ({
  toolCalls,
  className
}) => {
  const [expandedTools, setExpandedTools] = React.useState<Set<string>>(new Set())
  
  const toggleTool = (toolId: string) => {
    setExpandedTools(prev => {
      const next = new Set(prev)
      if (next.has(toolId)) {
        next.delete(toolId)
      } else {
        next.add(toolId)
      }
      return next
    })
  }
  
  return (
    <div className={cn(
      "rounded-lg border border-border/50 bg-muted/30 p-2 space-y-1",
      className
    )}>
      {toolCalls.map((tool) => {
        const isExpanded = expandedTools.has(tool.id)
        
        return (
          <div key={tool.id} className="rounded bg-background/50">
            <button
              className="flex items-center justify-between w-full px-2 py-1.5 text-left hover:bg-muted/50 transition-colors"
              onClick={() => toggleTool(tool.id)}
              aria-expanded={isExpanded}
              aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${tool.name} details`}
            >
              <div className="flex items-center gap-2">
                <Wrench className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs font-medium">
                  {tool.name}
                </span>
              </div>
              <ChevronDown className={cn(
                "h-3 w-3 text-muted-foreground transition-transform",
                isExpanded && "rotate-180"
              )} />
            </button>
            
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="overflow-hidden"
                >
                  <div className="px-2 pb-2 space-y-2">
                    {/* Parameters */}
                    {tool.input && (
                      <div className="pl-5">
                        <span className="text-xs text-muted-foreground">Parameters:</span>
                        <pre className="mt-1 p-2 bg-muted/30 rounded text-xs overflow-auto">
                          {JSON.stringify(tool.input, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )
      })}
    </div>
  )
}

export const MessageFooter = React.forwardRef<HTMLDivElement, MessageFooterProps>(
  ({ className, message, onEdit, onRegenerate, showTimestamp = true, ...props }, ref) => {
    const [copied, setCopied] = React.useState(false)
    const [showToolCalls, setShowToolCalls] = React.useState(false)
    
    const handleCopy = React.useCallback(() => {
      // Extract text content for copying
      let textContent = ''
      if (message.content === null) {
        textContent = ''
      } else if (typeof message.content === 'string') {
        textContent = message.content
      } else if (Array.isArray(message.content)) {
        // Extract text from content parts
        textContent = message.content
          .filter((part: any) => part.type === 'text')
          .map((part: any) => part.text || '')
          .join('\n')
      }
      
      navigator.clipboard.writeText(textContent)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }, [message.content])
    
    const hasToolCalls = message.toolCalls && message.toolCalls.length > 0
    const hasTokenCounts = message.metadata?.inputTokens || message.metadata?.outputTokens
    const isUserMessage = message.role === 'user'
    const isAssistantMessage = message.role === 'assistant'
    
    // Format timestamp
    const formattedTime = React.useMemo(() => {
      if (!showTimestamp || !message.timestamp) return null
      try {
        const date = new Date(message.timestamp)
        if (isNaN(date.getTime())) return null
        return date.toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
      } catch {
        return null
      }
    }, [message.timestamp, showTimestamp])
    
    // Always show footer for assistant messages (for copy button)
    // For other messages, only show if there's content to display
    if (!isAssistantMessage && !hasTokenCounts && !hasToolCalls && !onRegenerate && !isUserMessage && !formattedTime) {
      return null
    }
    
    return (
      <div 
        ref={ref}
        className={cn("space-y-2", className)}
        {...props}
      >
        {/* Primary Footer Row */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {/* Token Counts */}
          {hasTokenCounts && (
            <>
              {/* Input Tokens */}
              {message.metadata?.inputTokens !== undefined && (
                <div className="flex items-center gap-1" title="Input tokens">
                  <FileInput className="h-3 w-3" />
                  <span>{message.metadata.inputTokens.toLocaleString()}</span>
                </div>
              )}
              
              {/* Output Tokens */}
              {message.metadata?.outputTokens !== undefined && (
                <div className="flex items-center gap-1" title="Output tokens">
                  <FileOutput className="h-3 w-3" />
                  <span>{message.metadata.outputTokens.toLocaleString()}</span>
                </div>
              )}
              
              {/* Total Tokens */}
              {(message.metadata?.inputTokens !== undefined || message.metadata?.outputTokens !== undefined) && (
                <div className="flex items-center gap-1" title="Total tokens">
                  <Equal className="h-3 w-3" />
                  <span>
                    {(
                      (message.metadata?.inputTokens || 0) + 
                      (message.metadata?.outputTokens || 0)
                    ).toLocaleString()}
                  </span>
                </div>
              )}
            </>
          )}
          
          {/* Tool Calls Toggle */}
          {hasToolCalls && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 gap-1 -ml-2"
              onClick={() => setShowToolCalls(!showToolCalls)}
              aria-label={`${showToolCalls ? 'Hide' : 'Show'} tool calls`}
            >
              <Wrench className="h-3 w-3" />
              <span>{message.toolCalls!.length} tool{message.toolCalls!.length > 1 ? 's' : ''}</span>
              <ChevronDown className={cn(
                "h-3 w-3 transition-transform",
                showToolCalls && "rotate-180"
              )} />
            </Button>
          )}
          
          {/* Action Buttons and Timestamp - aligned on same line */}
          <div className="flex items-center gap-2 ml-auto">
            {/* Timestamp */}
            {formattedTime && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formattedTime}
              </span>
            )}
            
            {/* Copy Button */}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 gap-1"
              onClick={handleCopy}
              aria-label={copied ? "Content copied" : "Copy message content"}
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy</span>
                </>
              )}
            </Button>
            
            {/* Edit Button (for user messages on hover) */}
            {isUserMessage && onEdit && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={onEdit}
                aria-label="Edit message"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </Button>
            )}
            
            {/* Regenerate Button (for assistant messages) */}
            {!isUserMessage && onRegenerate && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 gap-1"
                onClick={onRegenerate}
                aria-label="Regenerate response"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Regenerate</span>
              </Button>
            )}
          </div>
        </div>
        
        {/* Expandable Tool Calls */}
        <AnimatePresence>
          {showToolCalls && hasToolCalls && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <ToolCallDisplay 
                toolCalls={message.toolCalls!}
                className="mt-2"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }
)

MessageFooter.displayName = 'MessageFooter'