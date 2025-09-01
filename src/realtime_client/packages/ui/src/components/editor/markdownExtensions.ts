import { Extension, InputRule } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { createLowlight } from 'lowlight';
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

// Create lowlight instance and register languages
const lowlight = createLowlight();

// Register all the languages we want to support
lowlight.register('javascript', javascript);
lowlight.register('js', javascript); // Alias
lowlight.register('typescript', typescript);
lowlight.register('ts', typescript); // Alias
lowlight.register('python', python);
lowlight.register('py', python); // Alias
lowlight.register('json', json);
lowlight.register('html', html);
lowlight.register('xml', html); // XML uses the same highlighter
lowlight.register('css', css);
lowlight.register('markdown', markdown);
lowlight.register('md', markdown); // Alias
lowlight.register('bash', bash);
lowlight.register('sh', shell);
lowlight.register('shell', shell);
lowlight.register('yaml', yaml);
lowlight.register('yml', yaml); // Alias
lowlight.register('sql', sql);
lowlight.register('dockerfile', dockerfile);
lowlight.register('docker', dockerfile); // Alias

/**
 * Custom Markdown InputRules Extension
 * Provides automatic markdown syntax conversion as users type
 */
const MarkdownInputRules = Extension.create({
  name: 'markdownInputRules',

  addInputRules() {
    return [
      // Bold: **text** → bold text
      new InputRule({
        find: /(?:^|\s)(\*\*|__)([^*_]+)(\*\*|__)$/,
        handler: ({ state: _state, range, match }) => {
          const _attributes = {};
          const start = range.from;
          const end = range.to;
          
          this.editor
            .chain()
            .deleteRange({ from: start, to: end })
            .insertContentAt(start, {
              type: 'text',
              text: match[2],
              marks: [{ type: 'bold' }]
            })
            .run();
        },
      }),

      // Italic: *text* or _text_ → italic text
      new InputRule({
        find: /(?:^|\s)(\*|_)([^*_]+)(\*|_)$/,
        handler: ({ state: _state, range, match }) => {
          const start = range.from;
          const end = range.to;
          
          this.editor
            .chain()
            .deleteRange({ from: start, to: end })
            .insertContentAt(start, {
              type: 'text',
              text: match[2],
              marks: [{ type: 'italic' }]
            })
            .run();
        },
      }),

      // Strikethrough: ~~text~~ → strikethrough text
      new InputRule({
        find: /(?:^|\s)(~~)([^~]+)(~~)$/,
        handler: ({ state: _state, range, match }) => {
          const start = range.from;
          const end = range.to;
          
          this.editor
            .chain()
            .deleteRange({ from: start, to: end })
            .insertContentAt(start, {
              type: 'text',
              text: match[2],
              marks: [{ type: 'strike' }]
            })
            .run();
        },
      }),

      // Inline code: `text` → inline code
      new InputRule({
        find: /(?:^|\s)(`([^`]+)`)$/,
        handler: ({ state: _state, range, match }) => {
          const start = range.from;
          const end = range.to;
          
          this.editor
            .chain()
            .deleteRange({ from: start, to: end })
            .insertContentAt(start, {
              type: 'text',
              text: match[2],
              marks: [{ type: 'code' }]
            })
            .run();
        },
      }),

      // Heading 1: # text → Heading 1
      new InputRule({
        find: /^# $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .setHeading({ level: 1 })
            .run();
        },
      }),

      // Heading 2: ## text → Heading 2
      new InputRule({
        find: /^## $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .setHeading({ level: 2 })
            .run();
        },
      }),

      // Heading 3: ### text → Heading 3
      new InputRule({
        find: /^### $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .setHeading({ level: 3 })
            .run();
        },
      }),

      // Bullet list: - or * → bullet list
      new InputRule({
        find: /^(\*|-) $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .toggleBulletList()
            .run();
        },
      }),

      // Ordered list: 1. → numbered list
      new InputRule({
        find: /^(\d+)\. $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .toggleOrderedList()
            .run();
        },
      }),

      // Blockquote: > → blockquote
      new InputRule({
        find: /^> $/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .toggleBlockquote()
            .run();
        },
      }),

      // Horizontal rule: --- → horizontal rule
      new InputRule({
        find: /^---$/,
        handler: ({ state: _state, range }) => {
          this.editor
            .chain()
            .deleteRange(range)
            .setHorizontalRule()
            .run();
        },
      }),

      // Code block: ```language → code block with language
      new InputRule({
        find: /^```([a-z]*)\s$/,
        handler: ({ state: _state, range, match }) => {
          const language = match[1] || 'plaintext';
          
          this.editor
            .chain()
            .deleteRange(range)
            .setCodeBlock({ language })
            .run();
        },
      }),
    ];
  },
});

/**
 * Custom Keyboard Shortcuts Extension
 * Adds our custom keyboard shortcuts on top of the defaults
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

        // Cancelled
        if (url === null) {
          return false;
        }

        // Empty
        if (url === '') {
          this.editor
            .chain()
            .focus()
            .extendMarkRange('link')
            .unsetLink()
            .run();
          return true;
        }

        // Update link
        this.editor
          .chain()
          .focus()
          .extendMarkRange('link')
          .setLink({ href: url })
          .run();

        return true;
      },
      
      // Cmd/Ctrl+Z → Undo (StarterKit already includes this)
      'Mod-z': () => this.editor.commands.undo(),
      
      // Cmd/Ctrl+Shift+Z → Redo
      'Mod-Shift-z': () => this.editor.commands.redo(),
      'Mod-y': () => this.editor.commands.redo(), // Alternative redo shortcut
    };
  },
});

/**
 * Get configured markdown extensions with keyboard shortcuts
 * @param options - Configuration options for extensions
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
      // Configure individual extensions within StarterKit
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
      // Disable codeBlock from StarterKit as we'll use CodeBlockLowlight
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
 * Get keyboard shortcut reference for documentation
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