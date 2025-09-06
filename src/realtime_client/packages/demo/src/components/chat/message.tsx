import * as React from 'react'
import { cn } from '@/lib/utils'
import { Check, Copy, User, Bot, AlertCircle, Clock } from 'lucide-react'
import { Button } from '@agentc/realtime-ui'

// Note: These imports will work once react-markdown and react-syntax-highlighter are installed
// For now, we'll create fallback components
let ReactMarkdown: any
let SyntaxHighlighter: any
let remarkGfm: any

// Attempt to import markdown libraries
try {
  ReactMarkdown = require('react-markdown').default
  remarkGfm = require('remark-gfm').default
  const { Prism } = require('react-syntax-highlighter')
  const { vscDarkPlus } = require('react-syntax-highlighter/dist/esm/styles/prism')
  SyntaxHighlighter = { Prism, style: vscDarkPlus }
} catch {
  // Fallback if libraries aren't installed yet
  ReactMarkdown = null
  SyntaxHighlighter = null
  remarkGfm = null
}

// Extend the SDK Message type with additional client-side properties
import type { Message as SDKMessage } from '@agentc/realtime-core'

export interface MessageData extends Omit<SDKMessage, 'timestamp'> {
  id?: string  // Optional ID for keying
  timestamp: Date | string
  status?: 'sending' | 'sent' | 'error'
  error?: string
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
}

const Message = React.forwardRef<HTMLDivElement, MessageProps>(
  ({ 
    className, 
    message,
    showTimestamp = true,
    isStreaming = false,
    avatarComponent,
    ...props 
  }, ref) => {
    const [copiedCode, setCopiedCode] = React.useState<string | null>(null)
    const isUser = message.role === 'user'
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
    const markdownComponents = ReactMarkdown ? {
      // Code blocks with syntax highlighting
      code({ node, inline, className, children, ...props }: any) {
        const match = /language-(\w+)/.exec(className || '')
        const language = match ? match[1] : ''
        const codeString = String(children).replace(/\n$/, '')
        
        if (!inline && SyntaxHighlighter) {
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
              <SyntaxHighlighter.Prism
                language={language || 'text'}
                style={SyntaxHighlighter.style}
                PreTag="div"
                className="rounded-md text-sm"
                {...props}
              >
                {codeString}
              </SyntaxHighlighter.Prism>
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
        return <thead className="bg-muted/50">{children}</thead>
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
    } : {}
    
    // Render content
    const renderContent = () => {
      if (!ReactMarkdown || isUser) {
        // Plain text for user messages or when markdown isn't available
        return (
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>
        )
      }
      
      // Markdown for assistant messages
      return (
        <ReactMarkdown
          remarkPlugins={remarkGfm ? [remarkGfm] : []}
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
          "flex gap-3",
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
          "flex-1 space-y-1",
          isUser && "flex flex-col items-end"
        )}>
          {/* Message bubble */}
          <div
            className={cn(
              "rounded-lg px-4 py-2 max-w-[80%] relative",
              isUser 
                ? "bg-primary text-primary-foreground" 
                : "bg-muted",
              isError && "bg-destructive/10 border border-destructive",
              isStreaming && "after:content-[''] after:inline-block after:w-1 after:h-4 after:ml-1 after:bg-current after:animate-pulse"
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
              "text-sm",
              isUser && "text-primary-foreground"
            )}>
              {renderContent()}
            </div>
          </div>
          
          {/* Metadata */}
          <div className="flex items-center gap-2 px-1">
            {/* Timestamp */}
            {formattedTime && (
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