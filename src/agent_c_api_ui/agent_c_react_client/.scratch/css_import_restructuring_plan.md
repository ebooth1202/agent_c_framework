# CSS Import Restructuring Plan

## Current Issues

1. **Duplicate Imports**: Many component CSS files are imported twice - once in `main.css` and again in `component-styles.css`
2. **Order Problems**: Tailwind CSS is imported after component styles in `index.css`, which can cause specificity issues
3. **Dual Theming Systems**: Using both shadcn/ui CSS variables and custom theme variables simultaneously

## Recommended Changes

### 1. Streamline CSS Imports

```css
/* index.css - Revised */
/* First import Tailwind base and components for proper cascade */
@tailwind base;
@tailwind components;

/* Import our core common styles */
@import './styles/common/variables.css';
@import './styles/common/reset.css';
@import './styles/common/typography.css';
@import './styles/common/layout.css';

/* Import component styles */
@import './styles/main.css';

/* Finally Tailwind utilities to override components if needed */
@tailwind utilities;

/* Custom overrides for specific components */
/* ... */
```

### 2. Simplify main.css

```css
/* main.css - Revised */
/* Description: Entry point for all component styles */

/* Import all component styles directly - no need for another layer of indirection */
@import './components/layout.css';
@import './components/thought-display.css';
/* ... other component imports ... */

/* Remove the duplicate import of component-styles.css */
```

### 3. Deprecate component-styles.css

After ensuring all component CSS files are properly imported through `main.css`, we can remove `component-styles.css` completely.

## Implementation Steps

1. Update `index.css` to use the proper import order (Tailwind base/components → common styles → component styles → Tailwind utilities)
2. Remove duplicate imports from `main.css`
3. Add a comment in `component-styles.css` marking it for removal after verifying all styles work correctly
4. Verify all components still appear correctly in both light and dark modes
5. After confirmation, remove the deprecated `component-styles.css` file

## Testing Plan

After making these changes, we should thoroughly test:

1. Light and dark mode appearance of all components
2. Transition animations between modes
3. Mobile responsiveness
4. Component interactions (hover, focus, active states)

This restructuring will provide a more consistent foundation for our continued migration to shadcn/ui and Radix UI components.