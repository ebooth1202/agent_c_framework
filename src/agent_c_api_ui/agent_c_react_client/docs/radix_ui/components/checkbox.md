# Checkbox Component

**Created:** 2025-04-24
**Source:** Radix UI Primitives

## Overview

Checkbox is a control that allows users to toggle between checked, unchecked, and indeterminate states.

## Key Features

- Supports standard checked/unchecked states plus indeterminate state
- Full keyboard navigation support
- Can be controlled or uncontrolled
- Form integration with native form elements

## Installation

```bash
npm install @radix-ui/react-checkbox
```

## Component Anatomy

```jsx
import { Checkbox } from "radix-ui";

export default () => (
  <Checkbox.Root>
    <Checkbox.Indicator />
  </Checkbox.Root>
);
```

## API Reference

### Root

Contains all parts of a checkbox. Renders a native `input` when used within a `form`.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `defaultChecked` | boolean \| 'indeterminate' | - | Initial checked state (uncontrolled) |
| `checked` | boolean \| 'indeterminate' | - | Controlled checked state |
| `onCheckedChange` | (checked: boolean \| 'indeterminate') => void | - | Handler for checked state changes |
| `disabled` | boolean | - | Prevents user interaction |
| `required` | boolean | - | Makes the checkbox required in a form |
| `name` | string | - | Name for form submission |
| `value` | string | "on" | Value for form submission |

**Data Attributes:**
- `[data-state="checked"|"unchecked"|"indeterminate"]`
- `[data-disabled]` - Present when disabled

### Indicator

Renders when checkbox is checked or indeterminate.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `forceMount` | boolean | - | Force mounting for animation control |

**Data Attributes:**
- `[data-state="checked"|"unchecked"|"indeterminate"]`
- `[data-disabled]` - Present when disabled

## Usage Examples

### Basic Checkbox

```jsx
import { Checkbox } from "radix-ui";
import { CheckIcon } from "@radix-ui/react-icons";

export default () => (
  <form>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <Checkbox.Root className="CheckboxRoot" id="c1">
        <Checkbox.Indicator className="CheckboxIndicator">
          <CheckIcon />
        </Checkbox.Indicator>
      </Checkbox.Root>
      <label htmlFor="c1" style={{ paddingLeft: 15 }}>
        Accept terms and conditions
      </label>
    </div>
  </form>
);
```

### Indeterminate State

```jsx
import { DividerHorizontalIcon, CheckIcon } from "@radix-ui/react-icons";
import { Checkbox } from "radix-ui";
import { useState } from "react";

export default () => {
  const [checked, setChecked] = useState("indeterminate");

  return (
    <>
      <Checkbox.Root
        className="CheckboxRoot"
        checked={checked}
        onCheckedChange={setChecked}
      >
        <Checkbox.Indicator className="CheckboxIndicator">
          {checked === "indeterminate" && <DividerHorizontalIcon />}
          {checked === true && <CheckIcon />}
        </Checkbox.Indicator>
      </Checkbox.Root>

      <button
        type="button"
        onClick={() =>
          setChecked((prev) =>
            prev === "indeterminate" ? false : "indeterminate"
          )
        }
      >
        Toggle indeterminate
      </button>
    </>
  );
};
```

## Accessibility

Implements the [tri-state Checkbox WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/checkbox).

### Keyboard Interactions

| Key | Action |
| --- | ------ |
| `Space` | Toggles the checkbox state |