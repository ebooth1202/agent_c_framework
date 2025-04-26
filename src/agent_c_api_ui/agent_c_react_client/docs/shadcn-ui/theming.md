# Theming in Shadcn UI

Created: 2025-04-24
Source: theming.mdx

## Overview

Shadcn UI supports two methods for theming your components: CSS variables (recommended) and utility classes. This document covers both approaches and provides guidance on customization.

## CSS Variables Approach

Configure your project to use CSS variables by setting `tailwind.cssVariables` to `true` in your `components.json` file:

```json
{
  "tailwind": {
    "cssVariables": true
  }
}
```

This enables using semantic class names that reference your theme variables:

```tsx
<div className="bg-background text-foreground" />
```

## Utility Classes Approach

Alternatively, you can use Tailwind utility classes directly by setting `tailwind.cssVariables` to `false` in your `components.json` file:

```json
{
  "tailwind": {
    "cssVariables": false
  }
}
```

This approach uses utility classes with your chosen base color:

```tsx
<div className="bg-zinc-950 dark:bg-white text-zinc-50 dark:text-zinc-950" />
```

## Color Convention

Shadcn UI uses a simple convention for colors:
- `background` - Used for component background colors
- `foreground` - Used for text/foreground colors

The `background` suffix is omitted when the variable is used as the background color of a component. For example, with the following CSS variables:

```css
--primary: oklch(0.205 0 0);
--primary-foreground: oklch(0.985 0 0);
```

You would use them as:

```tsx
<div className="bg-primary text-primary-foreground">Hello</div>
```

## Available Variables

Shadcn UI provides a comprehensive set of theme variables including:

- **Core variables**
  - `--radius` - Border radius for components
  - `--background`/`--foreground` - Base page colors

- **Component-specific variables**
  - `--card`/`--card-foreground` - Card component colors
  - `--popover`/`--popover-foreground` - Popover colors
  - `--primary`/`--primary-foreground` - Primary action colors
  - `--secondary`/`--secondary-foreground` - Secondary action colors
  - `--muted`/`--muted-foreground` - Muted/subdued element colors
  - `--accent`/`--accent-foreground` - Accent colors
  - `--destructive` - Destructive action colors

- **UI element variables**
  - `--border` - Border colors
  - `--input` - Form input colors
  - `--ring` - Focus ring colors

- **Data visualization**
  - `--chart-1` through `--chart-5` - Chart color scales

- **Sidebar variables**
  - `--sidebar`/`--sidebar-foreground` - Sidebar colors
  - `--sidebar-primary`/`--sidebar-primary-foreground` - Sidebar primary colors
  - `--sidebar-accent`/`--sidebar-accent-foreground` - Sidebar accent colors
  - `--sidebar-border` - Sidebar border colors
  - `--sidebar-ring` - Sidebar focus ring colors

## Adding Custom Colors

To add new custom colors to your theme:

1. Add the variables to your CSS file:

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}

.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}

@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

2. Use the new color classes in your components:

```tsx
<div className="bg-warning text-warning-foreground" />
```

## Base Color Options

Shadcn UI provides several base color palettes that you can use as starting points:

- Stone - Warm gray tones
- Zinc - Neutral gray with subtle blue undertones
- Neutral - Pure grayscale
- Gray - Slightly cooler gray
- Slate - Blue-gray

The base color is specified in your `components.json` file and cannot be changed after initialization without reinstalling components.

```json
{
  "tailwind": {
    "baseColor": "zinc"
  }
}
```

Each color palette provides a complete set of variables for both light and dark modes, optimized for accessibility and consistent aesthetics.