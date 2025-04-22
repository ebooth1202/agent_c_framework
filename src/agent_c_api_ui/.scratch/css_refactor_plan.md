# CSS Refactor Plan: Step-by-Step Inline Style Migration

## Core Principles

1. **One component at a time** - Never try to change multiple components in the same step
2. **Exact visual match** - No design changes, just code organization
3. **Each step must be validated** - Using screenshots, tests, etc. BEFORE moving on
4. **No global architecture changes** - Just moving inline styles to proper CSS

## Implementation Strategy

### Step 1: Create Component CSS File (One-time foundation step)

1. Create `src/styles/component-styles.css`
2. Import this CSS file in the main application entry point
3. **Validation**: Verify the CSS loads without affecting UI

### Step 2: ThoughtDisplay Component Refactoring

1. **Before**: Take screenshots in light and dark mode
2. Identify inline styles (scrollbar styling)
3. Add ThoughtDisplay CSS classes to component-styles.css
4. Update ThoughtDisplay.jsx to use new classes
5. **Validation**: Compare screenshots, verify identical appearance

### Step 3: MarkdownMessage Component Refactoring

1. **Before**: Take screenshots in light and dark mode
2. Identify inline styles (code blocks, inline code, etc.)
3. Add MarkdownMessage CSS classes to component-styles.css
4. Update MarkdownMessage.jsx to use new classes
5. **Validation**: Compare screenshots, verify identical appearance

### Step 4: Evaluate and Plan Next Components

1. Based on success of first components, plan next batch
2. Update this plan with next components to target

## Implementation Details

### Component CSS File Structure

```css
/* component-styles.css */

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

/* More component styles will be added as we progress */
```

### Integration Code

Add to main.jsx (or similar entry point):

```jsx
import './styles/globals.css';
import './styles/component-styles.css';
```

## Implementation Example: ThoughtDisplay.jsx

Current code has inline styles:
```jsx
<div
    ref={contentRef}
    className="text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1"
    style={{
        scrollbarWidth: 'thin',
        scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
    }}
>
```

Refactored code using CSS classes:
```jsx
<div
    ref={contentRef}
    className="thought-content"
>
```

## Troubleshooting Guide

If styles don't look the same after refactoring:

1. Use browser dev tools to inspect the CSS and compare computed styles
2. Check that the CSS classes are being applied properly
3. Verify that the CSS file is being loaded
4. Look for specificity issues with other existing styles
5. Check for typos in class names

## Progress Tracking

| Component | Status | Light Mode Verified | Dark Mode Verified | Notes |
|-----------|--------|---------------------|-------------------|-------|
| CSS File Setup | Not Started | - | - | Create basic file structure |
| ThoughtDisplay | Not Started | No | No | Scrollbar styles, container styles |
| MarkdownMessage | Not Started | No | No | Code block styles, blockquote styles |