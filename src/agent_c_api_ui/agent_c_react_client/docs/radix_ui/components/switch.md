# Switch Component

**Purpose**: A control that allows the user to toggle between checked and not checked states.

## Key Features

- Can be controlled or uncontrolled
- Integrates with forms
- Full keyboard navigation
- Simple two-part composition

## Installation

```bash
npm install @radix-ui/react-switch
```

## Component Anatomy

```jsx
import { Switch } from "radix-ui";

export default () => (
	<Switch.Root>
		<Switch.Thumb />
	</Switch.Root>
);
```

## API Reference

### Root

Contains all the parts of a switch. Renders an `input` element when used within a form.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `defaultChecked` (boolean) - Initial state when uncontrolled
- `checked` (boolean) - Controlled state, use with `onCheckedChange`
- `onCheckedChange` (function) - Handler called when state changes
- `disabled` (boolean) - Prevents user interaction when true
- `required` (boolean) - Indicates the switch must be checked for form submission
- `name` (string) - Form input name
- `value` (string, default: "on") - Value submitted with form

**Data Attributes:**
- `[data-state]`: "checked" | "unchecked"
- `[data-disabled]`: Present when disabled

### Thumb

The visual indicator showing whether the switch is on or off.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-state]`: "checked" | "unchecked"
- `[data-disabled]`: Present when disabled

## Accessibility

Adheres to the [`switch` role requirements](https://www.w3.org/WAI/ARIA/apg/patterns/switch).

### Keyboard Interactions

- **Space**: Toggles the switch state
- **Enter**: Toggles the switch state

## Usage in Forms

The Switch component can be used in forms like a checkbox input. When the form is submitted, if the switch is checked, the form data will include the name/value pair specified by the `name` and `value` props.