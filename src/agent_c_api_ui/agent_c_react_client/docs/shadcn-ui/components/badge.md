# Badge

**Created:** April 24, 2025  
**Source:** badge.mdx

## Description

Displays a badge or a component that looks like a badge. Badges are small status descriptors for UI elements, typically used to highlight status, category, or count information.

## Installation

### CLI Installation

```bash
npx shadcn@latest add badge
```

### Manual Installation

1. Copy the component code to your project's component directory
2. Update import paths to match your project structure

## Usage

### Basic Badge

```tsx
import { Badge } from "@/components/ui/badge"

<Badge variant="outline">Badge</Badge>
```

### Badge as Link

You can use the `badgeVariants` helper to create a link that looks like a badge:

```tsx
import { badgeVariants } from "@/components/ui/badge"
import Link from "next/link"

<Link className={badgeVariants({ variant: "outline" })}>Badge</Link>
```

## Variants

The badge component supports several variants:

1. **Default**: The standard badge style
   ```tsx
   <Badge>Default</Badge>
   ```

2. **Secondary**: Uses secondary colors for less emphasis
   ```tsx
   <Badge variant="secondary">Secondary</Badge>
   ```

3. **Outline**: Shows an outlined badge style
   ```tsx
   <Badge variant="outline">Outline</Badge>
   ```

4. **Destructive**: For error states or negative actions
   ```tsx
   <Badge variant="destructive">Destructive</Badge>
   ```

## Common Use Cases

- Status indicators (Active, Pending, Completed)
- Count notifications (message count, notification count)
- Category or tag labels
- Feature badges (New, Beta, Premium)
- Version indicators
- Approval status (Approved, Rejected)