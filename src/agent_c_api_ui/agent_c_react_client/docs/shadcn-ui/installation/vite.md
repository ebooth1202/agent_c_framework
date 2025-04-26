# Vite Installation Guide

**Source:** Original from `shadcn-ui/installation/vite.mdx`  
**Created:** April 24, 2025  

## Overview
Official installation guide for setting up shadcn/ui with Vite.

> **Note:** The following guide is for Tailwind v4. If using Tailwind v3, use `shadcn@2.3.0`.

## Installation Steps

### 1. Create Project
Start by creating a new React project using Vite. Select the **React + TypeScript** template:

```bash
npm create vite@latest
```

### 2. Add Tailwind CSS

```bash
npm install tailwindcss @tailwindcss/vite
```

Replace everything in `src/index.css` with:

```css
@import "../../../node_modules/tailwindcss";
```

### 3. Configure TypeScript
Edit `tsconfig.json` to add path aliases:

```json
{
  "files": [],
  "references": [
    {
      "path": "./tsconfig.app.json"
    },
    {
      "path": "./tsconfig.node.json"
    }
  ],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

And edit `tsconfig.app.json` similarly:

```json
{
  "compilerOptions": {
    // ... existing options
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
    // ... existing options
  }
}
```

### 4. Update Vite Config
Install the required dependency:

```bash
npm install -D @types/node
```

Update `vite.config.ts`:

```typescript
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

### 5. Run the CLI
Initialize shadcn/ui in your project:

```bash
npx shadcn@latest init
```

Follow the prompts to configure your project.

### 6. Add Components
Add components using the CLI:

```bash
npx shadcn@latest add button
```

Use the component in your project:

```tsx
import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="flex flex-col items-center justify-center min-h-svh">
      <Button>Click me</Button>
    </div>
  )
}

export default App
```