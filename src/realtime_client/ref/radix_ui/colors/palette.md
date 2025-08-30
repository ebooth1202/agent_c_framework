# Radix UI Color Palette Composition

*AI-optimized color palette reference*

Radix Colors provides a systematic approach to color palette composition, with each color scale carefully constructed to ensure accessibility, visual harmony, and functional utility across different UI elements and states.

## Scale Structure

Each color in the Radix system has 12 steps plus alpha (transparent) variants. The steps follow a consistent pattern:

| Steps | Purpose |
|-------|--------|
| 1-2 | Subtle backgrounds, app backgrounds |
| 3-5 | UI element backgrounds, hover/active states |
| 6-8 | Borders, separators, solid backgrounds |
| 9 | Low-contrast text, solid backgrounds (meets WCAG AA on white) |
| 10-12 | High-contrast text (steps 11-12 meet WCAG AAA) |

## Light and Dark Scales

Each color has dedicated light and dark scales. The dark scales are not simply inverted light scales; they're carefully designed to maintain appropriate contrast and visual harmony in dark mode interfaces.

### Example: Blue Scale

#### Light Mode Values

```css
--blue-1: hsl(206, 100%, 99.2%);
--blue-2: hsl(210, 100%, 98.0%);
--blue-3: hsl(209, 100%, 96.5%);
--blue-4: hsl(210, 98.8%, 94.0%);
--blue-5: hsl(209, 95.0%, 90.1%);
--blue-6: hsl(209, 81.2%, 84.5%);
--blue-7: hsl(208, 77.5%, 76.9%);
--blue-8: hsl(206, 81.9%, 65.3%);
--blue-9: hsl(206, 100%, 50.0%);
--blue-10: hsl(208, 100%, 47.3%);
--blue-11: hsl(211, 100%, 43.2%);
--blue-12: hsl(211, 100%, 15.0%);
```

#### Dark Mode Values

```css
--blue-dark-1: hsl(212, 35.0%, 9.2%);
--blue-dark-2: hsl(216, 50.0%, 11.8%);
--blue-dark-3: hsl(214, 59.4%, 15.3%);
--blue-dark-4: hsl(214, 65.8%, 17.9%);
--blue-dark-5: hsl(213, 71.2%, 20.2%);
--blue-dark-6: hsl(212, 77.4%, 23.1%);
--blue-dark-7: hsl(211, 85.1%, 27.4%);
--blue-dark-8: hsl(211, 89.7%, 34.1%);
--blue-dark-9: hsl(206, 100%, 50.0%);
--blue-dark-10: hsl(209, 100%, 60.6%);
--blue-dark-11: hsl(210, 100%, 66.1%);
--blue-dark-12: hsl(206, 98.0%, 95.8%);
```

## Alpha (Transparent) Variants

Each color also includes alpha variants, which provide semi-transparent versions useful for overlays, shadows, and subtle UI elements.

```css
--blue-a1: hsla(206, 100%, 50.0%, 0.016);
--blue-a2: hsla(210, 100%, 50.0%, 0.040);
--blue-a3: hsla(209, 100%, 50.0%, 0.071);
--blue-a4: hsla(210, 100%, 50.0%, 0.122);
--blue-a5: hsla(208, 98.6%, 47.5%, 0.193);
--blue-a6: hsla(209, 99.4%, 45.7%, 0.301);
--blue-a7: hsla(208, 99.9%, 43.8%, 0.443);
--blue-a8: hsla(206, 99.8%, 45.1%, 0.702);
--blue-a9: hsla(206, 100%, 50.0%, 1.000);
--blue-a10: hsla(208, 100%, 47.2%, 1.000);
--blue-a11: hsla(211, 100%, 43.2%, 1.000);
--blue-a12: hsla(211, 100%, 15.0%, 1.000);
```

## Semantic Color Mapping

A systematic approach to applying colors to UI elements creates a consistent user experience:

### Text Colors

```css
:root {
  /* Primary text */
  --text-primary: var(--slate-12);
  
  /* Secondary text */
  --text-secondary: var(--slate-11);
  
  /* Muted text */
  --text-muted: var(--slate-10);
  
  /* Accent text */
  --text-accent: var(--blue-9);
}

.dark-theme {
  --text-primary: var(--slate-dark-12);
  --text-secondary: var(--slate-dark-11);
  --text-muted: var(--slate-dark-10);
  --text-accent: var(--blue-dark-9);
}
```

### Background Colors

