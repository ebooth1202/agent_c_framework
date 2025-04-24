# Menubar Component

**Purpose:** Provides a visually persistent menu interface common in desktop applications, giving quick access to a consistent set of commands.

## Basic Usage

```jsx
import { Menubar } from "radix-ui";

export default () => (
  <Menubar.Root>
    <Menubar.Menu>
      <Menubar.Trigger>File</Menubar.Trigger>
      <Menubar.Portal>
        <Menubar.Content>
          <Menubar.Item>New</Menubar.Item>
          <Menubar.Item>Open</Menubar.Item>
          <Menubar.Separator />
          <Menubar.Item>Save</Menubar.Item>
        </Menubar.Content>
      </Menubar.Portal>
    </Menubar.Menu>
    
    <Menubar.Menu>
      <Menubar.Trigger>Edit</Menubar.Trigger>
      {/* Similar content structure */}
    </Menubar.Menu>
  </Menubar.Root>
);
```

## Key Features
- Controlled or uncontrolled menu state
- Support for submenus with configurable reading direction
- Groups, labels, checkable items (single/multiple)
- Customizable positioning with collision handling
- Fully managed focus with keyboard navigation
- Typeahead support for quick navigation

## Component API

### Menubar.Root

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `defaultValue` | string | - | Default open menu value (uncontrolled) |
| `value` | string | - | Controlled open menu value |
| `onValueChange` | (value: string) => void | - | Open menu value change handler |
| `dir` | "ltr" \| "rtl" | - | Reading direction |
| `loop` | boolean | false | Loop keyboard navigation |

### Menubar.Menu

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `value` | string | - | Unique identifier for menu item |

### Menubar.Trigger

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

**Data Attributes:**
- `[data-state]`: "open" or "closed"
- `[data-highlighted]`: Present when highlighted
- `[data-disabled]`: Present when disabled

### Menubar.Portal

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `forceMount` | boolean | - | Force content mounting |
| `container` | HTMLElement | document.body | Portal container |

### Menubar.Content

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `loop` | boolean | false | Loop keyboard navigation |
| `onCloseAutoFocus` | (event: Event) => void | - | Event handler when focus returns to trigger |
| `onEscapeKeyDown` | (event: KeyboardEvent) => void | - | Escape key handler |
| `onPointerDownOutside` | (event: PointerDownOutsideEvent) => void | - | Pointer outside handler |
| `onFocusOutside` | (event: FocusOutsideEvent) => void | - | Focus outside handler |
| `onInteractOutside` | (event: PointerDownOutsideEvent \| FocusOutsideEvent) => void | - | Interaction outside handler |
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

**Data Attributes & CSS Variables:** Same as DropdownMenu (data-state, data-side, data-align, transform-origin variables)

### Menubar.Item

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `disabled` | boolean | - | Disable the item |
| `onSelect` | (event: Event) => void | - | Selection handler |
| `textValue` | string | - | Text for typeahead |

**Data Attributes:** `[data-highlighted]`, `[data-disabled]`

### Menubar.Group / Menubar.Label / Menubar.Separator

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

### Menubar.CheckboxItem

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `checked` | boolean \| "indeterminate" | - | Checked state |
| `onCheckedChange` | (checked: boolean) => void | - | Checked state handler |
| `disabled` | boolean | - | Disable item |
| `onSelect` | (event: Event) => void | - | Selection handler |
| `textValue` | string | - | Text for typeahead |

**Data Attributes:** `[data-state]` ("checked", "unchecked"), `[data-highlighted]`, `[data-disabled]`

### Menubar.RadioGroup

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `value` | string | - | Selected radio value |
| `onValueChange` | (value: string) => void | - | Value change handler |

### Menubar.RadioItem

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `value` | string | Required | Item value |
| `disabled` | boolean | - | Disable item |
| `onSelect` | (event: Event) => void | - | Selection handler |
| `textValue` | string | - | Text for typeahead |

**Data Attributes:** Same as CheckboxItem

### Menubar.ItemIndicator

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `forceMount` | boolean | - | Force mounting |

**Data Attributes:** `[data-state]` ("checked", "unchecked")

### Menubar.Sub / Menubar.SubTrigger / Menubar.SubContent

Similar props as their Menubar counterparts with appropriate submenu context.

## Common Patterns

### With Submenus
```jsx
<Menubar.Sub>
  <Menubar.SubTrigger>More Options →</Menubar.SubTrigger>
  <Menubar.Portal>
    <Menubar.SubContent>
      <Menubar.Item>Submenu item</Menubar.Item>
      <Menubar.Item>Another item</Menubar.Item>
    </Menubar.SubContent>
  </Menubar.Portal>
</Menubar.Sub>
```

### Checkable Items
```jsx
<Menubar.CheckboxItem checked={checked} onCheckedChange={setChecked}>
  <Menubar.ItemIndicator>
    <CheckIcon />
  </Menubar.ItemIndicator>
  Toggle option
</Menubar.CheckboxItem>
```

### Radio Selection
```jsx
<Menubar.RadioGroup value={value} onValueChange={setValue}>
  <Menubar.RadioItem value="option1">
    <Menubar.ItemIndicator>
      <CheckIcon />
    </Menubar.ItemIndicator>
    Option 1
  </Menubar.RadioItem>
  <Menubar.RadioItem value="option2">Option 2</Menubar.RadioItem>
</Menubar.RadioGroup>
```

### Match Content Width to Trigger
```css
.MenubarContent {
  width: var(--radix-menubar-trigger-width);
  max-height: var(--radix-menubar-content-available-height);
}
```

## Accessibility Notes
- Implements the Menu Button WAI-ARIA design pattern
- Uses roving tabindex for focus management
- Full keyboard navigation:
  - Space/Enter: Open menu / activate item
  - Arrow keys: Navigate items
  - Esc: Close menu
- Screen readers announce menu items properly