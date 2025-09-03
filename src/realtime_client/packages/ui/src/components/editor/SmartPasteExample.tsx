import * as React from 'react';
import { MarkdownEditorClient } from './MarkdownEditorClient';

/**
 * Smart Paste Example Component
 * 
 * Demonstrates the image upload functionality with smart paste:
 * - Paste images from clipboard
 * - Drag and drop image files
 * - Shows upload placeholder with progress
 * - Handles success and error states
 * 
 * Usage:
 * 1. Copy an image to clipboard and paste (Ctrl/Cmd+V)
 * 2. Drag and drop an image file into the editor
 * 3. Watch the upload placeholder appear and transform
 */
export const SmartPasteExample: React.FC = () => {
  const [content, setContent] = React.useState('');
  const [uploadHistory, setUploadHistory] = React.useState<Array<{
    fileName: string;
    url: string;
    timestamp: Date;
    status: 'success' | 'error';
    error?: string;
  }>>([]);

  /**
   * Mock image upload handler
   * Simulates uploading to a server with a 2 second delay
   */
  const handleImageUpload = React.useCallback(async (file: File): Promise<string> => {
    // Track upload start internally
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate occasional failures (10% chance)
    if (Math.random() < 0.1) {
      const error = 'Network error: Failed to upload image';
      setUploadHistory(prev => [...prev, {
        fileName: file.name,
        url: '',
        timestamp: new Date(),
        status: 'error',
        error
      }]);
      throw new Error(error);
    }
    
    // Generate mock URL with file info
    const mockUrl = `https://via.placeholder.com/600x400/0055ff/ffffff?text=${encodeURIComponent(file.name)}`;
    
    // Add to history
    setUploadHistory(prev => [...prev, {
      fileName: file.name,
      url: mockUrl,
      timestamp: new Date(),
      status: 'success'
    }]);
    
    // Upload complete
    return mockUrl;
  }, []);

  /**
   * Handle upload start
   */
  const handleUploadStart = React.useCallback((_file: File) => {
    // Upload started - could update UI state here if needed
    // File: ${file.name} (${(file.size / 1024).toFixed(1)}KB)
  }, []);

  /**
   * Handle upload complete
   */
  const handleUploadComplete = React.useCallback((_url: string) => {
    // Image successfully inserted with URL
  }, []);

  /**
   * Handle upload error
   */
  const handleUploadError = React.useCallback((_error: Error) => {
    // Handle upload error - error already tracked in uploadHistory
    // Error message: ${error.message}
  }, []);

  /**
   * Submit handler
   */
  const handleSubmit = React.useCallback((text: string) => {
    // Submit the content
    alert(`Content submitted!\n\nWord count: ${text.split(/\s+/).length}\nCharacter count: ${text.length}`);
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Smart Paste Image Upload Demo</h2>
        <p className="text-muted-foreground">
          Try pasting images from your clipboard or dragging and dropping image files into the editor.
        </p>
      </div>

      {/* Instructions Card */}
      <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-3">
        <h3 className="font-semibold flex items-center gap-2">
          <span className="text-lg">📋</span>
          How to use Smart Paste
        </h3>
        <ul className="space-y-2 text-sm">
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            <span><strong>Paste from clipboard:</strong> Copy any image and press Ctrl/Cmd+V in the editor</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            <span><strong>Drag & Drop:</strong> Drag image files directly into the editor</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            <span><strong>Supported formats:</strong> PNG, JPEG, GIF, WebP (max 10MB)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">•</span>
            <span><strong>Upload behavior:</strong> Shows a placeholder while uploading (2s simulated delay)</span>
          </li>
        </ul>
      </div>

      {/* Main Editor */}
      <div className="space-y-3">
        <label className="text-sm font-medium">
          Editor with Smart Paste enabled:
        </label>
        <MarkdownEditorClient
          value={content}
          onChange={setContent}
          onSubmit={handleSubmit}
          placeholder="Type your message here... Try pasting an image!"
          enableSmartPaste={true}
          maxImageSize={10 * 1024 * 1024} // 10MB
          onImageUpload={handleImageUpload}
          onImageUploadStart={handleUploadStart}
          onImageUploadComplete={handleUploadComplete}
          onImageUploadError={handleUploadError}
          className="min-h-[300px]"
        />
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{content.length} characters</span>
          <span>Press Cmd/Ctrl+Enter to submit</span>
        </div>
      </div>

      {/* Upload History */}
      {uploadHistory.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold">Upload History</h3>
          <div className="space-y-2">
            {uploadHistory.map((upload, index) => (
              <div 
                key={index}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-md border",
                  upload.status === 'success' 
                    ? "bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-900" 
                    : "bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-900"
                )}
              >
                <div className="flex-shrink-0">
                  {upload.status === 'success' ? (
                    <span className="text-green-600">✅</span>
                  ) : (
                    <span className="text-red-600">❌</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{upload.fileName}</div>
                  {upload.status === 'success' ? (
                    <div className="text-xs text-muted-foreground truncate">
                      {upload.url}
                    </div>
                  ) : (
                    <div className="text-xs text-red-600">
                      {upload.error}
                    </div>
                  )}
                </div>
                <div className="text-xs text-muted-foreground">
                  {upload.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw Content Preview */}
      <div className="space-y-3">
        <h3 className="font-semibold">Raw Markdown Output</h3>
        <pre className="p-4 rounded-md bg-muted font-mono text-sm overflow-x-auto whitespace-pre-wrap">
          {content || '(Empty)'}
        </pre>
      </div>
    </div>
  );
};

// Helper function for class names
function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}