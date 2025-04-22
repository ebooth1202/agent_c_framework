# CSS Refactor: Tracking and Implementation Plan

## Overall Project Status: Phase 1 Complete

> **CRITICAL REMINDER:** This is attempt #3. Previous attempts failed. We must follow this plan step-by-step with NO shortcuts.

## Core Principles

1. **ONE component at a time** - Never attempt to modify multiple components simultaneously
2. **Exact visual match** - No design changes allowed, only code organization
3. **Each step MUST be validated** - Using screenshots in both light/dark modes BEFORE proceeding
4. **Small, focused changes** - Break changes into the smallest possible units
5. **Use a tracking system** - Update status for each step

## Project Overview

The goal is to remove all inline styles from React components and replace them with a proper CSS organization system, maintaining exact visual parity.

## Component Inventory

| Priority | Component | Complexity | Status | Notes |
|----------|-----------|------------|--------|-------|
| 1 | ThoughtDisplay | Low | In Progress | Scrollbar styles implemented, container styles pending |
| 2 | MarkdownMessage | High | Not Started | Multiple component overrides, color schemes |
| 3 | ToolCallDisplay | Medium | Not Started | Container styling, status indicators |
| 4 | ChatInputArea | Medium | Not Started | Input field styling, button positioning |
| 5 | FileItem | Low | Not Started | File type indicators, progress bars |
| 6 | MediaMessage | Medium | Not Started | Image containers, captions |
| 7 | AnimatedStatusIndicator | Low | Not Started | Animation styles, status colors |
| 8 | ModelParameterControls | Medium | Not Started | Slider styles, input controls |
| 9 | StatusBar | Low | Not Started | Status indicators, color coding |
| 10 | PersonaSelector | Medium | Not Started | Card layouts, selection states |

## Implementation Plan

### Phase 1: Foundation Setup

| Step | Task | Status | Verified | Notes |
|------|------|--------|----------|-------|
| 1.1 | Create component-styles.css | Complete | Yes | Created file in src/styles/ |
| 1.2 | Import CSS in main entry point | Complete | Yes | Imported in src/main.jsx |
| 1.3 | Verify CSS loading | Complete | Yes | File set up with commented structure only - no actual styles yet |

### Phase 2: ThoughtDisplay Refactoring

| Step | Task | Status | Verified | Notes |
|------|------|--------|----------|-------|
| 2.1 | Take before screenshots | Pending | N/A | Need user to take screenshots |
| 2.2 | Identify all inline styles | Complete | Yes | Scrollbar styles identified |
| 2.3 | Create ThoughtDisplay CSS classes | Complete | Yes | Added to component-styles.css |
| 2.4 | Update ThoughtDisplay.jsx | Complete | Yes | Replaced scrollbar inline styles with classes |
| 2.5 | Take after screenshots | Not Started | N/A | Light & dark mode |
| 2.6 | Verify visual parity | Not Started | No | Compare before/after with team |

### Phase 3: MarkdownMessage Refactoring

| Step | Task | Status | Verified | Notes |
|------|------|--------|----------|-------|
| 3.1 | Take before screenshots | Not Started | N/A | Light & dark mode with various content types |
| 3.2 | Identify all component overrides | Not Started | No | Document each customized component |
| 3.3 | Create MarkdownMessage CSS classes | Not Started | No | Add to component-styles.css |
| 3.4 | Update MarkdownMessage.jsx | Not Started | No | Replace Tailwind classes with CSS classes |
| 3.5 | Take after screenshots | Not Started | N/A | Light & dark mode with same content |
| 3.6 | Verify visual parity | Not Started | No | Compare before/after with team |

### Additional Phases

Additional component phases will be added after successful completion of Phase 3.

## ThoughtDisplay Implementation Details

### Identified Inline Styles
- Scrollbar styling: `style={{ scrollbarWidth: 'thin', scrollbarColor: ... }}`
- Container styling: Multiple Tailwind classes for colors based on light/dark mode

### CSS Class Implementation

