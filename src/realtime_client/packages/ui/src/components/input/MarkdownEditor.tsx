import * as React from "react"
import { forwardRef, useImperativeHandle, useRef, useState, useCallback, useEffect } from "react"
import { cn } from "../../lib/utils"
import { Bold, Italic, Code, List, ListOrdered, Link2, Quote, Hash } from "lucide-react"
import { Button } from "../ui/button"
import { Separator } from "../ui/separator"
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip"

export interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  onSubmit?: () => void
  placeholder?: string
  disabled?: boolean
  maxLength?: number
  className?: string
  showToolbar?: boolean
  toolbarPosition?: 'top' | 'bottom'
  autoFocus?: boolean
}

export interface MarkdownEditorRef {
  focus: () => void
  blur: () => void
  clear: () => void
  insertText: (text: string) => void
  wrapSelection: (before: string, after: string) => void
}

interface FormatButton {
  icon: React.ReactNode
  label: string
  shortcut?: string
  action: () => void
}

const MarkdownEditor = forwardRef<MarkdownEditorRef, MarkdownEditorProps>(
  ({ 
    value, 
    onChange, 
    onSubmit,
    placeholder = "Type your message...",
    disabled = false,
    maxLength,
    className,
    showToolbar = true,
    toolbarPosition = 'top',
    autoFocus = false
  }, ref) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const [selection, setSelection] = useState({ start: 0, end: 0 })

    // Track selection changes
    const handleSelectionChange = useCallback(() => {
      if (textareaRef.current) {
        setSelection({
          start: textareaRef.current.selectionStart,
          end: textareaRef.current.selectionEnd
        })
      }
    }, [])

    // Insert text at current cursor position
    const insertText = useCallback((text: string) => {
      if (!textareaRef.current) return
      
      const textarea = textareaRef.current
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const newValue = value.substring(0, start) + text + value.substring(end)
      
      onChange(newValue)
      
      // Restore cursor position
      setTimeout(() => {
        textarea.selectionStart = start + text.length
        textarea.selectionEnd = start + text.length
        textarea.focus()
      }, 0)
    }, [value, onChange])

    // Wrap selected text with markdown syntax
    const wrapSelection = useCallback((before: string, after: string = before) => {
      if (!textareaRef.current) return
      
      const textarea = textareaRef.current
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selectedText = value.substring(start, end)
      
      // Check if already wrapped
      const beforeStart = Math.max(0, start - before.length)
      const afterEnd = Math.min(value.length, end + after.length)
      const isWrapped = 
        value.substring(beforeStart, start) === before && 
        value.substring(end, afterEnd) === after
      
      if (isWrapped) {
        // Unwrap
        const newValue = 
          value.substring(0, beforeStart) + 
          selectedText + 
          value.substring(afterEnd)
        onChange(newValue)
        
        setTimeout(() => {
          textarea.selectionStart = beforeStart
          textarea.selectionEnd = beforeStart + selectedText.length
          textarea.focus()
        }, 0)
      } else {
        // Wrap
        const newValue = 
          value.substring(0, start) + 
          before + selectedText + after + 
          value.substring(end)
        onChange(newValue)
        
        setTimeout(() => {
          textarea.selectionStart = start + before.length
          textarea.selectionEnd = start + before.length + selectedText.length
          textarea.focus()
        }, 0)
      }
    }, [value, onChange])

    // Format buttons configuration
    const formatButtons: FormatButton[] = [
      {
        icon: <Bold className="h-4 w-4" />,
        label: "Bold",
        shortcut: "Ctrl+B",
        action: () => wrapSelection('**', '**')
      },
      {
        icon: <Italic className="h-4 w-4" />,
        label: "Italic",
        shortcut: "Ctrl+I",
        action: () => wrapSelection('*', '*')
      },
      {
        icon: <Code className="h-4 w-4" />,
        label: "Code",
        shortcut: "Ctrl+`",
        action: () => wrapSelection('`', '`')
      },
      {
        icon: <Link2 className="h-4 w-4" />,
        label: "Link",
        shortcut: "Ctrl+K",
        action: () => {
          const selectedText = value.substring(selection.start, selection.end) || 'link text'
          insertText(`[${selectedText}](url)`)
        }
      },
      {
        icon: <Quote className="h-4 w-4" />,
        label: "Quote",
        action: () => {
          const textarea = textareaRef.current
          if (!textarea) return
          
          const start = textarea.selectionStart
          const lineStart = value.lastIndexOf('\n', start - 1) + 1
          const newValue = value.substring(0, lineStart) + '> ' + value.substring(lineStart)
          onChange(newValue)
          
          setTimeout(() => {
            textarea.selectionStart = start + 2
            textarea.selectionEnd = start + 2
            textarea.focus()
          }, 0)
        }
      },
      {
        icon: <List className="h-4 w-4" />,
        label: "Bullet List",
        action: () => insertText('\n- ')
      },
      {
        icon: <ListOrdered className="h-4 w-4" />,
        label: "Numbered List",
        action: () => insertText('\n1. ')
      },
      {
        icon: <Hash className="h-4 w-4" />,
        label: "Heading",
        action: () => {
          const textarea = textareaRef.current
          if (!textarea) return
          
          const start = textarea.selectionStart
          const lineStart = value.lastIndexOf('\n', start - 1) + 1
          const newValue = value.substring(0, lineStart) + '## ' + value.substring(lineStart)
          onChange(newValue)
          
          setTimeout(() => {
            textarea.selectionStart = start + 3
            textarea.selectionEnd = start + 3
            textarea.focus()
          }, 0)
        }
      }
    ]

    // Handle keyboard shortcuts
    const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Submit on Enter (without shift)
      if (e.key === 'Enter' && !e.shiftKey && onSubmit) {
        e.preventDefault()
        onSubmit()
        return
      }

      // Markdown shortcuts
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'b':
            e.preventDefault()
            wrapSelection('**', '**')
            break
          case 'i':
            e.preventDefault()
            wrapSelection('*', '*')
            break
          case '`':
            e.preventDefault()
            wrapSelection('`', '`')
            break
          case 'k':
            e.preventDefault()
            formatButtons.find(b => b.label === 'Link')?.action()
            break
        }
      }
    }, [onSubmit, wrapSelection, formatButtons])

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      focus: () => textareaRef.current?.focus(),
      blur: () => textareaRef.current?.blur(),
      clear: () => onChange(''),
      insertText,
      wrapSelection
    }), [onChange, insertText, wrapSelection])

    // Auto-focus on mount
    useEffect(() => {
      if (autoFocus && textareaRef.current) {
        textareaRef.current.focus()
      }
    }, [autoFocus])

    // Toolbar component
    const Toolbar = () => (
      <div className="flex items-center gap-1 p-1 border-b">
        <TooltipProvider>
          {formatButtons.map((button, index) => (
            <React.Fragment key={button.label}>
              {index === 3 && <Separator orientation="vertical" className="h-6 mx-1" />}
              {index === 5 && <Separator orientation="vertical" className="h-6 mx-1" />}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={button.action}
                    disabled={disabled}
                    className="h-8 w-8 p-0"
                    type="button"
                  >
                    {button.icon}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{button.label}</p>
                  {button.shortcut && (
                    <p className="text-xs text-muted-foreground">{button.shortcut}</p>
                  )}
                </TooltipContent>
              </Tooltip>
            </React.Fragment>
          ))}
        </TooltipProvider>
        
        {maxLength && (
          <div className="ml-auto mr-2 text-xs text-muted-foreground">
            {value.length} / {maxLength}
          </div>
        )}
      </div>
    )

    return (
      <div className={cn("w-full rounded-md border bg-background", className)}>
        {showToolbar && toolbarPosition === 'top' && <Toolbar />}
        
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onSelect={handleSelectionChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            maxLength={maxLength}
            className={cn(
              "w-full resize-none bg-transparent px-3 py-2",
              "placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-0",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "min-h-[80px]",
              "font-mono text-sm"
            )}
            aria-label="Markdown editor"
            aria-describedby={maxLength ? "char-count" : undefined}
          />
          
          {/* Preview hint */}
          {value && (
            <div className="absolute bottom-2 right-2 text-xs text-muted-foreground opacity-50">
              Markdown supported
            </div>
          )}
        </div>
        
        {showToolbar && toolbarPosition === 'bottom' && <Toolbar />}
      </div>
    )
  }
)

MarkdownEditor.displayName = "MarkdownEditor"

export { MarkdownEditor }