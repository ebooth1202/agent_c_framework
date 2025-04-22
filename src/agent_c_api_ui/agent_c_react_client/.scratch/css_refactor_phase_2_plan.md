# CSS Refactor Phase 2: Plan

## Overview

Building on the successful methodology from Phase 1, we'll continue extracting inline Tailwind utility classes into the component-styles.css file. This phase will focus on the remaining components that still have significant inline styling.

## Core Principles (Maintained from Phase 1)

1. **One component at a time** - Never try to change multiple components in the same step
2. **Exact visual match** - No design changes, just code organization
3. **Each step must be validated** - Using screenshots, tests, etc. BEFORE moving on
4. **No global architecture changes** - Just moving inline styles to proper CSS

## Component Selection Criteria

We'll prioritize components based on:

1. **Usage frequency**: Components that appear most often in the application
2. **Styling complexity**: Components with excessive inline styling
3. **Visibility**: Components that are prominently visible to users
4. **Consistency with Phase 1**: Components that interact closely with already-refactored components

## Phase 2 Target Components

Based on initial analysis, here are the components we'll refactor in Phase 2:

1. **Layout.jsx** - Main application layout, high visibility
2. **MobileNav.jsx** - Mobile navigation menu
3. **AgentConfigDisplay.jsx** - Config display with substantial inline styling
4. **AgentConfigHoverCard.jsx** - Hover card with complex styling
5. **Sidebar.jsx** - Side navigation panel
6. **PageHeader.jsx** - Page headers across the application
7. **DragDropOverlay.jsx** - File upload overlay styling
8. **TokenUsageDisplay.jsx** - Token usage visualization
9. **ToolCallItem.jsx** - Individual tool call items
10. **CollapsibleOptions.jsx** - Options that expand/collapse

## Implementation Process

For each component, we'll follow this step-by-step process:

1. **Analysis**:
   - Take screenshots in light and dark modes for "before" reference
   - Identify all inline Tailwind classes
   - Group related styles for extraction

2. **CSS Creation**:
   - Create a new section in component-styles.css for the component
   - Follow BEM-inspired naming convention (component-element-modifier)
   - Add clear comments for each section
   - Support both light and dark themes

3. **Component Update**:
   - Replace inline classes with the new CSS classes
   - Retain any dynamic styles that must stay inline
   - Ensure accessibility is maintained

4. **Verification**:
   - Take screenshots in light and dark modes for "after" reference
   - Compare before/after to confirm visual parity
   - Test interactive states and animations
   - Verify responsive behavior

5. **Documentation**:
   - Update tracking document with completed status
   - Note any special considerations or challenges

## CSS Organization Approach

We'll continue using the established pattern in component-styles.css:

```css
/* ==============================
   ComponentName Component Styles
   ============================== */

/* Main container */
.component-container {
  /* Base styles */
}

.dark .component-container {
  /* Dark theme overrides */
}

/* Component elements */
.component-element {
  /* Element styles */
}

/* Component states and variants */
.component-element-variant {
  /* Variant styles */
}
```

## Tracking Progress

We'll create a tracking document that includes:

| Component | Status | Light Mode Verified | Dark Mode Verified | Notes |
|-----------|--------|---------------------|-------------------|-------|
| Layout.jsx | Not Started | No | No | Main app layout |  
| MobileNav.jsx | Not Started | No | No | Mobile navigation |
| ... | ... | ... | ... | ... |

## Potential Challenges

1. **Dynamic styling**: Some components may have styles that depend on state
2. **Complex interactions**: Components with hover/focus states may need special attention
3. **Responsive design**: We must ensure styles work across all screen sizes
4. **Nested components**: Some components may have complex nesting that requires careful style organization

## Testing Approach

1. **Visual comparison**: Take screenshots before and after refactoring
2. **Responsive testing**: Verify appearance on different screen sizes
3. **State testing**: Check hover, focus, active, and other interactive states
4. **Theme testing**: Verify both light and dark modes

## Timeline

For each component:
1. Analysis: 20-30 minutes
2. CSS Creation: 30-45 minutes
3. Component Update: 20-30 minutes
4. Verification: 15-20 minutes
5. Documentation: 10 minutes

Estimated total: 1.5-2 hours per component