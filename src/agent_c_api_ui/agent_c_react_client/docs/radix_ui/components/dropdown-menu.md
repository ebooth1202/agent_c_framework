# Dropdown Menu

*Created: 2025-04-24*

Displays a menu to the user—such as a set of actions or functions—triggered by a button.

## Component API

### Root

Contains all parts of a dropdown menu.

```jsx
<DropdownMenu.Root>
  <DropdownMenu.Trigger />
  <DropdownMenu.Portal>
    <DropdownMenu.Content>
      <DropdownMenu.Item />
    </DropdownMenu.Content>
  </DropdownMenu.Portal>
</DropdownMenu.Root>
```

**Props:**
- `defaultOpen`: Initial open state (uncontrolled) - boolean
- `open`: Controlled open state - boolean
- `onOpenChange`: Event handler for open state changes - `(open: boolean) => void`
- `modal`: Controls modality (default: true) - boolean
- `dir`: Reading direction for submenus - "ltr" | "rtl"

### Trigger

The button that toggles the dropdown menu.

**Props:**
- `asChild`: Merges props with child element - boolean

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-disabled]`: Present when disabled

### Content

The component that pops out when dropdown menu is open.

**Props:**
- `asChild`: Merges props with child element - boolean
- `loop`: Enables keyboard navigation looping - boolean
- `side`: Preferred side of trigger - "top" | "right" | "bottom" | "left" (default: "bottom")
- `sideOffset`: Distance from trigger - number (default: 0)
- `align`: Preferred alignment - "start" | "center" | "end" (default: "center")
- `alignOffset`: Offset from alignment - number (default: 0)
- `avoidCollisions`: Prevents boundary collisions - boolean (default: true)
- `collisionBoundary`: Element(s) used for collision detection - Element | null | Array
- `collisionPadding`: Distance from boundaries for collision detection - number | Partial<Record<Side, number>>
- `arrowPadding`: Padding between arrow and content edges - number
- `sticky`: Controls align axis sticky behavior - "partial" | "always" (default: "partial")
- `hideWhenDetached`: Hides content when trigger is occluded - boolean
- Event handlers: `onCloseAutoFocus`, `onEscapeKeyDown`, `onPointerDownOutside`, `onFocusOutside`, `onInteractOutside`

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-side]`: "left" | "right" | "bottom" | "top"
- `[data-align]`: "start" | "end" | "center"
- `[data-orientation]`: "vertical" | "horizontal"

**CSS Variables:**
- `--radix-dropdown-menu-content-transform-origin`
- `--radix-dropdown-menu-content-available-width`
- `--radix-dropdown-menu-content-available-height`
- `--radix-dropdown-menu-trigger-width`
- `--radix-dropdown-menu-trigger-height`

### Item

Selectable menu item.

**Props:**
- `asChild`: Merges props with child element - boolean
- `disabled`: Prevents interaction when true - boolean
- `onSelect`: Event handler for selection - `(event: Event) => void`
- `textValue`: Text for typeahead purposes - string

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"
- `[data-highlighted]`: Present when highlighted
- `[data-disabled]`: Present when disabled

### CheckboxItem

Item that can be controlled like a checkbox.

**Props:**
- Standard Item props
- `checked`: Controlled checked state - `boolean | 'indeterminate'`
- `onCheckedChange`: Event handler for checked state changes - `(checked: boolean) => void`

**Data Attributes:**
- Standard Item data attributes
- `[data-state]`: "checked" | "unchecked" | "indeterminate"

### RadioGroup & RadioItem

Group of items where only one can be checked.

**RadioGroup Props:**
- `asChild`: Merges props with child element - boolean
- `value`: Selected item value - string
- `onValueChange`: Event handler for value changes - `(value: string) => void`

**RadioItem Props:**
- Standard Item props
- `value`: Unique item value (required) - string

**RadioItem Data Attributes:**
- Standard Item data attributes
- `[data-state]`: "checked" | "unchecked"

### ItemIndicator

Visual indicator for checked state in CheckboxItem/RadioItem.

**Props:**
- `asChild`: Merges props with child element - boolean
- `forceMount`: Forces mounting regardless of parent state - boolean

**Data Attributes:**
- `[data-state]`: "checked" | "unchecked" | "indeterminate"

### Additional Components

- `DropdownMenu.Arrow`: Optional visual arrow element
- `DropdownMenu.Group`: Groups related items
- `DropdownMenu.Label`: Non-interactive label text
- `DropdownMenu.Separator`: Visual separator between items
- `DropdownMenu.Sub`: Container for submenu parts
- `DropdownMenu.SubTrigger`: Item that opens a submenu
- `DropdownMenu.SubContent`: Content displayed in the submenu

