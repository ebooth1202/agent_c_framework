import * as React from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import Placeholder from '@tiptap/extension-placeholder';
import Typography from '@tiptap/extension-typography';
import { cn } from '../../lib/utils';
import type { MarkdownEditorProps } from './types';
import { getMarkdownExtensions, keyboardShortcuts } from './markdownExtensions';
import { codeHighlightStyles } from './codeHighlightTheme';

/**
 * MarkdownEditor component
 * 
 * A Tiptap-based markdown editor with live markdown rendering and keyboard shortcuts.
 * 
 * Features:
 * - Automatic markdown syntax conversion as you type
 * - Keyboard shortcuts for formatting (Cmd/Ctrl+B for bold, etc.)
 * - Controlled component with value/onChange props
 * - Plain text output despite rich formatting display
 * 
 * Markdown patterns:
 * - **text** → bold
 * - *text* or _text_ → italic
 * - `text` → inline code
 * - ~~text~~ → strikethrough
 * - # Heading 1, ## Heading 2, ### Heading 3
 * - -, * for bullet lists, 1. for numbered lists
 * - > for blockquotes
 * - --- for horizontal rules
 * - ```language → code block with syntax highlighting
 * 
 * Image handling:
 * - Paste images from clipboard (Ctrl/Cmd+V)
 * - Drag and drop image files
 * - Shows upload progress placeholder
 * - Automatic markdown image syntax insertion
 * 
 * Keyboard shortcuts:
 * - Cmd/Ctrl+B: Bold
 * - Cmd/Ctrl+I: Italic
 * - Cmd/Ctrl+E: Inline code
 * - Cmd/Ctrl+Alt+C: Code block
 * - Cmd/Ctrl+Shift+S: Strikethrough
 * - Cmd/Ctrl+K: Add/edit link
 * - Cmd/Ctrl+Z: Undo
 * - Cmd/Ctrl+Shift+Z: Redo
 * - Cmd/Ctrl+Enter: Submit
 */
const MarkdownEditor = React.forwardRef<HTMLDivElement, MarkdownEditorProps>(
  ({ 
    value = '', 
    onChange, 
    placeholder = 'How can I help you today?',
    onSubmit,
    disabled = false,
    className,
    enableSmartPaste = true,
    maxImageSize,
    onImageUpload,
    onImageUploadStart,
    onImageUploadComplete,
    onImageUploadError,
    ...props 
  }, ref) => {
    
    // Initialize Tiptap editor with markdown extensions and shortcuts
    const editor = useEditor({
      extensions: [
        // Get all markdown extensions with InputRules and keyboard shortcuts
        ...getMarkdownExtensions({ 
          placeholder, 
          onSubmit, 
          disabled,
          enableSmartPaste,
          maxImageSize,
          onImageUpload,
          onImageUploadStart,
          onImageUploadComplete,
          onImageUploadError,
        }),
        // Placeholder extension for empty state
        Placeholder.configure({
          placeholder,
          emptyEditorClass: 'is-editor-empty',
        }),
        // Typography for smart quotes, dashes, and ellipsis
        Typography,
      ],
      content: value,
      editable: !disabled,
      onUpdate: ({ editor }) => {
        // Get plain text content and notify parent component
        const text = editor.getText();
        if (onChange) {
          onChange(text);
        }
      },
      editorProps: {
        attributes: {
          class: cn(
            'prose prose-sm max-w-none focus:outline-none',
            'min-h-[100px] p-3',
            // Prose overrides for better markdown display
            'prose-headings:mt-2 prose-headings:mb-1',
            'prose-p:my-1',
            'prose-ul:my-1 prose-ol:my-1',
            'prose-blockquote:my-2',
            'prose-code:before:content-none prose-code:after:content-none',
            'prose-hr:my-4',
            disabled && 'opacity-50 cursor-not-allowed',
            className
          ),
        },
        handleKeyDown: (view, event) => {
          // Handle Cmd/Ctrl+Enter for submit
          if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
            event.preventDefault();
            if (onSubmit && !disabled) {
              const text = editor?.getText() || '';
              onSubmit(text);
            }
            return true;
          }
          return false;
        },
      },
    });

    // Update editor content when value prop changes
    React.useEffect(() => {
      if (editor && value !== editor.getText()) {
        editor.commands.setContent(value);
      }
    }, [value, editor]);

    // Update editor editable state when disabled prop changes
    React.useEffect(() => {
      if (editor) {
        editor.setEditable(!disabled);
      }
    }, [disabled, editor]);

    // Cleanup editor on unmount
    React.useEffect(() => {
      return () => {
        editor?.destroy();
      };
    }, [editor]);

    return (
      <div 
        ref={ref}
        className={cn(
          'relative w-full rounded-md border border-input bg-background',
          'focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2',
          disabled && 'opacity-50',
          className
        )}
        {...props}
      >
        <EditorContent 
          editor={editor}
          className="w-full"
        />
        {/* Inject syntax highlighting styles */}
        <style dangerouslySetInnerHTML={{ __html: codeHighlightStyles }} />
      </div>
    );
  }
);

MarkdownEditor.displayName = 'MarkdownEditor';

// Export keyboard shortcuts for documentation
export { MarkdownEditor, keyboardShortcuts };