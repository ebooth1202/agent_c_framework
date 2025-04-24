# Dropdown Menu Component

**Source:** Original from `shadcn-ui/components/dropdown-menu.mdx`  
**Created:** April 24, 2025  

## Overview
Displays a menu to the user — such as a set of actions or functions — triggered by a button. The dropdown menu is a core navigation and action component.

## Installation

### CLI Installation
```bash
npx shadcn@latest add dropdown-menu
```

### Manual Installation
1. Install dependencies:
```bash
npm install @radix-ui/react-dropdown-menu
```
2. Copy and paste the code from the component source
3. Update import paths to match your project setup

## Usage

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
```

```tsx
<DropdownMenu>
  <DropdownMenuTrigger>Open</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Billing</DropdownMenuItem>
    <DropdownMenuItem>Team</DropdownMenuItem>
    <DropdownMenuItem>Subscription</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## Examples

### Checkboxes
A dropdown menu with checkbox items for multi-select options.

### Radio Group
A dropdown menu with radio items for single selection from a group.

## Changelog

### 2024-10-16: Classes for icons
Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the `DropdownMenuItem` to automatically style icons inside the dropdown menu item.

```diff
const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & {
    inset?: boolean
  }
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "relative ... gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
      inset && "pl-8",
      className
    )}
    {...props}
  />
))
```

### 2024-10-25: Classes for `<DropdownMenuSubTrigger />`
Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the `<DropdownMenuSubTrigger />` to automatically style icons inside.

```tsx
<DropdownMenuPrimitive.SubTrigger
  ref={ref}
  className={cn(
    "flex cursor-default gap-2 select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent data-[state=open]:bg-accent [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    inset && "pl-8",
    className
  )}
  {...props}
>
  {/* ... */}
</DropdownMenuPrimitive.SubTrigger>
```

## References
- Documentation: https://www.radix-ui.com/docs/primitives/components/dropdown-menu
- API Reference: https://www.radix-ui.com/docs/primitives/components/dropdown-menu#api-reference