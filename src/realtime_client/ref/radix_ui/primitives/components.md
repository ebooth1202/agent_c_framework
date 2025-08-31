# Radix UI Components Reference

*AI-optimized component reference documentation*

## Accordion

A vertically stacked set of interactive headings that each reveal a section of content.

### Usage

```jsx
import { Accordion } from "radix-ui";

export default () => (
  <Accordion.Root type="single" defaultValue="item-1" collapsible>
    <Accordion.Item value="item-1">
      <Accordion.Trigger>Item 1</Accordion.Trigger>
      <Accordion.Content>Content 1</Accordion.Content>
    </Accordion.Item>
    <Accordion.Item value="item-2">
      <Accordion.Trigger>Item 2</Accordion.Trigger>
      <Accordion.Content>Content 2</Accordion.Content>
    </Accordion.Item>
  </Accordion.Root>
);
```

### API Reference

#### Root
- `type`: "single" | "multiple" - Controls whether one or multiple items can be opened
- `collapsible`: boolean - For type="single", allows closing content when clicking the trigger
- `value`: string - For controlled accordion
- `defaultValue`: string - For uncontrolled accordion
- `onValueChange`: function - Called when value changes
- `orientation`: "horizontal" | "vertical" - Orientation of the accordion
- `dir`: "ltr" | "rtl" - Direction for RTL support

#### Item
- `value`: string - Unique identifier for the item
- `disabled`: boolean - When true, prevents user interaction

#### Trigger
- Standard button attributes

#### Content
- When animating, exposes `--radix-accordion-content-height` CSS variable

## Alert Dialog

A modal dialog that interrupts the user with important content and expects a response.

### Usage

```jsx
import { AlertDialog } from "radix-ui";

export default () => (
  <AlertDialog.Root>
    <AlertDialog.Trigger>Delete account</AlertDialog.Trigger>
    <AlertDialog.Portal>
      <AlertDialog.Overlay />
      <AlertDialog.Content>
        <AlertDialog.Title>Are you sure?</AlertDialog.Title>
        <AlertDialog.Description>
          This action cannot be undone.
        </AlertDialog.Description>
        <AlertDialog.Cancel>Cancel</AlertDialog.Cancel>
        <AlertDialog.Action>Delete</AlertDialog.Action>
      </AlertDialog.Content>
    </AlertDialog.Portal>
  </AlertDialog.Root>
);
```

### API Reference

#### Root
- `open`: boolean - Controlled open state
- `defaultOpen`: boolean - Uncontrolled default open state
- `onOpenChange`: function - Called when open state changes

#### Content
- `forceMount`: boolean - Forces mounting when used with animation libraries
- `onEscapeKeyDown`: function - Called when escape key is pressed
- `onPointerDownOutside`: function - Called when pointer is pressed outside

#### Title
- Required for accessibility

#### Description
- Accessible description that's announced to screen readers

#### Cancel
- Takes focus when AlertDialog opens

## Checkbox

A control that allows the user to toggle between checked and unchecked states.

### Usage

```jsx
import { Checkbox } from "radix-ui";

export default () => (
  <form>
    <Checkbox.Root defaultChecked id="c1">
      <Checkbox.Indicator>
        {/* Your checked indicator (e.g., checkmark icon) */}
      </Checkbox.Indicator>
    </Checkbox.Root>
    <label htmlFor="c1">Accept terms and conditions</label>
  </form>
);
```

### API Reference

#### Root
- `checked`: boolean - Controlled checked state
- `defaultChecked`: boolean - Uncontrolled default checked state
- `onCheckedChange`: function - Called when checked state changes
- `disabled`: boolean - When true, prevents user interaction
- `required`: boolean - When true, indicates input must have a value
- `name`: string - Name of the form input
- `value`: string - Value of the form input

## Dialog

A window overlaid on either the primary window or another dialog window, rendering the content underneath inert.

### Usage

