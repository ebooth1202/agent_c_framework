# Styling Radix UI with Tailwind CSS

*AI-optimized styling reference documentation*

Tailwind CSS works exceptionally well with Radix UI primitives, providing utility classes for rapid styling without requiring separate CSS files. This approach is ideal for teams that prefer the utility-first workflow.

## Basic Integration

```jsx
import { Dialog } from "radix-ui";

export function DialogExample() {
  return (
    <Dialog.Root>
      <Dialog.Trigger className="px-4 py-2 text-white bg-indigo-600 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
        Open Dialog
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 animate-fade-in" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-md max-h-[85vh] p-6 bg-white rounded-lg shadow-xl animate-content-show">
          <Dialog.Title className="text-xl font-semibold text-gray-900">
            Dialog Title
          </Dialog.Title>
          <Dialog.Description className="mt-2 text-gray-600">
            This is a dialog built with Radix UI and styled with Tailwind CSS.
          </Dialog.Description>
          <div className="mt-6 flex justify-end">
            <Dialog.Close className="px-4 py-2 text-white bg-indigo-600 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
              Close
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

## Styling Component States with Data Attributes

Tailwind CSS can target Radix component states using modifier syntax with data attributes:

```jsx
import { Accordion } from "radix-ui";

export function AccordionExample() {
  return (
    <Accordion.Root type="single" collapsible className="w-80 rounded-md bg-white shadow">
      <Accordion.Item value="item-1" className="border-b border-gray-200">
        <Accordion.Trigger className="group flex w-full items-center justify-between p-4 text-left hover:bg-gray-50 data-[state=open]:bg-gray-50">
          <span>Section 1</span>
          <svg 
            className="h-5 w-5 text-gray-500 transition-transform duration-300 group-data-[state=open]:rotate-180" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </Accordion.Trigger>
        <Accordion.Content className="overflow-hidden data-[state=open]:animate-slide-down data-[state=closed]:animate-slide-up">
          <div className="p-4 text-gray-600">
            Content for section 1
          </div>
        </Accordion.Content>
      </Accordion.Item>
    </Accordion.Root>
  );
}
```

## Tailwind Configuration for Animations

Add custom animations to your `tailwind.config.js` to work with Radix UI components:

```js
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "content-show": {
          "0%": { opacity: "0", transform: "translate(-50%, -48%) scale(0.96)" },
          "100%": { opacity: "1", transform: "translate(-50%, -50%) scale(1)" },
        },
        "slide-down": {
          "0%": { height: "0" },
          "100%": { height: "var(--radix-accordion-content-height)" },
        },
        "slide-up": {
          "0%": { height: "var(--radix-accordion-content-height)" },
          "100%": { height: "0" },
        },
      },
      animation: {
        "fade-in": "fade-in 150ms cubic-bezier(0.16, 1, 0.3, 1)",
        "content-show": "content-show 150ms cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-down": "slide-down 300ms cubic-bezier(0.87, 0, 0.13, 1)",
        "slide-up": "slide-up 300ms cubic-bezier(0.87, 0, 0.13, 1)",
      },
    },
  },
  plugins: [],
};
```

## Data Attribute Variants

Tailwind provides modifiers for targeting Radix UI states:

```jsx
/* Common data attributes modifiers */

// State indicators
<Dropdown.Trigger className="data-[state=open]:bg-gray-100" />
<Checkbox.Root className="data-[state=checked]:bg-indigo-600 data-[state=unchecked]:bg-gray-200" />

// Highlighted items
<Dropdown.Item className="data-[highlighted]:bg-gray-100" />

// Disabled elements
<Dropdown.Item className="data-[disabled]:opacity-50 data-[disabled]:pointer-events-none" />

// Side positioning
<Tooltip.Content className="data-[side=top]:animate-slide-down-fade data-[side=bottom]:animate-slide-up-fade" />

// Orientation
<ScrollArea.Scrollbar className="data-[orientation=vertical]:w-2 data-[orientation=horizontal]:h-2" />
```

## Complex Component Example: Dropdown Menu

```jsx
import { DropdownMenu } from "radix-ui";

