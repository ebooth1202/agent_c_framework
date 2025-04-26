# Next.js Installation Guide

**Source:** Original from `shadcn-ui/installation/next.mdx`  
**Created:** April 24, 2025  

## Overview
Official installation guide for setting up shadcn/ui with Next.js.

> **Note:** The following guide is for Tailwind v4. If using Tailwind v3, use `shadcn@2.3.0`.

## Installation Steps

### 1. Create Project
Run the initialization command to set up a new Next.js project or configure an existing one:

```bash
npx shadcn@latest init
```

When prompted, choose between a Next.js project or a Monorepo structure.

### 2. Add Components
Add components to your project using the CLI:

```bash
npx shadcn@latest add button
```

The command above adds the `Button` component to your project. You can then import it:

```tsx
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Key Benefits
- Simple initialization process
- Component-by-component addition
- Automatic path configuration
- Full TypeScript support