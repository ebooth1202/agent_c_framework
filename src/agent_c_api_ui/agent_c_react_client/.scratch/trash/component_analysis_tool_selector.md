# ToolSelector Component Analysis

## Component Overview

**Component Name**: ToolSelector
**File Location**: `src/components/chat_interface/ToolSelector.jsx`
**CSS File**: `src/styles/components/tool-selector.css`
**Component Purpose**: Provides a UI for selecting and equipping tools for an agent, with categorization and essential tools display
**Uses shadcn/ui Components?**: Yes (Card, CardContent, CardHeader, CardTitle, Checkbox, Button, ScrollArea, Toast, Tooltip, Badge, Tabs)
**Has Dedicated CSS File?**: Yes

## Component Structure

The component is composed of three main parts:

1. `ToolSelector` - The main component that manages overall state and rendering
2. `EssentialTools` - A sub-component for displaying non-toggleable essential tools
3. `ToolCategory` - A sub-component for rendering a category of tools with checkboxes

The component uses a tabbed interface to organize different categories of tools and provides status feedback with toasts.

## Current shadcn/ui Usage

- **Card**: Used as the main container with proper composition (CardHeader, CardContent)
- **Checkbox**: Used for tool selection
- **Button**: Used for equip action
- **Badge**: Used for essential tools
- **Tooltip**: Used to display tool descriptions
- **Tabs**: Used to organize tool categories
- **Toast**: Used for notifications

The component follows shadcn/ui patterns well, but has some custom styling that could be better aligned with shadcn/ui standards.

## Issues Identified

1. **Custom CSS Variables**: Uses custom color variables like `--primary-light` instead of shadcn/ui theme variables
2. **Hardcoded Responsive Breakpoints**: Uses hardcoded media queries instead of Tailwind's responsive utilities
3. **Shadow and Border Radius Variables**: Uses custom variables instead of shadcn/ui's design tokens
4. **Active State Handling**: Uses custom `.active` classes instead of shadcn/ui's data attributes 
5. **Error and Success States**: Has custom error and success styling instead of using shadcn/ui's alert components

## Key Functionality to Preserve

1. **Tool Categories**: Organization of tools by category with tabs
2. **Essential Tools**: Special display for non-toggleable tools
3. **Tool Selection**: Checkbox selection with active tool indication
4. **Tool Descriptions**: Tooltips for displaying tool documentation
5. **Equip Button**: Action button to equip selected tools
6. **State Feedback**: Loading states and error messages

## Styling Approach

The component uses a dedicated CSS file with proper organization:

```css
/* ===== COMPONENT: ToolSelector ===== */
/* Description: Component for selecting and equipping tools for an agent */

/* ToolSelector: Main container */
.tool-selector { ... }
```

The styles are well-organized by sub-component and include responsive styling, but use custom CSS variables instead of shadcn/ui theme variables.

## Recommendations

1. **Use shadcn/ui Theme Variables**: Replace custom color variables with proper shadcn/ui HSL variables
2. **Replace Custom Error States**: Use shadcn/ui Alert component for error messages
3. **Standardize Hover Effects**: Use consistent hover effects from shadcn/ui
4. **Use Data Attributes for States**: Replace custom `.active` classes with shadcn/ui's `data-state="active"` pattern
5. **Use Tailwind for Responsiveness**: Replace custom media queries with Tailwind's responsive utilities
6. **Consider component.json**: Verify component is properly registered in components.json

## Proposed CSS Structure Updates

```css
/* ===== COMPONENT: ToolSelector ===== */
/* Description: Component for selecting and equipping tools for an agent */

/* ToolSelector: Main container */
.tool-selector {
  width: 100%;
}

/* ToolSelector: Error message */
.tool-selector-error {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: hsl(var(--destructive) / 0.1);
  color: hsl(var(--destructive));
  border-radius: var(--radius);
  border: 1px solid hsl(var(--destructive) / 0.2);
}

/* ToolSelector: Tabs list */
.tool-selector-tabs-list {
  display: flex;
  width: 100%;
  overflow-x: auto;
  margin-bottom: 1rem;
  background-color: hsl(var(--muted));
  padding: 0.25rem;
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
}
```

## Implementation Priority

- **Priority**: Medium - Important for tool functionality but less critical than main chat interface
- **Estimated Effort**: 2-3 hours
- **Dependencies**: None - Can be implemented independently

## Migration Approach

1. Create a standardized prototype in the scratch folder
2. Update the CSS to use shadcn/ui theme variables
3. Replace custom active states with data attributes
4. Standardize the error and success handling
5. Test the prototype to ensure all functionality works
6. Replace the existing component with the standardized version

## Additional Notes

- The component already follows many shadcn/ui patterns, making this a less complex migration
- Special attention needed for tooltip positioning and interactivity
- Need to maintain the tabbed interface functionality
- Should preserve the loading state and error handling logic