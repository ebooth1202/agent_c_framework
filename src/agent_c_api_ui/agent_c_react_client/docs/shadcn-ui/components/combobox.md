# Combobox

_Created: 2025-04-24 | Source: combobox.mdx_

## Overview

An autocomplete input and command palette with a list of suggestions. This component combines the functionality of a dropdown and a search input, allowing users to filter through a list of options.

## Key Features

- Searchable dropdown interface
- Keyboard navigation support
- Customizable rendering of options
- Selection indicator
- Empty state handling
- Support for form integration
- Responsive variations available

## Installation

The Combobox is built using a composition of the `<Popover />` and the `<Command />` components. You'll need to install both of these components first.

1. Install the Popover component
2. Install the Command component

## Component Structure

The Combobox is composed of several parts:

- `Popover`: Container for the dropdown functionality
  - `PopoverTrigger`: The button that opens the dropdown
  - `PopoverContent`: The content shown when the dropdown is open
- `Command`: The command palette component
  - `CommandInput`: The search input
  - `CommandList`: Container for the list of options
  - `CommandEmpty`: Displayed when no results match the search
  - `CommandGroup`: Group of related command items
  - `CommandItem`: Individual selectable option

## Usage

```tsx
import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

// Define the options
const frameworks = [
  { value: "next.js", label: "Next.js" },
  { value: "sveltekit", label: "SvelteKit" },
  { value: "nuxt.js", label: "Nuxt.js" },
  { value: "remix", label: "Remix" },
  { value: "astro", label: "Astro" },
]

export function ComboboxDemo() {
  const [open, setOpen] = React.useState(false)
  const [value, setValue] = React.useState("")

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {value
            ? frameworks.find((framework) => framework.value === value)?.label
            : "Select framework..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search framework..." />
          <CommandList>
            <CommandEmpty>No framework found.</CommandEmpty>
            <CommandGroup>
              {frameworks.map((framework) => (
                <CommandItem
                  key={framework.value}
                  value={framework.value}
                  onSelect={(currentValue) => {
                    setValue(currentValue === value ? "" : currentValue)
                    setOpen(false)
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === framework.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {framework.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
```

## Common Variants

### Standard Combobox
A basic combobox with a list of options and search functionality.

### Popover Combobox
A combobox that opens in a popover instead of directly below the input.

### Dropdown Menu Combobox
A combobox embedded within a dropdown menu for more complex UIs.

### Responsive Combobox
Uses `<Popover />` on desktop and `<Drawer />` on mobile for better small-screen experience:

```tsx
// Determine if mobile based on viewport width
const isDesktop = useMediaQuery("(min-width: 768px)")

// Use appropriate component based on screen size
{isDesktop ? (
  <Popover>/* Combobox content */</Popover>
) : (
  <Drawer>/* Combobox content */</Drawer>
)}
```

### Form-Integrated Combobox
A combobox that integrates with form libraries like React Hook Form.