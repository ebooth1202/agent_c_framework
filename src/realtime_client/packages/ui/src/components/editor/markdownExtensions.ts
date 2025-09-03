/**
 * TipTap v2 Compatible Version of markdownExtensions.ts
 * 
 * Key changes from v3:
 * - Import statements are simpler (no module resolution issues)
 * - All extensions work with standard imports
 * - Better Next.js compatibility
 */
import { Extension, markInputRule, InputRule } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import { SmartPasteExtension, type SmartPasteOptions } from './SmartPasteExtension';

// Import language modules from highlight.js
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import python from 'highlight.js/lib/languages/python';
import json from 'highlight.js/lib/languages/json';
import html from 'highlight.js/lib/languages/xml';
import css from 'highlight.js/lib/languages/css';
import markdown from 'highlight.js/lib/languages/markdown';
import bash from 'highlight.js/lib/languages/bash';
import shell from 'highlight.js/lib/languages/shell';
import yaml from 'highlight.js/lib/languages/yaml';
import sql from 'highlight.js/lib/languages/sql';
import dockerfile from 'highlight.js/lib/languages/dockerfile';

// Create lowlight instance with common languages
const lowlight = createLowlight(common);

// Register additional languages
lowlight.register('dockerfile', dockerfile);
lowlight.register('docker', dockerfile); // Alias

/**
 * Custom Markdown InputRules Extension - v2 Compatible
 * Uses proper TipTap v2 InputRule patterns with transaction handling
 */
