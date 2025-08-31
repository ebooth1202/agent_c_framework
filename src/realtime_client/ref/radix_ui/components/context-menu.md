# Context Menu

*Created: 2025-04-24*

Displays a menu located at the pointer, triggered by a right-click or long press.

## Component API

### Root

Contains all parts of a context menu.

```jsx
<ContextMenu.Root>
  <ContextMenu.Trigger />
  <ContextMenu.Content />
</ContextMenu.Root>
```

**Props:**
- `dir`: Reading direction - "ltr" | "rtl"
- `onOpenChange`: Event handler for open state changes - `(open: boolean) => void`
- `modal`: Controls menu modality (default: true) - boolean

### Trigger

The area that opens the context menu on right-click.

**Props:**
- `asChild`: Merges props with child element - boolean
- `disabled`: Prevents opening when true - boolean

**Data Attributes:**
- `[data-state]`: "open" | "closed"

### Content

The component that pops out when context menu is open.

**Props:**
- `asChild`: Merges props with child element - boolean
- `loop`: Enables keyboard navigation looping - boolean
- `alignOffset`: Vertical distance from anchor - number
- `avoidCollisions`: Prevents boundary collisions - boolean
- `collisionBoundary`: Element(s) used for collision detection
- `collisionPadding`: Distance from boundaries for collision detection
- `sticky`: Controls align axis sticky behavior - "partial" | "always"
- `hideWhenDetached`: Hides content when trigger is occluded - boolean
- Event handlers: `onCloseAutoFocus`, `onEscapeKeyDown`, `onPointerDownOutside`, `onFocusOutside`, `onInteractOutside`

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-side]`: "left" | "right" | "bottom" | "top"
- `[data-align]`: "start" | "end" | "center"

**CSS Variables:**
- `--radix-context-menu-content-transform-origin`
- `--radix-context-menu-content-available-width`
- `--radix-context-menu-content-available-height`
- `--radix-context-menu-trigger-width`
- `--radix-context-menu-trigger-height`

### Item

Selectable menu item.

**Props:**
- `asChild`: Merges props with child element - boolean
- `disabled`: Prevents interaction when true - boolean
- `onSelect`: Event handler for selection - `(event: Event) => void`
- `textValue`: Text for typeahead purposes - string

**Data Attributes:**
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

### Sub Components

For creating nested submenus:

- `ContextMenu.Sub`: Container for submenu parts
- `ContextMenu.SubTrigger`: Item that opens a submenu
- `ContextMenu.SubContent`: Content displayed in the submenu

### Other Components

- `ContextMenu.Label`: Non-interactive label text
- `ContextMenu.Group`: Groups related items
- `ContextMenu.Separator`: Visual separator between items
- `ContextMenu.Arrow`: Optional visual arrow element

## Accessibility

- Uses roving tabindex for keyboard navigation
- Follows WAI-ARIA Menu pattern
- Supports typeahead for quick item selection

**Keyboard Interactions:**
- Space/Enter: Activates focused item
- ArrowDown/ArrowUp: Navigate between items
- ArrowRight/ArrowLeft: Open/close submenus
- Esc: Close menu

## Usage Examples

### Basic Context Menu

```jsx
<ContextMenu.Root>
  <ContextMenu.Trigger>Right click me</ContextMenu.Trigger>
  <ContextMenu.Portal>
    <ContextMenu.Content>
      <ContextMenu.Item>Edit</ContextMenu.Item>
      <ContextMenu.Item>Duplicate</ContextMenu.Item>
      <ContextMenu.Separator />
      <ContextMenu.Item>Archive</ContextMenu.Item>
    </ContextMenu.Content>
  </ContextMenu.Portal>
</ContextMenu.Root>
```

### With Checkbox Items

```jsx
import * as React from "react";

export default () => {
  const [checked, setChecked] = React.useState(true);
  
  return (
    <ContextMenu.Root>
      <ContextMenu.Trigger>Right click me</ContextMenu.Trigger>
      <ContextMenu.Portal>
        <ContextMenu.Content>
          <ContextMenu.CheckboxItem
            checked={checked}
            onCheckedChange={setChecked}
          >
            <ContextMenu.ItemIndicator>
              <CheckIcon />
            </ContextMenu.ItemIndicator>
            Show Details
          </ContextMenu.CheckboxItem>
        </ContextMenu.Content>
      </ContextMenu.Portal>
    </ContextMenu.Root>
  );
};
```

### With Submenu

```jsx
<ContextMenu.Root>
  <ContextMenu.Trigger>Right click me</ContextMenu.Trigger>
  <ContextMenu.Portal>
    <ContextMenu.Content>
      <ContextMenu.Item>Back</ContextMenu.Item>
      <ContextMenu.Item>Forward</ContextMenu.Item>
      <ContextMenu.Separator />
      <ContextMenu.Sub>
        <ContextMenu.SubTrigger>More Options →</ContextMenu.SubTrigger>
        <ContextMenu.Portal>
          <ContextMenu.SubContent>
            <ContextMenu.Item>Save Page As...</ContextMenu.Item>
            <ContextMenu.Item>Create Shortcut...</ContextMenu.Item>
            <ContextMenu.Arrow />
          </ContextMenu.SubContent>
        </ContextMenu.Portal>
      </ContextMenu.Sub>
    </ContextMenu.Content>
  </ContextMenu.Portal>
</ContextMenu.Root>
```