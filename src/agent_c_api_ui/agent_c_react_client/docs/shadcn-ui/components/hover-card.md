# Hover Card Component
Created: 2025-04-24
Source: hover-card.mdx

## Overview
The Hover Card component displays floating content when users hover over a trigger element. It's ideal for providing additional context or preview information without requiring a click.

## Features
- Preview content on hover without navigation
- Customizable trigger elements
- Configurable positioning and appearance
- Built on Radix UI's accessible primitives
- Automatic positioning within viewport

## Installation

```bash
npx shadcn@latest add hover-card
```

Or manually:

```bash
npm install @radix-ui/react-hover-card
```

## Component Structure

```tsx
<HoverCard>
  <HoverCardTrigger>...</HoverCardTrigger>
  <HoverCardContent>...</HoverCardContent>
</HoverCard>
```

## Basic Usage

```tsx
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"

function UserHoverPreview() {
  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="link">@username</Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-80">
        <div className="flex justify-between space-x-4">
          <Avatar>
            <AvatarImage src="https://github.com/vercel.png" />
            <AvatarFallback>VC</AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold">@username</h4>
            <p className="text-sm">
              The React Framework – created and maintained by @vercel.
            </p>
            <div className="flex items-center pt-2">
              <CalendarDays className="mr-2 h-4 w-4 opacity-70" />
              <span className="text-xs text-muted-foreground">
                Joined December 2021
              </span>
            </div>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  )
}
```

## Props

### HoverCard

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `defaultOpen` | boolean | The default open state of the hover card |
| `open` | boolean | Controls the open state of the hover card |
| `onOpenChange` | function | Called when the open state changes |
| `openDelay` | number | Duration from when the mouse enters the trigger until the hover card opens (default: 700ms) |
| `closeDelay` | number | Duration from when the mouse leaves the trigger or content until the hover card closes (default: 300ms) |

### HoverCardTrigger

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `asChild` | boolean | Change the default rendered element for the one passed as a child |

### HoverCardContent

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `forceMount` | boolean | Force mounting when controlled |
| `side` | "top" \| "right" \| "bottom" \| "left" | Preferred side of the trigger to render against |
| `sideOffset` | number | Distance from the trigger (default: 4) |
| `align` | "start" \| "center" \| "end" | Preferred alignment against the trigger |
| `alignOffset` | number | Distance from the start or end alignment |
| `avoidCollisions` | boolean | When true, overrides the side and align preferences to prevent collisions with boundary edges |
| `collisionBoundary` | Element \| null \| Array<Element \| null> | Element used as boundary for collision detection |
| `collisionPadding` | number \| Partial<Record<"top" \| "right" \| "bottom" \| "left", number>> | Distance from boundary edges where collision detection should occur |

## Use Cases

### User Profile Previews
Show user profile information when hovering over a username or avatar.

### Link Previews
Provide a preview of the content behind a link before users click through.

### Tooltip Alternatives
For cases where more rich content is needed than a simple tooltip provides.

### Term Definitions
Quickly display definitions or explanations for specialized terms without disrupting reading flow.

## Accessibility

- Focus is automatically trapped within the hover card when opened
- Keyboard users can access hover card content through focus
- Uses appropriate ARIA attributes for screen readers
- Proper dismissal handling with Escape key