'use client'

import * as React from 'react'
import { cn } from '../../../lib/utils'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '../../ui/button'
import { Check, Copy } from 'lucide-react'

export interface MarkdownRendererProps {
  /**
   * The markdown content to render
   */
  content: string
  
  /**
   * Optional CSS classes to apply to the prose wrapper
   */
  className?: string
  
  /**
   * Optional role context for accessibility
   */
  ariaLabel?: string
  
  /**
   * Whether to enable code copy buttons (default: true)
   */
  enableCodeCopy?: boolean
  
  /**
   * Compact mode for thoughts/condensed displays (default: false)
   * - Reduces spacing
   * - Smaller text sizes
   * - Simplified code blocks
   */
  compact?: boolean
}

/**
 * Shared markdown renderer for all chat message types
 * Provides consistent markdown rendering across regular messages,
 * thoughts, and media content with full feature support including:
 * - Code blocks with copy functionality
 * - Tables with GFM support
 * - Lists, headings, links, blockquotes
 * - Images
 * - Full accessibility support
 */
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className,
  ariaLabel = 'Markdown content',
  enableCodeCopy = true,
  compact = false
}) => {
  const [copiedCode, setCopiedCode] = React.useState<string | null>(null)
  
  // Handle code copy
  const handleCopyCode = React.useCallback((code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedCode(code)
      setTimeout(() => setCopiedCode(null), 2000)
    }).catch(err => {
      console.error('Failed to copy code:', err)
    })
  }, [])
  
  // Markdown components configuration
  const markdownComponents = React.useMemo(() => ({
    // Code blocks with copy functionality
    code({ inline, className: codeClassName, children, ...props }: any) {
      const match = /language-(\w+)/.exec(codeClassName || '')
      const language = match ? match[1] : ''
      const codeString = String(children).replace(/\n$/, '')
      
      if (!inline && language) {
        return (
          <div className={cn(
            "relative group w-full overflow-hidden",
            compact ? "my-2" : "my-4"
          )}>
            {enableCodeCopy && (
              <div className="absolute right-2 top-2 z-10">
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "px-2 opacity-0 group-hover:opacity-100 transition-opacity",
                    compact ? "h-6 text-xs" : "h-8"
                  )}
                  onClick={() => handleCopyCode(codeString)}
                  aria-label={`Copy ${language} code`}
                >
                  {copiedCode === codeString ? (
                    <>
                      <Check className={cn(compact ? "h-2.5 w-2.5 mr-0.5" : "h-3 w-3 mr-1")} aria-hidden="true" />
                      <span className="text-xs">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className={cn(compact ? "h-2.5 w-2.5 mr-0.5" : "h-3 w-3 mr-1")} aria-hidden="true" />
                      <span className="text-xs">Copy</span>
                    </>
                  )}
                </Button>
              </div>
            )}
            <pre 
              className={cn(
                "bg-muted rounded-md overflow-x-auto w-full",
                compact ? "p-2" : "p-4"
              )}
              aria-label={`Code block in ${language}`}
            >
              <code className={cn(
                "font-mono block min-w-0",
                compact ? "text-xs" : "text-sm"
              )} {...props}>
                {codeString}
              </code>
            </pre>
          </div>
        )
      }
      
      // Inline code
      return (
        <code 
          className={cn(
            "bg-muted rounded font-mono",
            compact ? "px-1 py-0.5 text-xs" : "px-1.5 py-0.5 text-sm"
          )}
          {...props}
        >
          {children}
        </code>
      )
    },
    
    // Custom paragraph styling
    p({ children }: any) {
      return (
        <p className={cn(
          "last:mb-0 leading-relaxed",
          compact ? "mb-2" : "mb-3"
        )}>
          {children}
        </p>
      )
    },
    
    // Lists
    ul({ children }: any) {
      return (
        <ul className={cn(
          "list-disc pl-6 space-y-1",
          compact ? "mb-2" : "mb-3"
        )}>
          {children}
        </ul>
      )
    },
    ol({ children }: any) {
      return (
        <ol className={cn(
          "list-decimal pl-6 space-y-1",
          compact ? "mb-2" : "mb-3"
        )}>
          {children}
        </ol>
      )
    },
    
    // Headings
    h1({ children }: any) {
      return (
        <h1 className={cn(
          "font-bold",
          compact ? "text-lg mb-2" : "text-2xl mb-3"
        )}>
          {children}
        </h1>
      )
    },
    h2({ children }: any) {
      return (
        <h2 className={cn(
          "font-semibold",
          compact ? "text-base mb-1.5" : "text-xl mb-2"
        )}>
          {children}
        </h2>
      )
    },
    h3({ children }: any) {
      return (
        <h3 className={cn(
          "font-semibold",
          compact ? "text-sm mb-1.5" : "text-lg mb-2"
        )}>
          {children}
        </h3>
      )
    },
    h4({ children }: any) {
      return (
        <h4 className={cn(
          "font-semibold",
          compact ? "text-sm mb-1" : "text-base mb-2"
        )}>
          {children}
        </h4>
      )
    },
    h5({ children }: any) {
      return (
        <h5 className={cn(
          "font-semibold",
          compact ? "text-xs mb-1" : "text-sm mb-1"
        )}>
          {children}
        </h5>
      )
    },
    h6({ children }: any) {
      return (
        <h6 className={cn(
          "font-medium",
          compact ? "text-xs mb-1" : "text-sm mb-1"
        )}>
          {children}
        </h6>
      )
    },
    
    // Links
    a({ href, children }: any) {
      return (
        <a 
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
          aria-label={`External link: ${children}`}
        >
          {children}
        </a>
      )
    },
    
    // Blockquotes
    blockquote({ children }: any) {
      return (
        <blockquote className={cn(
          "border-l-4 border-muted pl-4 py-1 text-muted-foreground",
          compact ? "my-2" : "my-3"
        )}>
          {children}
        </blockquote>
      )
    },
    
    // Horizontal rule
    hr() {
      return <hr className={cn(
        "border-border",
        compact ? "my-2" : "my-4"
      )} />
    },
    
    // Tables (with GFM)
    table({ children }: any) {
      return (
        <div className={cn(
          "overflow-x-auto",
          compact ? "my-2" : "my-3"
        )}>
          <table className="min-w-full divide-y divide-border">
            {children}
          </table>
        </div>
      )
    },
    thead({ children }: any) {
      return <thead className="bg-muted/30">{children}</thead>
    },
    tbody({ children }: any) {
      return <tbody className="divide-y divide-border">{children}</tbody>
    },
    th({ children, align }: any) {
      return (
        <th 
          className={cn(
            "text-left font-medium uppercase tracking-wider",
            compact ? "px-2 py-1 text-xs" : "px-3 py-2 text-xs"
          )}
          style={{ textAlign: align || 'left' }}
        >
          {children}
        </th>
      )
    },
    td({ children, align }: any) {
      return (
        <td 
          className={cn(
            compact ? "px-2 py-1 text-xs" : "px-3 py-2 text-sm"
          )}
          style={{ textAlign: align || 'left' }}
        >
          {children}
        </td>
      )
    },
    
    // Strong/emphasis
    strong({ children }: any) {
      return <strong className="font-semibold">{children}</strong>
    },
    em({ children }: any) {
      return <em className="italic">{children}</em>
    },
    
    // Images
    img({ src, alt }: any) {
      return (
        <img 
          src={src} 
          alt={alt || 'Image'} 
          className={cn(
            "max-w-full h-auto rounded-lg",
            compact ? "my-2" : "my-3"
          )}
        />
      )
    }
  }), [compact, enableCodeCopy, copiedCode, handleCopyCode])
  
  return (
    <div 
      className={cn(
        "prose max-w-none overflow-hidden",
        compact ? "prose-sm" : "prose-sm",
        "prose-headings:text-foreground",
        "prose-p:text-foreground",
        "prose-strong:text-foreground",
        "prose-ul:text-foreground prose-ol:text-foreground",
        "prose-blockquote:text-muted-foreground",
        "prose-code:text-foreground prose-code:bg-muted",
        "prose-pre:bg-muted prose-pre:overflow-x-auto",
        "prose-th:text-muted-foreground",
        "prose-td:text-foreground",
        "prose-a:text-primary",
        className
      )}
      role="article"
      aria-label={ariaLabel}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownRenderer
