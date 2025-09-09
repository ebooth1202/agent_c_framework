'use client'

import * as React from 'react'
import { cn } from '../../../lib/utils'
import { CheckCircle, XCircle, ChevronRight, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ContentPart } from '@agentc/realtime-core'
import { ContentPartRenderer } from '../MessageContentRenderer'

export interface ToolResultContentRendererProps {
  /**
   * ID of the tool use this result corresponds to
   */
  toolUseId: string
  /**
   * The result content - can be string or nested ContentPart array
   */
  content: string | ContentPart[]
  /**
   * Whether this result represents an error
   */
  isError?: boolean
  /**
   * The role context for nested content rendering
   */
  role?: 'user' | 'assistant' | 'system'
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Renders tool execution results with success/error indication
 * Can contain nested content that needs recursive rendering
 */
export const ToolResultContentRenderer: React.FC<ToolResultContentRendererProps> = ({
  toolUseId,
  content,
  isError = false,
  role = 'assistant',
  className
}) => {
  // Auto-expand successful results, collapse errors by default
  const [isExpanded, setIsExpanded] = React.useState(!isError)
  
  // Determine styling based on success/error state
  const statusColor = isError 
    ? "border-destructive bg-destructive/10 dark:bg-destructive/5" 
    : "border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/30"
  
  const statusIcon = isError 
    ? <XCircle className="h-4 w-4 text-destructive" aria-hidden="true" />
    : <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" aria-hidden="true" />
  
  const statusText = isError ? "Tool Error" : "Tool Result"
  
  const hoverColor = isError 
    ? "hover:bg-destructive/20 dark:hover:bg-destructive/10" 
    : "hover:bg-green-100/50 dark:hover:bg-green-900/30"
  
  const iconColor = isError 
    ? "text-destructive" 
    : "text-green-600 dark:text-green-400"
  
  const textColor = isError 
    ? "text-destructive dark:text-destructive" 
    : "text-green-900 dark:text-green-100"
  
  // Get a preview of the content for collapsed state
  const contentPreview = React.useMemo(() => {
    if (typeof content === 'string') {
      const preview = content.trim()
      return preview.length > 60 ? `${preview.substring(0, 57)}...` : preview
    }
    if (Array.isArray(content)) {
      return `${content.length} content part${content.length !== 1 ? 's' : ''}`
    }
    return 'Empty result'
  }, [content])
  
  // Check if content is empty
  const hasContent = React.useMemo(() => {
    if (typeof content === 'string') return content.trim().length > 0
    if (Array.isArray(content)) return content.length > 0
    return false
  }, [content])
  
  return (
    <div 
      className={cn(
        "rounded-lg border transition-colors",
        statusColor,
        className
      )}
      role={isError ? "alert" : "region"}
      aria-label={`${statusText} for tool invocation`}
      aria-expanded={isExpanded}
    >
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          "flex items-center justify-between w-full px-3 py-2 text-left transition-colors",
          hoverColor,
          "focus-visible:outline-none focus-visible:ring-2",
          "focus-visible:ring-ring focus-visible:ring-inset rounded-t-lg"
        )}
        aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${statusText.toLowerCase()}`}
      >
        <div className="flex items-center gap-2 min-w-0">
          {statusIcon}
          <span className={cn("text-sm font-medium", textColor)}>
            {statusText}
          </span>
          <span 
            className="text-xs text-muted-foreground font-mono"
            title={toolUseId}
          >
            (ID: {toolUseId.slice(0, 8)}...)
          </span>
          {!isExpanded && hasContent && (
            <span className="text-xs text-muted-foreground truncate">
              - {contentPreview}
            </span>
          )}
        </div>
        <ChevronRight 
          className={cn(
            "h-4 w-4 transition-transform shrink-0",
            iconColor,
            isExpanded && "rotate-90"
          )}
          aria-hidden="true"
        />
      </button>
      
      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3">
              {hasContent ? (
                <div 
                  className="bg-background/60 rounded p-3 border border-border/50"
                  role="region"
                  aria-label="Tool result content"
                >
                  {typeof content === 'string' ? (
                    // String content - display as preformatted text
                    <pre className="text-sm whitespace-pre-wrap font-mono">
                      {content}
                    </pre>
                  ) : (
                    // Array of ContentPart - recursively render each part
                    <div className="space-y-2">
                      {content.map((part, index) => (
                        <ContentPartRenderer
                          key={`tool-result-${toolUseId}-${index}`}
                          part={part}
                          role={role}
                          index={index}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                // Empty result
                <div className="bg-background/60 rounded p-3 border border-border/50">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <AlertCircle className="h-4 w-4" aria-hidden="true" />
                    <span className="text-sm italic">
                      {isError ? 'No error details available' : 'No result data'}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Error indicator for better visibility */}
              {isError && (
                <div className="mt-2 text-xs text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" aria-hidden="true" />
                  <span>This tool execution failed. Check the error details above.</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ToolResultContentRenderer