# Contributing Blocks to Shadcn UI

Created: 2025-04-24
Source: blocks.mdx

## Overview

Shadcn UI welcomes community contributions to its blocks library - a collection of reusable, higher-level components and patterns. This guide covers the process for creating and submitting your own blocks.

## Getting Started

### Setting Up Your Workspace

1. Fork the repository:
   ```bash
   git clone https://github.com/shadcn-ui/ui.git
   ```

2. Create a new branch:
   ```bash
   git checkout -b username/my-new-block
   ```

3. Install dependencies:
   ```bash
   pnpm install
   ```

4. Start the development server:
   ```bash
   pnpm www:dev
   ```

## Creating a Block

A block can range from a simple component variation to a complex multi-component pattern like a dashboard.

### Step 1: Create the Block Directory

Create a new folder in the `apps/www/registry/new-york/blocks` directory. Use kebab-case naming:

```
apps
└── www
    └── registry
        └── new-york
            └── blocks
                └── dashboard-01
```

> Note: The build script automatically handles creating versions for other styles.

### Step 2: Add Your Block Files

Add your component files to the block directory. A typical structure might include:

```
dashboard-01
└── page.tsx             # Main page component
└── components           # Supporting components
    └── hello-world.tsx
    └── example-card.tsx
└── hooks                # Custom hooks
    └── use-hello-world.ts
└── lib                  # Utility functions
    └── format-date.ts
```

You can start with a single file and expand later as needed.

## Registering Your Block

### Step 1: Update the Registry Definition

Add your block's metadata to `registry-blocks.tsx`:

```tsx
export const blocks = [
  // ...
  {
    name: "dashboard-01",
    author: "shadcn (https://ui.shadcn.com)",
    title: "Dashboard",
    description: "A simple dashboard with a hello world component.",
    type: "registry:block",
    registryDependencies: ["input", "button", "card"],
    dependencies: ["zod"],
    files: [
      {
        path: "blocks/dashboard-01/page.tsx",
        type: "registry:page",
        target: "app/dashboard/page.tsx",
      },
      {
        path: "blocks/dashboard-01/components/hello-world.tsx",
        type: "registry:component",
      },
      {
        path: "blocks/dashboard-01/components/example-card.tsx",
        type: "registry:component",
      },
      {
        path: "blocks/dashboard-01/hooks/use-hello-world.ts",
        type: "registry:hook",
      },
      {
        path: "blocks/dashboard-01/lib/format-date.ts",
        type: "registry:lib",
      },
    ],
    categories: ["dashboard"],
  },
]
```

### Step 2: Build the Registry

Run the build script to process your block:

```bash
pnpm registry:build
```

### Step 3: Preview Your Block

View your block at:
- Category view: `http://localhost:3333/blocks/[CATEGORY]`
- Full-screen preview: `http://localhost:3333/view/styles/new-york/dashboard-01`

## Publishing Your Block

When your block is ready for submission:

1. Run the build script:
   ```bash
   pnpm registry:build
   ```

2. Capture screenshots:
   ```bash
   pnpm registry:capture
   ```
   
   > Note: You may need to delete existing screenshots at `apps/www/public/r/styles/new-york` first.

3. Submit a pull request to the main repository.

## Block Categories

Categories help organize blocks in the registry. Available categories include:
- dashboard
- application
- marketing
- form
- card
- etc.

### Adding a New Category

To add a new category, update the `registryCategories` array in `apps/www/registry/registry-categories.ts`:

```tsx
export const registryCategories = [
  // ...
  {
    name: "Input",
    slug: "input",
    hidden: false,
  },
]
```

## Guidelines

- Required block properties: `name`, `description`, `type`, `files`, and `categories`
- List all Shadcn UI components used in `registryDependencies` (e.g., "input", "button")
- List all npm packages used in `dependencies` (e.g., "zod", "sonner")
- If including a page component, make it the first entry in `files` with a `target` property
- Always use the `@/registry` path for imports: `import { Input } from "@/registry/new-york/input"`