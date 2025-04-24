# Popover Component

## Overview
Displays rich content in a portal, triggered by a button. The Popover provides a way to show additional UI content when a user interacts with a trigger element.

## Key Features
- Can be controlled or uncontrolled
- Customizable side, alignment, offsets, and collision handling
- Optional pointing arrow for visual connection to trigger
- Fully managed focus handling
- Supports both modal and non-modal modes
- Customizable dismissing and layering behavior

## Installation
```bash
npm install @radix-ui/react-popover
```

## Component Structure
```jsx
import { Popover } from "radix-ui";

export default () => (
  <Popover.Root>
    <Popover.Trigger />
    <Popover.Anchor /> {/* Optional */}
    <Popover.Portal>
      <Popover.Content>
        <Popover.Close />
        <Popover.Arrow /> {/* Optional */}
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
);
```

## API Reference

### Root
Contains all parts of a popover.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `defaultOpen` | boolean | - | Initial open state (uncontrolled) |
| `open` | boolean | - | Controlled open state |
| `onOpenChange` | (open: boolean) => void | - | Event handler for open state changes |
| `modal` | boolean | false | When true, disables outside interactions and limits screen reader access to popover content |

### Trigger
The button that toggles the popover.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |

**Data Attributes:**
- `[data-state]`: "open" or "closed"

### Anchor
Optional element to position content against (instead of the Trigger).

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |

### Portal
Portals the content into the document body.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `forceMount` | boolean | - | Forces mounting of portal content |
| `container` | HTMLElement | document.body | Container element for the portal |

### Content
The component that appears when popover is open.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `onOpenAutoFocus` | (event: Event) => void | - | Event handler when focus moves inside |
| `onCloseAutoFocus` | (event: Event) => void | - | Event handler when focus returns to trigger |
| `onEscapeKeyDown` | (event: KeyboardEvent) => void | - | Event handler for Escape key |
| `onPointerDownOutside` | (event: PointerDownOutsideEvent) => void | - | Event handler for pointer outside |
| `onFocusOutside` | (event: FocusOutsideEvent) => void | - | Event handler for focus outside |
| `onInteractOutside` | (event: PointerDownOutsideEvent \| FocusOutsideEvent) => void | - | Event handler for any outside interaction |
| `forceMount` | boolean | - | Forces mounting regardless of open state |
| `side` | "top" \| "right" \| "bottom" \| "left" | "bottom" | Preferred side for positioning |
| `sideOffset` | number | 0 | Distance from anchor in pixels |
| `align` | "start" \| "center" \| "end" | "center" | Alignment against the anchor |
| `alignOffset` | number | 0 | Offset from alignment position |
| `avoidCollisions` | boolean | true | Whether to adjust position to prevent boundary collisions |
| `collisionBoundary` | Element \| null \| Array<Element \| null> | [] | Elements to consider for collision detection |
| `collisionPadding` | number \| Partial<Record<Side, number>> | 0 | Padding from boundary edges |
| `arrowPadding` | number | 0 | Padding between arrow and content edges |
| `sticky` | "partial" \| "always" | "partial" | Behavior for keeping content in boundary |
| `hideWhenDetached` | boolean | false | Whether to hide content when trigger is fully occluded |

**Data Attributes:**
- `[data-state]`: "open" or "closed"
- `[data-side]`: "left", "right", "bottom", or "top"
- `[data-align]`: "start", "end", or "center"

**CSS Variables:**
- `--radix-popover-content-transform-origin`: Computed transform origin
- `--radix-popover-content-available-width`: Available width between trigger and boundary
- `--radix-popover-content-available-height`: Available height between trigger and boundary
- `--radix-popover-trigger-width`: Width of the trigger
- `--radix-popover-trigger-height`: Height of the trigger

### Arrow
Optional arrow element to visually connect content with anchor.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `width` | number | 10 | Arrow width in pixels |
| `height` | number | 5 | Arrow height in pixels |

### Close
Button that closes an open popover.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |

## Usage Examples

### Match Content Width to Trigger
```jsx
// index.jsx
import { Popover } from "radix-ui";
import "./styles.css";

export default () => (
  <Popover.Root>
    <Popover.Trigger>…</Popover.Trigger>
    <Popover.Portal>
      <Popover.Content className="PopoverContent" sideOffset={5}>
        …
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
);
```

```css
/* styles.css */
.PopoverContent {
  width: var(--radix-popover-trigger-width);
  max-height: var(--radix-popover-content-available-height);
}
```

### Origin-aware Animation
```jsx
// index.jsx
import { Popover } from "radix-ui";
import "./styles.css";

export default () => (
  <Popover.Root>
    <Popover.Trigger>…</Popover.Trigger>
    <Popover.Portal>
      <Popover.Content className="PopoverContent">…</Popover.Content>
    </Popover.Portal>
  </Popover.Root>
);
```

```css
/* styles.css */
.PopoverContent {
  transform-origin: var(--radix-popover-content-transform-origin);
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

### Using Custom Anchor
```jsx
// index.jsx
import { Popover } from "radix-ui";
import "./styles.css";

export default () => (
  <Popover.Root>
    <Popover.Anchor asChild>
      <div className="Row">
        Row as anchor <Popover.Trigger>Trigger</Popover.Trigger>
      </div>
    </Popover.Anchor>

    <Popover.Portal>
      <Popover.Content>…</Popover.Content>
    </Popover.Portal>
  </Popover.Root>
);
```

## Accessibility
- Follows the Dialog WAI-ARIA design pattern
- Full keyboard navigation support
- Manages focus states according to WAI-ARIA guidelines

### Keyboard Interactions
| Key | Action |
| --- | ------ |
| Space | Opens/closes the popover |
| Enter | Opens/closes the popover |
| Tab | Moves focus to next focusable element |
| Shift + Tab | Moves focus to previous focusable element |
| Esc | Closes popover and returns focus to trigger |