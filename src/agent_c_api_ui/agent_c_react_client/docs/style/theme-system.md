# Theme System

## Overview

This document explains the theme system used in the Agent C React UI, detailing how light and dark modes are implemented, how theme variables are organized, and how to work with the theme system.

## Contents

- [Theme Architecture](#theme-architecture)
- [Color System](#color-system)
- [Theme Variables](#theme-variables)
- [Theme Switching](#theme-switching)
- [Using Theme Variables](#using-theme-variables)
- [Extending the Theme](#extending-the-theme)

## Theme Architecture

The theme system is built around CSS variables and uses a class-based approach for theme switching:

1. **Base Variables**: Defined in `:root` for the light theme (default)
2. **Dark Theme Overrides**: Applied when the `.dark` class is present on the root element
3. **Theme Context**: Managed by React through the `ThemeProvider` component

### Key Files

- `src/styles/common/variables.css`: Defines all theme variables
- `src/contexts/ThemeProvider.jsx`: Manages theme state and switching
- `src/lib/theme.ts`: Contains theme utility functions

## Color System

The color system uses a hierarchical approach with three levels of abstraction:

### 1. Base Color Scales

Consistent HSL values defined as CSS variables that don't change between themes:

```css
--color-blue-50: 214 100% 97%;
--color-blue-100: 214 95% 93%;
--color-blue-200: 213 97% 87%;
/* ... more color values ... */
```

These scales include:

- Gray scale
- Blue scale
- Purple scale
- Green scale
- Amber scale

### 2. Semantic Color Tokens

Purpose-based variables that reference base colors but change between themes:

```css
/* Light theme */
:root {
  --background: 210 20% 98%;
  --foreground: 224 71% 4%;
  --primary: 221 83% 53%;
  /* ... more semantic tokens ... */
}

/* Dark theme */
.dark {
  --background: 41 20% 9%;
  --foreground: 0 0% 100%;
  --primary: 213 94% 68%;
  /* ... dark theme overrides ... */
}
```

These semantic tokens are used for consistent theming of UI elements.

### 3. Component-Specific Colors

Variables for specific UI components that reference semantic colors:

```css
/* Message-specific colors */
--assistant-message-background: hsl(213, 94%, 97%);
--assistant-message-foreground: hsl(224, 76%, 30%);
/* ... more component colors ... */
```

## Theme Variables

Beyond colors, the theme system includes variables for:

### Typography

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, ...
--font-mono: 'JetBrains Mono', Menlo, Monaco, ...
--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
/* ... more typography variables ... */
```

### Spacing

```css
--spacing-1: 0.25rem;
--spacing-2: 0.5rem;
--spacing-3: 0.75rem;
/* ... more spacing variables ... */
```

### Borders and Shadows

```css
--border-radius-sm: 0.125rem;
--border-radius-md: 0.375rem;
/* ... more border variables ... */

--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05), ...
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.04), ...
/* ... more shadow variables ... */
```

### Component-Specific Variables

```css
--card-padding-x: var(--spacing-4);
--card-padding-y: var(--spacing-3);
--button-height-sm: 2rem;
/* ... more component variables ... */
```

## Theme Switching

Theme switching is handled by the `ThemeProvider` component in `src/contexts/ThemeProvider.jsx`:

1. The provider manages theme state using React's `useState`
2. It adds or removes the `.dark` class on the root element based on the current theme
3. It persists the theme preference to localStorage
4. It provides a context with the current theme and a toggle function

### Usage

```jsx
// In a component
import { useTheme } from '@/contexts/ThemeProvider';

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
```

## Using Theme Variables

### In CSS

Theme variables can be used in CSS files:

```css
.my-component {
  color: hsl(var(--foreground));
  background-color: hsl(var(--background));
  border-radius: var(--radius);
  padding: var(--spacing-4);
}
```

Note that color variables use HSL notation, so they need to be wrapped in `hsl()` function.

### With Tailwind

When using Tailwind CSS, the theme variables are mapped to Tailwind classes through the Tailwind configuration. This allows using them with Tailwind's utility classes.

```jsx
<div className="bg-background text-foreground rounded-md p-4">
  Themed content
</div>
```

## Extending the Theme

### Adding New Variables

To add new theme variables:

1. Define the variable in `:root` in `variables.css`
2. Add the dark mode override in the `.dark` section if needed
3. Use the variable in your CSS

### Adding Component-Specific Variables

For component-specific theming:

1. Add component variables to the "COMPONENT-SPECIFIC VARIABLES" section in `variables.css`
2. Use semantic naming that starts with the component name
3. Reference existing theme variables when possible

### Extending Color Scales

If new color scales are needed:

1. Add the complete scale (from 50 to 900) to the color scales section
2. Follow the existing HSL pattern
3. Create semantic tokens that reference these scales

## Related Documentation

- [Styling Guide](./styling-guide.md)
- [CSS Organization](./css-organization.md)
- [CSS Variables Reference](./css-variables-reference.md)