export function DropdownMenuExample() {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger className="inline-flex items-center justify-center rounded px-4 py-2 text-sm font-medium bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
        Options
        <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </DropdownMenu.Trigger>
      
      <DropdownMenu.Portal>
        <DropdownMenu.Content 
          className="min-w-[220px] bg-white rounded-md p-1 shadow-lg will-change-[opacity,transform] data-[side=top]:animate-slide-down-fade data-[side=bottom]:animate-slide-up-fade data-[side=left]:animate-slide-right-fade data-[side=right]:animate-slide-left-fade"
          sideOffset={5}
        >
          <DropdownMenu.Item className="group relative flex h-8 select-none items-center rounded-md px-2 text-sm outline-none data-[disabled]:text-gray-300 data-[disabled]:pointer-events-none data-[highlighted]:bg-indigo-50 data-[highlighted]:text-indigo-600">
            New Tab
          </DropdownMenu.Item>
          
          <DropdownMenu.Item className="group relative flex h-8 select-none items-center rounded-md px-2 text-sm outline-none data-[disabled]:text-gray-300 data-[disabled]:pointer-events-none data-[highlighted]:bg-indigo-50 data-[highlighted]:text-indigo-600">
            New Window
          </DropdownMenu.Item>
          
          <DropdownMenu.Separator className="my-1 h-px bg-gray-200" />
          
          <DropdownMenu.CheckboxItem 
            className="group relative flex h-8 select-none items-center rounded-md pl-8 pr-2 text-sm outline-none data-[disabled]:text-gray-300 data-[disabled]:pointer-events-none data-[highlighted]:bg-indigo-50 data-[highlighted]:text-indigo-600"
            checked={true}
          >
            <DropdownMenu.ItemIndicator className="absolute left-2 inline-flex items-center justify-center">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </DropdownMenu.ItemIndicator>
            Show Bookmarks
          </DropdownMenu.CheckboxItem>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
```

## Using Tailwind JIT for Custom Data Attribute Selectors

If you need more custom data attribute selectors, you can add them to your Tailwind configuration:

```js
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      // Extension options here
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    function({ addVariant }) {
      // Add custom variants for Radix UI
      addVariant('highlighted', '&[data-highlighted]')
      addVariant('open', '&[data-state="open"]')
      addVariant('closed', '&[data-state="closed"]')
      addVariant('checked', '&[data-state="checked"]')
      addVariant('unchecked', '&[data-state="unchecked"]')
    }
  ],
};
```

Then use them in your components:

```jsx
<Dropdown.Trigger className="highlighted:bg-indigo-50 open:text-indigo-600" />
```

## Best Practices

1. **Group common styles**: Create reusable components for common patterns

```jsx
const DialogButton = ({ children, ...props }) => (
  <button 
    className="px-4 py-2 text-white bg-indigo-600 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" 
    {...props}
  >
    {children}
  </button>
);

// Usage
<Dialog.Trigger asChild>
  <DialogButton>Open Dialog</DialogButton>
</Dialog.Trigger>
```

2. **Use CSS variables for theme values**: Leverage CSS variables for consistent theming

```jsx
// styles.css
:root {
  --primary: 250 80% 50%;
  --primary-foreground: 0 0% 100%;
}

// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'hsl(var(--primary))',
        'primary-foreground': 'hsl(var(--primary-foreground))',
      },
    },
  },
}

// Usage
<Button className="bg-primary text-primary-foreground" />
```

3. **Combine with `clsx` or `tailwind-merge`**: For conditional classes and merging tailwind classes

```jsx
import clsx from 'clsx';

<Dialog.Trigger 
  className={clsx(
    "px-4 py-2 rounded",
    isDestructive ? "bg-red-600 text-white" : "bg-indigo-600 text-white"
  )}
>
  {isDestructive ? 'Delete' : 'Open'}
</Dialog.Trigger>
```