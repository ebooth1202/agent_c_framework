# Registry FAQ

Created: 2025-04-24
Source: faq.mdx

## Frequently Asked Questions

### What does a complex component look like?

Here's an example of a complex component that installs a page, two components, a hook, a format-date utils and a config file:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "title": "Hello World",
  "type": "registry:block",
  "description": "A complex hello world component",
  "files": [
    {
      "path": "registry/new-york/hello-world/page.tsx",
      "type": "registry:page",
      "target": "app/hello/page.tsx"
    },
    {
      "path": "registry/new-york/hello-world/components/hello-world.tsx",
      "type": "registry:component"
    },
    {
      "path": "registry/new-york/hello-world/components/formatted-message.tsx",
      "type": "registry:component"
    },
    {
      "path": "registry/new-york/hello-world/hooks/use-hello.ts",
      "type": "registry:hook"
    },
    {
      "path": "registry/new-york/hello-world/lib/format-date.ts",
      "type": "registry:utils"
    },
    {
      "path": "registry/new-york/hello-world/hello.config.ts",
      "type": "registry:file",
      "target": "~/hello.config.ts"
    }
  ]
}
```

### How do I add a new Tailwind color?

#### For Tailwind CSS v4

To add a new color you need to add it to `cssVars` under `light` and `dark` keys:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "title": "Hello World",
  "type": "registry:block",
  "description": "A complex hello world component",
  "files": [
    // ...
  ],
  "cssVars": {
    "light": {
      "brand-background": "20 14.3% 4.1%",
      "brand-accent": "20 14.3% 4.1%"
    },
    "dark": {
      "brand-background": "20 14.3% 4.1%",
      "brand-accent": "20 14.3% 4.1%"
    }
  }
}
```

The CLI will update the project CSS file. Once updated, the new colors will be available to be used as utility classes: `bg-brand` and `text-brand-accent`.

#### For Tailwind CSS v3

To add a new color you need to add it to `cssVars` and `tailwind.config.theme.extend.colors`:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "title": "Hello World",
  "type": "registry:block",
  "description": "A complex hello world component",
  "files": [
    // ...
  ],
  "cssVars": {
    "light": {
      "brand-background": "20 14.3% 4.1%",
      "brand-accent": "20 14.3% 4.1%"
    },
    "dark": {
      "brand-background": "20 14.3% 4.1%",
      "brand-accent": "20 14.3% 4.1%"
    }
  },
  "tailwind": {
    "config": {
      "theme": {
        "extend": {
          "colors": {
            "brand": {
              "DEFAULT": "hsl(var(--brand-background))",
              "accent": "hsl(var(--brand-accent))"
            }
          }
        }
      }
    }
  }
}
```

The CLI will update the project CSS file and tailwind.config.js file. Once updated, the new colors will be available to be used as utility classes: `bg-brand` and `text-brand-accent`.

### How do I add or override a Tailwind theme variable?

#### For Tailwind CSS v4

To add or override a theme variable you add it to `cssVars.theme` under the key you want to add or override:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "title": "Hello World",
  "type": "registry:block",
  "description": "A complex hello world component",
  "files": [
    // ...
  ],
  "cssVars": {
    "theme": {
      "text-base": "3rem",
      "ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      "font-heading": "Poppins, sans-serif"
    }
  }
}
```

#### For Tailwind CSS v3

To override a theme variable you add it to `tailwind.config.theme.extend` under the key you want to override:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "hello-world",
  "title": "Hello World",
  "type": "registry:block",
  "description": "A complex hello world component",
  "files": [
    // ...
  ],
  "tailwind": {
    "config": {
      "theme": {
        "extend": {
          "text": {
            "base": "3rem"
          }
        }
      }
    }
  }
}
```