/**
 * Tests for Markdown InputRules in TipTap v2
 * Verifies that all markdown transformations work correctly
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { Editor } from '@tiptap/react';
import { getMarkdownExtensions } from './markdownExtensions';

describe('Markdown InputRules', () => {
  let editor: Editor;

  beforeEach(() => {
    // Create a fresh editor instance with markdown extensions
    editor = new Editor({
      extensions: getMarkdownExtensions(),
      content: '<p></p>',
    });
  });

  describe('Inline Marks', () => {
    it('should convert **text** to bold', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('**bold text**');
      
      const html = editor.getHTML();
      expect(html).toContain('<strong>bold text</strong>');
    });

    it('should convert *text* to italic', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('*italic text*');
      
      const html = editor.getHTML();
      expect(html).toContain('<em>italic text</em>');
    });

    it('should convert _text_ to italic', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('_italic text_');
      
      const html = editor.getHTML();
      expect(html).toContain('<em>italic text</em>');
    });

    it('should convert ~~text~~ to strikethrough', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('~~strike text~~');
      
      const html = editor.getHTML();
      expect(html).toContain('<s>strike text</s>');
    });

    it('should convert `text` to inline code', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('`code text`');
      
      const html = editor.getHTML();
      expect(html).toContain('<code>code text</code>');
    });
  });

  describe('Block Elements', () => {
    it('should convert # to heading 1', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('# ');
      
      const html = editor.getHTML();
      expect(html).toContain('<h1>');
    });

    it('should convert ## to heading 2', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('## ');
      
      const html = editor.getHTML();
      expect(html).toContain('<h2>');
    });

    it('should convert ### to heading 3', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('### ');
      
      const html = editor.getHTML();
      expect(html).toContain('<h3>');
    });

    it('should convert - to bullet list', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('- ');
      
      const html = editor.getHTML();
      expect(html).toContain('<ul>');
      expect(html).toContain('<li>');
    });

    it('should convert * to bullet list', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('* ');
      
      const html = editor.getHTML();
      expect(html).toContain('<ul>');
      expect(html).toContain('<li>');
    });

    it('should convert 1. to ordered list', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('1. ');
      
      const html = editor.getHTML();
      expect(html).toContain('<ol>');
      expect(html).toContain('<li>');
    });

    it('should convert > to blockquote', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('> ');
      
      const html = editor.getHTML();
      expect(html).toContain('<blockquote>');
    });

    it('should convert --- to horizontal rule', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('---');
      
      const html = editor.getHTML();
      expect(html).toContain('<hr');
    });

    it('should convert ``` to code block', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('``` ');
      
      const html = editor.getHTML();
      expect(html).toContain('<pre><code');
    });

    it('should convert ```javascript to code block with language', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('```javascript ');
      
      const html = editor.getHTML();
      expect(html).toContain('<pre><code');
      expect(html).toMatch(/language-javascript|data-language="javascript"/);
    });
  });

  describe('Edge Cases', () => {
    it('should properly handle italic without missing first character', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('*foo*');
      
      const html = editor.getHTML();
      expect(html).toContain('<em>foo</em>');
      expect(html).not.toContain('*');
    });

    it('should not throw errors when applying bold', () => {
      expect(() => {
        editor.commands.setContent('<p></p>');
        editor.commands.insertContent('**test**');
      }).not.toThrow();
    });

    it('should not throw InvalidCharacterError for headers', () => {
      expect(() => {
        editor.commands.setContent('<p></p>');
        editor.commands.insertContent('# ');
      }).not.toThrow();
    });

    it('should handle multiple markdown elements in sequence', () => {
      editor.commands.setContent('<p></p>');
      editor.commands.insertContent('**bold** and *italic* and `code`');
      
      const html = editor.getHTML();
      expect(html).toContain('<strong>bold</strong>');
      expect(html).toContain('<em>italic</em>');
      expect(html).toContain('<code>code</code>');
    });
  });

  afterEach(() => {
    editor.destroy();
  });
});