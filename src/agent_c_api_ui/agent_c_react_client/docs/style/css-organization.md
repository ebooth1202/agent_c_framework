# CSS Organization

## Overview

This document details how CSS is organized within the Agent C React UI project. It explains the file structure, naming conventions, and methodologies used to maintain a scalable and maintainable styling system.

## Contents

- [Directory Structure](#directory-structure)
- [File Naming and Organization](#file-naming-and-organization)
- [Component CSS Files](#component-css-files)
- [Global and Common Styles](#global-and-common-styles)
- [Import Structure](#import-structure)
- [Naming Conventions](#naming-conventions)

## Directory Structure

The CSS files in the project are organized into a clear directory structure:

```
src/styles/
  common/           # Global styles and variables
    reset.css       # CSS reset/normalization
    variables.css   # Global CSS variables
    typography.css  # Typography styles
    utilities.css   # Utility classes
    badges.css      # Global badge styles
    cards.css       # Global card styles
    interactive.css # Interactive element styles
    layout.css      # Layout utilities
    tooltips.css    # Tooltip styles
  components/       # Component-specific styles
    layout.css      # Layout component styles
    app-sidebar.css # Sidebar component styles
    chat-interface.css # Chat interface styles
    ...
  globals.css       # Global styles and imports
  main.css         # Main CSS entry point
```

## File Naming and Organization

### Naming Convention

CSS files are named using kebab-case that corresponds to the component they style:

- React component: `ComponentName.jsx`
- CSS file: `component-name.css`

For example:
- `Layout.jsx` → `layout.css`
- `ChatInterface.jsx` → `chat-interface.css`
- `ToolCallDisplay.jsx` → `tool-call-display.css`

### Component-to-CSS Mapping

Each React component should have a corresponding CSS file in the `src/styles/components/` directory. This one-to-one mapping ensures styles can be easily located and maintained.

## Component CSS Files

### File Header Format

Each component CSS file begins with a standardized header:

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose and functionality */
```

### Section Organization

Within the file, styles are grouped into logical sections with clear comment headers:

```css
/* ComponentName: Section description */
```

For example:

```css
/* ===== COMPONENT: Layout ===== */
/* Description: Main application layout component providing the page structure */

/* Layout: Main content area */
.layout-main {
  /* styles */
}

/* Layout: Sidebar area */
.layout-sidebar {
  /* styles */
}
```

### Class Naming Pattern

Classes within component files generally follow a component-scoped naming approach:

```css
.component-name {}
.component-name__element {}
.component-name--variant {}
```

This pattern ensures that styles remain scoped to their components and reduces the risk of collision.

## Global and Common Styles

### Variables

Global CSS variables are defined in `src/styles/common/variables.css` and are organized into logical groups:

- Color scales (base HSL values)
- Semantic color tokens (theme-specific values)
- Typography variables
- Spacing values
- Border properties
- Shadow definitions
- Z-index layers
- Component-specific variables

### Reset and Base Styles

The `reset.css` file provides normalization of browser styles, ensuring a consistent starting point across different browsers.

### Utility Styles

Common utility styles are defined in `utilities.css` and provide reusable classes for common styling needs:

- Text alignment and formatting
- Flexbox utilities
- Spacing helpers
- Visibility controls

## Import Structure

The main CSS entry point is `src/styles/main.css`, which imports other CSS files in the correct order:

1. Common styles (reset, variables, etc.)
2. Global component styles
3. Utility styles
4. Tailwind CSS directives

Individual component styles are imported separately in their respective components or through a component style aggregator.

## Naming Conventions

### Class Naming

The project uses a hybrid naming approach:

1. **Component-Scoped Classes**: For component-specific styling
   ```css
   .component-name {}
   .component-name__element {}
   ```

2. **Utility Classes**: For commonly reused styles
   ```css
   .flex {}
   .text-center {}
   ```

3. **State Classes**: For interactive states
   ```css
   .is-active {}
   .is-disabled {}
   ```

### Variable Naming

CSS variables follow a structured naming pattern:

1. **General Purpose**: `--category-name`
   ```css
   --spacing-4: 1rem;
   --font-size-lg: 1.125rem;
   ```

2. **Component-Specific**: `--component-property`
   ```css
   --card-padding-x: var(--spacing-4);
   --input-border-radius: var(--border-radius-md);
   ```

3. **Theme Variables**: Semantic tokens that change with theme
   ```css
   --background: 210 20% 98%;
   --foreground: 224 71% 4%;
   ```

## Best Practices

### File Organization

- Keep files focused on a single component or concern
- Break large CSS files into smaller, more manageable ones
- Group related styles within the same file using clear section comments

### Class Naming

- Use descriptive, purpose-based names
- Keep specificity as low as reasonably possible
- Avoid using IDs for styling
- Use consistent naming patterns throughout the project

### CSS Variables

- Define base variables in `variables.css`
- Use component-specific variables for values that are used multiple times within a component
- Reference global variables for consistency with the design system

## Related Documentation

- [Styling Guide](./styling-guide.md)
- [Theme System](./theme-system.md)
- [CSS Variables Reference](./css-variables-reference.md)