# Menubar Component
Created: 2025-04-24
Source: menubar.mdx

## Overview
The Menubar component provides a visually persistent menu commonly used in desktop applications, giving quick access to a consistent set of commands. It implements the WAI-ARIA Menubar pattern.

## Features
- Horizontal navigation menu with dropdown submenus
- Keyboard navigation support
- Visual persistence across application views
- Support for nested menus
- Keyboard shortcuts display
- Built on Radix UI's accessible primitives

## Installation

```bash
npx shadcn@latest add menubar
```

Or manually:

```bash
npm install @radix-ui/react-menubar
```

## Component Structure

```tsx
<Menubar>
  <MenubarMenu>
    <MenubarTrigger>...</MenubarTrigger>
    <MenubarContent>
      <MenubarItem>...</MenubarItem>
      <MenubarSeparator />
      <MenubarCheckboxItem>...</MenubarCheckboxItem>
      <MenubarRadioGroup>
        <MenubarRadioItem>...</MenubarRadioItem>
      </MenubarRadioGroup>
      <MenubarSub>
        <MenubarSubTrigger>...</MenubarSubTrigger>
        <MenubarSubContent>...</MenubarSubContent>
      </MenubarSub>
    </MenubarContent>
  </MenubarMenu>
</Menubar>
```

## Basic Usage

```tsx
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarShortcut,
  MenubarTrigger,
} from "@/components/ui/menubar"

function AppMenubar() {
  return (
    <Menubar>
      <MenubarMenu>
        <MenubarTrigger>File</MenubarTrigger>
        <MenubarContent>
          <MenubarItem>
            New Tab <MenubarShortcut>⌘T</MenubarShortcut>
          </MenubarItem>
          <MenubarItem>New Window</MenubarItem>
          <MenubarSeparator />
          <MenubarItem>Share</MenubarItem>
          <MenubarSeparator />
          <MenubarItem>Print</MenubarItem>
        </MenubarContent>
      </MenubarMenu>

      <MenubarMenu>
        <MenubarTrigger>Edit</MenubarTrigger>
        <MenubarContent>
          <MenubarItem>
            Undo <MenubarShortcut>⌘Z</MenubarShortcut>
          </MenubarItem>
          <MenubarItem>
            Redo <MenubarShortcut>⇧⌘Z</MenubarShortcut>
          </MenubarItem>
          <MenubarSeparator />
          <MenubarItem>
            Cut <MenubarShortcut>⌘X</MenubarShortcut>
          </MenubarItem>
          <MenubarItem>
            Copy <MenubarShortcut>⌘C</MenubarShortcut>
          </MenubarItem>
          <MenubarItem>
            Paste <MenubarShortcut>⌘V</MenubarShortcut>
          </MenubarItem>
        </MenubarContent>
      </MenubarMenu>

      <MenubarMenu>
        <MenubarTrigger>View</MenubarTrigger>
        <MenubarContent>
          <MenubarCheckboxItem>Show Toolbar</MenubarCheckboxItem>
          <MenubarCheckboxItem checked>Show Statusbar</MenubarCheckboxItem>
        </MenubarContent>
      </MenubarMenu>
    </Menubar>
  )
}
```

## Components and Props

### Menubar
Main container for the menubar.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `defaultValue` | string | The value of the menu that should be active when initially rendered |
| `value` | string | The controlled value of the menu to activate |
| `onValueChange` | function | Callback for when a menu value changes |
| `loop` | boolean | When `true`, keyboard navigation will loop from last item to first item and vice versa |

### MenubarMenu
Gives the menu item its functionality.

### MenubarTrigger
The button that toggles the menu. By default, this button is a `MenubarTrigger`.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `asChild` | boolean | Change the component to the provided element |

### MenubarContent
Contains the menu items. By default, this centers aligned relative to its trigger.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `loop` | boolean | When `true`, keyboard navigation will loop from last item to first item and vice versa |
| `sideOffset` | number | Distance in pixels from the trigger |
| `align` | "start" \| "center" \| "end" | Preferred alignment against the trigger |
| `alignOffset` | number | Offset in pixels from the "start" or "end" alignment |

### MenubarItem
The component for menu items without any interactions.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `inset` | boolean | When `true`, renders with indentation to account for the presence of a checkbox |

### MenubarCheckboxItem
A menu item that can be controlled and toggled like a checkbox.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `checked` | boolean | The controlled checked state of the item |
| `onCheckedChange` | function | Event handler called when the checked state changes |

### MenubarRadioGroup
Used to group multiple `MenubarRadioItem`s together.

### MenubarRadioItem
An item that can be controlled and toggled like a radio button.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `value` | string | The unique value of the item |
| `checked` | boolean | The controlled checked state of the item |

### MenubarSeparator
Visually or semantically separates menu items.

### MenubarShortcut
Displays keyboard shortcut hints alongside menu items.

## Use Cases

### Application Menus
Implement desktop-like application menus in web apps for consistent command access.

### Command Palettes
Provide an organized structure for accessing application commands.

### Navigation Systems
Create complex navigation with contextual submenus and actions.

### Settings Menus
Organize application settings in a familiar menu structure.

## Accessibility

- Follows the WAI-ARIA [Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) design pattern
- Keyboard navigation with arrow keys, home/end keys, and typeahead
- ARIA roles, states, and properties managed automatically
- Focus management for keyboard and screen reader users