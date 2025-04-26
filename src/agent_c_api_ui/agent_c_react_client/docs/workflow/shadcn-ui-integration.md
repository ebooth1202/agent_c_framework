# shadcn/ui Integration Guide

## Overview

This guide explains how to properly integrate and use shadcn/ui components within the Agent C React UI. shadcn/ui provides a collection of reusable components built on top of Radix UI primitives, styled with Tailwind CSS.

## Contents
- [What is shadcn/ui?](#what-is-shadcnui)
- [Installation](#installation)
- [Adding Components](#adding-components)
- [Using Components](#using-components)
- [Customizing Components](#customizing-components)
- [Theme Configuration](#theme-configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## What is shadcn/ui?

shadcn/ui is not a traditional npm package. It's a collection of reusable components that you install directly into your project. This approach gives you complete control over the components, including their styling and behavior.

Key characteristics:

- Built on Radix UI primitives for accessibility and functionality
- Styled with Tailwind CSS for customization and consistency
- Components are copied into your project, not imported from a package
- Fully customizable, as you own the component code

## Installation

### Prerequisites

The Agent C React UI is already set up with the necessary configuration for shadcn/ui. This includes:

- Tailwind CSS
- PostCSS
- CSS variables for theming
- The `components.json` configuration file

### Adding New Components

To add a new shadcn/ui component to the project, use the CLI:

```bash
npx shadcn-ui@latest add [component-name]
```

For example:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
```

This will:
1. Create the component file in `src/components/ui/`
2. Add any necessary dependencies
3. Configure the component with your project's styling

## Using Components

### Importing Components

Import shadcn/ui components from your local components directory:

```jsx
import { Button } from "@/components/ui/button";
import { Dialog, DialogTrigger, DialogContent } from "@/components/ui/dialog";
```

### Basic Usage

```jsx
import { Button } from "@/components/ui/button";

export function SaveButton() {
  return (
    <Button variant="default">
      Save Changes
    </Button>
  );
}
```

### Component Variants

Many shadcn/ui components support variants:

```jsx
<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>
```

### Component Sizes

Some components support different sizes:

```jsx
<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
```

## Customizing Components

### Extending with Tailwind Classes

You can extend components with additional Tailwind classes:

```jsx
import { Button } from "@/components/ui/button";

export function CustomButton() {
  return (
    <Button className="bg-blue-500 hover:bg-blue-700">
      Custom Blue Button
    </Button>
  );
}
```

### Using the `cn` Utility

For conditional classes, use the `cn` utility function:

```jsx
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function ConditionalButton({ isActive }) {
  return (
    <Button
      className={cn(
        "transition-all",
        isActive ? "bg-green-500 shadow-lg" : "bg-gray-200"
      )}
    >
      {isActive ? "Active" : "Inactive"}
    </Button>
  );
}
```

### Modifying Component Source

Since shadcn/ui components are copied into your project, you can modify them directly:

1. Open the component file in `src/components/ui/`
2. Make your changes to the component
3. The changes will apply everywhere the component is used

For example, to modify the Button component:

```jsx
// src/components/ui/button.jsx
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";

import { cn } from "@/lib/utils";

// Modify the variants here
const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // Add a new custom variant
        custom: "bg-blue-600 text-white hover:bg-blue-700",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  );
});
Button.displayName = "Button";

export { Button, buttonVariants };
```

## Theme Configuration

### CSS Variables

shadcn/ui uses CSS variables for theming, defined in your project's CSS:

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

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... other dark theme variables */
}
```

### Tailwind Configuration

The theme in `tailwind.config.js` is set up to use these CSS variables:

```js
module.exports = {
  darkMode: ["class"],
  content: [
    './src/**/*.{js,jsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ... other color extensions
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      // ... other theme extensions
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## Best Practices

### 1. Keep Component Modifications Minimal

When possible, extend components using className rather than modifying the source:

```jsx
// Preferred
<Button className="custom-styles">Button</Button>

// Instead of modifying button.jsx directly
```

### 2. Create Wrapper Components

For significant customizations, create wrapper components:

```jsx
import { Button } from "@/components/ui/button";

export const PrimaryActionButton = ({ children, ...props }) => (
  <Button 
    variant="default"
    className="font-bold tracking-wide py-6"
    {...props}
  >
    {children}
  </Button>
);
```

### 3. Use the Composition Pattern

Leverage composition for complex components:

```jsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const FeatureCard = ({ title, description, onAction }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <p>{description}</p>
      <div className="mt-4">
        <Button onClick={onAction}>Learn More</Button>
      </div>
    </CardContent>
  </Card>
);
```

### 4. Maintain Theme Consistency

Stick to the theme variables for colors and spacing:

```jsx
// Good - uses theme variables
<div className="bg-background text-foreground p-4 rounded-md border border-border">

// Avoid - hardcoded colors
<div className="bg-white text-black p-4 rounded-md border border-gray-200">
```

### 5. Follow Accessibility Guidelines

- Maintain proper keyboard navigation
- Use appropriate ARIA attributes when needed
- Preserve focus management in interactive components

## Troubleshooting

### Common Issues

#### 1. Components Not Styled Correctly

Ensure Tailwind CSS is properly configured and classes are being processed:

- Check that the component file is included in Tailwind's content configuration
- Verify CSS variables are properly defined in your CSS
- Check for conflicting styles in your custom CSS

#### 2. Type Errors with Components

If using TypeScript:

- Ensure types are properly exported from component files
- Check that the `tsconfig.json` is correctly configured
- Verify that you're importing components correctly

#### 3. Dark Mode Not Working

- Verify that your dark mode configuration is correct in `tailwind.config.js`
- Check that the `ThemeProvider` component is properly implemented
- Ensure dark mode class is being applied to the right element

## Related Documentation

- [Component Creation Workflow](./component-creation-workflow.md)
- [Component Organization](../project/component-organization.md)
- [CSS Variables Reference](../style/css-variables.md)