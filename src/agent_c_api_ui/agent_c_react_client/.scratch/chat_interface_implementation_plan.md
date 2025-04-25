# ChatInterface Implementation Plan

## Overview

This implementation plan outlines the specific steps needed to standardize the ChatInterface component to fully comply with our shadcn/ui and Radix UI implementation standards. The plan focuses on component replacements, CSS updates, and accessibility improvements.

## Component Changes

### 1. Update Component Imports

```jsx
// Add these imports
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
```

### 2. Replace Custom Textarea

**Current Implementation:**
```jsx
<textarea
  placeholder="Type your message..."
  value={inputText}
  onChange={(e) => setInputText(e.target.value)}
  onKeyDown={handleKeyPress}
  disabled={isStreaming}
  rows="2"
  className="chat-interface-textarea"
/>
```

**New Implementation:**
```jsx
<Textarea
  placeholder="Type your message..."
  value={inputText}
  onChange={(e) => setInputText(e.target.value)}
  onKeyDown={handleKeyPress}
  disabled={isStreaming}
  rows={2}
  className="min-h-[3rem] max-h-[12rem] pr-[84px] resize-none chat-interface-textarea"
/>
```

### 3. Add Tooltips to Action Buttons

**Current Implementation:**
```jsx
<Button
  onClick={toggleOptionsPanel}
  variant="ghost"
  size="icon"
  className="chat-interface-action-button chat-interface-settings-button"
  aria-label="Toggle options panel"
>
  <Settings className="h-4 w-4" />
</Button>
```

**New Implementation:**
```jsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button
        onClick={toggleOptionsPanel}
        variant="ghost"
        size="icon"
        className="chat-interface-action-button chat-interface-settings-button"
        aria-label="Toggle options panel"
      >
        <Settings className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Toggle options panel</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### 4. Use Badge for Selected Files

**Current Implementation:**
The current implementation displays selected files in FileUploadManager. We'll update how the files are displayed in the ChatInterface.

**New Implementation:**
```jsx
{selectedFiles.length > 0 && (
  <div className="flex flex-wrap gap-2 mt-1">
    {selectedFiles.map((file) => (
      <Badge 
        key={file.id} 
        variant="outline"
        className="flex items-center gap-1 py-1"
      >
        <span className="truncate max-w-[150px]">{file.name}</span>
        <button
          onClick={() => handleRemoveFile(file.id)}
          className="ml-1 rounded-full hover:bg-muted p-0.5"
          aria-label={`Remove ${file.name}`}
        >
          <X className="h-3 w-3" />
        </button>
      </Badge>
    ))}
  </div>
)}
```

### 5. Add Separator Between Sections

**Current Implementation:**
Currently using border-top CSS in chat-interface-input-area.

**New Implementation:**
```jsx
<CardContent className="chat-interface-messages flex-grow p-0 overflow-hidden">
  {/* ...ScrollArea content... */}
</CardContent>

<Separator className="my-0" />

{isOptionsOpen && (
  <div className="mx-4 mb-2">
    <CollapsibleOptions
      {/* ...props... */}
    />
  </div>
)}
```

## CSS Updates

### 1. Update chat-interface.css

```css
/* ===== COMPONENT: ChatInterface ===== */
/* Description: Main chat interface component providing message display, input, and interactions */

/* ChatInterface: Container */
.chat-interface-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  position: relative;
  z-index: 0;
}

/* ChatInterface: Card */
.chat-interface-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background-color: hsl(var(--card) / 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-xl, 12px);
  box-shadow: var(--shadow-xl, 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1));
}

/* ChatInterface: Messages area */
.chat-interface-messages {
  flex-grow: 1;
  overflow: hidden;
}

/* ChatInterface: Input area */
.chat-interface-input-area {
  background-color: hsl(var(--card) / 0.9);
  backdrop-filter: blur(4px);
  padding: 0.75rem 1rem;
  border-bottom-left-radius: var(--radius-xl, 12px);
  border-bottom-right-radius: var(--radius-xl, 12px);
  flex-direction: column;
  gap: 0.75rem;
}

