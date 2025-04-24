# Toggle

_Created: 2025-04-24 | Source: toggle.mdx_

## Overview

A two-state button that can be either on or off. This component provides a simple way to toggle between two states with visual feedback.

## Key Features

- Two distinct states (on/off)
- Multiple visual variants (default, outline)
- Size variations (small, default, large)
- Support for disabled state
- Support for text content
- Built on Radix UI primitives for accessibility

## Installation

**CLI Method:**
```bash
npx shadcn@latest add toggle
```

**Manual Installation:**
1. Install dependencies:
   ```bash
   npm install @radix-ui/react-toggle
   ```
2. Copy the component source code
3. Update import paths for your project

## Component Structure

The Toggle component is a single interactive element that can be pressed to toggle between on and off states.

## Usage

```tsx
import { Toggle } from "@/components/ui/toggle"

<Toggle>Toggle</Toggle>
```

## Common Variants

### Default Toggle
Basic toggle with default styling

### Outline Toggle
Toggle with outline variant styling

### Toggle with Text
Toggle containing text content

### Size Variants
- Small (`sm`)
- Default (no size prop)
- Large (`lg`)

### Disabled State
A toggle that cannot be interacted with

## Accessibility

Built on Radix UI's Toggle primitive which ensures proper accessibility features including:
- Keyboard navigation
- ARIA attributes
- Focus management
- Screen reader support