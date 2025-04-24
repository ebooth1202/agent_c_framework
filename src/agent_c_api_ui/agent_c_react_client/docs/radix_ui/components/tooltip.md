# Tooltip Component

**Purpose**: A popup that displays information related to an element when it receives keyboard focus or mouse hover.

## Key Features

- Provider component for global delay configuration
- Opens on focus or hover
- Closes on trigger activation or Escape key
- Supports custom display timing
- Offers positioning and collision handling
- Exposes CSS variables for animations and sizing

## Installation

```bash
npm install @radix-ui/react-tooltip
```

## Component Anatomy

```jsx
import { Tooltip } from "radix-ui";

export default () => (
	<Tooltip.Provider>
		<Tooltip.Root>
			<Tooltip.Trigger />
			<Tooltip.Portal>
				<Tooltip.Content>
					<Tooltip.Arrow />
				</Tooltip.Content>
			</Tooltip.Portal>
		</Tooltip.Root>
	</Tooltip.Provider>
);
```

## API Reference

### Provider

Wraps your app to provide global functionality to tooltips.

**Props:**
- `delayDuration` (number, default: 700) - Milliseconds before tooltip opens on hover
- `skipDelayDuration` (number, default: 300) - Milliseconds for moving between triggers without incurring delay
- `disableHoverableContent` (boolean) - Prevents content from staying open on hover

### Root

Contains all the parts of a tooltip.

**Props:**
- `defaultOpen` (boolean) - Initial open state when uncontrolled
- `open` (boolean) - Controlled open state, use with `onOpenChange`
- `onOpenChange` (function) - Handler when open state changes
- `delayDuration` (number, default: 700) - Override provider delay for this tooltip
- `disableHoverableContent` (boolean, default: false) - Prevents content from staying open on hover

### Trigger

The element that triggers the tooltip. The Content positions against this element.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-state]`: "closed" | "delayed-open" | "instant-open"

### Portal

Portals the content into the body.

**Props:**
- `forceMount` (boolean) - Forces mounting for animation control
- `container` (HTMLElement, default: document.body) - Container for the portal

### Content

The tooltip popup component.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `aria-label` (string) - Accessible label when content isn't descriptive enough
- `onEscapeKeyDown` (function) - Handler for Escape key press
- `onPointerDownOutside` (function) - Handler for pointer events outside
- `forceMount` (boolean) - Forces mounting for animation control
- `side` ("top" | "right" | "bottom" | "left", default: "top") - Preferred side for positioning
- `sideOffset` (number, default: 0) - Distance from trigger in pixels
- `align` ("start" | "center" | "end", default: "center") - Alignment against trigger
- `alignOffset` (number, default: 0) - Offset from alignment
- `avoidCollisions` (boolean, default: true) - Adjust position to prevent boundary collisions
- `collisionBoundary` (Element | null | Array<Element | null>, default: []) - Elements to use as collision boundary
- `collisionPadding` (number | Partial<Record<Side, number>>, default: 0) - Space from boundaries where collision detection occurs
- `arrowPadding` (number, default: 0) - Padding between arrow and content edges
- `sticky` ("partial" | "always", default: "partial") - Behavior for keeping content in boundary
- `hideWhenDetached` (boolean, default: false) - Hide when trigger is fully occluded

**Data Attributes:**
- `[data-state]`: "closed" | "delayed-open" | "instant-open"
- `[data-side]`: "left" | "right" | "bottom" | "top"
- `[data-align]`: "start" | "end" | "center"

**CSS Variables:**
- `--radix-tooltip-content-transform-origin` - Transform origin for animations
- `--radix-tooltip-content-available-width` - Available width between trigger and boundary
- `--radix-tooltip-content-available-height` - Available height between trigger and boundary
- `--radix-tooltip-trigger-width` - Width of the trigger element
- `--radix-tooltip-trigger-height` - Height of the trigger element

### Arrow

An optional arrow element to visually connect the tooltip to the trigger.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `width` (number, default: 10) - Arrow width in pixels
- `height` (number, default: 5) - Arrow height in pixels

## Implementation Examples

### Global Configuration

```jsx
<Tooltip.Provider delayDuration={800} skipDelayDuration={500}>
  <Tooltip.Root>
    <Tooltip.Trigger>...</Tooltip.Trigger>
    <Tooltip.Content>...</Tooltip.Content>
  </Tooltip.Root>
</Tooltip.Provider>
```

### Instant Display

```jsx
<Tooltip.Root delayDuration={0}>
  <Tooltip.Trigger>...</Tooltip.Trigger>
  <Tooltip.Content>...</Tooltip.Content>
</Tooltip.Root>
```

### Size Constraints

```css
.TooltipContent {
  width: var(--radix-tooltip-trigger-width);
  max-height: var(--radix-tooltip-content-available-height);
}
```

### Origin-Aware Animations

```css
.TooltipContent {
  transform-origin: var(--radix-tooltip-content-transform-origin);
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

## Accessibility

Implements standard tooltip accessibility practices.

### Keyboard Interactions

- **Tab**: Opens/closes the tooltip without delay
- **Space**: If open, closes the tooltip without delay
- **Enter**: If open, closes the tooltip without delay
- **Escape**: If open, closes the tooltip without delay