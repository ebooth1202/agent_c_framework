# Command Component

*Created: April 24, 2025 from source file command.mdx*

## Overview
A fast, composable command menu (command palette) for React applications, built using the cmdk component.

## Key Features
- Keyboard-navigable command interface
- Search functionality
- Grouping of commands
- Dialog mode for global access
- Customizable styling
- Keyboard shortcut support

## Installation

```bash
npm install cmdk
```

## Usage Example

```tsx
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

<Command>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search Emoji</CommandItem>
      <CommandItem>Calculator</CommandItem>
    </CommandGroup>
    <CommandSeparator />
    <CommandGroup heading="Settings">
      <CommandItem>Profile</CommandItem>
      <CommandItem>Billing</CommandItem>
      <CommandItem>Settings</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

## Component Structure
The Command component consists of several parts:
- `Command`: The main container
- `CommandInput`: Search input field
- `CommandList`: Container for command items
- `CommandEmpty`: Displayed when no results match search
- `CommandGroup`: Groups related commands with headings
- `CommandItem`: Individual command option
- `CommandSeparator`: Visual divider between groups
- `CommandShortcut`: Displays keyboard shortcut
- `CommandDialog`: Modal version of the command menu

## Dialog Usage
Implement a global command menu with keyboard shortcut (Cmd/Ctrl+K):

```tsx
export function CommandMenu() {
  const [open, setOpen] = React.useState(false)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>Calendar</CommandItem>
          <CommandItem>Search Emoji</CommandItem>
          <CommandItem>Calculator</CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

## Common Use Cases
- Application command palette
- Enhanced search interfaces
- Navigation systems
- Feature discovery
- Quick action menus
- As a base for combobox components

## Recent Updates
- 2024-10-25: Added styling for icons inside CommandItem with automatic spacing and sizing