## Accessibility

- Adheres to the Menu Button WAI-ARIA pattern
- Uses roving tabindex for keyboard navigation
- Supports typeahead for quick item selection
- Automatically manages focus when opened/closed

**Keyboard Interactions:**
- Space/Enter: Opens menu and focuses first item when trigger is focused; activates item when item is focused
- ArrowDown: Opens menu when trigger is focused; moves focus to next item when menu is open
- ArrowUp: Moves focus to previous item
- ArrowRight/ArrowLeft: Opens/closes submenus depending on reading direction
- Esc: Closes menu and returns focus to trigger

## Usage Examples

### Basic Dropdown Menu

```jsx
<DropdownMenu.Root>
  <DropdownMenu.Trigger>Options</DropdownMenu.Trigger>
  <DropdownMenu.Portal>
    <DropdownMenu.Content>
      <DropdownMenu.Item>Edit</DropdownMenu.Item>
      <DropdownMenu.Item>Duplicate</DropdownMenu.Item>
      <DropdownMenu.Separator />
      <DropdownMenu.Item>Archive</DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Portal>
</DropdownMenu.Root>
```

### With Checkbox Items

```jsx
import * as React from "react";
import { CheckIcon } from "@radix-ui/react-icons";

export default () => {
  const [showStatus, setShowStatus] = React.useState(true);
  
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>Settings</DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content>
          <DropdownMenu.Label>Preferences</DropdownMenu.Label>
          <DropdownMenu.CheckboxItem
            checked={showStatus}
            onCheckedChange={setShowStatus}
          >
            <DropdownMenu.ItemIndicator>
              <CheckIcon />
            </DropdownMenu.ItemIndicator>
            Show status bar
          </DropdownMenu.CheckboxItem>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
};
```

### With Submenu

```jsx
<DropdownMenu.Root>
  <DropdownMenu.Trigger>Edit</DropdownMenu.Trigger>
  <DropdownMenu.Portal>
    <DropdownMenu.Content>
      <DropdownMenu.Item>Cut</DropdownMenu.Item>
      <DropdownMenu.Item>Copy</DropdownMenu.Item>
      <DropdownMenu.Item>Paste</DropdownMenu.Item>
      <DropdownMenu.Separator />
      <DropdownMenu.Sub>
        <DropdownMenu.SubTrigger>More Options u2192</DropdownMenu.SubTrigger>
        <DropdownMenu.Portal>
          <DropdownMenu.SubContent>
            <DropdownMenu.Item>Select All</DropdownMenu.Item>
            <DropdownMenu.Item>Find & Replace...</DropdownMenu.Item>
            <DropdownMenu.Arrow />
          </DropdownMenu.SubContent>
        </DropdownMenu.Portal>
      </DropdownMenu.Sub>
    </DropdownMenu.Content>
  </DropdownMenu.Portal>
</DropdownMenu.Root>
```

### Styled With CSS Variables

```jsx
// index.jsx
import { DropdownMenu } from "radix-ui";
import "./styles.css";

export default () => (
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>Options</DropdownMenu.Trigger>
    <DropdownMenu.Portal>
      <DropdownMenu.Content className="DropdownMenuContent" sideOffset={5}>
        <DropdownMenu.Item className="DropdownMenuItem">New Tab</DropdownMenu.Item>
        <DropdownMenu.Item className="DropdownMenuItem">New Window</DropdownMenu.Item>
        <DropdownMenu.Arrow className="DropdownMenuArrow" />
      </DropdownMenu.Content>
    </DropdownMenu.Portal>
  </DropdownMenu.Root>
);
```

```css
/* styles.css */
.DropdownMenuContent {
  width: var(--radix-dropdown-menu-trigger-width);
  max-height: var(--radix-dropdown-menu-content-available-height);
  background-color: white;
  border-radius: 6px;
  padding: 5px;
  box-shadow: 0px 10px 38px -10px rgba(22, 23, 24, 0.35);
  animation: scaleIn 0.2s ease-out;
  transform-origin: var(--radix-dropdown-menu-content-transform-origin);
}

.DropdownMenuItem {
  padding: 8px 12px;
  outline: none;
  border-radius: 4px;
}

.DropdownMenuItem[data-highlighted] {
  background-color: #f5f5f5;
}

.DropdownMenuArrow {
  fill: white;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}
```