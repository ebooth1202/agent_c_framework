# Next.js 15 + React 19 Compatibility

Created: 2025-04-24
Source: react-19.mdx

## Overview

This guide covers using Shadcn UI with React 19 and Next.js 15, addressing compatibility issues and solutions. While titled for Next.js 15, this information applies to any framework supporting React 19.

> **Note**: Full support for React 19 and Tailwind v4 is now available in the `canary` release.

## Quick Solution

For npm users, install Shadcn UI dependencies with a flag (`--force` or `--legacy-peer-deps`). The CLI will prompt for this when run. No flags are required for pnpm, bun, or yarn.

## Background

React 19 is in release candidate status and is officially supported by Next.js 15. Package maintainers are in the process of updating peer dependencies to include React 19 compatibility:

```diff
"peerDependencies": {
-  "react": "^16.8 || ^17.0 || ^18.0",
+  "react": "^16.8 || ^17.0 || ^18.0 || ^19.0",
-  "react-dom": "^16.8 || ^17.0 || ^18.0"
+  "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0"
},
```

When installing packages that don't list React 19 as a peer dependency, npm will show errors (pnpm and Bun only show warnings).

## Solutions

### Option 1: Force Installation

Install packages with flags to bypass peer dependency checks:

```bash
npm i <package> --force
# OR
npm i <package> --legacy-peer-deps
```

**Flag differences:**
- `--force`: Ignores and overrides dependency conflicts completely
- `--legacy-peer-deps`: Skips strict peer dependency checks, allowing installation with unmet dependencies

### Option 2: Use React 18

Downgrade to React 18 until dependencies are updated:

```bash
npm i react@18 react-dom@18
```

## Installation Process

### Using pnpm, bun, or yarn
Follow standard installation instructions without special flags.

### Using npm
When running `npx shadcn@latest init -d`, select an option to resolve peer dependency issues when prompted:

```
It looks like you are using React 19.
Some packages may fail to install due to peer dependency issues.

? How would you like to proceed? › 
❯   Use --force
    Use --legacy-peer-deps
```

## React 19 Compatibility Status

| Package | Status | Note |
|---------|--------|------|
| radix-ui | ✅ | Compatible |
| lucide-react | ✅ | Compatible |
| class-variance-authority | ✅ | No React peer dependency |
| tailwindcss-animate | ✅ | No React peer dependency |
| embla-carousel-react | ✅ | Compatible |
| recharts | ✅ | Requires react-is override (see below) |
| react-hook-form | ✅ | Compatible |
| react-resizable-panels | ✅ | Compatible |
| sonner | ✅ | Compatible |
| react-day-picker | ✅ | Works with flag for npm |
| input-otp | ✅ | Compatible |
| vaul | ✅ | Compatible |
| @radix-ui/react-icons | 🚧 | PR in progress |
| cmdk | ✅ | Compatible |

**Legend:**
- ✅ Works with React 19 using npm, pnpm, and bun
- 🚧 Works with React 19 using pnpm and bun; requires flag for npm

## Recharts Configuration

To use Recharts with React 19:

1. Add the following to your `package.json`:
   ```json
   "overrides": {
     "react-is": "^19.0.0-rc-69d4b800-20241021"
   }
   ```
   Note: Match the react-is version to your React 19 version

2. Run `npm install --legacy-peer-deps`