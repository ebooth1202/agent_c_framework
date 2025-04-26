# Radix UI Primitives Overview

*AI-optimized documentation processed on April 24, 2025*

## Introduction

Radix Primitives is a low-level UI component library with a focus on accessibility, customization and developer experience. You can use these components either as the base layer of your design system, or adopt them incrementally.

The library provides unstyled, accessible components that adhere to WAI-ARIA design patterns, giving you complete control over styling while handling complex accessibility concerns.

## Key Features

### Accessible

Components adhere to the WAI-ARIA design patterns where possible. Radix handles many difficult implementation details related to accessibility, including:

- Appropriate ARIA and role attributes
- Focus management
- Keyboard navigation
- Screen reader announcements

### Unstyled

Components ship without styles, giving you complete control over the look and feel. Components can be styled with any styling solution including plain CSS, CSS Modules, Tailwind, or CSS-in-JS libraries.

### Opened

Radix Primitives are designed to be customized. The open component architecture provides granular access to each component part, so you can wrap them and add your own event listeners, props, or refs.

### Uncontrolled

Where applicable, components are uncontrolled by default but can also be controlled. All behavior wiring is handled internally, allowing you to get up and running quickly without needing to create local states.

### Developer Experience

Components provide a fully-typed API with consistent patterns across primitives. The `asChild` prop allows for complete control over rendered elements.

## Getting Started

### Installation

Install Radix Primitives from your command line:

```bash
npm install radix-ui@latest
```

### Quick Example

Implementing a Popover component:

```jsx
import * as React from "react";
import { Popover } from "radix-ui";
import "./styles.css";

const PopoverDemo = () => (
  <Popover.Root>
    <Popover.Trigger className="PopoverTrigger">Show info</Popover.Trigger>
    <Popover.Portal>
      <Popover.Content className="PopoverContent">
        Some content
        <Popover.Arrow className="PopoverArrow" />
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
);

export default PopoverDemo;
```

```css
/* styles.css */
.PopoverTrigger {
  background-color: white;
  border-radius: 4px;
}

.PopoverContent {
  border-radius: 4px;
  padding: 20px;
  width: 260px;
  background-color: white;
}

.PopoverArrow {
  fill: white;
}
```

## Accessibility

Radix Primitives follow the WAI-ARIA authoring practices guidelines and are tested in a wide selection of modern browsers and commonly used assistive technologies.

### WAI-ARIA

WAI-ARIA specifies the semantics for common UI patterns. Radix implements these semantics automatically, providing the appropriate ARIA attributes and behaviors expected by assistive technologies.

### Accessible Labels

Where possible, Radix Primitives include abstractions to make labeling controls simple. The `Label` primitive works with many Radix controls to provide proper context for users.

### Keyboard Navigation

Complex components like `Tabs`, `Dialog`, and dropdown menus come with proper keyboard navigation according to WAI-ARIA practices. Focus management is handled automatically, ensuring a good experience for keyboard users.

## Incremental Adoption

Radix UI can be gradually adopted in your project:

```jsx
// Import everything from a single package
import { Dialog, DropdownMenu, Tooltip } from "radix-ui";

// Or import individual components
import * as Dialog from "@radix-ui/react-dialog";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as Tooltip from "@radix-ui/react-tooltip";
```

The main `radix-ui` package is tree-shakeable, so you only ship what you use.