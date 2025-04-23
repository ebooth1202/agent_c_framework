# Component-Specific Styling Documentation

This document provides guidelines and standards for how component-specific CSS files should be structured and documented in the Agent C React Client.

## Table of Contents

1. [Component CSS File Organization](#component-css-file-organization)
2. [Component CSS File Header Format](#component-css-file-header-format)
3. [Section Documentation](#section-documentation)
4. [CSS Property Documentation](#css-property-documentation)
5. [Example Component CSS Documentation](#example-component-css-documentation)
6. [Implementation Checklist](#implementation-checklist)

## Component CSS File Organization

Each React component should have its corresponding CSS file located in the `src/styles/components/` directory, named using kebab-case that matches the component's name.

For example:
- `Layout.jsx` → `layout.css`
- `AgentConfigDisplay.jsx` → `agent-config-display.css`
- `MarkdownMessage.jsx` → `markdown-message.css`

## Component CSS File Header Format

Each component CSS file should begin with a standardized header in one of two approved formats:

### Preferred Format

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose and functionality */
```

## Section Documentation

Within the CSS file, styles should be grouped into logical sections with clear comment headers:

```css
/* ComponentName: Section description */
```

For example:

```css
/* Layout: Header section */
.layout-header {
  /* styles */
}

/* Layout: Main content area */
.layout-content {
  /* styles */
}
```

## CSS Property Documentation

For complex or non-obvious CSS properties, include inline comments explaining their purpose or their Tailwind CSS equivalent:

```css
.component-element {
  display: flex; /* flex */
  align-items: center; /* items-center */
  gap: var(--spacing-4); /* gap-4 */
  z-index: 10; /* Must be above content but below header */
}
```

## Example Component CSS Documentation

Below is a complete example of a well-documented component CSS file:

```css
/* ===== COMPONENT: Layout ===== */
/* Description: Main application layout component providing the page structure with header, navigation and content area */

/* Layout: Main container */
.layout-container {
  min-height: 100vh; /* min-h-screen */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-image: linear-gradient(to bottom, var(--layout-gradient-from), var(--layout-gradient-to));
}

/* Layout: Header */
.layout-header {
  display: flex;
  align-items: center; /* items-center */
  justify-content: space-between; /* justify-between */
  padding: var(--spacing-4);
  background-color: hsl(var(--color-background));
  border-bottom: 1px solid hsl(var(--color-border));
  z-index: var(--z-index-header); /* Ensure header is above other content */
}

/* Layout: Content area */
.layout-content {
  flex: 1; /* flex-1 */
  display: flex;
  overflow: hidden;
}

/* Layout: Main content */
.layout-main {
  flex: 1; /* flex-1 */
  overflow-y: auto;
  padding: var(--spacing-4);
}

/* Dark mode styles */
.dark .layout-header {
  background-color: hsl(var(--color-background-dark));
  border-bottom-color: hsl(var(--color-border-dark));
}

/* Responsive styles */
@media (max-width: 768px) {
  .layout-header {
    padding: var(--spacing-2); /* Reduced padding on mobile */
  }
  
  .layout-main {
    padding: var(--spacing-2);
  }
}
```

## Implementation Checklist

When creating or updating component CSS files, ensure they include:

- [ ] Proper header with component name and description
- [ ] Logical grouping of styles with section comments
- [ ] Use of CSS variables from `variables.css` instead of hardcoded values
- [ ] Dark mode variants where appropriate
- [ ] Responsive styles with appropriate media queries
- [ ] Inline comments for complex properties or Tailwind equivalents
- [ ] Component-specific class names that avoid conflicts
- [ ] Accessibility considerations (focus states, color contrast, etc.)

## Best Practices

1. **Consistency**: Follow the established patterns and naming conventions
2. **Maintainability**: Write clear comments explaining the purpose of each section
3. **Reusability**: Use existing common patterns when possible
4. **Modularity**: Keep styles scoped to the component they belong to
5. **Documentation**: Update this documentation when new patterns emerge

---

By following these guidelines, we ensure that our component CSS files are well-structured, properly documented, and maintainable by the entire development team.