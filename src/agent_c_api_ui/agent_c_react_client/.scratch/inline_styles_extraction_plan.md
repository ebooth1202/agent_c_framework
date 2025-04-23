# Inline Styles Extraction Plan

## Goals

- Identify and extract inline styles from React components
- Convert inline styles to shadcn/ui and Tailwind patterns
- Ensure consistent styling across the application
- Prepare components for full shadcn/ui conversion

## Analysis Strategy

### 1. Inline Style Detection

Examine components for instances of:
- Inline `style={{}}` props
- Style objects declared within components
- Dynamic styles calculated within components
- Hardcoded class strings instead of `cn()` utility

### 2. Categorization of Inline Styles

Categorize inline styles based on their purpose:

- **Layout styling**: positioning, flexbox, grid, etc.
- **Appearance styling**: colors, borders, shadows
- **Typography styling**: font sizes, weights, families
- **Interactive styling**: hover, focus, active states
- **Responsive styling**: conditional styles based on screen size
- **Animation styling**: transitions, transforms

### 3. Migration Approach

Based on the category, determine the appropriate migration approach:

- **Direct Tailwind Conversion**: Straight replacement with Tailwind utility classes
- **shadcn/ui Component Replacement**: Replace with appropriate shadcn/ui component
- **Variant Creation**: Create component variants using cva
- **Theme Variable Usage**: Use theme CSS variables
- **CSS Extraction**: Move to external CSS for complex animations or special cases

## Implementation Steps

### 1. Component Analysis

- [ ] Create list of components with significant inline styling
- [ ] For each component, document inline styles and their purpose
- [ ] Identify patterns of repeated inline styles across components

### 2. Tailwind Class Mapping

- [ ] Create mapping document for common inline styles to Tailwind equivalents
- [ ] Document cases where Tailwind cannot directly replace inline styles
- [ ] Identify responsive breakpoints used in inline media queries

### 3. Component-by-Component Migration

For each component:

- [ ] Extract inline styles to appropriate format (Tailwind, shadcn/ui, cva)
- [ ] Replace `style={{}}` props with className using the `cn()` utility
- [ ] Convert style objects to Tailwind utility classes
- [ ] Update dynamic styles to use conditional class application

### 4. Pattern Standardization

- [ ] Document common styling patterns that emerge during migration
- [ ] Create reusable style compositions for frequently used combinations
- [ ] Establish guidelines for consistent component styling

## Priority Components

Based on preliminary analysis, these components have significant inline styling that needs attention:

1. ChatInterface.jsx
2. MessageItem.jsx
3. ToolCallDisplay.jsx
4. CollapsibleOptions.jsx
5. FileItem.jsx
6. StatusBar.jsx
7. PersonaSelector.jsx

## Expected Outcomes

- Elimination of inline styles across the application
- Consistent use of Tailwind utility classes
- Proper utilization of shadcn/ui styling patterns
- Clear documentation of styling patterns for future development
- Components ready for full shadcn/ui migration

## Tracking

Progress will be tracked in a separate document to monitor the status of each component's inline style extraction.