```css
:root {
  /* App background */
  --bg-app: var(--slate-1);
  
  /* Subtle backgrounds */
  --bg-subtle: var(--slate-2);
  
  /* UI element backgrounds */
  --bg-element: white;
  --bg-element-hover: var(--slate-3);
  --bg-element-active: var(--slate-4);
  
  /* Accent backgrounds */
  --bg-accent: var(--blue-9);
  --bg-accent-hover: var(--blue-10);
  --bg-accent-active: var(--blue-11);
}

.dark-theme {
  --bg-app: var(--slate-dark-1);
  --bg-subtle: var(--slate-dark-2);
  --bg-element: var(--slate-dark-3);
  --bg-element-hover: var(--slate-dark-4);
  --bg-element-active: var(--slate-dark-5);
  --bg-accent: var(--blue-dark-9);
  --bg-accent-hover: var(--blue-dark-10);
  --bg-accent-active: var(--blue-dark-11);
}
```

### Border Colors

```css
:root {
  /* Subtle borders */
  --border-subtle: var(--slate-6);
  
  /* Default borders */
  --border-default: var(--slate-7);
  
  /* Emphasized borders */
  --border-emphasis: var(--slate-8);
  
  /* Accent borders */
  --border-accent: var(--blue-8);
}

.dark-theme {
  --border-subtle: var(--slate-dark-6);
  --border-default: var(--slate-dark-7);
  --border-emphasis: var(--slate-dark-8);
  --border-accent: var(--blue-dark-8);
}
```

## Creating Color Combinations

### UI Element State Mapping

Consistent mapping for interactive elements:

```css
/* Button - Default (gray) */
.button {
  background-color: var(--slate-3);
  color: var(--slate-11);
  border: 1px solid var(--slate-7);
}

.button:hover {
  background-color: var(--slate-4);
}

.button:active {
  background-color: var(--slate-5);
}

/* Button - Primary */
.button-primary {
  background-color: var(--blue-9);
  color: white;
  border: none;
}

.button-primary:hover {
  background-color: var(--blue-10);
}

.button-primary:active {
  background-color: var(--blue-11);
}

/* Button - Danger */
.button-danger {
  background-color: var(--red-9);
  color: white;
  border: none;
}

.button-danger:hover {
  background-color: var(--red-10);
}

.button-danger:active {
  background-color: var(--red-11);
}
```

### Message Types

Consistent color application for different message types:

```css
/* Info message */
.message-info {
  background-color: var(--blue-2);
  border: 1px solid var(--blue-6);
  color: var(--blue-11);
}

/* Success message */
.message-success {
  background-color: var(--green-2);
  border: 1px solid var(--green-6);
  color: var(--green-11);
}

/* Warning message */
.message-warning {
  background-color: var(--amber-2);
  border: 1px solid var(--amber-6);
  color: var(--amber-11);
}

/* Error message */
.message-error {
  background-color: var(--red-2);
  border: 1px solid var(--red-6);
  color: var(--red-11);
}
```

## Building Custom Palette Combinations

When building a custom palette, consider these guidelines:

### Primary/Secondary Color Selection

1. Select a primary color (often blue, purple, or green variants)
2. Choose a complementary or analogous secondary color
3. Select a gray scale that harmonizes with your choices:
   - With blue primaries: Use Slate
   - With purple primaries: Use Mauve
   - With green primaries: Use Sage
   - With yellow/orange primaries: Use Sand or Olive

### Semantic Color Assignment

1. Use the primary color for main actions and brand elements
2. Use red/tomato for destructive actions and errors
3. Use amber/yellow for warnings
4. Use green for success states
5. Use your selected gray scale for most UI surfaces

### Dark Mode Adaptation

For dark mode, don't simply invert your light theme:

1. Use the corresponding dark scale (e.g., blueDark instead of blue)
2. Adjust contrast - dark backgrounds need higher contrast for text
3. Reduce saturation for large areas to prevent eye strain
4. Maintain accessible contrast ratios (test with tools)

## Performance Optimization

To optimize performance when using Radix Colors:

1. Import only the colors you need
2. Use CSS variables to create a semantic layer
3. Consider using a bundler to tree-shake unused colors

```jsx
// Import only what you need
import '@radix-ui/colors/blue.css';
import '@radix-ui/colors/blue-dark.css';
import '@radix-ui/colors/red.css';
import '@radix-ui/colors/red-dark.css';
import '@radix-ui/colors/slate.css';
import '@radix-ui/colors/slate-dark.css';
```