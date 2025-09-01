# Radix UI Colors Overview

*AI-optimized color system reference*

Radix Colors is a color system designed for building accessible and aesthetically pleasing user interfaces. It provides a comprehensive set of color scales with appropriate contrast ratios for building interfaces that meet WCAG accessibility standards.

## Key Features

### Accessibility Focused

Each color scale is carefully designed to provide sufficient contrast ratios for various UI elements. Color values at step 9 provide a 4.5:1 contrast ratio against white, meeting WCAG AA requirements for text.

### Consistent Scale Structure

Every color in Radix Colors follows the same scale pattern:

- **Steps 1-2**: Subtle background colors
- **Steps 3-5**: UI element backgrounds (hover, active states)
- **Steps 6-8**: Borders, separators, and solid backgrounds
- **Step 9**: Low-contrast text, solid backgrounds
- **Steps 10-12**: High-contrast text

### Design System Ready

Designed to integrate with design systems, each color scale provides values for various design contexts like text, backgrounds, borders, and interactive states.

### Light and Dark Mode Support

All color scales come with light and dark mode variants, ensuring consistent appearance and accessibility in both modes.

## Color Scale System

Radix Colors includes several distinct color sets:

### Gray Scales

The gray scales form the foundation of UI design and include:

- **Gray**: A neutral gray with a slight warmth
- **Mauve**: Purple-tinted gray (ideal for purple/violet accents)
- **Slate**: Blue-tinted gray (works well with blue)
- **Sage**: Green-tinted gray (complements green accents)
- **Olive**: Yellow/green-tinted gray (pairs with gold/lime)
- **Sand**: Yellow-tinted gray (works with brown/amber)

### Color Scales

The main colors provide a range of options for UI elements and branding:

- **Red, Tomato, Crimson**: Red hues for error states, warnings, or accent colors
- **Pink, Plum, Purple, Violet**: Purple hues for various accent elements
- **Indigo, Blue, Cyan**: Blue hues for primary actions, links, and information
- **Teal, Green, Grass, Lime**: Green hues for success states and positive elements
- **Yellow, Amber, Orange, Brown**: Yellow-orange hues for warnings and earth tones
- **Gold, Bronze**: Metallic colors for badges and special elements

### Alpha Colors

Each color also comes with alpha (transparent) variants, providing semi-transparent options for overlays, shadows, and subtle UI elements.

## Usage Patterns

### Component States

Color scales are designed to support common component states:

```jsx
// Button states using the blue scale
.button {
  /* Default state */
  background-color: var(--blue-9);
  color: white;
}

.button:hover {
  /* Hover state - slightly darker */
  background-color: var(--blue-10);
}

.button:active {
  /* Active state - even darker */
  background-color: var(--blue-11);
}

.button:disabled {
  /* Disabled state */
  background-color: var(--gray-8);
  color: var(--gray-11);
}
```

### Semantic Usage

Typical semantic usage patterns:

- **Primary actions**: Blue, Indigo
- **Success/confirmation**: Green, Grass, Teal
- **Warnings**: Yellow, Amber, Orange
- **Errors/destructive actions**: Red, Tomato
- **Neutral UI elements**: Gray, Slate, Mauve

## Installation and Setup

### CSS Variables (Recommended)

```bash
npm install @radix-ui/colors
```

```jsx
// Import the colors you need
import '@radix-ui/colors/blue.css';
import '@radix-ui/colors/blue-dark.css';
import '@radix-ui/colors/red.css';
import '@radix-ui/colors/red-dark.css';
import '@radix-ui/colors/slate.css';
import '@radix-ui/colors/slate-dark.css';
```

This will expose CSS variables you can use in your styles:

```css
.button {
  background-color: var(--blue-9);
  color: white;
}

/* In dark mode (add .dark-theme class to a parent element) */
.dark-theme .button {
  background-color: var(--blue-dark-9);
}
```

### CSS-in-JS Usage

For CSS-in-JS libraries, you can import the color values directly:

```jsx
import { blue, blueDark, slate, slateDark } from '@radix-ui/colors';

const Button = styled('button', {
  backgroundColor: blue.blue9,
  color: 'white',
  
  '.dark-theme &': {
    backgroundColor: blueDark.blue9,
  },
});
```

## Dark Mode Implementation

### Manual Dark Mode Switching

```css
/* Light mode (default) */
:root {
  --background: var(--slate-1);
  --foreground: var(--slate-12);
  --muted: var(--slate-6);
  --primary: var(--blue-9);
  --primary-foreground: white;
}

/* Dark mode */
.dark-theme {
  --background: var(--slate-dark-1);
  --foreground: var(--slate-dark-12);
  --muted: var(--slate-dark-6);
  --primary: var(--blue-dark-9);
  --primary-foreground: white;
}
```

### Media Query-Based Dark Mode

```css
/* Light mode (default) */
:root {
  --background: var(--slate-1);
  --foreground: var(--slate-12);
  /* other tokens */
}

/* Dark mode based on system preference */
@media (prefers-color-scheme: dark) {
  :root {
    --background: var(--slate-dark-1);
    --foreground: var(--slate-dark-12);
    /* other tokens */
  }
}
```

## Color Combinations

Recommended color combinations for common UI scenarios:

### Default Button

```css
.button {
  background-color: var(--slate-3);
  color: var(--slate-11);
  border: 1px solid var(--slate-7);
}

.button:hover {
  background-color: var(--slate-4);
}

.button:focus {
  box-shadow: 0 0 0 2px var(--slate-8);
}
```

### Primary Button

```css
.button-primary {
  background-color: var(--blue-9);
  color: white;
}

.button-primary:hover {
  background-color: var(--blue-10);
}

.button-primary:focus {
  box-shadow: 0 0 0 2px var(--blue-7);
}
```

### Alert/Error Message

```css
.alert-error {
  background-color: var(--red-2);
  border: 1px solid var(--red-6);
  color: var(--red-11);
}
```

### Success Message

```css
.alert-success {
  background-color: var(--green-2);
  border: 1px solid var(--green-6);
  color: var(--green-11);
}
```

## Color Accessibility Guidelines

When using Radix Colors, follow these guidelines for maximum accessibility:

1. Use steps 9-12 for text on light backgrounds
2. Use steps 1-3 for text on dark backgrounds
3. For large text (18pt or 14pt bold), step 8 can be used on a light background
4. For UI controls and graphical objects, aim for a 3:1 contrast ratio
5. Test your color combinations with accessibility tools to verify contrast ratios