/* ChatInterface: Text input - only for custom styling on top of Textarea component */
.chat-interface-textarea {
  border-radius: var(--radius-xl, 12px);
}

/* ChatInterface: Action buttons */
.chat-interface-action-button {
  position: absolute;
  bottom: 0.5rem;
  height: 2rem;
  width: 2rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms ease;
}

.chat-interface-send-button {
  right: 0.5rem;
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.chat-interface-send-button:hover:not(:disabled) {
  background-color: hsl(var(--primary) / 0.9);
}

.chat-interface-upload-button {
  right: 3rem;
  color: hsl(var(--muted-foreground));
}

.chat-interface-upload-button:hover:not(:disabled) {
  color: hsl(var(--primary));
  background-color: hsl(var(--primary) / 0.1);
}

.chat-interface-settings-button {
  right: 5.5rem;
  color: hsl(var(--muted-foreground));
}

.chat-interface-settings-button:hover {
  color: hsl(var(--primary));
  background-color: hsl(var(--primary) / 0.1);
}

/* ChatInterface: Status bar */
.chat-interface-status-bar {
  margin-top: -0.25rem;
  display: flex;
  justify-content: center;
  width: 100%;
  transform: translateY(0.25rem);
}

/* ChatInterface: Selected files area */
.chat-interface-selected-files {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
```

## Accessibility Improvements

### 1. Add ARIA Attributes

- Add aria-live for message updates
- Add aria-label for the chat container
- Add aria-labels for all interactive elements

```jsx
<DragDropArea 
  onFileDrop={handleFileDrop}
  disabled={isStreaming}
  className="chat-interface-container"
  aria-label="Chat conversation area"
>
  <Card className="chat-interface-card">
    <CardContent 
      className="chat-interface-messages flex-grow p-0 overflow-hidden"
      aria-live="polite"
      aria-atomic="false"
    >
      {/* ... */}
    </CardContent>
    {/* ... */}
  </Card>
</DragDropArea>
```

### 2. Add Keyboard Navigation Support

- Ensure all interactive elements are keyboard accessible
- Add focus trapping for modal-like behaviors
- Add keyboard shortcuts with proper documentation

## Implementation Steps

1. **Create Updated Component**
   - Start with a copy of the current component
   - Implement changes systematically
   - Test each change individually

2. **Update Imports**
   - Add all necessary shadcn/ui component imports

3. **Replace Textarea**
   - Replace the custom textarea with the shadcn/ui Textarea component
   - Ensure all event handlers and props are properly migrated

4. **Add Tooltips**
   - Add TooltipProvider wrapper to the appropriate section
   - Wrap each action button with Tooltip components

5. **Enhance File Selection Display**
   - Add Badge components for selected files
   - Implement proper file removal functionality

6. **Add Separators**
   - Replace border styling with Separator components

7. **Update CSS**
   - Update chat-interface.css to remove redundant styles
   - Ensure all necessary styles are preserved

8. **Add Accessibility Improvements**
   - Add ARIA attributes to key elements
   - Ensure proper keyboard navigation

9. **Testing**
   - Test in light mode
   - Test in dark mode
   - Test theme switching
   - Test keyboard navigation
   - Test with screen reader
   - Test all existing functionality

## Rollout Plan

1. **Development**
   - Implement changes in a development environment
   - Test thoroughly with all supported browsers

2. **Review**
   - Review changes with the team
   - Ensure all standards are followed

3. **Integration**
   - Integrate changes with the main codebase
   - Test in the integrated environment

4. **Deployment**
   - Deploy changes to production
   - Monitor for any issues

## Success Criteria

- Component fully adheres to shadcn/ui and Radix UI standards
- All functionality works as expected in both light and dark modes
- Component is fully accessible via keyboard and screen readers
- Performance is maintained or improved
- Code is clean, maintainable, and follows best practices