# CSS Variable Mapping for shadcn/ui Integration

## Overview

This document maps our custom CSS variables to the standard shadcn/ui theme variables to ensure consistency across the application. It provides a reference for converting existing styles to use the standard shadcn/ui approach.

## Tailwind/shadcn CSS Variables (shadcn format)

These are the standard CSS variables used by shadcn/ui components when using the Tailwind plugin. They use the HSL format without the `hsl()` wrapper and are accessed in CSS files using `hsl(var(--variable))` syntax.

```css
--background: 210 40% 98%;          /* Light mode background */
--foreground: 221 39% 11%;          /* Light mode text */
--card: 0 0% 100%;                  /* Card background */
--card-foreground: 222.2 84% 4.9%;  /* Card text */
--popover: 0 0% 100%;               /* Popover background */
--popover-foreground: 222.2 84% 4.9%; /* Popover text */
--primary: 221 83% 53%;             /* Primary color (blue) */
--primary-foreground: 210 40% 98%;  /* Text on primary background */
--secondary: 210 40% 96.1%;         /* Secondary color */
--secondary-foreground: 222.2 47.4% 11.2%; /* Text on secondary background */
--muted: 210 40% 96.1%;             /* Muted background */
--muted-foreground: 215.4 16.3% 46.9%; /* Muted text */
--accent: 210 40% 96.1%;            /* Accent background */
--accent-foreground: 222.2 47.4% 11.2%; /* Text on accent background */
--destructive: 0 84.2% 60.2%;       /* Destructive color (red) */
--destructive-foreground: 210 40% 98%; /* Text on destructive background */
--border: 214.3 31.8% 91.4%;        /* Border color */
--input: 214.3 31.8% 91.4%;         /* Input border */
--ring: 221 83% 53%;                /* Focus ring color */
--radius: 0.5rem;                   /* Border radius base */
```

## Current Custom Theme Variables (Our format)

These are the custom CSS variables we've defined in our application. They use a mix of HSL values and direct references to other variables.

```css
--theme-background: var(--color-gray-100);      /* Background color */
--theme-foreground: var(--color-gray-900);      /* Text color */
--theme-card: var(--color-gray-50);             /* Card background */
--theme-card-foreground: var(--color-gray-900); /* Card text */
--theme-popover: var(--color-gray-50);          /* Popover background */
--theme-popover-foreground: var(--color-gray-900); /* Popover text */
--theme-primary: var(--color-blue-600);         /* Primary color */
--theme-primary-foreground: white;              /* Text on primary */
--theme-secondary: var(--color-blue-100);       /* Secondary color */
--theme-secondary-foreground: var(--color-blue-800); /* Text on secondary */
--theme-muted: var(--color-gray-100);           /* Muted background */
--theme-muted-foreground: var(--color-gray-600); /* Muted text */
--theme-accent: var(--color-purple-100);        /* Accent background */
--theme-accent-foreground: var(--color-purple-800); /* Text on accent */
--theme-border: var(--color-gray-200);          /* Border color */
--theme-input: var(--color-gray-300);           /* Input border */
```

## Mapping Table

| Our Variable | shadcn/ui Variable | Notes |
|--------------|-------------------|-------|
| `--theme-background` | `--background` | Use `hsl(var(--background))` in CSS |
| `--theme-foreground` | `--foreground` | Use `hsl(var(--foreground))` in CSS |
| `--theme-card` | `--card` | Use `hsl(var(--card))` in CSS |
| `--theme-card-foreground` | `--card-foreground` | Use `hsl(var(--card-foreground))` in CSS |
| `--theme-popover` | `--popover` | Use `hsl(var(--popover))` in CSS |
| `--theme-popover-foreground` | `--popover-foreground` | Use `hsl(var(--popover-foreground))` in CSS |
| `--theme-primary` | `--primary` | Use `hsl(var(--primary))` in CSS |
| `--theme-primary-foreground` | `--primary-foreground` | Use `hsl(var(--primary-foreground))` in CSS |
| `--theme-secondary` | `--secondary` | Use `hsl(var(--secondary))` in CSS |
| `--theme-secondary-foreground` | `--secondary-foreground` | Use `hsl(var(--secondary-foreground))` in CSS |
| `--theme-muted` | `--muted` | Use `hsl(var(--muted))` in CSS |
| `--theme-muted-foreground` | `--muted-foreground` | Use `hsl(var(--muted-foreground))` in CSS |
| `--theme-accent` | `--accent` | Use `hsl(var(--accent))` in CSS |
| `--theme-accent-foreground` | `--accent-foreground` | Use `hsl(var(--accent-foreground))` in CSS |
| `--theme-border` | `--border` | Use `hsl(var(--border))` in CSS |
| `--theme-input` | `--input` | Use `hsl(var(--input))` in CSS |

## Component-Specific Variables

We've defined additional component-specific variables that don't have direct equivalents in shadcn/ui. For these, we should create consistent naming and usage patterns:

| Our Component Variable | Recommended Approach | Notes |
|------------------------|---------------------|-------|
| `--theme-thought-background` | Keep as is, but use HSL format | Use semantic naming for component-specific styling |
| `--theme-tool-call-background` | Keep as is, but use HSL format | Use semantic naming for component-specific styling |
| `--theme-user-message-background` | Keep as is, but use HSL format | Use semantic naming for component-specific styling |

## Usage Examples

### Before (Our Custom Variables)

```css
.card {
  background-color: var(--theme-card);
  color: var(--theme-card-foreground);
  border: 1px solid var(--theme-border);
}
```

### After (shadcn/ui Variables)

```css
.card {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border: 1px solid hsl(var(--border));
}
```

## Implementation Plan

1. Update the `variables.css` file to use the shadcn/ui variable names in the `:root` and `.dark` selectors
2. Keep our original variables temporarily with redirects to the new variables for backward compatibility
3. Gradually update component CSS files to use the new variable format
4. Once all components are updated, remove the legacy variables