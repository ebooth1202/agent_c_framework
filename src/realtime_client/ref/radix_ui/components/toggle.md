# Toggle Component

**Purpose**: A two-state button that can be either on or off.

## Key Features

- Simple two-state toggle button
- Can be controlled or uncontrolled
- Full keyboard navigation
- Accessible button implementation

## Installation

```bash
npm install @radix-ui/react-toggle
```

## Component Anatomy

```jsx
import { Toggle } from "radix-ui";

export default () => <Toggle.Root />;
```

## API Reference

### Root

The toggle button component.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `defaultPressed` (boolean) - Initial pressed state when uncontrolled
- `pressed` (boolean) - Controlled pressed state, use with `onPressedChange`
- `onPressedChange` (function) - Handler called when pressed state changes
- `disabled` (boolean) - Prevents user interaction when true

**Data Attributes:**
- `[data-state]`: "on" | "off"
- `[data-disabled]`: Present when disabled

## Accessibility

Implements standard button accessibility practices.

### Keyboard Interactions

- **Space**: Activates/deactivates the toggle
- **Enter**: Activates/deactivates the toggle