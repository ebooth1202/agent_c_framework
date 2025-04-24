# Sonner Component

*Created: 2025-04-24 | Source: sonner.mdx*

## Overview
An opinionated toast component for React built and maintained by emilkowalski_.

## Installation

### CLI Method
```bash
npx shadcn@latest add sonner
```

### Manual Method
1. Install dependencies:
```bash
npm install sonner next-themes
```
2. Copy the component source code to your project

### Add to Layout
After installation, add the Toaster component to your layout:

```tsx
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

## Usage

Import and use the toast function:

```tsx
import { toast } from "sonner"

// Basic usage
toast("Event has been created.")
```

## External Documentation
For more detailed usage, see the [official Sonner documentation](https://sonner.emilkowal.ski).