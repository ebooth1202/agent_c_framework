# Chat Interface Maximize Fix Plan

## Issue Analysis

When the browser is maximized, the chat interface doesn't display properly due to several factors:

1. The message bubbles (assistant and user messages) have max-width constraints of 80%, which doesn't account for very large screens
2. The layout structure doesn't properly handle maximized browser windows
3. There's limited responsive design handling for larger screens
4. The content positioning isn't optimized for maximized windows

## Proposed Fixes

### 1. Improve Message Bubble Sizing

Update the CSS for `.assistant-message-card` and `.user-message-content` to use a more sophisticated width calculation that works better on large screens:

```css
/* For assistant messages */
.assistant-message-card {
  max-width: min(80%, 800px);
  /* other styles remain the same */
}

/* For user messages */
.user-message-content {
  max-width: min(80%, 800px);
  /* other styles remain the same */
}
```

This will ensure messages don't get too wide on large screens while still being responsive.

### 2. Enhance Layout Responsiveness

Improve the `.layout-main-page` CSS to better handle maximized windows:

```css
.layout-main-page {
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: clamp(1rem, 2vw, 2rem);
  height: calc(100vh - 60px);
  height: calc(100dvh - 60px);
  overflow-y: auto;
}
```

### 3. Optimize Chat Interface Container

Add responsive padding to the chat interface container:

```css
.chat-interface-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  position: relative;
  z-index: 0;
  padding: clamp(0.5rem, 1vw, 1.5rem);
}
```

### 4. Add Media Queries for Large Screens

Add specific CSS rules for large screens:

```css
/* Large screen optimizations */
@media (min-width: 1600px) {
  .messages-list-container {
    max-width: 90%;
    margin: 0 auto;
  }
  
  .message-item-wrapper {
    max-width: 1400px;
    margin-left: auto;
    margin-right: auto;
  }
}
```

### 5. Ensure Proper Chat Interface Padding

Update the chat interface card padding:

```css
.chat-interface-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background-color: hsl(var(--card) / 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-xl, 12px);
  box-shadow: var(--shadow-xl);
  padding: clamp(0.5rem, 1vw, 1rem);
}
```

## Implementation Plan

1. Update the message bubble CSS for both assistant and user messages
2. Enhance the layout and chat interface container CSS
3. Add media queries for large screens
4. Test in maximized windows of different sizes
5. Ensure both light and dark mode display correctly