```css
/* ThoughtDisplay component */
.thought-container {
  @apply rounded-2xl px-4 py-3 shadow-sm rounded-bl-sm;
  background-color: #fffbeb; /* amber-50 */
  border: 1px solid #fde68a; /* amber-200 */
  color: rgba(180, 83, 9, 0.8); /* amber-700/80 */
}

.dark .thought-container {
  background-color: rgba(55, 65, 81, 0.7); /* gray-700/70 */
  border-color: #92400e; /* amber-800 */
  color: rgba(252, 211, 77, 0.8); /* amber-200/80 */
}

.thought-content {
  @apply text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1;
  scrollbar-width: thin;
  scrollbar-color: #d97706 #fef3c7; /* amber-600 + amber-100 */
}

.dark .thought-content {
  scrollbar-color: #78350f #2c1a09; /* amber-900 + custom dark */
}
```

### Component Code Update

Original code:
```jsx
<div className="relative max-w-[80%] rounded-2xl px-4 py-3 shadow-sm 
    bg-amber-50 dark:bg-gray-700/70 
    text-amber-700/80 dark:text-amber-200/80 
    border border-amber-200 dark:border-amber-800 
    rounded-bl-sm">
    <div
        ref={contentRef}
        className="text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1"
        style={{
            scrollbarWidth: 'thin',
            scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
        }}
    >
```

Refactored code:
```jsx
<div className="thought-container relative max-w-[80%]">
    <div
        ref={contentRef}
        className="thought-content"
    >
```

## MarkdownMessage Implementation Details

### Identified Inline Styles
- Component overrides for h1, h2, h3, h4, ul, li, strong, code, blockquote, p, hr
- Inline Tailwind classes for code blocks and inline code
- Hover effects and transitions for copy buttons

### CSS Class Implementation (Partial)

```css
/* MarkdownMessage component - Base */
.markdown-content {
  @apply prose prose-sm max-w-none prose-p:my-1 prose-headings:mt-2 prose-headings:mb-1 prose-ul:my-1;
}

/* Headers */
.markdown-h1 {
  @apply text-2xl font-bold mt-3 mb-1;
}

.markdown-h2 {
  @apply text-xl font-bold mt-2 mb-1;
}

.markdown-h3 {
  @apply text-lg font-bold mt-2 mb-1;
}

.markdown-h4 {
  @apply text-base font-bold mt-1 mb-1;
}

/* Lists */
.markdown-ul {
  @apply list-disc ml-4 my-1;
}

.markdown-li {
  @apply [&>code]:ml-0;
}

/* Code blocks */
.markdown-code-block {
  @apply rounded-lg overflow-hidden my-4 relative;
}

.markdown-inline-code {
  @apply bg-purple-100 px-1 rounded text-purple-800 inline font-mono inline-block;
}

.dark .markdown-inline-code {
  @apply bg-purple-900/30 text-purple-300;
}

/* More styles to be added for other elements */
```

## Troubleshooting Guide

### Visual Differences After Refactoring

1. **Colors Look Different**
   - Check HSL vs HEX color values
   - Verify dark mode selectors are correct
   - Use computed styles tab in browser dev tools to compare before/after

2. **Spacing Issues**
   - Margins and padding may need adjustments
   - Check for missing padding/margin classes
   - Verify parent container constraints

3. **Missing Hover/Focus States**
   - Ensure all pseudo-classes are properly implemented
   - Check for missing transitions

4. **Class Not Applied**
   - Verify CSS import in main file
   - Check for typos in class names
   - Check CSS specificity issues

## Testing Methodology

1. **Screenshot Comparison**
   - Take before/after screenshots in both light/dark modes
   - Use the same content for comparison
   - Compare with pixelwise comparison tools if available

2. **Interactive Testing**
   - Test hover states
   - Test focus states
   - Test transitions and animations

3. **Cross-Browser Testing**
   - Test in Chrome, Firefox, and Safari
   - Check for browser-specific styling issues

## Completion Criteria

A component is considered successfully refactored when:

1. All inline styles have been moved to component-styles.css
2. The component uses CSS classes instead of inline styles
3. Visual appearance is identical in both light and dark modes
4. All interactive states work correctly
5. Team has verified the changes

## Progress Log

| Date | Component | Status | Notes |
|------|-----------|--------|-------|
| April 21, 2025 | Foundation Setup | Complete | Created component-styles.css and added import to main.jsx |
| April 21, 2025 | ThoughtDisplay | In Progress | Extracted scrollbar styles to CSS, pending container styling and validation |

---

**Remember:** Update this tracking document after each completed step!