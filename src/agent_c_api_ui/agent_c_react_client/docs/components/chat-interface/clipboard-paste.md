# Clipboard Paste Functionality

## Overview

The clipboard paste functionality allows users to paste images and other files directly from their clipboard into the chat interface. This feature makes it easier and faster to share visual content without having to save files locally first.

## How It Works

### User Experience

1. Copy an image or file to the clipboard (using Print Screen, screenshot tools, or copy from another application)
2. Focus the chat input area
3. Paste using Ctrl+V (or Cmd+V on Mac)
4. The file is automatically uploaded and appears in the chat

### Technical Implementation

The clipboard paste functionality is implemented through the following components:

- `ChatInputArea.jsx`: Contains the paste event listener that captures clipboard content
- `ChatInterface.jsx`: Processes pasted files similar to dropped files
- `clipboard-paste.css`: Provides styling and visual feedback for the paste functionality

## Supported Content Types

The paste functionality primarily supports:

- Images (PNG, JPEG, GIF, etc.)
- Other file types that can be represented in the clipboard

## Considerations

- File size limits are the same as regular file uploads
- Images pasted without names are automatically named with a timestamp (e.g., `pasted-image-1650123456789.png`)
- On mobile devices, clipboard access depends on the browser's capabilities

## Usage Example

```jsx
// The paste event handler in ChatInputArea.jsx
const handlePaste = (e) => {
  // Check for files in clipboard
  const items = e.clipboardData?.items;
  if (!items) return;
  
  // Process files
  const files = [];
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.kind === 'file') {
      const file = item.getAsFile();
      if (file) {
        files.push(file);
      }
    }
  }
  
  // Handle files if found
  if (files.length > 0) {
    handleClipboardPaste(files);
  }
};
```

## Future Enhancements

- Support for pasting multiple files simultaneously
- Preview of pasted content before upload
- Option to edit/crop pasted images
- Better support for text+image mixed content