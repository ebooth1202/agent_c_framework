# Resizable

**Created:** 2025-04-24 | **Source:** resizable.mdx

## Overview
Accessible resizable panel groups and layouts with keyboard support. Built on top of [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) by bvaughn.

## Key Features
- Resizable panels with drag handles
- Support for both horizontal and vertical resizing
- Keyboard accessibility for resizing operations
- Customizable handle appearance
- Persistent layout sizes with local storage
- Responsive design support

## Installation

**CLI Method:**
```bash
npx shadcn@latest add resizable
```

**Manual Installation:**
1. Install dependencies:
```bash
npm install react-resizable-panels
```
2. Copy component source code
3. Update import paths as needed

## Component Structure
The Resizable component consists of three main parts:

- `ResizablePanelGroup`: Container for managing a group of panels
- `ResizablePanel`: Individual panel that can be resized
- `ResizableHandle`: Draggable handle between panels for resizing

## Basic Usage

```tsx
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

<ResizablePanelGroup direction="horizontal">
  <ResizablePanel>One</ResizablePanel>
  <ResizableHandle />
  <ResizablePanel>Two</ResizablePanel>
</ResizablePanelGroup>
```

## Examples

### Vertical Resizing

```tsx
<ResizablePanelGroup direction="vertical">
  <ResizablePanel>One</ResizablePanel>
  <ResizableHandle />
  <ResizablePanel>Two</ResizablePanel>
</ResizablePanelGroup>
```

### Custom Handle

```tsx
<ResizablePanelGroup direction="horizontal">
  <ResizablePanel>One</ResizablePanel>
  <ResizableHandle withHandle />
  <ResizablePanel>Two</ResizablePanel>
</ResizablePanelGroup>
```

## Common Props

### ResizablePanelGroup Props
- `direction`: "horizontal" or "vertical" orientation for resizing
- `onLayout`: Callback when layout changes

### ResizablePanel Props
- `defaultSize`: Initial size of the panel (in percentage)
- `minSize`: Minimum size constraint (in percentage)
- `maxSize`: Maximum size constraint (in percentage)
- `id`: Unique identifier for the panel (useful for persistent layouts)

### ResizableHandle Props
- `withHandle`: Shows a visible grab handle when true

## Common Use Cases
- Code editors with resizable panels
- Dashboard layouts with adjustable sections
- File explorers with resizable navigation panels
- Split view interfaces
- Customizable workspace layouts
- Adjustable form and preview panes

## Accessibility
- Supports keyboard navigation for resizing (Arrow keys)
- Proper ARIA attributes for screen readers
- Focus management between panels