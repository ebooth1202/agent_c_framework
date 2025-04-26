# TanStack Router Installation Guide

Created: 2025-04-24
Source: tanstack-router.mdx

## Overview

This guide provides instructions for installing and configuring shadcn/ui for TanStack Router.

## Installation Steps

### 1. Create project

Create a new TanStack Router project with built-in shadcn/ui support:

```bash
npx create-tsrouter-app@latest my-app --template file-router --tailwind --add-ons shadcn
```

### 2. Add Components

You can add components to your project:

```bash
npx shadcn@canary add button
```

## Usage Example

After adding components, you can import and use them in your routes:

```tsx
import { createFileRoute } from "@tanstack/react-router"

import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/")({ 
  component: App,
})

function App() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Notes

- The TanStack Router installation is streamlined with the built-in shadcn template
- Use the `@canary` version of the shadcn CLI when adding components