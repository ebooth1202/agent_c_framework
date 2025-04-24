# Toggle Group

_Created: 2025-04-24 | Source: toggle-group.mdx_

## Overview

A set of two-state buttons that can be toggled on or off. Toggle groups can be configured for single or multiple selection modes.

## Key Features

- Multiple selection types (single or multiple)
- Various styling variants (default and outline)
- Different size options (small, default, large)
- Support for disabled state
- Built on Radix UI primitives for accessibility

## Installation

**CLI Method:**
```bash
npx shadcn@latest add toggle-group
```

**Manual Installation:**
1. Install dependencies:
   ```bash
   npm install @radix-ui/react-toggle-group
   ```
2. Copy the component source code
3. Update import paths for your project

## Component Structure

The component consists of two main parts:
- `ToggleGroup`: The container component that groups toggle items
- `ToggleGroupItem`: Individual toggle buttons within the group

## Usage

```tsx
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"

<ToggleGroup type="single">
  <ToggleGroupItem value="a">A</ToggleGroupItem>
  <ToggleGroupItem value="b">B</ToggleGroupItem>
  <ToggleGroupItem value="c">C</ToggleGroupItem>
</ToggleGroup>
```

## Common Variants

### Default Toggle Group
Basic toggle group with default styling

### Outline Toggle Group
Toggle group with outline variant styling

### Single Selection Mode
Toggle group that only allows one item to be selected at a time

### Multiple Selection Mode
Toggle group that allows multiple items to be selected simultaneously

### Size Variants
- Small (`sm`)
- Default (no size prop)
- Large (`lg`)

### Disabled State
The entire toggle group can be disabled to prevent user interaction

## Accessibility

Built on Radix UI's primitives which ensure proper accessibility features including:
- Keyboard navigation
- ARIA attributes
- Focus management
- Screen reader support