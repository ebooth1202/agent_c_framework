"use client"

/**
 * TipTap v2 Compatible Version of MarkdownEditor.tsx
 * 
 * Key changes from v3:
 * - Import statements are cleaner
 * - No immediatelyRender prop (v2 doesn't have it)
 * - Better Next.js compatibility out of the box
 */
import * as React from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import Placeholder from '@tiptap/extension-placeholder';
import Typography from '@tiptap/extension-typography';
import { cn } from '../../lib/utils';
import type { MarkdownEditorProps } from './types';
import { getMarkdownExtensions, keyboardShortcuts } from './markdownExtensions';
import { codeHighlightStyles } from './codeHighlightTheme';
import { editorStyles } from './editorStyles';

/**
 * MarkdownEditor component - v2 Compatible
 * 
 * This version works with TipTap v2 which has better Next.js compatibility
 * and doesn't have the module resolution issues of v3.
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
    onKeyDown,
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
      // Note: v2 doesn't have immediatelyRender prop
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
          // Custom key handler takes precedence
          if (onKeyDown) {
            const handled = onKeyDown(event);
            if (handled) {
              return true;
            }
          }
          
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
        {/* Inject editor and syntax highlighting styles */}
        <style dangerouslySetInnerHTML={{ __html: editorStyles + codeHighlightStyles }} />
      </div>
    );
  }
);

MarkdownEditor.displayName = 'MarkdownEditor';

// Export keyboard shortcuts for documentation
export { MarkdownEditor, keyboardShortcuts };