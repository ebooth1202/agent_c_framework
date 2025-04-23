# Theme Consistency Guidelines

## Overview

This document provides guidelines for maintaining theme consistency in the Agent C React UI, ensuring that both light and dark modes work correctly without one breaking the other.

## CSS Variable Best Practices

### 1. Always use HSL format for colors

```css
/* Correct */
--theme-background: hsl(var(--color-gray-950));

/* Avoid */
--theme-background: rgb(10, 15, 20);
```

### 2. Maintain parallel variable definitions

Every variable defined in the root scope must have a matching override in the dark theme section:

```css
:root {
  /* Light mode default */
  --theme-component-background: hsl(var(--color-gray-100));
}

.dark {
  /* Dark mode override */
  --theme-component-background: hsl(var(--color-gray-800));
}
```

### 3. Use theme variables, not direct color references

```css
/* Correct */
.component {
  background-color: var(--theme-component-background);
}

/* Avoid */
.component {
  background-color: hsl(var(--color-gray-100));
}
```

## Component Styling

### 1. Avoid conditional class application

```jsx
/* Avoid this approach */
<div className={`component ${isDarkMode ? 'dark-variant' : 'light-variant'}`}>

/* Prefer this approach */
<div className="component"> /* will use CSS variables automatically */
```

### 2. Use the `.dark` selector for targeted overrides only

Use the `.dark` selector only when you need specific overrides that can't be handled through variables:

```css
/* Use variables when possible */
.component {
  background-color: var(--theme-component-background);
}

/* For special cases only */
.dark .component .special-element {
  /* Special dark-mode only override */
}
```

## Testing Changes

When modifying theme-related CSS:

1. Test both light and dark modes explicitly
2. Verify all component states in both modes
3. Check transitions between modes
4. Test on different browsers

## Common Issues and Solutions

### Inconsistent Variable Names

Ensure variable naming is consistent across the codebase. Use kebab-case for all CSS variables.

### Missing Dark Mode Overrides

After adding a new light mode variable, always add the corresponding dark mode override.

### Hard-coded Colors

Refactor any hard-coded colors to use theme variables.

## Review Checklist

Before submitting theme-related changes, check that:

- [ ] All new variables have both light and dark mode definitions
- [ ] No hard-coded colors are used in component styles
- [ ] Components use variables instead of conditional classes
- [ ] Both themes have been tested visually