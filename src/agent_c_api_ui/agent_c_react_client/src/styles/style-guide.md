# Agent C React Client CSS Style Guide

This document provides detailed guidelines for CSS styling in the Agent C React Client. It outlines the conventions, patterns, and best practices that should be followed when writing or modifying CSS in this project.

## Table of Contents

1. [CSS Variable Naming Conventions](#css-variable-naming-conventions)
2. [Component Style Structure](#component-style-structure)
3. [Class Naming Conventions](#class-naming-conventions)
4. [Comment Standards](#comment-standards)
5. [CSS Architecture Principles](#css-architecture-principles)
6. [Responsive Design Guidelines](#responsive-design-guidelines)
7. [Dark Mode Implementation](#dark-mode-implementation)
8. [Tailwind CSS Integration](#tailwind-css-integration)
9. [Accessibility Considerations](#accessibility-considerations)
10. [Performance Optimization](#performance-optimization)

## CSS Variable Naming Conventions

### Naming Pattern

CSS variables follow these naming conventions:

- Use kebab-case (lowercase with hyphens)
- Start with category/purpose
- Be specific but concise
- Use logical grouping prefixes

### Categories

```css
/* Colors */
--color-{purpose}-{variant}: value;
--color-{scale}-{number}: value;

/* Typography */
--font-{property}: value;
--font-size-{size}: value;
--font-weight-{weight}: value;

/* Spacing */
--spacing-{size}: value;

/* Borders */
--border-{property}-{size}: value;
--border-radius-{size}: value;

/* Shadows */
--shadow-{size}: value;

/* Transitions */
--transition-{type}: value;

/* Z-index layers */
--z-index-{layer}: value;

/* Component-specific */
--{component}-{property}: value;
```

### Examples

```css
/* Color variables */
--color-primary: 211 96% 62%;
--color-gray-800: 215 28% 17%;

/* Typography variables */
--font-sans: 'Inter', sans-serif;
--font-size-xl: 1.25rem;

/* Component variables */
--card-padding-x: var(--spacing-4);
--layout-max-width: 80rem;
```

## Component Style Structure

### File Organization

Each component should have its own CSS file in the `/components` directory, named after the component using kebab-case.

### Internal Structure

Component CSS files should follow this structure:

1. **Component Header**: Component name and description
2. **Base Elements**: Core component elements
3. **Variations**: Component variations or states
4. **Dark Mode Styles**: Dark mode overrides
5. **Responsive Styles**: Media queries for different screen sizes

### Example

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose */

/* ComponentName: Main element */
.componentname-element {
  property: value;
}

/* ComponentName: Variation */
.componentname-element.variation {
  property: value;
}

/* Dark mode variants */
.dark .componentname-element {
  property: dark-mode-value;
}

/* Responsive styles */
@media (min-width: 768px) {
  .componentname-element {
    property: tablet-value;
  }
}
```

## Class Naming Conventions

### BEM-Inspired Approach

We use a simplified BEM-inspired naming approach with component prefixing:

- **Component prefix**: The component name in lowercase
- **Element**: Describes a part of the component
- **Modifier**: Indicates a variation or state

```
.{component}-{element}[.{modifier}]
```

### Examples

```css
/* Component element */
.layout-container {
  /* styles */
}

/* Nested element */
.layout-header {
  /* styles */
}

/* Element with modifier */
.button-icon.small {
  /* styles */
}
```

### Utility Classes

Utility classes are prefixed with their purpose:

```css
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

## Comment Standards

### Component Headers

Each component CSS file should begin with a header:

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose */
```

### Section Comments

Use section comments to group related styles:

```css
/* ComponentName: Section description */
```

### Inline Comments

Include inline comments for complex rules or to explain the purpose of specific properties:

```css
.element {
  display: flex; /* Required for proper alignment */
  z-index: 10; /* Must be below header (z-index: 20) */
}
```

### Tailwind Equivalents

When using CSS properties that have Tailwind equivalents, note them in comments:

```css
.element {
  padding: var(--spacing-4); /* p-4 */
  margin-top: var(--spacing-2); /* mt-2 */
}
```

## CSS Architecture Principles

### Separation of Concerns

- **Component Styles**: Specific to a single component
- **Common Patterns**: Reusable patterns shared across components
- **Utilities**: Single-purpose helper classes
- **Variables**: Design tokens for theming

### Specificity Management

- Keep selector specificity as low as possible
- Avoid using `!important` except in utilities
- Use class-based selectors rather than element or attribute selectors
- Limit nesting to maximum 2-3 levels

### CSS Inheritance

- Use inheritance for appropriate properties (typography, color)
- Set base styles on container elements
- Override only what's necessary in child elements

## Responsive Design Guidelines

### Mobile-First Approach

Default styles should target mobile devices, with media queries adding complexity for larger screens:

```css
/* Mobile by default */
.element {
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .element {
    width: 50%;
  }
}
```

### Standard Breakpoints

```css
@media (min-width: 640px) { /* Small screens (sm) */ }
@media (min-width: 768px) { /* Medium screens (md) */ }
@media (min-width: 1024px) { /* Large screens (lg) */ }
@media (min-width: 1280px) { /* Extra large screens (xl) */ }
```

### Responsive Strategies

1. **Fluid Layout**: Use percentages, flexbox, and grid
2. **Relative Units**: Prefer rem/em over fixed pixel values
3. **Container Queries**: For component-specific responsiveness
4. **Responsive Typography**: Scale font sizes at different breakpoints

## Dark Mode Implementation

### Using the Dark Class

Dark mode is implemented using a `.dark` class on the root element:

```css
/* Light mode (default) */
.element {
  color: hsl(var(--color-gray-900));
  background: hsl(var(--color-gray-100));
}

/* Dark mode */
.dark .element {
  color: hsl(var(--color-gray-50));
  background: hsl(var(--color-gray-800));
}
```

### Color Implementation

For colors that need to support dark mode:

1. Define the base color using HSL in variables.css
2. Use the `hsl()` function to apply the color
3. Override in dark mode when needed

```css
:root {
  --color-background: 0 0% 100%;
}

.dark {
  --color-background: 222 47% 11%;
}

.element {
  background-color: hsl(var(--color-background));
}
```

### Alpha Transparency

Use the HSL alpha channel for transparency:

```css
/* With opacity */
background-color: hsl(var(--color-primary) / 0.5);
```

## Tailwind CSS Integration

### When to Use Which

- **Component CSS Files**: For complex components with multiple elements and states
- **Tailwind Classes**: For simple components or quick one-off styling needs

### Maintaining Consistency

- CSS variables match Tailwind's design scale
- Document Tailwind equivalents in comments when applicable
- When overriding Tailwind, follow the same naming convention

### Common Patterns

```css
/* In CSS file */
.element {
  display: flex; /* flex */
  align-items: center; /* items-center */
  gap: var(--spacing-4); /* gap-4 */
}

/* In JSX with Tailwind */
<div className="flex items-center gap-4">...</div>
```

## Accessibility Considerations

### Focus States

Ensure all interactive elements have visible focus states:

```css
.interactive-element:focus-visible {
  outline: var(--border-width-medium) solid hsl(var(--color-primary));
  outline-offset: 2px;
}
```

### Color Contrast

- Maintain WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text)
- Test both light and dark modes
- Don't rely solely on color to convey information

### Motion and Animation

Respect user preferences for reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    transition: none;
    animation: none;
  }
}
```

## Performance Optimization

### Selector Efficiency

- Use class selectors when possible
- Avoid deeply nested selectors
- Limit universal selectors (*)

### Critical CSS

- Place critical styles in the head
- Defer non-critical CSS
- Use appropriate media queries to conditionally load styles

### Reflow and Repaint

Use properties that trigger fewer reflows:

- Prefer `transform` over position changes
- Prefer `opacity` over visibility changes
- Batch DOM updates that could trigger reflows

```css
/* Better performance */
.element {
  transform: translateY(10px);
  opacity: 0.8;
}

/* Worse performance */
.element {
  top: 10px;
  position: relative;
  visibility: 0.8;
}
```

---

By following these guidelines, we maintain a consistent, maintainable CSS codebase that provides a great user experience across all devices and themes. For questions or clarifications, contact the UI development team.