# Monorepo Integration

Created: 2025-04-24
Source: monorepo.mdx

## Overview

Shadcn UI provides enhanced support for monorepo setups, making it easier to manage components across multiple packages or apps in a monorepo structure. The CLI now understands monorepo structures and handles component installation and import paths automatically.

## Getting Started

### Creating a New Monorepo Project

1. Initialize a new project using the canary version of the CLI:
   ```bash
   npx shadcn@canary init
   ```

2. Select the "Next.js (Monorepo)" option when prompted.

3. This creates a new monorepo with two workspaces:
   - `web`: Your application
   - `ui`: Your component library
   
   The setup uses Turborepo as the build system and includes React 19 and Tailwind CSS v4.

### Adding Components

1. Navigate to your app directory:
   ```bash
   cd apps/web
   ```

2. Add components using the CLI:
   ```bash
   npx shadcn@canary add [COMPONENT]
   ```

3. The CLI automatically:
   - Installs UI components to the `packages/ui` directory
   - Installs block components to the app's `components` directory
   - Updates import paths correctly

### Importing Components

Components can be imported from the workspace UI package:

```tsx
// UI components
import { Button } from "@workspace/ui/components/button"

// Hooks and utilities
import { useTheme } from "@workspace/ui/hooks/use-theme"
import { cn } from "@workspace/ui/lib/utils"
```

## File Structure

```
apps
└── web         # Your application
    ├── app
    │   └── page.tsx
    ├── components
    │   └── login-form.tsx  # Block components go here
    ├── components.json
    └── package.json
packages
└── ui          # UI component library
    ├── src
    │   ├── components     # UI components go here
    │   │   └── button.tsx
    │   ├── hooks
    │   ├── lib
    │   │   └── utils.ts
    │   └── styles
    │       └── globals.css
    ├── components.json
    └── package.json
package.json
turbo.json
```

## Requirements

1. Each workspace requires a `components.json` configuration file.

2. The `components.json` file must properly define aliases for each workspace.

3. For Tailwind v4, use empty config in the `components.json` file.

4. Ensure the same `style`, `iconLibrary`, and `baseColor` values in both `components.json` files.

## Configuration Example (Tailwind CSS v4)

**Apps Web Configuration:**
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "../../packages/ui/src/styles/globals.css",
    "baseColor": "zinc",
    "cssVariables": true
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "hooks": "@/hooks",
    "lib": "@/lib",
    "utils": "@workspace/ui/lib/utils",
    "ui": "@workspace/ui/components"
  }
}
```

**Packages UI Configuration:**
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/styles/globals.css",
    "baseColor": "zinc",
    "cssVariables": true
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@workspace/ui/components",
    "utils": "@workspace/ui/lib/utils",
    "hooks": "@workspace/ui/hooks",
    "lib": "@workspace/ui/lib",
    "ui": "@workspace/ui/components"
  }
}
```