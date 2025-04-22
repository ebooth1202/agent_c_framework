# CSS Refactoring Phase 2 Strategy

## Component Conversion Best Practices

### 1. Safe Conversion Process

To avoid syntax errors and ensure safe updates:

1. Use `css_get_component` to extract the current component CSS
2. Create a new version in the new format in a temporary variable
3. Double-check the formatting before writing back
4. For updates, prefer `css_update_style` for individual changes when possible
5. When updating entire components, use `workspace_replace_strings` with precise boundaries

### 2. Component Header Template

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of what the component does */
/* Location: src/path/to/ComponentName.jsx */

/* Component-specific styles here */

/* ===== END COMPONENT: ComponentName ===== */
```

### 3. Individual Style Template

```css
/* ComponentName: Description of the element */
.component-class-name {
  property: value; /* tailwind equivalent if applicable */
}
```

## Analysis Methodology

When analyzing components for consolidation opportunities:

1. Look for repeated color values that could become variables
2. Identify common spacing patterns (padding, margin, gap)
3. Note repeated structural patterns (cards, containers, headers)
4. Check for inconsistent values that should be standardized
5. Document findings in analysis files with specific examples

## Common Styles Section Structure

```css
/* ===== COMMON: Shared Styles ===== */
/* Description: Reusable styles shared across multiple components */

/* Common: Card containers */
.common-card {
  /* Base card styles */
}

/* Common: Buttons */
.common-button {
  /* Base button styles */
}

/* Common: Form elements */
.common-input {
  /* Base input styles */
}

/* ===== END COMMON: Shared Styles ===== */
```

## CSS Variables Naming Conventions

```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-muted: #9ca3af;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  
  /* Typography */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  
  /* Transitions */
  --transition-standard: 0.2s ease;
}
```

## Safe Testing Process

After each component update:

1. Run the application to verify no CSS syntax errors
2. Navigate to screens using the component
3. Test interactions with the component
4. Verify appearance in both light and dark modes

## Tools Usage Guidelines

### css_overview
Use at the beginning of a session to get an overview of current components.

### css_get_component
Use to extract a specific component's styles for inspection or modification.

### css_get_style_source
Use to examine a specific style rule including its comment.

### css_update_style
Use for targeted updates to individual style rules without affecting surrounding code.

## Handling Edge Cases

1. **Nested Selectors**: Keep parent-child relationships clear in comments
2. **Media Queries**: Include in the component section they apply to
3. **Animations**: Include in the component section or create a dedicated animations section
4. **!important Rules**: Document why they're necessary in comments