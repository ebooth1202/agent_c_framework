# Drawer Component

*Created: 2025-04-24 | Source: drawer.mdx*

## Overview

Drawer is a slide-in panel component built on top of [Vaul](https://github.com/emilkowalski/vaul) by Emil Kowalski. It provides a way to display additional content that slides into view from the edge of the screen.

## Key Features

- Slide-in panel interface from screen edges
- Customizable header and footer sections
- Supports nested content structure
- Can be combined with Dialog for responsive interfaces

## Installation

**CLI Method:**
```bash
npx shadcn@latest add drawer
```

**Manual Installation:**
1. Install required dependencies:
   ```bash
   npm install vaul
   ```
2. Copy component source code to your project
3. Update import paths to match your project structure

## Component Structure

- `Drawer`: Main container component
- `DrawerTrigger`: Element that triggers the drawer to open
- `DrawerContent`: The content displayed within the drawer
- `DrawerHeader`: Container for drawer title and description
- `DrawerTitle`: Drawer title component
- `DrawerDescription`: Drawer description component
- `DrawerFooter`: Container for drawer action buttons
- `DrawerClose`: Button to close the drawer

## Usage Example

```tsx
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"

<Drawer>
  <DrawerTrigger>Open</DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Are you absolutely sure?</DrawerTitle>
      <DrawerDescription>This action cannot be undone.</DrawerDescription>
    </DrawerHeader>
    <DrawerFooter>
      <Button>Submit</Button>
      <DrawerClose>
        <Button variant="outline">Cancel</Button>
      </DrawerClose>
    </DrawerFooter>
  </DrawerContent>
</Drawer>
```

## Common Use Cases

### Responsive Dialog-Drawer Pattern

You can combine the `Dialog` and `Drawer` components to create a responsive pattern that renders a `Dialog` component on desktop and a `Drawer` on mobile.

```tsx
// Example of a responsive Dialog-Drawer pattern
<Dialog>
  {/* Dialog implementation */}
</Dialog>

<Drawer>
  {/* Drawer implementation with same content */}
</Drawer>
```

### Common Applications

- Mobile navigation menus
- Filter panels in e-commerce
- Submission forms
- Settings panels
- Detailed information slides