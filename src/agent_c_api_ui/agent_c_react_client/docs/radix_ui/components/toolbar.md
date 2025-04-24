# Toolbar Component

**Purpose**: A container for grouping a set of controls, such as buttons, toggle groups or dropdown menus.

## Key Features

- Provides accessible grouping of related controls
- Supports horizontal and vertical orientation
- Full keyboard navigation with roving tabindex
- Can be composed with other interactive components

## Installation

```bash
npm install @radix-ui/react-toolbar
```

## Component Anatomy

```jsx
import { Toolbar } from "radix-ui";

export default () => (
	<Toolbar.Root>
		<Toolbar.Button />
		<Toolbar.Separator />
		<Toolbar.Link />
		<Toolbar.ToggleGroup>
			<Toolbar.ToggleItem />
		</Toolbar.ToggleGroup>
	</Toolbar.Root>
);
```

## API Reference

### Root

Container for all toolbar parts.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `orientation` ("horizontal" | "vertical", default: "horizontal") - Toolbar orientation
- `dir` ("ltr" | "rtl") - Reading direction
- `loop` (boolean, default: true) - Whether keyboard navigation loops from last to first item

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### Button

A button item within the toolbar.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### Link

A link item within the toolbar.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### ToggleGroup

A set of two-state buttons that can be toggled on or off.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `type` ("single" | "multiple", required) - Selection mode
- `value` (string or string[]) - Controlled value(s) of pressed item(s)
- `defaultValue` (string or string[]) - Initial value(s) when uncontrolled
- `onValueChange` (function) - Handler when pressed state changes
- `disabled` (boolean, default: false) - Disables all toggle items

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### ToggleItem

An item in the toggle group.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `value` (string, required) - Unique identifier for the item
- `disabled` (boolean) - Disables just this item

**Data Attributes:**
- `[data-state]`: "on" | "off"
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

### Separator

Used to visually separate items in the toolbar.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

## Implementation Examples

### Composition with Other Primitives

Toolbar can be composed with other components that have a trigger part:

```jsx
import { Toolbar, DropdownMenu } from "radix-ui";

export default () => (
  <Toolbar.Root>
    <Toolbar.Button>Action 1</Toolbar.Button>
    <Toolbar.Separator />
    <DropdownMenu.Root>
      <Toolbar.Button asChild>
        <DropdownMenu.Trigger>Trigger</DropdownMenu.Trigger>
      </Toolbar.Button>
      <DropdownMenu.Content>…</DropdownMenu.Content>
    </DropdownMenu.Root>
  </Toolbar.Root>
);
```

## Accessibility

Uses [roving tabindex](https://www.w3.org/TR/wai-aria-practices-1.2/examples/radio/radio.html) to manage focus movement among items.

### Keyboard Interactions

- **Tab**: Moves focus to the first item in the toolbar
- **Space/Enter**: Activates/deactivates the focused item
- **Arrow Down/Right**: Moves focus to the next item based on orientation
- **Arrow Up/Left**: Moves focus to the previous item based on orientation
- **Home**: Moves focus to the first item
- **End**: Moves focus to the last item