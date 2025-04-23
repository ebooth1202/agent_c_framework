# Agent C React Client CSS Architecture

## Overview

This directory contains the CSS styling system for the Agent C React Client. The CSS architecture follows a modular, component-based approach with a focus on maintainability, reusability, and consistency. We use a combination of component-specific CSS files and common utility styles, all built on a foundation of CSS variables for theming.

## Directory Structure

```
/styles
  /common            # Shared styles and utilities
    variables.css    # Global CSS variables for theming
    reset.css        # CSS reset and normalization
    typography.css   # Text styling and formatting
    layout.css       # Common layout patterns
    utilities.css    # Utility classes
    badges.css       # Badge styling patterns
    cards.css        # Card component patterns
    interactive.css  # Interactive element patterns
    tooltips.css     # Tooltip styling patterns
  /components        # Component-specific styles
    layout.css       # Layout component styles
    sidebar.css      # Sidebar component styles
    ... (other component files)
  main.css           # Main CSS entry point
  globals.css        # Global styles
  component-styles.css # Legacy file (being phased out)
```

## Styling Approach

### CSS Variables

We use CSS variables (custom properties) extensively for consistent theming across the application. These are defined in `common/variables.css` and include:

- Color palettes (base colors, UI elements, state colors, color scales)
- Typography (font families, sizes, weights)
- Spacing values
- Border properties (radius, width)
- Shadows
- Transitions
- Z-index layers
- Component-specific variables

### Component Styles

Each React component has its own CSS file in the `/components` directory. Component CSS files follow these conventions:

1. **Header Comment**: Each file starts with a header that identifies the component and provides a description
2. **Scoped Class Names**: Class names are prefixed with the component name to avoid conflicts
3. **Logical Grouping**: Related styles are grouped together with descriptive comments
4. **Dark Mode Support**: Dark mode variants use the `.dark` selector
5. **Responsive Design**: Media queries for different screen sizes when needed

Example component CSS structure:

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose */

/* ComponentName: Element description */
.componentname-element {
  property: value;
}

/* ComponentName: Another element */
.componentname-another-element {
  property: value;
}

/* Dark mode variants */
.dark .componentname-element {
  property: dark-mode-value;
}
```

### Common Styles

Common styles are shared patterns extracted to the `/common` directory to promote consistency and reduce duplication. These include:

- **Reset**: Normalizes browser defaults
- **Typography**: Text styles, headings, paragraphs
- **Layout**: Common layout patterns like containers, grids
- **Utilities**: Helper classes for common styling needs
- **Cards**: Card component styling patterns
- **Badges**: Badge and tag styling patterns
- **Interactive**: Buttons, links, and form control patterns
- **Tooltips**: Tooltip and popover styling patterns

## Usage Guidelines

### Adding New Component Styles

1. Create a new file in `/components` named after your component (kebab-case)
2. Follow the component styling format with proper header and comments
3. Use CSS variables from `variables.css` for consistent styling
4. Include both light and dark mode styles
5. Import the new file in `main.css`

### Modifying Existing Styles

1. Component-specific changes should be made in the component's CSS file
2. For changes that affect multiple components, consider:
   - Adding new variables to `variables.css` if it's a theming concern
   - Adding styles to the appropriate common file if it's a shared pattern
   - Using utilities.css for one-off helper classes

### Using CSS Variables

Always use CSS variables for:

- Colors: `hsl(var(--color-name))` or `hsl(var(--color-name) / 0.5)` for opacity
- Spacing: `var(--spacing-4)` instead of hardcoded pixel values
- Font properties: `var(--font-size-lg)`, `var(--font-weight-bold)`
- Transitions: `var(--transition-hover)`
- Border radius: `var(--border-radius-md)`

### Responsive Design

Use standard media query breakpoints:

```css
/* Mobile-first approach */
.element { /* Mobile styles */ }

@media (min-width: 640px) { /* Small screens (sm) */ }
@media (min-width: 768px) { /* Medium screens (md) */ }
@media (min-width: 1024px) { /* Large screens (lg) */ }
@media (min-width: 1280px) { /* Extra large screens (xl) */ }
```

## Dark Mode

Dark mode is supported via the `.dark` class applied to the root HTML element. Component styles should include dark mode variants where appropriate:

```css
/* Light mode (default) */
.element {
  color: hsl(var(--color-gray-900));
  background: hsl(var(--color-gray-100));
}

/* Dark mode */
.dark .element {
  color: hsl(var(--color-gray-100));
  background: hsl(var(--color-gray-800));
}
```

## Tailwind CSS Integration

This project uses some Tailwind CSS utility classes alongside our custom CSS. When working with both:

- Prefer component CSS files for complex components with many styles
- Tailwind utilities are useful for simple components or one-off styling needs
- For consistency, component CSS should use the same design values as Tailwind (our CSS variables match Tailwind's default scale)

## Best Practices

1. **Consistency**: Use the established patterns and variables
2. **Specificity**: Keep selector specificity low to avoid conflicts
3. **Comments**: Use comments to explain the purpose of style blocks
4. **Organization**: Group related styles together
5. **Responsive Design**: Design mobile-first, then add breakpoints
6. **Accessibility**: Ensure styles support accessibility requirements (contrast, focus states, etc.)
7. **Performance**: Avoid deeply nested selectors or excessive use of `!important`