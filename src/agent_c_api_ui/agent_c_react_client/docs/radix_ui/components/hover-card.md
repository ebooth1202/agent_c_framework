# Hover Card Component

**Purpose:** Provides a preview of content when hovering over a trigger element, useful for showing additional information without requiring a click.

## Basic Usage

```jsx
import { HoverCard } from "radix-ui";

export default () => (
  <HoverCard.Root>
    <HoverCard.Trigger>Hover over me</HoverCard.Trigger>
    <HoverCard.Portal>
      <HoverCard.Content>
        Preview content here
        <HoverCard.Arrow />
      </HoverCard.Content>
    </HoverCard.Portal>
  </HoverCard.Root>
);
```

## Key Features
- Can be controlled or uncontrolled
- Customizable positioning (side, alignment, offsets)
- Optional pointing arrow
- Configurable open/close delays
- Designed for sighted users (ignored by screen readers)

## Component API

### HoverCard.Root

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `defaultOpen` | boolean | - | Initial open state (uncontrolled) |
| `open` | boolean | - | Controlled open state |
| `onOpenChange` | (open: boolean) => void | - | Open state change handler |
| `openDelay` | number | 700 | Delay before opening (ms) |
| `closeDelay` | number | 300 | Delay before closing (ms) |

### HoverCard.Trigger

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

**Data Attributes:** `[data-state]`: "open" or "closed"

### HoverCard.Portal

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `forceMount` | boolean | - | Force content mounting |
| `container` | HTMLElement | document.body | Portal container |

### HoverCard.Content

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `forceMount` | boolean | - | Force content mounting |
| `side` | "top" \| "right" \| "bottom" \| "left" | "bottom" | Preferred side position |
| `sideOffset` | number | 0 | Distance from trigger (px) |
| `align` | "start" \| "center" \| "end" | "center" | Alignment against trigger |
| `alignOffset` | number | 0 | Offset from alignment (px) |
| `avoidCollisions` | boolean | true | Prevent boundary collisions |
| `collisionBoundary` | Element \| null \| Array<Element \| null> | [] | Collision boundary elements |
| `collisionPadding` | number \| Partial<Record<Side, number>> | 0 | Collision detection padding |
| `arrowPadding` | number | 0 | Arrow edge padding |
| `sticky` | "partial" \| "always" | "partial" | Keep content in boundary behavior |
| `hideWhenDetached` | boolean | false | Hide when trigger is occluded |

**Data Attributes:**
- `[data-state]`: "open" or "closed"
- `[data-side]`: "left", "right", "bottom", "top"
- `[data-align]`: "start", "end", "center"

**CSS Variables:**
- `--radix-hover-card-content-transform-origin`: Transform origin based on position
- `--radix-hover-card-content-available-width`: Available width between trigger and boundary
- `--radix-hover-card-content-available-height`: Available height between trigger and boundary
- `--radix-hover-card-trigger-width`: Width of trigger element
- `--radix-hover-card-trigger-height`: Height of trigger element

### HoverCard.Arrow

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `width` | number | 10 | Arrow width (px) |
| `height` | number | 5 | Arrow height (px) |

## Common Patterns

### Show Preview Instantly
```jsx
<HoverCard.Root openDelay={0}>
  {/* components */}
</HoverCard.Root>
```

### Match Content Width to Trigger
```jsx
// JSX
<HoverCard.Content className="HoverCardContent">
  {/* content */}
</HoverCard.Content>

// CSS
.HoverCardContent {
  width: var(--radix-hover-card-trigger-width);
  max-height: var(--radix-hover-card-content-available-height);
}
```

### Direction-Aware Animations
```css
.HoverCardContent {
  transform-origin: var(--radix-hover-card-content-transform-origin);
  animation: scaleIn 0.5s ease-out;
}

/* Or using data-side for different animations */
.HoverCardContent[data-side="top"] {
  animation-name: slideUp;
}
.HoverCardContent[data-side="bottom"] {
  animation-name: slideDown;
}
```

## Accessibility Notes
- Hover Card is for sighted users only
- Content is inaccessible to keyboard-only users
- Tab key will open/close the hover card
- Enter key opens the hover card link