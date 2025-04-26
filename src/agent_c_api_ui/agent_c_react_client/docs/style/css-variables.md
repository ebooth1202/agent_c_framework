# CSS Variables Reference

## Overview

This document provides a comprehensive reference of CSS variables used throughout the Agent C React UI. These variables define colors, spacing, typography, and other design tokens that create a consistent visual language across the application.

## Contents
- [Theme Variables](#theme-variables)
- [Color Variables](#color-variables)
- [Typography Variables](#typography-variables)
- [Layout & Spacing Variables](#layout--spacing-variables)
- [Component-Specific Variables](#component-specific-variables)
- [Usage Guidelines](#usage-guidelines)

## Theme Variables

These variables define the core theme colors used throughout the application. They're designed to support both light and dark themes.

### Base Scales

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;

  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;

  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;

  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;

  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;

  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;

  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;

  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;

  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;

  --radius: 0.5rem;
}
```

### Dark Theme Variables

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;

  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;

  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;

  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;

  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;

  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;

  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;

  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;

  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}
```

## Color Variables

### Message Type Colors

These colors are used to distinguish different message types in the chat interface:

```css
:root {
  --message-user-bg: 210 40% 98%;
  --message-assistant-bg: 210 40% 96.1%;
  --message-system-bg: 217.2 32.6% 17.5%;
  --message-system-text: 210 40% 98%;
  --message-error-bg: 0 84.2% 60.2%;
  --message-error-text: 210 40% 98%;
}

.dark {
  --message-user-bg: 222.2 47.4% 11.2%;
  --message-assistant-bg: 217.2 32.6% 17.5%;
  --message-system-bg: 215.4 16.3% 46.9%;
  --message-system-text: 210 40% 98%;
  --message-error-bg: 0 62.8% 30.6%;
  --message-error-text: 210 40% 98%;
}
```

### Status Colors

Colors used for status indicators and notifications:

```css
:root {
  --status-online: 142.1 76.2% 36.3%;
  --status-offline: 0 84.2% 60.2%;
  --status-loading: 48 96.5% 53.3%;
  --status-thinking: 214.3 31.8% 91.4%;
}

.dark {
  --status-online: 142.1 70.6% 45.3%;
  --status-offline: 0 62.8% 30.6%;
  --status-loading: 48 96.5% 53.3%;
  --status-thinking: 217.2 32.6% 17.5%;
}
```

## Typography Variables

Variables controlling text appearance throughout the application:

```css
:root {
  /* Font families */
  --font-sans: ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  
  /* Font sizes */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  /* Line heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Font weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

## Layout & Spacing Variables

Variables for consistent spacing and layout:

```css
:root {
  /* Spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  
  /* Layout variables */
  --sidebar-width: 280px;
  --sidebar-width-collapsed: 80px;
  --header-height: 60px;
  --chat-input-height: 140px;
  --chat-max-width: 1200px;
}
```

## Component-Specific Variables

### Chat Interface

```css
:root {
  --message-border-radius: 0.75rem;
  --message-spacing: 1rem;
  --message-padding: 1rem;
  --message-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

### Tool Call Display

```css
:root {
  --tool-call-bg: 210 40% 96.1%;
  --tool-call-border: 214.3 31.8% 91.4%;
  --tool-call-header-bg: 210 40% 98%;
  --tool-call-code-bg: 222.2 84% 4.9%;
  --tool-call-code-text: 210 40% 98%;
}

.dark {
  --tool-call-bg: 217.2 32.6% 17.5%;
  --tool-call-border: 215.4 16.3% 46.9%;
  --tool-call-header-bg: 222.2 47.4% 11.2%;
  --tool-call-code-bg: 222.2 84% 4.9%;
  --tool-call-code-text: 210 40% 98%;
}
```

### Status Indicator

```css
:root {
  --status-indicator-size: 10px;
  --status-indicator-pulse-opacity: 0.6;
  --status-indicator-pulse-duration: 1.5s;
}
```

## Usage Guidelines

### Using CSS Variables

CSS variables should be accessed using the `var()` function:

```css
.element {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  padding: var(--space-4);
}
```

### HSL Color Format

Many color variables use HSL format without the full `hsl()` wrapper. When using these variables, include the `hsl()` function:

```css
/* Correct usage */
.element {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

/* Incorrect usage */
.element {
  background-color: var(--primary); /* Will not work as expected */
}
```

### Variable Overrides

Components can override variables for specific contexts:

```css
.custom-card {
  --card: 0 0% 95%;
  --card-foreground: 222.2 84% 4.9%;
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
}
```

### Responsive Adjustments

Variables can be changed at different breakpoints:

```css
:root {
  --sidebar-width: 280px;
}

@media (max-width: 768px) {
  :root {
    --sidebar-width: 240px;
  }
}

@media (max-width: 640px) {
  :root {
    --sidebar-width: 0;
  }
}
```

## Related Documentation

- [Theme System](./theme-system.md)
- [CSS Organization](./css-organization.md)
- [Styling Guide](./styling-guide.md)