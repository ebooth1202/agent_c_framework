# Next.js Dark Mode Implementation

**Source:** Original from `shadcn-ui/dark-mode/next.mdx`  
**Created:** April 24, 2025  

## Overview
Step-by-step guide for adding dark mode to a Next.js application using the next-themes package.

## Implementation Steps

### 1. Install next-themes
Start by installing the required package:

```bash
npm install next-themes
```

### 2. Create a Theme Provider
Create a theme provider component:

```tsx
// components/theme-provider.tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### 3. Wrap Your Root Layout
Add the ThemeProvider to your root layout and add the `suppressHydrationWarning` prop to the html tag:

```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <>
      <html lang="en" suppressHydrationWarning>
        <head />
        <body>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            {children}
          </ThemeProvider>
        </body>
      </html>
    </>
  )
}
```

### 4. Add a Mode Toggle
Implement a mode toggle component to switch between light and dark modes.

## Key Configuration Options
- `attribute="class"`: Uses CSS classes for theme switching
- `defaultTheme="system"`: Default to system preferences
- `enableSystem`: Enables system preference detection
- `disableTransitionOnChange`: Prevents transition flicker on theme change