# Collapsible Component

**Created:** 2025-04-24
**Source:** Radix UI Primitives

## Overview

Collapsible is an interactive component that expands/collapses a panel, providing a way to hide content until it's needed.

## Key Features

- Full keyboard navigation support
- Can be controlled or uncontrolled
- Animatable with CSS variables for content dimensions
- Follows WAI-ARIA disclosure pattern

## Installation

```bash
npm install @radix-ui/react-collapsible
```

## Component Anatomy

```jsx
import { Collapsible } from "radix-ui";

export default () => (
  <Collapsible.Root>
    <Collapsible.Trigger />
    <Collapsible.Content />
  </Collapsible.Root>
);
```

## API Reference

### Root

Contains all parts of a collapsible.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `defaultOpen` | boolean | - | Initial open state (uncontrolled) |
| `open` | boolean | - | Controlled open state |
| `onOpenChange` | (open: boolean) => void | - | Handler for open state changes |
| `disabled` | boolean | - | Prevents user interaction |

**Data Attributes:**
- `[data-state="open"|"closed"]`
- `[data-disabled]` - Present when disabled

### Trigger

Button that toggles the collapsible.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

**Data Attributes:**
- `[data-state="open"|"closed"]`
- `[data-disabled]` - Present when disabled

### Content

Component that contains the collapsible content.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `forceMount` | boolean | - | Force mounting for animation control |

**Data Attributes:**
- `[data-state="open"|"closed"]`
- `[data-disabled]` - Present when disabled

**CSS Variables:**
- `--radix-collapsible-content-width` - Width of content during open/close
- `--radix-collapsible-content-height` - Height of content during open/close

## Usage Examples

### Basic Collapsible

```jsx
import { Collapsible } from "radix-ui";

export default () => (
  <Collapsible.Root className="CollapsibleRoot">
    <Collapsible.Trigger className="CollapsibleTrigger">
      Toggle content
    </Collapsible.Trigger>
    <Collapsible.Content className="CollapsibleContent">
      <p>Here is the collapsible content.</p>
    </Collapsible.Content>
  </Collapsible.Root>
);
```

### Animated Content

```jsx
// index.jsx
import { Collapsible } from "radix-ui";
import "./styles.css";

export default () => (
  <Collapsible.Root>
    <Collapsible.Trigger className="CollapsibleTrigger">
      Click to expand
    </Collapsible.Trigger>
    <Collapsible.Content className="CollapsibleContent">
      <div className="ContentInner">
        <p>Content that will be animated when expanding/collapsing.</p>
      </div>
    </Collapsible.Content>
  </Collapsible.Root>
);
```

```css
/* styles.css */
.CollapsibleContent {
  overflow: hidden;
}

.CollapsibleContent[data-state="open"] {
  animation: slideDown 300ms ease-out;
}

.CollapsibleContent[data-state="closed"] {
  animation: slideUp 300ms ease-out;
}

@keyframes slideDown {
  from {
    height: 0;
  }
  to {
    height: var(--radix-collapsible-content-height);
  }
}

@keyframes slideUp {
  from {
    height: var(--radix-collapsible-content-height);
  }
  to {
    height: 0;
  }
}
```

### Controlled Example

```jsx
import { Collapsible } from "radix-ui";
import { useState } from "react";

export default () => {
  const [open, setOpen] = useState(false);
  
  return (
    <Collapsible.Root
      open={open}
      onOpenChange={setOpen}
      className="CollapsibleRoot"
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>Section title</span>
        <Collapsible.Trigger className="CollapsibleTrigger">
          {open ? 'Hide' : 'Show'} content
        </Collapsible.Trigger>
      </div>
      
      <Collapsible.Content className="CollapsibleContent">
        <p>Here is the controlled collapsible content.</p>
      </Collapsible.Content>
    </Collapsible.Root>
  );
};
```

## Accessibility

Implements the [Disclosure WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure).

### Keyboard Interactions

| Key | Action |
| --- | ------ |
| `Space` | Opens/closes the collapsible |
| `Enter` | Opens/closes the collapsible |