# Remix Installation Guide

Created: 2025-04-24
Source: remix.mdx

## Overview

This guide provides instructions for installing and configuring shadcn/ui for Remix applications.

## Important Notes

- The following guide is for Tailwind v4. If using Tailwind v3, use `shadcn@2.3.0`.
- This guide is specifically for Remix. For React Router, see the React Router installation guide.

## Installation Steps

### 1. Create project

Start by creating a new Remix project:

```bash
npx create-remix@latest my-app
```

### 2. Run the CLI

Run the shadcn init command to setup your project:

```bash
npx shadcn@latest init
```

### 3. Configure components.json

You will be prompted with configuration questions:

```txt
Which style would you like to use? › New York
Which color would you like to use as base color? › Zinc
Do you want to use CSS variables for colors? › no / yes
```

### 4. Suggested App Structure

- UI components: `app/components/ui` folder
- Custom components: `app/components` folder
- Utility functions: `app/lib` folder (including `utils.ts` with the `cn` helper)
- Global CSS: `app/tailwind.css`

### 5. Install Tailwind CSS

```bash
npm install -D tailwindcss@latest autoprefixer@latest
```

Create a `postcss.config.js` file:

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Update your `remix.config.js` file:

```js
/** @type {import('@remix-run/dev').AppConfig} */
export default {
  ...
  tailwind: true,
  postcss: true,
  ...
};
```

### 6. Add tailwind.css to your app

In your `app/root.tsx` file, import the `tailwind.css` file:

```js
import styles from "./tailwind.css?url"

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: styles },
  ...(cssBundleHref ? [{ rel: "stylesheet", href: cssBundleHref }] : []),
]
```

## Adding Components

After setup, you can add components to your project:

```bash
npx shadcn@latest add button
```

## Usage Example

Import and use components in your pages:

```tsx
import { Button } from "~/components/ui/button"

export default function Home() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```