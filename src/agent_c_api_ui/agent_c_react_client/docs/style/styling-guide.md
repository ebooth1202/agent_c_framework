# Styling Guide

## Overview

This document provides a comprehensive guide to the styling approach used in the Agent C React UI. It covers the core principles, technologies, and patterns used to create a consistent, maintainable, and visually cohesive application.

## Contents

- [Styling Philosophy](#styling-philosophy)
- [Technology Stack](#technology-stack)
- [Theme System](#theme-system)
- [CSS Organization](#css-organization)
- [Component Styling Patterns](#component-styling-patterns)
- [Best Practices](#best-practices)

## Styling Philosophy

The Agent C React UI follows several key principles for styling:

1. **Separation of Concerns**: Styling is separated from component logic where possible, using dedicated CSS files for components.

2. **Consistency Through Variables**: CSS variables are used extensively to maintain consistency and enable theming.

3. **Component-First Approach**: Styles are organized around components rather than pages or features.

4. **Progressive Enhancement**: Base functionality is styled first, with additional styling for interactive and animated elements added secondarily.

5. **Responsive By Default**: All components are designed to be responsive from the start.

## Technology Stack

The application uses a combination of styling technologies:

### Tailwind CSS

Tailwind CSS provides utility classes for rapid development and consistent spacing, typography, and colors. It's configured to use the application's design tokens through CSS variables.

### CSS Variables

CSS variables (custom properties) are extensively used for theming and consistent values across the application. These are defined in `src/styles/common/variables.css`.

### Component CSS Files

Each React component has a corresponding CSS file in `src/styles/components/` that contains component-specific styles. These files follow a standardized format with clear section comments.

### shadcn/ui Components

The application uses shadcn/ui components which are built with Radix UI primitives and styled with Tailwind CSS. These components are integrated with the application's theme system.

## Theme System

The application supports light and dark modes through a comprehensive theme system:

### Theme Variables

Colors and other theme-specific values are defined as CSS variables in two contexts:

- `:root` selector for light mode (default)
- `.dark` selector for dark mode

### Color System

The color system is organized into:

1. **Base Color Scales**: HSL color values that remain consistent between themes (e.g., `--color-blue-500`)

2. **Semantic Color Tokens**: Purpose-based variables that reference base colors but change between themes (e.g., `--primary`, `--background`)

3. **Component-Specific Colors**: Variables for specific UI components that reference semantic colors

### Theme Switching

Theme switching is handled by the `ThemeProvider` context which toggles the `.dark` class on the root element.

## CSS Organization

CSS is organized into a structured hierarchy:

### Directory Structure

```
src/styles/
  common/           # Global styles and variables
    reset.css       # CSS reset/normalization
    variables.css   # Global CSS variables
    typography.css  # Typography styles
    utilities.css   # Utility classes
  components/       # Component-specific styles
    layout.css      # Layout component styles
    button.css      # Button component styles
    ...
  globals.css       # Global styles and imports
  main.css         # Main CSS entry point
```

### File Structure

Component CSS files follow a standardized format:

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of the component */

/* ComponentName: Section description */
.component-class {
  /* styles */
}

/* ComponentName: Another section */
.another-class {
  /* styles */
}
```

## Component Styling Patterns

The application uses several patterns for styling components:

### BEM-Inspired Class Naming

Class names generally follow a BEM-inspired pattern for clarity and specificity:

```css
.component-name {}
.component-name__element {}
.component-name--modifier {}
```

### CSS Variable Usage

Components use CSS variables for themeable properties:

```css
.component {
  color: hsl(var(--foreground));
  background-color: hsl(var(--background));
  border-radius: var(--radius);
}
```

### Mobile-First Responsive Design

Styles start with mobile layouts and use media queries to adapt to larger screens:

```css
.component {
  width: 100%;
}

@media (min-width: 768px) {
  .component {
    width: 50%;
  }
}
```

### State Classes

Interactive states are often managed with state classes:

```css
.component {}
.component.is-active {}
.component.is-disabled {}
```

## Best Practices

### Do

- Use CSS variables for any value that might change with theme
- Keep component styles in their dedicated CSS files
- Use semantic class names that describe the component's purpose
- Follow the established file and comment structure for consistency
- Add descriptive comments for complex styling logic

### Don't

- Use hard-coded color values (use CSS variables instead)
- Create overly specific selectors that are hard to override
- Mix different styling methodologies within the same component
- Duplicate styles that could be shared through variables or utility classes

## Related Documentation

- [CSS Organization](./css-organization.md)
- [Theme System](./theme-system.md)
- [CSS Variables Reference](./css-variables-reference.md)