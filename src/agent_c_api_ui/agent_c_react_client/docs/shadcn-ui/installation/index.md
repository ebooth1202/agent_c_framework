# Installation Overview

**Created**: April 24, 2025  
**Source**: installation/index.mdx

## Supported Frameworks

The shadcn-ui library can be installed in various frameworks. Each framework has its own installation guide with specific instructions:

- [Next.js](/docs/shadcn-ui/agent_context/installation/next.md)
- [Vite](/docs/shadcn-ui/agent_context/installation/vite.md)
- [Laravel](/docs/shadcn-ui/agent_context/installation/laravel.md)
- [React Router](/docs/shadcn-ui/agent_context/installation/react-router.md)
- [Astro](/docs/shadcn-ui/agent_context/installation/astro.md)
- [TanStack](/docs/shadcn-ui/agent_context/installation/tanstack.md)
- [TanStack Router](/docs/shadcn-ui/agent_context/installation/tanstack-router.md)
- [Gatsby](/docs/shadcn-ui/agent_context/installation/gatsby.md)
- [Manual Installation](/docs/shadcn-ui/agent_context/installation/manual.md)

## TypeScript Support

The project and components are written in TypeScript, which is recommended for your project as well.

A JavaScript version is also available via the CLI. To opt-out of TypeScript, set the `tsx` flag in your `components.json` file:

```json
{
  "style": "default",
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true
  },
  "rsc": false,
  "tsx": false,
  "aliases": {
    "utils": "~/lib/utils",
    "components": "~/components"
  }
}
```

## JavaScript Configuration

For JavaScript projects, configure import aliases using `jsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": [".//*"]
    }
  }
}
```