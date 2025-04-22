# Sample Implementation Examples

This document provides specific code examples showing how components would be changed during the CSS refactoring process.

## Original vs. Refactored Examples

### Example 1: MarkdownMessage.jsx

#### Original Code (with inline styles)

```jsx
// Inline code (single backticks) formatting
<code className="bg-purple-100 px-1 rounded text-purple-800 inline font-mono inline-block" {...props}>
    {children}
</code>
```

#### Refactored Code (with CSS variables + Tailwind)

```jsx
// Inline code (single backticks) formatting
<code className="markdown-code-inline" {...props}>
    {children}
</code>
```

Where `markdown-code-inline` is defined in component-classes.css:

```css
.markdown-code-inline {
  @apply bg-code-inline-bg text-code-inline-text px-1 rounded font-mono inline-block;
}
```

And the colors are defined as CSS variables in globals.css:

```css
:root {
  /* ... other variables ... */
  --code-inline-bg: 270 60% 96%;
  --code-inline-text: 270 60% 50%;
}

.dark {
  /* ... other variables ... */
  --code-inline-bg: 270 30% 20%;
  --code-inline-text: 270 70% 80%;
}
```

### Example 2: ThoughtDisplay.jsx

#### Original Code (with inline styles)

```jsx
<div className="relative max-w-[80%] rounded-2xl px-4 py-3 shadow-sm 
    bg-amber-50 dark:bg-gray-700/70 
    text-amber-700/80 dark:text-amber-200/80 
    border border-amber-200 dark:border-amber-800 
    rounded-bl-sm">
    {/* Content area with markdown */}
    <div className="flex justify-between items-start gap-4">
        <div
            ref={contentRef}
            className="text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1"
            style={{
                scrollbarWidth: 'thin',
                scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
            }}
        >
            <div ref={markdownRef}>
                <MarkdownMessage content={content} />
            </div>
        </div>
        <CopyButton
            content={content}
            tooltipText="Copy thinking"
            position="left"
            variant="secondary"
            size="xs"
            className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-amber-700 hover:bg-amber-100 dark:text-amber-300 dark:hover:bg-amber-900/30"
        />
    </div>
</div>
```

#### Refactored Code (with CSS variables + Tailwind)

```jsx
<div className="relative max-w-[80%] thought-container">
    {/* Content area with markdown */}
    <div className="flex justify-between items-start gap-4">
        <div
            ref={contentRef}
            className="thought-content"
        >
            <div ref={markdownRef}>
                <MarkdownMessage content={content} />
            </div>
        </div>
        <CopyButton
            content={content}
            tooltipText="Copy thinking"
            position="left"
            variant="secondary"
            size="xs"
            className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity thought-copy-button"
        />
    </div>
</div>
```

Where component classes are defined in component-classes.css:

```css
.thought-container {
  @apply bg-thought-bg border border-thought-border text-thought-text rounded-2xl px-4 py-3 shadow-sm rounded-bl-sm;
}

.thought-content {
  @apply text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1 scrollbar-thin scrollbar-thought;
}

.thought-copy-button {
  @apply text-thought-text hover:bg-thought-hover-bg dark:text-thought-text-dark dark:hover:bg-thought-hover-bg-dark;
}
```

### Example 3: Custom Component Class Plugin

#### Adding a Tailwind Plugin for Custom Functionality

```js
// tailwind.config.js
module.exports = {
  // ... existing config
  plugins: [
    // ... existing plugins
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.scrollbar-thin': {
          'scrollbarWidth': 'thin',
        },
        '.scrollbar-thought': {
          'scrollbarColor': `${theme('colors.thought.scrollbar-thumb')} ${theme('colors.thought.scrollbar-track')}`
        },
        // Add more custom utilities as needed
      };
      
      addUtilities(newUtilities, ['responsive', 'dark']);
    }
  ]
}
```

## Directory Structure for New Files

```
src/
  styles/
    globals.css                # Enhanced with new CSS variables
    component-classes.css      # New file with component class definitions
  lib/
    utils/
      styles.js               # Utility functions for styling (optional)
```

## Integration into the Project

To integrate component-classes.css, add an import to the main app entry point:

```jsx
// src/main.jsx or similar
import './styles/globals.css';
import './styles/component-classes.css';

// Rest of the file...
```

Or add it to globals.css:

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@import './component-classes.css';

/* Rest of the file... */
```