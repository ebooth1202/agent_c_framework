# ToolCallDisplay Standardization Plan

## Current Analysis

### ToolCallDisplay.jsx
- Already uses shadcn/ui components (Card, Collapsible, Badge)
- Uses Tailwind classes for styling
- Uses Lucide icons
- Uses cn() utility for className composition
- Properly handles tool calls data and validation
- Follows correct shadcn/ui usage patterns

### tool-call-display.css
- Contains styles for elements that are not easily expressed with Tailwind
- Contains some styles for ToolCallItem that should be moved to tool-call-item.css
- Uses HSL CSS variables for theming

### ToolCallItem.jsx
- Uses shadcn/ui components (Card, Collapsible)
- Has formatting utilities for JSON data
- Handles both integrated and standalone display modes
- Implements copy functionality

### tool-call-item.css and tool-call-item-integrated.css
- Contains specific styling for ToolCallItem in both display modes
- Some duplication between files
- Uses CSS variables for theming

## Improvement Areas

1. **Consolidate CSS Files**: tool-call-item.css and tool-call-item-integrated.css should be consolidated
2. **Utilize More shadcn/ui Components**: Use more shadcn/ui components like Badge where appropriate
3. **Standardize Theme Variables**: Ensure all color references use the standardized theme variables
4. **Improve Accessibility**: Add ARIA attributes for better screen reader support
5. **Add PropTypes Validation**: Add proper PropTypes validation for components
6. **Consistent Spacing**: Use Tailwind spacing classes consistently
7. **Optimize Component Structure**: Consider component splitting for better code organization

## Implementation Plan

### 1. ToolCallDisplay.jsx Updates

- Add PropTypes validation
- Add proper ARIA attributes for accessibility
- Simplify class usage with more Tailwind utility classes
- Use shadcn Badge component more consistently
- Improve responsive design for mobile

### 2. tool-call-display.css Updates

- Standardize CSS variable usage
- Remove styles that should be in tool-call-item.css
- Follow component CSS file header format
- Organize CSS with clear section headers

### 3. ToolCallItem.jsx Updates

- Add PropTypes validation
- Improve formatting utilities for better error handling
- Enhance accessibility with ARIA attributes
- Use shadcn/ui Button component for actions
- Standardize integrated and standalone mode implementations

### 4. Consolidate tool-call-item CSS Files

- Merge tool-call-item.css and tool-call-item-integrated.css
- Use CSS variables consistently
- Organize with clear section headers
- Remove duplicated code

## Implementation Steps

1. Update ToolCallDisplay.jsx
2. Update tool-call-display.css
3. Update ToolCallItem.jsx
4. Consolidate and update tool-call-item CSS files
5. Test in both light and dark modes
6. Verify accessibility
7. Test on mobile and desktop viewports