const MarkdownInputRules = Extension.create({
  name: 'markdownInputRules',

  addInputRules() {
    return [
      // Bold: **text** → bold text
      markInputRule({
        find: /(\*\*|__)([^*_]+)(\*\*|__)$/,
        type: this.editor.schema.marks.bold,
      }),

      // Italic: *text* or _text_ → italic text
      // Fixed to properly capture single asterisk/underscore
      markInputRule({
        find: /(^|[^*_])([*_])([^*_]+?)\2$/,
        type: this.editor.schema.marks.italic,
      }),

      // Strikethrough: ~~text~~ → strikethrough text
      markInputRule({
        find: /~~([^~]+)~~$/,
        type: this.editor.schema.marks.strike,
      }),

      // Inline code: `text` → inline code
      markInputRule({
        find: /`([^`]+)`$/,
        type: this.editor.schema.marks.code,
      }),

      // Heading 1: # text → Heading 1
      new InputRule({
        find: /^#\s$/,
        handler: ({ state, range, commands }) => {
          commands.deleteRange(range);
          commands.setHeading({ level: 1 });
          return;
        },
      }),

      // Heading 2: ## text → Heading 2  
      new InputRule({
        find: /^##\s$/,
        handler: ({ state, range, commands }) => {
          commands.deleteRange(range);
          commands.setHeading({ level: 2 });
          return;
        },
      }),

      // Heading 3: ### text → Heading 3
      new InputRule({
        find: /^###\s$/,
        handler: ({ state, range, commands }) => {
          commands.deleteRange(range);
          commands.setHeading({ level: 3 });
          return;
        },
      }),

      // Bullet list: - or * → bullet list
      new InputRule({
        find: /^[-*]\s$/,
        handler: ({ commands, range }) => {
          commands.deleteRange(range);
          commands.toggleBulletList();
          return;
        },
      }),

      // Ordered list: 1. → numbered list
      new InputRule({
        find: /^(\d+)\.\s$/,
        handler: ({ commands, range }) => {
          commands.deleteRange(range);
          commands.toggleOrderedList();
          return;
        },
      }),

      // Blockquote: > → blockquote
      new InputRule({
        find: /^>\s$/,
        handler: ({ commands, range }) => {
          commands.deleteRange(range);
          commands.toggleBlockquote();
          return;
        },
      }),

      // Horizontal rule: --- → horizontal rule
      new InputRule({
        find: /^(-{3,})$/,
        handler: ({ commands, range }) => {
          commands.deleteRange(range);
          commands.setHorizontalRule();
          return;
        },
      }),

      // Code block: ```language → code block with language
      new InputRule({
        find: /^```([a-z]*)\s$/,
        handler: ({ commands, range, match }) => {
          const language = match[1] || 'plaintext';
          commands.deleteRange(range);
          commands.setCodeBlock({ language });
          return;
        },
      }),
    ];
  },
});

/**
 * Custom Keyboard Shortcuts Extension - v2 Compatible
 */
const KeyboardShortcuts = Extension.create({
  name: 'customKeyboardShortcuts',

  addKeyboardShortcuts() {
    return {
      // Cmd/Ctrl+B → Toggle bold
      'Mod-b': () => this.editor.commands.toggleBold(),
      'Mod-B': () => this.editor.commands.toggleBold(),
      
      // Cmd/Ctrl+I → Toggle italic
      'Mod-i': () => this.editor.commands.toggleItalic(),
      'Mod-I': () => this.editor.commands.toggleItalic(),
      
      // Cmd/Ctrl+Shift+S → Toggle strikethrough
      'Mod-Shift-s': () => this.editor.commands.toggleStrike(),
      'Mod-Shift-S': () => this.editor.commands.toggleStrike(),
      
      // Cmd/Ctrl+E → Toggle inline code
      'Mod-e': () => this.editor.commands.toggleCode(),
      'Mod-E': () => this.editor.commands.toggleCode(),
      
      // Cmd/Ctrl+Alt+C → Toggle code block
      'Mod-Alt-c': () => this.editor.commands.toggleCodeBlock(),
      'Mod-Alt-C': () => this.editor.commands.toggleCodeBlock(),
      
      // Cmd/Ctrl+K → Add/edit link
      'Mod-k': () => {
        const previousUrl = this.editor.getAttributes('link').href;
        const url = window.prompt('URL', previousUrl);

        if (url === null) {
          return false;
        }

        if (url === '') {
          this.editor
            .chain()
            .focus()
            .extendMarkRange('link')
            .unsetLink()
            .run();
          return true;
        }

        this.editor
          .chain()
          .focus()
          .extendMarkRange('link')
          .setLink({ href: url })
          .run();

        return true;
      },
      
      // Cmd/Ctrl+Z → Undo
      'Mod-z': () => this.editor.commands.undo(),
      
      // Cmd/Ctrl+Shift+Z → Redo
      'Mod-Shift-z': () => this.editor.commands.redo(),
      'Mod-y': () => this.editor.commands.redo(),
    };
  },
});

/**
 * Get configured markdown extensions - v2 Compatible
 */
export function getMarkdownExtensions(options: {
  placeholder?: string;
  onSubmit?: (text: string) => void;
  disabled?: boolean;
  enableSmartPaste?: boolean;
  maxImageSize?: number;
  onImageUpload?: (file: File) => Promise<string>;
  onImageUploadStart?: (file: File) => void;
  onImageUploadComplete?: (url: string) => void;
  onImageUploadError?: (error: Error) => void;
} = {}) {
  return [
    // StarterKit bundles most of what we need
    StarterKit.configure({
      bold: {
        HTMLAttributes: {
          class: 'font-bold',
        },
      },
      italic: {
        HTMLAttributes: {
          class: 'italic',
        },
      },
      strike: {
        HTMLAttributes: {
          class: 'line-through',
        },
      },
      code: {
        HTMLAttributes: {
          class: 'bg-muted px-1 py-0.5 rounded font-mono text-sm',
        },
      },
      heading: {
        levels: [1, 2, 3],
        HTMLAttributes: {
          1: { class: 'text-2xl font-bold' },
          2: { class: 'text-xl font-semibold' },
          3: { class: 'text-lg font-semibold' },
        },
      },
      bulletList: {
        HTMLAttributes: {
          class: 'list-disc list-inside ml-4',
        },
      },
      orderedList: {
        HTMLAttributes: {
          class: 'list-decimal list-inside ml-4',
        },
      },
      listItem: {
        HTMLAttributes: {
          class: 'ml-2',
        },
      },
      blockquote: {
        HTMLAttributes: {
          class: 'border-l-4 border-muted pl-4 italic',
        },
      },
      horizontalRule: {
        HTMLAttributes: {
          class: 'border-t border-border my-4',
        },
      },
      paragraph: {
        HTMLAttributes: {
          class: 'leading-relaxed',
        },
      },
      // Disable default codeBlock as we use CodeBlockLowlight
      codeBlock: false,
    }),

    // Enhanced code block with syntax highlighting
    CodeBlockLowlight.configure({
      lowlight,
      defaultLanguage: 'plaintext',
      HTMLAttributes: {
        class: 'not-prose',
      },
    }),

    // Link extension (not in StarterKit)
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: 'text-primary underline hover:text-primary/80',
      },
    }),

    // Custom keyboard shortcuts
    KeyboardShortcuts,

    // Custom markdown input rules
    MarkdownInputRules,
    
    // Smart paste handler for images (if enabled)
    ...(options.enableSmartPaste !== false ? [
      SmartPasteExtension.configure({
        maxFileSize: options.maxImageSize || 10 * 1024 * 1024, // 10MB default
        uploadImage: options.onImageUpload || undefined,
        onUploadStart: options.onImageUploadStart,
        onUploadComplete: options.onImageUploadComplete,
        onUploadError: options.onImageUploadError,
      } as SmartPasteOptions),
    ] : []),
  ];
}

/**
 * Keyboard shortcut reference (same as v3)
 */
export const keyboardShortcuts = {
  formatting: [
    { keys: 'Cmd/Ctrl+B', description: 'Toggle bold' },
    { keys: 'Cmd/Ctrl+I', description: 'Toggle italic' },
    { keys: 'Cmd/Ctrl+E', description: 'Toggle inline code' },
    { keys: 'Cmd/Ctrl+Alt+C', description: 'Toggle code block' },
    { keys: 'Cmd/Ctrl+Shift+S', description: 'Toggle strikethrough' },
    { keys: 'Cmd/Ctrl+K', description: 'Add/edit link' },
  ],
  history: [
    { keys: 'Cmd/Ctrl+Z', description: 'Undo' },
    { keys: 'Cmd/Ctrl+Shift+Z', description: 'Redo' },
  ],
  actions: [
    { keys: 'Cmd/Ctrl+Enter', description: 'Submit' },
  ],
  markdown: [
    { syntax: '**text**', description: 'Bold text' },
    { syntax: '*text* or _text_', description: 'Italic text' },
    { syntax: '`text`', description: 'Inline code' },
    { syntax: '~~text~~', description: 'Strikethrough text' },
    { syntax: '# ', description: 'Heading 1' },
    { syntax: '## ', description: 'Heading 2' },
    { syntax: '### ', description: 'Heading 3' },
    { syntax: '- or * ', description: 'Bullet list' },
    { syntax: '1. ', description: 'Numbered list' },
    { syntax: '> ', description: 'Blockquote' },
    { syntax: '---', description: 'Horizontal rule' },
    { syntax: '```language ', description: 'Code block with syntax highlighting' },
  ],
};