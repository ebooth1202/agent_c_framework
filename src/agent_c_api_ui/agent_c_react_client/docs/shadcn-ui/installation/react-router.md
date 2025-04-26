# React Router Installation Guide

Created: 2025-04-24
Source: react-router.mdx

## Overview

This guide provides instructions for installing and configuring shadcn/ui with React Router.

## Installation Steps

### 1. Create project

```bash
npx create-react-router@latest my-app
```

### 2. Run the CLI

Run the shadcn init command to set up your project:

```bash
npx shadcn@latest init
```

### 3. Add Components

You can now add components to your project:

```bash
npx shadcn@latest add button
```

## Usage Example

After adding components, you can import and use them in your routes:

```tsx
import { Button } from "~/components/ui/button"

import type { Route } from "./+types/home"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ]
}

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-svh">
      <Button>Click me</Button>
    </div>
  )
}
```