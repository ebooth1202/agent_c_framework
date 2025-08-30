# Select Component

**Purpose**: Displays a list of options for the user to pick from—triggered by a button.

## Key Features

- Can be controlled or uncontrolled
- Offers two positioning modes: item-aligned and popper
- Supports items, labels, and groups of items
- Focus is fully managed with keyboard navigation
- Supports custom placeholder
- Provides typeahead support
- Supports Right to Left direction

## Installation

```bash
npm install @radix-ui/react-select
```

## Component Anatomy

```jsx
import { Select } from "radix-ui";

export default () => (
	<Select.Root>
		<Select.Trigger>
			<Select.Value />
			<Select.Icon />
		</Select.Trigger>

		<Select.Portal>
			<Select.Content>
				<Select.ScrollUpButton />
				<Select.Viewport>
					<Select.Item>
						<Select.ItemText />
						<Select.ItemIndicator />
					</Select.Item>

					<Select.Group>
						<Select.Label />
						<Select.Item>
							<Select.ItemText />
							<Select.ItemIndicator />
						</Select.Item>
					</Select.Group>

					<Select.Separator />
				</Select.Viewport>
				<Select.ScrollDownButton />
				<Select.Arrow />
			</Select.Content>
		</Select.Portal>
	</Select.Root>
);
```

## API Reference

### Root

Contains all parts of a select.

**Props:**
- `defaultValue` (string) - Initial uncontrolled value
- `value` (string) - Controlled value, use with `onValueChange`
- `onValueChange` (function) - Handler when value changes
- `defaultOpen` (boolean) - Initial open state when uncontrolled
- `open` (boolean) - Controlled open state, use with `onOpenChange`
- `onOpenChange` (function) - Handler when open state changes
- `dir` ("ltr" | "rtl") - Reading direction
- `name` (string) - Form input name
- `disabled` (boolean) - Prevents user interaction
- `required` (boolean) - Marks the select as required in a form

### Trigger

The button that toggles the select.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-disabled]`: Present when disabled
- `[data-placeholder]`: Present when has placeholder

### Value

Reflects the selected value.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `placeholder` (ReactNode) - Content shown when no value is selected

### Icon

Icon displayed next to the value.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Portal

Portals the content into the body.

**Props:**
- `container` (HTMLElement, default: document.body) - Portal container

### Content

The dropdown component containing the select options.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `onCloseAutoFocus` (function) - Handler when focus returns to trigger
- `onEscapeKeyDown` (function) - Handler for escape key press
- `onPointerDownOutside` (function) - Handler for pointer events outside
- `position` ("item-aligned" | "popper", default: "item-aligned") - Positioning mode
- `side` ("top" | "right" | "bottom" | "left", default: "bottom") - Preferred side when using popper
- `sideOffset` (number, default: 0) - Distance from anchor in popper mode
- `align` ("start" | "center" | "end", default: "start") - Alignment against anchor in popper mode
- `alignOffset` (number, default: 0) - Offset from alignment in popper mode
- `avoidCollisions` (boolean, default: true) - Adjust position to prevent collisions
- `collisionBoundary` (Element | null | Array<Element | null>, default: []) - Boundary for collision detection
- `collisionPadding` (number | Partial<Record<Side, number>>, default: 10) - Padding for collision detection
- `arrowPadding` (number, default: 0) - Arrow padding
- `sticky` ("partial" | "always", default: "partial") - Sticky behavior on align axis
- `hideWhenDetached` (boolean, default: false) - Hide when trigger is fully occluded

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-side]`: "left" | "right" | "bottom" | "top"
- `[data-align]`: "start" | "end" | "center"

**CSS Variables:**
- `--radix-select-content-transform-origin` - Transform origin based on position
- `--radix-select-content-available-width` - Available width between trigger and boundary
- `--radix-select-content-available-height` - Available height between trigger and boundary
- `--radix-select-trigger-width` - Width of the trigger
- `--radix-select-trigger-height` - Height of the trigger

### Viewport

Scrolling viewport containing the items.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Item

Selectable item in the dropdown.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `value` (string, required) - Item value
- `disabled` (boolean) - Prevents user interaction
- `textValue` (string) - Optional text for typeahead functionality

**Data Attributes:**
- `[data-state]`: "checked" | "unchecked"
- `[data-highlighted]`: Present when highlighted
- `[data-disabled]`: Present when disabled

### ItemText

Textual part of the item that displays in the trigger when selected.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### ItemIndicator

Indicator displayed when item is selected.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### ScrollUpButton

Button for scrolling up when viewport content overflows.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### ScrollDownButton

Button for scrolling down when viewport content overflows.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Group

Groups related items together.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Label

Label for a group of items.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Separator

Visual separator between items.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Arrow

Optional arrow element to visually link trigger and content (only in popper positioning).

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `width` (number, default: 10) - Arrow width in pixels
- `height` (number, default: 5) - Arrow height in pixels

## Implementation Examples

### Key Patterns

1. **Positioning modes**: Use `position="popper"` for dropdown-style positioning
2. **Width constraints**: Use `--radix-select-trigger-width` CSS variable to match content width to trigger
3. **Disabled items**: Style using `[data-disabled]` attribute
4. **Placeholders**: Use the `placeholder` prop on `Value`
5. **Item grouping**: Use `Group` and `Label` parts together
6. **Custom scrolling**: Integrate with `ScrollArea` component for custom scrollbars

## Accessibility

Implements the [ListBox WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/listbox).

### Keyboard Interactions

- **Space**: Opens select and focuses selected item; selects focused item
- **Enter**: Opens select and focuses first item; selects focused item
- **Arrow Down**: Opens select; moves focus to next item
- **Arrow Up**: Opens select; moves focus to previous item
- **Esc**: Closes select and moves focus to trigger

### Labelling

Use the `Label` component to provide an accessible label for the select:

```jsx
<Label htmlFor="country">Country</Label>
<Select.Root>
  <Select.Trigger id="country">...</Select.Trigger>
  ...
</Select.Root>
```