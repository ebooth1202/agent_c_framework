'use client'

import * as React from 'react'
import { cn } from '../../../lib/utils'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '../../ui/button'
import { Check, Copy } from 'lucide-react'

export interface TextContentRendererProps {
  /**
   * The text content to render with markdown support
   */
  content: string
  /**
   * The role of the message sender
   */
  role: 'user' | 'assistant' | 'system'
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Renders text content with full markdown support
 * Includes code blocks with syntax highlighting and copy functionality
 */
export const TextContentRenderer: React.FC<TextContentRendererProps> = ({
  content,
  role,
  className
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
  
  // For user messages, render as plain text with line breaks
  if (role === 'user') {
    return (
      <div 
        className={cn(
          "whitespace-pre-wrap break-words",
          className
        )}
        aria-label="User message text"
      >
        {content}
      </div>
    )
  }
  
  // Markdown components configuration for assistant/system messages
  const markdownComponents = {
    // Code blocks with copy functionality
    code({ inline, className: codeClassName, children, ...props }: any) {
      const match = /language-(\w+)/.exec(codeClassName || '')
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
                aria-label={`Copy ${language} code`}
              >
                {copiedCode === codeString ? (
                  <>
                    <Check className="h-3 w-3 mr-1" aria-hidden="true" />
                    <span className="text-xs">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 mr-1" aria-hidden="true" />
                    <span className="text-xs">Copy</span>
                  </>
                )}
              </Button>
            </div>
            <pre 
              className="bg-muted rounded-md p-4 overflow-x-auto"
              aria-label={`Code block in ${language}`}
            >
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
    h4({ children }: any) {
      return <h4 className="text-base font-semibold mb-2">{children}</h4>
    },
    h5({ children }: any) {
      return <h5 className="text-sm font-semibold mb-1">{children}</h5>
    },
    h6({ children }: any) {
      return <h6 className="text-sm font-medium mb-1">{children}</h6>
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
        <blockquote className="border-l-4 border-muted pl-4 py-1 my-3 text-muted-foreground">
          {children}
        </blockquote>
      )
    },
    
    // Horizontal rule
    hr() {
      return <hr className="my-4 border-border" />
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
      return <thead className="bg-muted/30">{children}</thead>
    },
    tbody({ children }: any) {
      return <tbody className="divide-y divide-border">{children}</tbody>
    },
    th({ children, align }: any) {
      return (
        <th 
          className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider"
          style={{ textAlign: align || 'left' }}
        >
          {children}
        </th>
      )
    },
    td({ children, align }: any) {
      return (
        <td 
          className="px-3 py-2 text-sm"
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
          className="max-w-full h-auto rounded-lg my-3"
        />
      )
    }
  }
  
  return (
    <div 
      className={cn(
        "prose prose-sm max-w-none",
        "prose-headings:text-foreground",
        "prose-p:text-foreground",
        "prose-strong:text-foreground",
        "prose-ul:text-foreground prose-ol:text-foreground",
        "prose-blockquote:text-muted-foreground",
        "prose-code:text-foreground prose-code:bg-muted",
        "prose-pre:bg-muted",
        "prose-th:text-muted-foreground",
        "prose-td:text-foreground",
        "prose-a:text-primary",
        className
      )}
      role="article"
      aria-label={`${role} message with markdown content`}
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

export default TextContentRenderer