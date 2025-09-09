'use client'

import * as React from 'react'
import { cn } from '../../lib/utils'
import { 
  User, Bot, Brain, AlertCircle, Clock, 
  ChevronRight, Loader2, Check, Copy
} from 'lucide-react'
import { Button } from '../ui/button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion, AnimatePresence } from 'framer-motion'
import type { Message as SDKMessage } from '@agentc/realtime-core'

export interface MessageData extends Omit<SDKMessage, 'timestamp'> {
  id?: string  // Optional ID for keying
  timestamp: Date | string
  status?: 'sending' | 'sent' | 'error'
  error?: string
  isThought?: boolean  // Flag for thought messages
  metadata?: {
    inputTokens?: number
    outputTokens?: number
  }
  toolCalls?: Array<{
    id: string
    type: 'function'
    function: {
      name: string
      arguments: any
    }
    results?: any
  }>
}

export interface MessageProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * The message data to display
   */
  message: MessageData
  /**
   * Show timestamp
   */
  showTimestamp?: boolean
  /**
   * Message is currently streaming
   */
  isStreaming?: boolean
  /**
   * Custom avatar component
   */
  avatarComponent?: React.ReactNode
  /**
   * Callback for message actions
   */
  onEdit?: (id: string, content: string) => void
  /**
   * Show footer with metadata
   */
  showFooter?: boolean
}

// Thought message component
interface ThoughtMessageProps {
  message: MessageData
  isStreaming?: boolean
}

const ThoughtMessage: React.FC<ThoughtMessageProps> = ({
  message,
  isStreaming = false
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false)
  const [copied, setCopied] = React.useState(false)
  
  // Extract first line for preview
  const firstLine = React.useMemo(() => {
    const lines = message.content.split('\n')
    const first = lines[0] || ''
    return first.length > 80 ? `${first.slice(0, 77)}...` : first
  }, [message.content])
  
  const handleCopy = React.useCallback(() => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [message.content])
  
  return (
    <div className={cn(
      "rounded-lg border border-border/50 my-2",
      "transition-all duration-200 ease-out",
      "hover:bg-muted/20 hover:border-border/70"
    )}>
      <button
        className={cn(
          "group/thought flex w-full items-center justify-between",
          "gap-4 rounded-lg px-3 py-2 h-[2.625rem]",
          "text-muted-foreground hover:text-foreground",
          "transition-colors duration-200 cursor-pointer",
          "focus-visible:outline-none focus-visible:ring-2",
          "focus-visible:ring-ring focus-visible:ring-offset-2"
        )}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? "Collapse thought" : "Expand thought"}
      >
        <div className="flex items-center gap-2 min-w-0">
          <Brain className="h-4 w-4 shrink-0 text-muted-foreground/70" />
          <span className="text-sm leading-tight truncate">
            {isExpanded ? "Thought process" : firstLine}
          </span>
        </div>
        
        <div className="flex items-center gap-1.5 shrink-0">
          {isStreaming && (
            <Loader2 className="h-3 w-3 animate-spin text-muted-foreground/70" />
          )}
          <ChevronRight className={cn(
            "h-4 w-4 transition-transform duration-200",
            isExpanded && "rotate-90"
          )} />
        </div>
      </button>
      
      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div 
              className="px-3 pb-3 text-sm text-muted-foreground"
              style={{
                maskImage: "linear-gradient(transparent 0%, black 1rem, black calc(100% - 1rem), transparent 100%)"
              }}
            >
              <div className="prose prose-sm prose-muted max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
              
              {/* Thought Footer */}
              {message.metadata?.outputTokens && (
                <div className="mt-3 pt-2 border-t border-border/30 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground/70">
                    {message.metadata.outputTokens} tokens
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-xs"
                    onClick={handleCopy}
                  >
                    {copied ? (
                      <>
                        <Check className="h-3 w-3 mr-1" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Import MessageFooter from separate file
import { MessageFooter } from './MessageFooter'

const Message = React.forwardRef<HTMLDivElement, MessageProps>(
  ({ 
    className, 
    message,
    showTimestamp = true,
    isStreaming = false,
    avatarComponent,
    onEdit,
    showFooter = true,
    ...props 
  }, ref) => {
    const [copiedCode, setCopiedCode] = React.useState<string | null>(null)
    const [isEditing, setIsEditing] = React.useState(false)
    const [editContent, setEditContent] = React.useState(message.content)
    
    // Check for thought messages
    if (message.isThought || message.role === 'assistant (thought)') {
      return (
        <ThoughtMessage 
          message={message}
          isStreaming={isStreaming}
        />
      )
    }
    
    const isUser = message.role === 'user'
    const isAssistant = message.role === 'assistant'
    const isError = message.status === 'error'
    
    // Handle code copy
    const handleCopyCode = React.useCallback((code: string) => {
      navigator.clipboard.writeText(code).then(() => {
        setCopiedCode(code)
        setTimeout(() => setCopiedCode(null), 2000)
      })
    }, [])
    
    // Format timestamp
    const formattedTime = React.useMemo(() => {
      if (!showTimestamp || !message.timestamp) return null
      const date = message.timestamp instanceof Date 
        ? message.timestamp 
        : new Date(message.timestamp)
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    }, [message.timestamp, showTimestamp])
    
    // Avatar component
    const Avatar = () => {
      if (avatarComponent) return <>{avatarComponent}</>
      
      if (isUser) {
        return (
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
        )
      }
      
      return (
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      )
    }
    
    // Markdown components configuration
    const markdownComponents = {
      // Code blocks 
      code({ inline, className, children, ...props }: any) {
        const match = /language-(\w+)/.exec(className || '')
        const language = match ? match[1] : ''
        const codeString = String(children).replace(/\n$/, '')
        
        if (!inline && language) {
          return (
            <div className="relative group my-4">
              <div className="absolute right-2 top-2 z-10">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => handleCopyCode(codeString)}
                >
                  {copiedCode === codeString ? (
                    <>
                      <Check className="h-3 w-3 mr-1" />
                      <span className="text-xs">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3 mr-1" />
                      <span className="text-xs">Copy</span>
                    </>
                  )}
                </Button>
              </div>
              <pre className="bg-muted rounded-md p-4 overflow-x-auto">
                <code className="text-sm font-mono" {...props}>
                  {codeString}
                </code>
              </pre>
            </div>
          )
        }
        
        // Inline code
        return (
          <code 
            className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono"
            {...props}
          >
            {children}
          </code>
        )
      },
      // Custom paragraph styling
      p({ children }: any) {
        return <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>
      },
      // Lists
      ul({ children }: any) {
        return <ul className="list-disc pl-6 mb-3 space-y-1">{children}</ul>
      },
      ol({ children }: any) {
        return <ol className="list-decimal pl-6 mb-3 space-y-1">{children}</ol>
      },
      // Headings
      h1({ children }: any) {
        return <h1 className="text-2xl font-bold mb-3">{children}</h1>
      },
      h2({ children }: any) {
        return <h2 className="text-xl font-semibold mb-2">{children}</h2>
      },
      h3({ children }: any) {
        return <h3 className="text-lg font-semibold mb-2">{children}</h3>
      },
      // Links
      a({ href, children }: any) {
        return (
          <a 
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {children}
          </a>
        )
      },
      // Blockquotes
      blockquote({ children }: any) {
        return (
          <blockquote className="border-l-4 border-muted pl-4 py-1 my-3 text-muted-foreground">
            {children}
          </blockquote>
        )
      },
      // Tables (with GFM)
      table({ children }: any) {
        return (
          <div className="overflow-x-auto my-3">
            <table className="min-w-full divide-y divide-border">
              {children}
            </table>
          </div>
        )
      },
      thead({ children }: any) {
        return <thead className="bg-accent/20">{children}</thead>
      },
      th({ children }: any) {
        return (
          <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">
            {children}
          </th>
        )
      },
      td({ children }: any) {
        return <td className="px-3 py-2 text-sm">{children}</td>
      }
    }
    
    // Render content
    const renderContent = () => {
      if (isUser) {
        // Plain text for user messages
        return (
          <div className="whitespace-pre-wrap break-words">
            {isEditing ? (
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault()
                    if (onEdit && message.id) {
                      onEdit(message.id, editContent)
                      setIsEditing(false)
                    }
                  } else if (e.key === 'Escape') {
                    e.preventDefault()
                    setEditContent(message.content)
                    setIsEditing(false)
                  }
                }}
                className="w-full bg-transparent border-none outline-none resize-none min-h-[80px]"
                autoFocus
              />
            ) : (
              message.content
            )}
          </div>
        )
      }
      
      // Markdown for assistant messages
      return (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {message.content}
        </ReactMarkdown>
      )
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          "group relative flex gap-3 py-2",
          isUser && "flex-row-reverse",
          className
        )}
        role="article"
        aria-label={`Message from ${isUser ? 'user' : 'assistant'}`}
        {...props}
      >
        {/* Avatar */}
        <div className="flex-shrink-0">
          <Avatar />
        </div>
        
        {/* Message content */}
        <div className={cn(
          "flex-1 max-w-[75ch] space-y-2",
          isUser && "flex flex-col items-end"
        )}>
          {/* Message bubble */}
          <div
            className={cn(
              "relative rounded-xl px-4 py-2.5 transition-all duration-200",
              isUser 
                ? "bg-muted" 
                : "bg-background",
              isError && "bg-destructive/10 border border-destructive",
              isStreaming && "after:content-[''] after:inline-block after:w-1.5 after:h-4 after:ml-1 after:bg-current after:animate-pulse after:rounded-full"
            )}
          >
            {/* Error message */}
            {isError && message.error && (
              <div className="flex items-start gap-2 mb-2 text-destructive">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span className="text-sm">{message.error}</span>
              </div>
            )}
            
            {/* Main content */}
            <div className={cn(
              "text-[0.9375rem] leading-6 tracking-tight",
              isUser ? "text-foreground" : "prose prose-sm max-w-none"
            )}>
              {renderContent()}
            </div>
            
            {/* Edit controls for user messages */}
            {isEditing && isUser && (
              <div className="flex items-center gap-2 mt-2">
                <Button
                  size="sm"
                  onClick={() => {
                    if (onEdit && message.id) {
                      onEdit(message.id, editContent)
                      setIsEditing(false)
                    }
                  }}
                  disabled={!editContent.trim()}
                >
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setEditContent(message.content)
                    setIsEditing(false)
                  }}
                >
                  Cancel
                </Button>
                <span className="ml-auto text-xs text-muted-foreground">
                  ⌘+Enter to save, Esc to cancel
                </span>
              </div>
            )}
            
            {/* User message hover actions */}
            {isUser && !isEditing && (
              <div className="absolute -bottom-1 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </Button>
              </div>
            )}
          </div>
          
          {/* Message Footer for assistant messages */}
          {isAssistant && showFooter && !isStreaming && (
            <MessageFooter 
              message={message}
            />
          )}
          
          {/* Message Footer for user messages */}
          {isUser && showFooter && !isStreaming && !isEditing && (
            <MessageFooter 
              message={message}
              onEdit={() => setIsEditing(true)}
            />
          )}
          
          {/* Metadata */}
          <div className="flex items-center gap-2 px-1">
            {/* Timestamp */}
            {formattedTime && showTimestamp && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formattedTime}
              </span>
            )}
            
            {/* Status indicator */}
            {message.status === 'sending' && (
              <span className="text-xs text-muted-foreground">
                Sending...
              </span>
            )}
            {message.status === 'sent' && !isError && (
              <Check className="h-3 w-3 text-muted-foreground" />
            )}
          </div>
        </div>
      </div>
    )
  }
)

Message.displayName = 'Message'

export { Message }