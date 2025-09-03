/**
 * Tests for MarkdownEditorClient SSR compatibility wrapper
 */

import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MarkdownEditorClient } from './MarkdownEditorClient';

// Mock the MarkdownEditor module to simulate SSR environment
jest.mock('./MarkdownEditor', () => ({
  MarkdownEditor: React.forwardRef<HTMLDivElement, any>(
    ({ value, placeholder }, ref) => (
      <div ref={ref} data-testid="markdown-editor">
        <div>{value || placeholder || 'Mocked MarkdownEditor'}</div>
      </div>
    )
  ),
}));

describe('MarkdownEditorClient', () => {
  it('should render loading fallback initially', () => {
    const { container } = render(
      <MarkdownEditorClient 
        value="Test content" 
        placeholder="Test placeholder"
      />
    );
    
    // Should show the textarea fallback initially
    const textarea = container.querySelector('textarea');
    expect(textarea).toBeTruthy();
    expect(textarea?.value).toBe('Test content');
    expect(textarea?.placeholder).toBe('Test placeholder');
  });

  it('should load the actual editor after mounting', async () => {
    const { rerender } = render(
      <MarkdownEditorClient 
        value="Test content" 
        placeholder="Test placeholder"
      />
    );
    
    // Wait for useEffect to run and component to update
    await waitFor(() => {
      rerender(
        <MarkdownEditorClient 
          value="Test content" 
          placeholder="Test placeholder"
        />
      );
    });

    // After client hydration, should show the actual editor
    await waitFor(() => {
      expect(screen.queryByTestId('markdown-editor')).toBeTruthy();
    });
  });

  it('should handle onChange callbacks in fallback', () => {
    const handleChange = jest.fn();
    const { container } = render(
      <MarkdownEditorClient 
        value="Initial" 
        onChange={handleChange}
      />
    );
    
    const textarea = container.querySelector('textarea');
    expect(textarea).toBeTruthy();
    
    // Simulate typing in the fallback textarea
    const event = new Event('change', { bubbles: true });
    Object.defineProperty(event, 'target', {
      value: { value: 'Updated content' },
      writable: false,
    });
    
    textarea?.dispatchEvent(event);
    expect(handleChange).toHaveBeenCalledWith('Updated content');
  });

  it('should handle onSubmit with Cmd+Enter in fallback', () => {
    const handleSubmit = jest.fn();
    const { container } = render(
      <MarkdownEditorClient 
        value="Test content" 
        onSubmit={handleSubmit}
      />
    );
    
    const textarea = container.querySelector('textarea');
    expect(textarea).toBeTruthy();
    
    // Simulate Cmd+Enter
    const event = new KeyboardEvent('keydown', {
      key: 'Enter',
      metaKey: true,
      bubbles: true,
    });
    
    textarea?.dispatchEvent(event);
    expect(handleSubmit).toHaveBeenCalledWith('Test content');
  });

  it('should forward ref properly', () => {
    const ref = React.createRef<HTMLDivElement>();
    render(
      <MarkdownEditorClient 
        ref={ref}
        value="Test" 
      />
    );
    
    // The ref should be attached to the container div
    expect(ref.current).toBeTruthy();
    expect(ref.current?.tagName).toBe('DIV');
  });

  it('should pass all props through to the loaded editor', async () => {
    const props = {
      value: 'Test value',
      onChange: jest.fn(),
      onSubmit: jest.fn(),
      placeholder: 'Test placeholder',
      disabled: true,
      className: 'custom-class',
      enableSmartPaste: false,
      maxImageSize: 5000000,
      onImageUpload: jest.fn(),
      onImageUploadStart: jest.fn(),
      onImageUploadComplete: jest.fn(),
      onImageUploadError: jest.fn(),
    };
    
    const { rerender } = render(<MarkdownEditorClient {...props} />);
    
    // Wait for client hydration
    await waitFor(() => {
      rerender(<MarkdownEditorClient {...props} />);
    });
    
    // The actual editor should receive all props
    await waitFor(() => {
      const editor = screen.queryByTestId('markdown-editor');
      expect(editor).toBeTruthy();
      expect(editor?.textContent).toContain('Test value');
    });
  });

  it('should be safe to use in SSR environment', () => {
    // Simulate SSR environment where window is undefined
    const originalWindow = global.window;
    // @ts-ignore
    delete global.window;
    
    // Should not throw during render
    expect(() => {
      render(<MarkdownEditorClient value="SSR test" />);
    }).not.toThrow();
    
    // Restore window
    global.window = originalWindow;
  });
});