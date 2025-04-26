# Assistant Message Size Fix

## Problem
The assistant message bubble in the chat interface had an issue with excessive empty space between the message content and the token usage/tool call controls at the bottom. This was particularly noticeable with short messages, as shown in the screenshot.

## Root Cause
The message card was expanding to fill available vertical space, creating a large gap between the message content and the footer controls. This was happening because:

1. The message body was using `justify-content: space-between` which pushed the footer to the bottom regardless of content size
2. The markdown content container didn't have proper constraints to prevent unnecessary expansion
3. There was no intermediate container to properly separate the message content from the footer

## Solution

### 1. Modified AssistantMessage.jsx structure
Added a new `assistant-message-main-content` container to properly isolate the message content:

```jsx
<div className="assistant-message-body">
  <div className="assistant-message-main-content">
    <MarkdownMessage content={content} />
  </div>
  
  {/* Footer with token usage and tool call info */}
  <div className="assistant-message-footer">
    // Footer content
  </div>
</div>
```

### 2. Updated CSS properties

#### For the message body:
- Changed `justify-content` from `space-between` to `flex-start` to prevent pushing footer far away

#### Added new CSS for the main content area:
```css
.assistant-message-main-content {
  flex-grow: 0;  /* Don't expand to fill space */
  flex-shrink: 0; /* Don't shrink */
  margin-bottom: 0.5rem;
}
```

#### Updated the footer:
- Changed `margin-top` to `auto` to push it to the bottom when there's actual content
- Added `flex-shrink: 0` to prevent the footer from being compressed

#### Fixed the markdown container:
- Added `align-self: flex-start` to prevent it from expanding to fill all available space

## Result
Now the assistant message bubble properly sizes itself based on the content, keeping the token information and tool call controls close to the message content without unnecessary empty space in between. This creates a more polished and professional appearance in the chat interface.