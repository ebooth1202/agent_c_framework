# Tabs Component

**Purpose**: A set of layered sections of content (tab panels) that are displayed one at a time.

## Key Features

- Can be controlled or uncontrolled
- Supports horizontal or vertical orientation
- Supports automatic or manual activation modes
- Full keyboard navigation
- Accessible tab panel implementation

## Installation

```bash
npm install @radix-ui/react-tabs
```

## Component Anatomy

```jsx
import { Tabs } from "radix-ui";

export default () => (
	<Tabs.Root>
		<Tabs.List>
			<Tabs.Trigger />
		</Tabs.List>
		<Tabs.Content />
	</Tabs.Root>
);
```

## API Reference

### Root

Contains all the tabs component parts.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `defaultValue` (string) - Initial active tab value when uncontrolled
- `value` (string) - Controlled active tab value, use with `onValueChange`
- `onValueChange` (function) - Handler called when the active tab changes
- `orientation` ("horizontal" | "vertical", default: "horizontal") - Component orientation
- `dir` ("ltr" | "rtl") - Reading direction
- `activationMode` ("automatic" | "manual", default: "automatic") - Controls when tabs are activated (focus or click)

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### List

Contains the tab triggers aligned along the edge of the active content.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `loop` (boolean, default: true) - Whether keyboard navigation loops from last to first tab

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

### Trigger

The button that activates its associated content panel.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `value` (string, required) - Unique value linking trigger to content
- `disabled` (boolean, default: false) - Prevents user interaction

**Data Attributes:**
- `[data-state]`: "active" | "inactive"
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

### Content

Contains the content associated with a specific trigger.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `value` (string, required) - Unique value linking content to a trigger
- `forceMount` (boolean) - Forces mounting for animation control

**Data Attributes:**
- `[data-state]`: "active" | "inactive"
- `[data-orientation]`: "vertical" | "horizontal"

## Implementation Examples

### Vertical Tabs

```jsx
<Tabs.Root defaultValue="tab1" orientation="vertical">
  <Tabs.List aria-label="tabs example">
    <Tabs.Trigger value="tab1">One</Tabs.Trigger>
    <Tabs.Trigger value="tab2">Two</Tabs.Trigger>
    <Tabs.Trigger value="tab3">Three</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="tab1">Tab one content</Tabs.Content>
  <Tabs.Content value="tab2">Tab two content</Tabs.Content>
  <Tabs.Content value="tab3">Tab three content</Tabs.Content>
</Tabs.Root>
```

## Accessibility

Adheres to the [Tabs WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs).

### Keyboard Interactions

- **Tab**: When focus moves to tabs, focuses the active trigger; when a trigger is focused, moves focus to active content
- **Arrow Down/Right**: Moves focus to next trigger and activates its content
- **Arrow Up/Left**: Moves focus to previous trigger and activates its content
- **Home**: Moves focus to first trigger and activates its content
- **End**: Moves focus to last trigger and activates its content