```jsx
import { Dialog } from "radix-ui";

export default () => (
  <Dialog.Root>
    <Dialog.Trigger>Open dialog</Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay />
      <Dialog.Content>
        <Dialog.Title>Dialog Title</Dialog.Title>
        <Dialog.Description>Dialog Description</Dialog.Description>
        <Dialog.Close>Close</Dialog.Close>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
);
```

### API Reference

#### Root
- `open`: boolean - Controlled open state
- `defaultOpen`: boolean - Uncontrolled default open state
- `onOpenChange`: function - Called when open state changes
- `modal`: boolean - Whether to render a modal dialog

#### Content
- `forceMount`: boolean - Forces mounting when used with animation libraries
- `onEscapeKeyDown`: function - Called when escape key is pressed
- `onPointerDownOutside`: function - Called when pointer is pressed outside
- `onInteractOutside`: function - Called when an interaction happens outside

## DropdownMenu

Displays a menu to the user—such as a set of actions or functions—triggered by a button.

### Usage

```jsx
import { DropdownMenu } from "radix-ui";

export default () => (
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>Options</DropdownMenu.Trigger>
    <DropdownMenu.Portal>
      <DropdownMenu.Content>
        <DropdownMenu.Item>New Tab</DropdownMenu.Item>
        <DropdownMenu.Item>New Window</DropdownMenu.Item>
        <DropdownMenu.Separator />
        <DropdownMenu.CheckboxItem checked>
          Show Bookmarks
        </DropdownMenu.CheckboxItem>
        <DropdownMenu.Sub>
          <DropdownMenu.SubTrigger>More Tools</DropdownMenu.SubTrigger>
          <DropdownMenu.Portal>
            <DropdownMenu.SubContent>
              <DropdownMenu.Item>Save Page As…</DropdownMenu.Item>
              <DropdownMenu.Item>Create Shortcut…</DropdownMenu.Item>
            </DropdownMenu.SubContent>
          </DropdownMenu.Portal>
        </DropdownMenu.Sub>
      </DropdownMenu.Content>
    </DropdownMenu.Portal>
  </DropdownMenu.Root>
);
```

### API Reference

#### Root
- `open`: boolean - Controlled open state
- `defaultOpen`: boolean - Uncontrolled default open state
- `onOpenChange`: function - Called when open state changes
- `modal`: boolean - Whether interaction with outside elements should be disabled
- `dir`: "ltr" | "rtl" - Direction for submenus

#### Content
- `alignOffset`: number - Offset distance for alignment
- `avoidCollisions`: boolean - When true, overrides side/align to prevent collisions
- `collisionPadding`: number | object - Padding between content and viewport edges
- `sticky`: "partial" | "always" - Controls content's sticky behavior during scrolling

## HoverCard

For sighted users to preview content available behind a link.

### Usage

```jsx
import { HoverCard } from "radix-ui";

export default () => (
  <HoverCard.Root>
    <HoverCard.Trigger>Hover me</HoverCard.Trigger>
    <HoverCard.Portal>
      <HoverCard.Content>
        Hover card content
        <HoverCard.Arrow />
      </HoverCard.Content>
    </HoverCard.Portal>
  </HoverCard.Root>
);
```

### API Reference

#### Root
- `open`: boolean - Controlled open state
- `defaultOpen`: boolean - Uncontrolled default open state
- `onOpenChange`: function - Called when open state changes
- `openDelay`: number - Delay in ms before opening
- `closeDelay`: number - Delay in ms before closing

## Other Components

Radix UI includes many more primitives including:

- **NavigationMenu**: A collection of links for site navigation.
- **Popover**: Displays rich content in a portal, triggered by a button.
- **RadioGroup**: A set of checkable buttons where only one can be checked.
- **Select**: Displays a list of options for the user to pick from.
- **Slider**: Allows users to select a value from a range.
- **Switch**: A control that allows toggling between on and off states.
- **Tabs**: Organizes content into separate views where only one can be visible.
- **Toast**: A succinct message that's displayed temporarily.
- **Tooltip**: A popup that displays information related to an element.

Each component follows similar patterns with consistent APIs for controlling, styling, and extending behavior.