---
Title: Card Component
Created: 2025-04-24
Source: ui/docs/shadcn-ui/components/card.mdx
---

# Card

Displays a card with header, content, and footer sections. Cards are versatile containers for related information and actions.

## Installation

### Option 1: Using CLI

```bash
npx shadcn@latest add card
```

### Option 2: Manual Installation

Copy the component source code and update import paths to match your project structure.

## Usage

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card Content</p>
  </CardContent>
  <CardFooter>
    <p>Card Footer</p>
  </CardFooter>
</Card>
```

## Components

- `Card`: Main container component
- `CardHeader`: Top section for title and description
- `CardTitle`: Card heading element (rendered as div for flexibility)
- `CardDescription`: Subtitle or explanatory text (rendered as div)
- `CardContent`: Main content area
- `CardFooter`: Bottom section typically used for actions

## Accessibility

As of March 11, 2024, the `CardTitle` and `CardDescription` components were changed to use `div` elements instead of `h3` and `p` elements to improve accessibility and allow for more flexible heading structures.

```tsx
const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
```

## Common Use Cases

- Settings panels
- Form containers
- Information displays
- Feature showcases
- Dashboard widgets