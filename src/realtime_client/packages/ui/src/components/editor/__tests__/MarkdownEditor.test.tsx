import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MarkdownEditor } from '../MarkdownEditor';
// TODO: Uncomment when jest-axe is installed
// import { axe, toHaveNoViolations } from 'jest-axe';

// TODO: Uncomment when jest-axe is installed
// expect.extend(toHaveNoViolations);

describe('MarkdownEditor', () => {
  const user = userEvent.setup();
  
  const defaultProps = {
    value: '',
    onChange: vi.fn(),
    placeholder: 'Type your message...',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the editor', () => {
      render(<MarkdownEditor {...defaultProps} />);
      const editor = screen.getByRole('textbox');
      expect(editor).toBeInTheDocument();
    });

    it('should display placeholder text', () => {
      render(<MarkdownEditor {...defaultProps} />);
      expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    });

    it('should display initial value', () => {
      render(<MarkdownEditor {...defaultProps} value="Initial content" />);
      expect(screen.getByText('Initial content')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <MarkdownEditor {...defaultProps} className="custom-editor" />
      );
      expect(container.firstChild).toHaveClass('custom-editor');
    });
  });

  describe('Text Input', () => {
    it('should handle text input', async () => {
      const onChange = vi.fn();
      render(<MarkdownEditor {...defaultProps} onChange={onChange} />);
      
      const editor = screen.getByRole('textbox');
      await user.type(editor, 'Hello world');
      
      await waitFor(() => {
        expect(onChange).toHaveBeenCalled();
      });
    });

    it('should handle paste events', async () => {
      const onChange = vi.fn();
      render(<MarkdownEditor {...defaultProps} onChange={onChange} />);
      
      const editor = screen.getByRole('textbox');
      const pasteData = 'Pasted content';
      
      await user.click(editor);
      await user.paste(pasteData);
      
      await waitFor(() => {
        expect(onChange).toHaveBeenCalled();
      });
    });
  });

  describe('Markdown Formatting', () => {
    it('should apply bold formatting', async () => {
      render(<MarkdownEditor {...defaultProps} value="Select this text" />);
      
      const boldButton = screen.getByRole('button', { name: /bold/i });
      await user.click(boldButton);
      
      // Check that bold markdown syntax is applied
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('**')
        );
      });
    });

    it('should apply italic formatting', async () => {
      render(<MarkdownEditor {...defaultProps} value="Select this text" />);
      
      const italicButton = screen.getByRole('button', { name: /italic/i });
      await user.click(italicButton);
      
      // Check that italic markdown syntax is applied
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('*')
        );
      });
    });

    it('should insert links', async () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const linkButton = screen.getByRole('button', { name: /link/i });
      await user.click(linkButton);
      
      // Should show link dialog
      const urlInput = await screen.findByLabelText(/url/i);
      await user.type(urlInput, 'https://example.com');
      
      const insertButton = screen.getByRole('button', { name: /insert/i });
      await user.click(insertButton);
      
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('[')
        );
      });
    });

    it('should insert code blocks', async () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const codeButton = screen.getByRole('button', { name: /code block/i });
      await user.click(codeButton);
      
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('```')
        );
      });
    });
  });

  describe('Toolbar', () => {
    it('should display formatting toolbar', () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: /bold/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /italic/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /link/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /code/i })).toBeInTheDocument();
    });

    it('should hide toolbar when showToolbar is false', () => {
      render(<MarkdownEditor {...defaultProps} showToolbar={false} />);
      
      expect(screen.queryByRole('button', { name: /bold/i })).not.toBeInTheDocument();
    });

    it('should disable toolbar buttons when editor is disabled', () => {
      render(<MarkdownEditor {...defaultProps} disabled />);
      
      const boldButton = screen.getByRole('button', { name: /bold/i });
      expect(boldButton).toBeDisabled();
    });
  });

  describe('Preview Mode', () => {
    it('should toggle preview mode', async () => {
      render(<MarkdownEditor {...defaultProps} value="# Heading\n**Bold text**" />);
      
      const previewButton = screen.getByRole('button', { name: /preview/i });
      await user.click(previewButton);
      
      // Should render markdown as HTML
      const heading = await screen.findByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Heading');
      
      const boldText = screen.getByText('Bold text');
      expect(boldText.tagName).toBe('STRONG');
    });

    it('should switch back to edit mode', async () => {
      render(<MarkdownEditor {...defaultProps} value="# Heading" />);
      
      const previewButton = screen.getByRole('button', { name: /preview/i });
      await user.click(previewButton);
      
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);
      
      // Should show editor again
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should support Ctrl+B for bold', async () => {
      render(<MarkdownEditor {...defaultProps} value="text" />);
      
      const editor = screen.getByRole('textbox');
      await user.click(editor);
      await user.keyboard('{Control>}b{/Control}');
      
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('**')
        );
      });
    });

    it('should support Ctrl+I for italic', async () => {
      render(<MarkdownEditor {...defaultProps} value="text" />);
      
      const editor = screen.getByRole('textbox');
      await user.click(editor);
      await user.keyboard('{Control>}i{/Control}');
      
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('*')
        );
      });
    });

    it('should support Tab for indentation', async () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const editor = screen.getByRole('textbox');
      await user.click(editor);
      await user.keyboard('{Tab}');
      
      await waitFor(() => {
        expect(defaultProps.onChange).toHaveBeenCalledWith(
          expect.stringContaining('  ')
        );
      });
    });
  });

  describe('Accessibility', () => {
    // TODO: Uncomment when jest-axe is installed
    it.skip('should have no accessibility violations', async () => {
      // const { container } = render(<MarkdownEditor {...defaultProps} />);
      // const results = await axe(container);
      // expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels', () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const editor = screen.getByRole('textbox');
      expect(editor).toHaveAttribute('aria-label', 'Markdown editor');
      
      const toolbar = screen.getByRole('toolbar');
      expect(toolbar).toHaveAttribute('aria-label', 'Formatting toolbar');
    });

    it('should support keyboard navigation in toolbar', async () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      // Tab to toolbar
      await user.tab();
      const boldButton = screen.getByRole('button', { name: /bold/i });
      expect(boldButton).toHaveFocus();
      
      // Arrow navigation between toolbar buttons
      await user.keyboard('{ArrowRight}');
      const italicButton = screen.getByRole('button', { name: /italic/i });
      expect(italicButton).toHaveFocus();
    });

    it('should announce formatting changes to screen readers', async () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const boldButton = screen.getByRole('button', { name: /bold/i });
      await user.click(boldButton);
      
      // Check for live region announcement
      const announcement = screen.getByRole('status');
      expect(announcement).toHaveTextContent(/bold formatting applied/i);
    });

    it('should have descriptive button labels', () => {
      render(<MarkdownEditor {...defaultProps} />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName();
        expect(button).toHaveAttribute('aria-label');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error state', () => {
      render(<MarkdownEditor {...defaultProps} error="Invalid markdown syntax" />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('Invalid markdown syntax');
    });

    it('should apply error styling', () => {
      const { container } = render(
        <MarkdownEditor {...defaultProps} error="Error" />
      );
      
      const editor = container.querySelector('[role="textbox"]');
      expect(editor).toHaveClass('border-destructive');
    });
  });

  describe('Character Limit', () => {
    it('should display character count', () => {
      render(<MarkdownEditor {...defaultProps} maxLength={100} value="Hello" />);
      
      expect(screen.getByText('5 / 100')).toBeInTheDocument();
    });

    it('should prevent input beyond max length', async () => {
      const onChange = vi.fn();
      render(
        <MarkdownEditor 
          {...defaultProps} 
          onChange={onChange}
          maxLength={10}
          value="123456789"
        />
      );
      
      const editor = screen.getByRole('textbox');
      await user.type(editor, 'xyz');
      
      // Should not exceed max length
      expect(onChange).toHaveBeenLastCalledWith(expect.stringMatching(/^.{0,10}$/));
    });

    it('should show warning near limit', () => {
      render(
        <MarkdownEditor {...defaultProps} maxLength={100} value={'a'.repeat(95)} />
      );
      
      const counter = screen.getByText('95 / 100');
      expect(counter).toHaveClass('text-warning');
    });
  });
});