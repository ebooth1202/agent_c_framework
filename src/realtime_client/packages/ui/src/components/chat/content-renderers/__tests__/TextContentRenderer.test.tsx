/**
 * TextContentRenderer Component Tests
 * 
 * Tests the refactored TextContentRenderer which delegates to the shared
 * MarkdownRenderer component. This ensures consistent markdown rendering
 * across user, assistant, and system messages.
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TextContentRenderer } from '../TextContentRenderer';

describe('TextContentRenderer', () => {
  
  // ===========================================================================
  // MARKDOWN RENDERER DELEGATION TESTS
  // ===========================================================================
  
  describe('MarkdownRenderer Delegation', () => {
    it('should render content using MarkdownRenderer', () => {
      const { container } = render(
        <TextContentRenderer
          content="# Heading\n\nThis is **bold** text."
          role="assistant"
        />
      );

      // Should render markdown features
      const heading = container.querySelector('h1');
      expect(heading).toBeInTheDocument();
      expect(heading).toHaveTextContent('Heading');
      
      const strong = container.querySelector('strong');
      expect(strong).toBeInTheDocument();
      expect(strong).toHaveTextContent('bold');
    });

    it('should pass content prop to MarkdownRenderer', () => {
      const content = 'Test content with `inline code`';
      const { container } = render(
        <TextContentRenderer content={content} role="user" />
      );

      // Should render the content
      expect(container.textContent).toContain('Test content with');
      
      // Inline code should be rendered
      const code = container.querySelector('code');
      expect(code).toHaveTextContent('inline code');
    });

    it('should use standard mode (compact=false)', () => {
      const { container } = render(
        <TextContentRenderer
          content="# Heading\n\nParagraph"
          role="assistant"
        />
      );

      // Check for standard spacing classes (not compact)
      const heading = container.querySelector('h1');
      expect(heading).toHaveClass('text-2xl'); // Standard size, not compact
      
      const paragraph = container.querySelector('p');
      expect(paragraph).toHaveClass('mb-3'); // Standard margin, not compact
    });

    it('should pass className through to MarkdownRenderer', () => {
      const { container } = render(
        <TextContentRenderer
          content="Test"
          role="user"
          className="custom-class"
        />
      );

      const wrapper = container.querySelector('[role="article"]');
      expect(wrapper).toHaveClass('custom-class');
    });

    it('should NOT enable compact mode', () => {
      const { container } = render(
        <TextContentRenderer
          content="## Heading 2"
          role="assistant"
        />
      );

      // Should use standard heading sizes
      const h2 = container.querySelector('h2');
      expect(h2).toHaveClass('text-xl'); // Standard, not compact (text-base)
    });
  });

  // ===========================================================================
  // ARIA LABEL TESTS
  // ===========================================================================
  
  describe('ARIA Labels', () => {
    it('should set aria-label for user messages', () => {
      const { container } = render(
        <TextContentRenderer content="User message" role="user" />
      );

      const wrapper = container.querySelector('[role="article"]');
      expect(wrapper).toHaveAttribute('aria-label', 'user message with markdown content');
    });

    it('should set aria-label for assistant messages', () => {
      const { container } = render(
        <TextContentRenderer content="Assistant message" role="assistant" />
      );

      const wrapper = container.querySelector('[role="article"]');
      expect(wrapper).toHaveAttribute('aria-label', 'assistant message with markdown content');
    });

    it('should set aria-label for system messages', () => {
      const { container } = render(
        <TextContentRenderer content="System message" role="system" />
      );

      const wrapper = container.querySelector('[role="article"]');
      expect(wrapper).toHaveAttribute('aria-label', 'system message with markdown content');
    });
  });

  // ===========================================================================
  // CONTENT RENDERING TESTS
  // ===========================================================================
  
  describe('Content Rendering', () => {
    it('should render plain text correctly', () => {
      render(<TextContentRenderer content="Plain text" role="user" />);

      expect(screen.getByText('Plain text')).toBeInTheDocument();
    });

    it('should render markdown formatting (bold, italic)', () => {
      const { container } = render(
        <TextContentRenderer
          content="This is **bold** and *italic* text"
          role="assistant"
        />
      );

      const strong = container.querySelector('strong');
      expect(strong).toHaveTextContent('bold');
      
      const em = container.querySelector('em');
      expect(em).toHaveTextContent('italic');
    });

    it('should render code blocks', () => {
      const content = '```javascript\nconst x = 1;\n```';
      const { container } = render(
        <TextContentRenderer content={content} role="assistant" />
      );

      const code = container.querySelector('code');
      expect(code).toHaveTextContent('const x = 1;');
    });

    it('should render lists', () => {
      const content = '- Item 1\n- Item 2\n- Item 3';
      const { container } = render(
        <TextContentRenderer content={content} role="user" />
      );

      const ul = container.querySelector('ul');
      expect(ul).toBeInTheDocument();
      
      const items = ul?.querySelectorAll('li');
      expect(items).toHaveLength(3);
    });

    it('should render links', () => {
      const content = '[Click here](https://example.com)';
      const { container } = render(
        <TextContentRenderer content={content} role="assistant" />
      );

      const link = container.querySelector('a');
      expect(link).toHaveAttribute('href', 'https://example.com');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should render headings', () => {
      const content = '# H1\n## H2\n### H3';
      const { container } = render(
        <TextContentRenderer content={content} role="user" />
      );

      expect(container.querySelector('h1')).toHaveTextContent('H1');
      expect(container.querySelector('h2')).toHaveTextContent('H2');
      expect(container.querySelector('h3')).toHaveTextContent('H3');
    });

    it('should render tables', () => {
      const content = '| Col1 | Col2 |\n|------|------|\n| A    | B    |';
      const { container } = render(
        <TextContentRenderer content={content} role="assistant" />
      );

      const table = container.querySelector('table');
      expect(table).toBeInTheDocument();
      
      const headers = table?.querySelectorAll('th');
      expect(headers).toHaveLength(2);
    });

    it('should render blockquotes', () => {
      const content = '> This is a quote';
      const { container } = render(
        <TextContentRenderer content={content} role="user" />
      );

      const blockquote = container.querySelector('blockquote');
      expect(blockquote).toBeInTheDocument();
      expect(blockquote).toHaveTextContent('This is a quote');
    });
  });

  // ===========================================================================
  // ROLE-BASED BEHAVIOR TESTS
  // ===========================================================================
  
  describe('Role-Based Behavior', () => {
    it('should accept user role', () => {
      const { container } = render(
        <TextContentRenderer content="User message" role="user" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should accept assistant role', () => {
      const { container } = render(
        <TextContentRenderer content="Assistant message" role="assistant" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should accept system role', () => {
      const { container } = render(
        <TextContentRenderer content="System message" role="system" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should use role in aria-label appropriately', () => {
      const { container: userContainer } = render(
        <TextContentRenderer content="Test" role="user" />
      );
      
      const { container: assistantContainer } = render(
        <TextContentRenderer content="Test" role="assistant" />
      );

      const userArticle = userContainer.querySelector('[role="article"]');
      const assistantArticle = assistantContainer.querySelector('[role="article"]');

      expect(userArticle).toHaveAttribute('aria-label', 'user message with markdown content');
      expect(assistantArticle).toHaveAttribute('aria-label', 'assistant message with markdown content');
    });
  });

  // ===========================================================================
  // EDGE CASES TESTS
  // ===========================================================================
  
  describe('Edge Cases', () => {
    it('should handle empty content', () => {
      const { container } = render(
        <TextContentRenderer content="" role="user" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should handle very long content', () => {
      const longContent = 'Lorem ipsum '.repeat(1000);
      const { container } = render(
        <TextContentRenderer content={longContent} role="assistant" />
      );

      expect(container.textContent).toContain('Lorem ipsum');
    });

    it('should handle malformed markdown', () => {
      const malformed = '**Unclosed bold\n\n```\nUnclosed code';
      const { container } = render(
        <TextContentRenderer content={malformed} role="user" />
      );

      // Should not crash
      expect(container.firstChild).toBeInTheDocument();
    });

    it('should handle special characters', () => {
      const special = 'Text with <>&"\'` special chars';
      const { container } = render(
        <TextContentRenderer content={special} role="assistant" />
      );

      expect(container.textContent).toContain('<>&"\'`');
    });

    it('should handle mixed content types', () => {
      const mixed = '# Heading\n\n**Bold** and *italic* with `code` and [link](https://example.com)';
      const { container } = render(
        <TextContentRenderer content={mixed} role="user" />
      );

      expect(container.querySelector('h1')).toBeInTheDocument();
      expect(container.querySelector('strong')).toBeInTheDocument();
      expect(container.querySelector('em')).toBeInTheDocument();
      expect(container.querySelector('code')).toBeInTheDocument();
      expect(container.querySelector('a')).toBeInTheDocument();
    });
  });

  // ===========================================================================
  // CONSISTENCY TESTS
  // ===========================================================================
  
  describe('Consistency Across Roles', () => {
    it('should render identical content for different roles', () => {
      const content = '# Test\n\nThis is **test** content.';
      
      const { container: userContainer } = render(
        <TextContentRenderer content={content} role="user" />
      );
      
      const { container: assistantContainer } = render(
        <TextContentRenderer content={content} role="assistant" />
      );

      // Both should have same markdown structure
      expect(userContainer.querySelector('h1')).toHaveTextContent('Test');
      expect(assistantContainer.querySelector('h1')).toHaveTextContent('Test');
      
      expect(userContainer.querySelector('strong')).toHaveTextContent('test');
      expect(assistantContainer.querySelector('strong')).toHaveTextContent('test');
    });

    it('should use same MarkdownRenderer regardless of role', () => {
      const content = 'Test with `code`';
      
      const { container: userContainer } = render(
        <TextContentRenderer content={content} role="user" />
      );
      
      const { container: systemContainer } = render(
        <TextContentRenderer content={content} role="system" />
      );

      // Both should render code identically
      const userCode = userContainer.querySelector('code');
      const systemCode = systemContainer.querySelector('code');
      
      expect(userCode).toHaveTextContent('code');
      expect(systemCode).toHaveTextContent('code');
      
      // Same styling
      expect(userCode).toHaveClass('bg-muted');
      expect(systemCode).toHaveClass('bg-muted');
    });
  });
});
