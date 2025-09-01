# Label Component

**Purpose:** Renders an accessible label associated with form controls, providing proper accessibility semantics.

## Basic Usage

```jsx
import { Label } from "radix-ui";

// Associated by wrapping the control
export default () => (
  <Label.Root>
    Email
    <input type="email" />
  </Label.Root>
);

// Associated by htmlFor
export default () => (
  <>
    <Label.Root htmlFor="email">Email</Label.Root>
    <input type="email" id="email" />
  </>
);
```

## Key Features
- Text selection prevention when double-clicking label
- Support for nested controls
- Based on the native HTML `<label>` element

## Component API

### Label.Root

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `htmlFor` | string | - | ID of the associated control element |

## Accessibility Notes

- This component uses the native HTML `<label>` element for built-in accessibility
- Labels can be associated with controls either by:
  1. Wrapping the control within the Label component
  2. Using the `htmlFor` prop that references the control's ID
- When using custom controls, ensure they use native elements such as `button` or `input` as a base for proper association
- Screen readers announce the label text when the associated control gets focus
- Clicking the label will activate the associated control (useful for checkboxes, radio buttons)