# Tailwind CSS v4 Integration

Created: 2025-04-24
Source: tailwind-v4.mdx

## Overview

Shadcn UI now fully supports Tailwind CSS v4 and React 19. The integration provides enhanced styling capabilities, better performance, and modern component architecture.

## Key Features

- CLI support for initializing projects with Tailwind v4
- Full support for the new `@theme` directive and `@theme inline` option
- Components updated for Tailwind v4 and React 19 compatibility
- Removed forwardRefs and adjusted types for modern React patterns
- Added `data-slot` attributes to all components for improved styling
- Deprecated the `toast` component in favor of `sonner`
- Standardized buttons to use default cursor
- Deprecated the `default` style in favor of `new-york`
- Converted HSL colors to OKLCH for better color representation

> **Note**: Existing projects using Tailwind v3 and React 18 will continue to work. The new Tailwind v4 support only applies to newly created projects or when explicitly upgrading.

## Getting Started

You can test Tailwind v4 + React 19 using the `canary` release of the CLI. Installation guides are available for various frameworks including Next.js, Vite, Laravel, React Router, Astro, TanStack, Gatsby, and manual setup.

## Upgrading Existing Projects

> **Important**: Before upgrading, read the [Tailwind v4 Compatibility Docs](https://tailwindcss.com/docs/compatibility) to ensure your project is ready. Tailwind v4 uses cutting-edge browser features designed for modern browsers.

Follow these steps to upgrade your existing Shadcn UI projects:

### 1. Follow the Tailwind v4 Upgrade Guide

- Upgrade to Tailwind v4 using the official guide: https://tailwindcss.com/docs/upgrade-guide
- Use the `@tailwindcss/upgrade@next` codemod to remove deprecated utilities and update your Tailwind config

### 2. Update CSS Variables

Transform your CSS variables to work with the new `@theme inline` directive:

```css
/* Before */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
  }
}

@theme {
  --color-background: hsl(var(--background));
  --color-foreground: hsl(var(--foreground));
}

/* After */
:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(0 0% 3.9%);
}

.dark {
  --background: hsl(0 0% 3.9%);
  --foreground: hsl(0 0% 98%);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
}
```

### 3. Update Chart Colors

Remove the `hsl()` wrapper from chart color references:

```diff
const chartConfig = {
  desktop: {
    label: "Desktop",
-    color: "hsl(var(--chart-1))",
+    color: "var(--chart-1)",
  },
}
```

### 4. Use the New `size-*` Utility

Replace width and height combinations with the new `size-*` utility:

```diff
- w-4 h-4
+ size-4
```

### 5. Update Dependencies

```bash
pnpm up "@radix-ui/*" cmdk lucide-react recharts tailwind-merge clsx --latest
```

### 6. Remove forwardRef

Use the `remove-forward-ref` codemod to migrate your components or update manually:

**Before:**
```tsx
const AccordionItem = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Item>
>(({ className, ...props }, ref) => (
  <AccordionPrimitive.Item
    ref={ref}
    className={cn("border-b last:border-b-0", className)}
    {...props}
  />
))
AccordionItem.displayName = "AccordionItem"
```

**After:**
```tsx
function AccordionItem({
  className,
  ...props
}: React.ComponentProps<typeof AccordionPrimitive.Item>) {
  return (
    <AccordionPrimitive.Item
      data-slot="accordion-item"
      className={cn("border-b last:border-b-0", className)}
      {...props}
    />
  )
}
```

## Recent Changes

### March 19, 2025 - Deprecated `tailwindcss-animate`

Now using `tw-animate-css` instead. Migration steps:

1. Remove `tailwindcss-animate` dependency
2. Remove `@plugin 'tailwindcss-animate'` from globals.css
3. Install `tw-animate-css` as a dev dependency
4. Add `@import "tw-animate-css"` to globals.css

### March 12, 2025 - New Dark Mode Colors

Updated dark mode colors for better accessibility. For existing Tailwind v4 projects, update components using:

```bash
npx shadcn@latest add --all --overwrite
```

Then update your dark mode colors in globals.css to the new OKLCH colors.