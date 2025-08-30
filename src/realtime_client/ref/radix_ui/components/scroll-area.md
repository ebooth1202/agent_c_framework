# Scroll Area Component

**Purpose**: Augments native scroll functionality for custom, cross-browser styling.

## Key Features

- Scrollbar sits on top of scrollable content, taking up no space
- Uses native scrolling (no CSS transformations)
- Preserves native keyboard controls
- Supports Right to Left direction

## Installation

```bash
npm install @radix-ui/react-scroll-area
```

## Component Anatomy

```jsx
import { ScrollArea } from "radix-ui";

export default () => (
	<ScrollArea.Root>
		<ScrollArea.Viewport />
		<ScrollArea.Scrollbar orientation="horizontal">
			<ScrollArea.Thumb />
		</ScrollArea.Scrollbar>
		<ScrollArea.Scrollbar orientation="vertical">
			<ScrollArea.Thumb />
		</ScrollArea.Scrollbar>
		<ScrollArea.Corner />
	</ScrollArea.Root>
);
```

## API Reference

### Root

Contains all parts of a scroll area.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `type` (enum: "auto" | "always" | "scroll" | "hover", default: "hover") - Controls scrollbar visibility:
  - "auto": visible when content overflows
  - "always": always visible
  - "scroll": visible when user is scrolling
  - "hover": visible when scrolling or hovering
- `scrollHideDelay` (number, default: 600) - Milliseconds before hiding scrollbars
- `dir` (enum: "ltr" | "rtl") - Reading direction
- `nonce` (string) - Optional for CSP-enabled environments

### Viewport

The viewport area of the scroll area.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Scrollbar

The scrollbar component. Use two Scrollbars with different orientations for both vertical and horizontal scrolling.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `forceMount` (boolean) - Force mounting for animation control
- `orientation` (enum: "horizontal" | "vertical", default: "vertical") - Scrollbar orientation

**Data Attributes:**
- `[data-state]`: "visible" | "hidden"
- `[data-orientation]`: "vertical" | "horizontal"

### Thumb

The draggable thumb within the scrollbar.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-state]`: "visible" | "hidden"

### Corner

The corner where both scrollbars meet.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

## Accessibility

Maintains browser's native scroll behavior and keyboard scrolling functionality. While CSS customization is generally preferred for scrollbars, this component provides additional styling options while preserving accessibility features.

### Keyboard Support

Native keyboard scrolling is supported by default, with specific interactions varying by platform.