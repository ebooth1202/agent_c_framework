# Toggle Group Component

**Purpose**: A set of two-state buttons that can be toggled on or off.

## Key Features

- Supports single or multiple selected items
- Full keyboard navigation with roving tabindex
- Supports horizontal and vertical orientation
- Can be controlled or uncontrolled

## Installation

```bash
npm install @radix-ui/react-toggle-group
```

## Component Anatomy

```jsx
import { ToggleGroup } from "radix-ui";

export default () => (
	<ToggleGroup.Root>
		<ToggleGroup.Item />
	</ToggleGroup.Root>
);
```

## API Reference

### Root

Contains all the parts of a toggle group.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `type` ("single" | "multiple", required) - Determines selection mode
- `value` (string or string[]) - Controlled value(s) of pressed item(s)
- `defaultValue` (string or string[]) - Initial value(s) when uncontrolled
- `onValueChange` (function) - Handler when pressed state changes
- `disabled` (boolean, default: false) - Disables the entire group
- `rovingFocus` (boolean, default: true) - Enables arrow key navigation
- `orientation` ("horizontal" | "vertical") - Controls focus movement direction
- `dir` ("ltr" | "rtl") - Reading direction
- `loop` (boolean, default: true) - Whether focus wraps around edges

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### Item

An individual toggle button in the group.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `value` (string, required) - Unique identifier for the item
- `disabled` (boolean) - Disables just this item

**Data Attributes:**
- `[data-state]`: "on" | "off"
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

## Implementation Examples

### Ensuring a Value is Always Selected

```jsx
import * as React from "react";
import { ToggleGroup } from "radix-ui";

export default () => {
  const [value, setValue] = React.useState("left");

  return (
    <ToggleGroup.Root
      type="single"
      value={value}
      onValueChange={(value) => {
        if (value) setValue(value);
      }}
    >
      <ToggleGroup.Item value="left">
        <TextAlignLeftIcon />
      </ToggleGroup.Item>
      <ToggleGroup.Item value="center">
        <TextAlignCenterIcon />
      </ToggleGroup.Item>
      <ToggleGroup.Item value="right">
        <TextAlignRightIcon />
      </ToggleGroup.Item>
    </ToggleGroup.Root>
  );
};
```

## Accessibility

Uses [roving tabindex](https://www.w3.org/TR/wai-aria-practices-1.2/examples/radio/radio.html) to manage focus movement among items.

### Keyboard Interactions

- **Tab**: Moves focus to either the pressed item or the first item in the group
- **Space/Enter**: Activates or deactivates the focused item
- **Arrow Down/Right**: Moves focus to the next item
- **Arrow Up/Left**: Moves focus to the previous item
- **Home**: Moves focus to the first item
- **End**: Moves focus to the last item