import { describe, it, expect, beforeEach } from 'vitest';
import { Editor } from '@tiptap/core';
import { getMarkdownExtensions } from '../src/components/editor/markdownExtensions';

describe('Markdown Extensions InputRules', () => {
  let editor: Editor;

  beforeEach(() => {
    editor = new Editor({
      extensions: getMarkdownExtensions(),
      content: '',
    });
  });

  afterEach(() => {
    editor.destroy();
  });

  describe('Bold InputRule', () => {
    it('should convert **text** to bold', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('**bold**');
      
      // The bold mark should be applied
      const html = editor.getHTML();
      expect(html).toContain('<strong>');
      expect(html).toContain('bold');
    });
  });

  describe('Italic InputRule', () => {
    it('should convert *text* to italic', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('*italic*');
      
      // The italic mark should be applied
      const html = editor.getHTML();
      expect(html).toContain('<em>');
      expect(html).toContain('italic');
    });
  });

  describe('Header InputRules', () => {
    it('should convert # to heading 1', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('# ');
      editor.commands.insertContent('Heading 1');
      
      const html = editor.getHTML();
      expect(html).toContain('<h1');
      expect(html).toContain('Heading 1');
    });

    it('should convert ## to heading 2', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('## ');
      editor.commands.insertContent('Heading 2');
      
      const html = editor.getHTML();
      expect(html).toContain('<h2');
      expect(html).toContain('Heading 2');
    });
  });

  describe('List InputRules', () => {
    it('should convert - to bullet list', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('- ');
      editor.commands.insertContent('List item');
      
      const html = editor.getHTML();
      expect(html).toContain('<ul>');
      expect(html).toContain('<li>');
      expect(html).toContain('List item');
    });

    it('should convert 1. to ordered list', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('1. ');
      editor.commands.insertContent('First item');
      
      const html = editor.getHTML();
      expect(html).toContain('<ol>');
      expect(html).toContain('<li>');
      expect(html).toContain('First item');
    });
  });

  describe('Code InputRules', () => {
    it('should convert `text` to inline code', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('`code`');
      
      const html = editor.getHTML();
      expect(html).toContain('<code>');
      expect(html).toContain('code');
    });

    it('should convert ```language to code block', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('```javascript ');
      editor.commands.insertContent('const x = 1;');
      
      const html = editor.getHTML();
      expect(html).toContain('<pre>');
      expect(html).toContain('<code');
      expect(html).toContain('const x = 1;');
    });
  });

  describe('Blockquote InputRule', () => {
    it('should convert > to blockquote', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('> ');
      editor.commands.insertContent('Quote text');
      
      const html = editor.getHTML();
      expect(html).toContain('<blockquote>');
      expect(html).toContain('Quote text');
    });
  });

  describe('Horizontal Rule InputRule', () => {
    it('should convert --- to horizontal rule', () => {
      editor.commands.setContent('');
      editor.commands.insertContent('--- ');
      
      const html = editor.getHTML();
      expect(html).toContain('<hr>');
    });
  });
});