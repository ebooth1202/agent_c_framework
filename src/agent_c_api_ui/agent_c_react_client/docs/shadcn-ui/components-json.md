# Components.json Configuration

Created: 2025-04-24
Source: components-json.mdx

## Overview

The `components.json` file is a configuration file used by the Shadcn UI CLI to understand your project structure and generate components accordingly. This file is only required if you're using the CLI to add components to your project.

## Creating the Configuration File

Create a `components.json` file by running:

```bash
npx shadcn@latest init
```

## Configuration Options

### $schema

The JSON Schema for validation (available at https://ui.shadcn.com/schema.json).

```json
{
  "$schema": "https://ui.shadcn.com/schema.json"
}
```

### style

The component style preset. This cannot be changed after initialization.

```json
{
  "style": "new-york"
}
```

Note: The "default" style has been deprecated in favor of "new-york".

### tailwind

Tailwind CSS configuration for the project.

#### tailwind.config

Path to your Tailwind config file. For Tailwind CSS v4, leave this blank.

```json
{
  "tailwind": {
    "config": "tailwind.config.js" 
  }
}
```

#### tailwind.css

Path to the CSS file that imports Tailwind.

```json
{
  "tailwind": {
    "css": "styles/global.css"
  }
}
```

#### tailwind.baseColor

Base color for component palette generation. Cannot be changed after initialization.

```json
{
  "tailwind": {
    "baseColor": "gray" | "neutral" | "slate" | "stone" | "zinc"
  }
}
```

#### tailwind.cssVariables

Whether to use CSS variables for theming (true) or Tailwind utility classes (false).

```json
{
  "tailwind": {
    "cssVariables": true | false
  }
}
```

This setting cannot be changed after initialization.

#### tailwind.prefix

Optional prefix for Tailwind utility classes.

```json
{
  "tailwind": {
    "prefix": "tw-"
  }
}
```

### rsc

Whether to enable React Server Components support. When true, the CLI adds `"use client"` directives to client components.

```json
{
  "rsc": true | false
}
```

### tsx

Whether to use TypeScript (.tsx) or JavaScript (.jsx) for components.

```json
{
  "tsx": true | false
}
```

### aliases

Import path aliases for your project. These work with the `paths` config from your tsconfig.json or jsconfig.json file.

#### aliases.utils

Import alias for utility functions.

```json
{
  "aliases": {
    "utils": "@/lib/utils"
  }
}
```

#### aliases.components

Import alias for components.

```json
{
  "aliases": {
    "components": "@/components"
  }
}
```

#### aliases.ui

Import alias for UI components. This determines where UI components are installed.

```json
{
  "aliases": {
    "ui": "@/app/ui"
  }
}
```

#### aliases.lib

Import alias for lib functions like date formatters.

```json
{
  "aliases": {
    "lib": "@/lib"
  }
}
```

#### aliases.hooks

Import alias for React hooks.

```json
{
  "aliases": {
    "hooks": "@/hooks"
  }
}
```

## Important Notes

1. If you're using a `src` directory, ensure it's included in the `paths` configuration of your tsconfig.json or jsconfig.json file.

2. The configuration options `style`, `tailwind.baseColor`, and `tailwind.cssVariables` cannot be changed after initialization without reinstalling components.