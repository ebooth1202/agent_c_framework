# UserMessage Component Implementation Plan

## Current Analysis

The UserMessage component shows user messages in the chat interface, with:

- User avatar on the right
- Message text in a primary-colored "bubble"
- Support for voice messages
- Support for file attachments
- Copy button that appears on hover
- Markdown content rendering

The component is already using several shadcn/ui components:
- Card and CardContent
- Avatar and AvatarFallback

The CSS file is minimal since most styling is handled via Tailwind classes.

## Issues to Address

1. File attachments display is simple text, could use shadcn/ui Badge components
2. Missing proper PropTypes validation
3. Copy button could be enhanced with shadcn/ui Tooltip
4. Some accessibility improvements needed
5. CSS organization could be improved with more structured class names

## Implementation Plan

### 1. Improve File Attachments Display

- Use shadcn/ui Badge components for file attachments
- Add more structured display for multiple files
- Improve the separator between message and files

### 2. Add PropTypes Validation

- Add comprehensive PropTypes for all component props
- Document all props with JSDoc comments

### 3. Enhance Copy Button

- Use shadcn/ui Tooltip component
- Maintain hover behavior

### 4. Improve Accessibility

- Add ARIA labels to all interactive elements
- Ensure proper semantic structure
- Add role attributes where needed

### 5. Improve CSS Structure

- Move any inline styles to the CSS file
- Create better class naming structure
- Organize CSS with proper comments

### 6. Code Quality Improvements

- Extract helper functions for complex logic
- Enhance code comments
- Improve component structure

## Implementation Details

### Imports to Add
```jsx
import PropTypes from 'prop-types';
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
```

### File Attachments Rendering
```jsx
{files && files.length > 0 && (
  <div className="user-message-files">
    <Separator className="my-2" />
    <div className="flex flex-wrap gap-1.5">
      <FileIcon className="h-3.5 w-3.5" />
      {files.map((file, index) => (
        <Badge key={index} variant="secondary" className="text-xs">
          {file}
        </Badge>
      ))}
    </div>
  </div>
)}
```

### Copy Button Enhancement
```jsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <div className="user-message-copy-container">
        <CopyButton
          content={content}
          position="left"
          variant="secondary"
          size="xs"
          className="user-message-copy-button"
        />
      </div>
    </TooltipTrigger>
    <TooltipContent side="left" className="user-message-tooltip">
      Copy message
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### PropTypes Validation
```jsx
UserMessage.propTypes = {
  content: PropTypes.string.isRequired,
  files: PropTypes.arrayOf(PropTypes.string),
  isVoiceMessage: PropTypes.bool,
  className: PropTypes.string
};

UserMessage.defaultProps = {
  files: [],
  isVoiceMessage: false,
  className: ''
};
```

### CSS Updates
```css
/* ===== COMPONENT: UserMessage ===== */
/* Description: Displays messages sent by the user in the chat interface with consistent styling and copy functionality */

/* UserMessage: Container */
.user-message-container {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 0.5rem;
}

/* UserMessage: Content */
.user-message-content {
  max-width: 80%;
  border-radius: 1rem;
  border-bottom-right-radius: 0.25rem;
  padding: 1rem;
  background-color: var(--primary);
  color: var(--primary-foreground);
  border: 1px solid rgba(var(--primary-rgb), 0.2);
  box-shadow: var(--shadow-sm);
}

/* UserMessage: Markdown content */
.markdown-user-message > * {
  color: inherit;
}

/* UserMessage: Files section */
.user-message-files {
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

/* UserMessage: Copy button */
.user-message-copy-button {
  margin-top: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.user-message-container:hover .user-message-copy-button {
  opacity: 1;
}
```