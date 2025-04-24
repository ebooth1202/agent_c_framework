# Registry Item JSON Schema

**Source:** Original from `shadcn-ui/registry/registry-item-json.mdx`  
**Created:** April 24, 2025  

## Overview
Specification for the `registry-item.json` schema used to define custom registry items in shadcn/ui.

## Schema Example

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "type": "registry:block",
  "title": "Hello World",
  "description": "A simple hello world component.",
  "files": [
    {
      "path": "registry/new-york/hello-world/hello-world.tsx",
      "type": "registry:component"
    },
    {
      "path": "registry/new-york/hello-world/use-hello-world.ts",
      "type": "registry:hook"
    }
  ],
  "cssVars": {
    "theme": {
      "font-heading": "Poppins, sans-serif"
    },
    "light": {
      "brand": "20 14.3% 4.1%"
    },
    "dark": {
      "brand": "20 14.3% 4.1%"
    }
  }
}
```

## Schema Properties

### $schema
Specifies the schema for the `registry-item.json` file.
```json
"$schema": "https://ui.shadcn.com/schema/registry-item.json"
```

### name
Unique identifier for the item within your registry.
```json
"name": "hello-world"
```

### title
Human-readable title for your registry item.
```json
"title": "Hello World"
```

### description
Detailed description of your registry item.
```json
"description": "A simple hello world component."
```

### type
Specifies the type of your registry item, determining its handling by the CLI.

```json
"type": "registry:block"
```

Supported types:
- `registry:block`: Complex components with multiple files
- `registry:component`: Simple components
- `registry:lib`: Lib and utils
- `registry:hook`: Hooks
- `registry:ui`: UI components and single-file primitives
- `registry:page`: Page or file-based routes
- `registry:file`: Miscellaneous files
- `registry:style`: Registry styles
- `registry:theme`: Themes

### author
Specifies the author of the registry item.
```json
"author": "John Doe <john@doe.com>"
```

### dependencies
Specifies npm package dependencies for your registry item.
```json
"dependencies": ["@radix-ui/react-accordion", "zod", "lucide-react", "name@1.0.2"]
```

### registryDependencies
Specifies other registry items this item depends on.
```json
"registryDependencies": [
  "button", 
  "input", 
  "select", 
  "https://example.com/r/editor.json"
]
```

### files
Specifies the files included in your registry item.
```json
"files": [
  {
    "path": "registry/new-york/hello-world/page.tsx",
    "type": "registry:page",
    "target": "app/hello/page.tsx"
  },
  {
    "path": "registry/new-york/hello-world/hello-world.tsx",
    "type": "registry:component"
  }
]
```

### cssVars
Defines CSS variables for your registry item.
```json
"cssVars": {
  "theme": {
    "font-heading": "Poppins, sans-serif"
  },
  "light": {
    "brand": "20 14.3% 4.1%",
    "radius": "0.5rem"
  },
  "dark": {
    "brand": "20 14.3% 4.1%"
  }
}
```

### css
Adds new CSS rules to the project's CSS file.
```json
"css": {
  "@layer base": {
    "body": {
      "font-size": "var(--text-base)",
      "line-height": "1.5"
    }
  }
}
```

### docs
Custom documentation or messages shown when installing your registry item.
```json
"docs": "Remember to add the FOO_BAR environment variable to your .env file."
```

### categories
Organizational tags for your registry item.
```json
"categories": ["sidebar", "dashboard"]
```

### meta
Additional metadata for your registry item.
```json
"meta": { "foo": "bar" }
```