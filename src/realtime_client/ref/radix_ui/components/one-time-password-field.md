# One-Time Password Field Component

**Purpose:** Provides a group of single-character text inputs for one-time password verification codes, optimized for authentication flows.

## Basic Usage

```jsx
import { unstable_OneTimePasswordField as OneTimePasswordField } from "radix-ui";

export default () => (
  <OneTimePasswordField.Root>
    {/* Render one Input for each character in the OTP code */}
    <OneTimePasswordField.Input />
    <OneTimePasswordField.Input />
    <OneTimePasswordField.Input />
    <OneTimePasswordField.Input />
    <OneTimePasswordField.Input />
    <OneTimePasswordField.Input />
    {/* Hidden input to store the complete value */}
    <OneTimePasswordField.HiddenInput />
  </OneTimePasswordField.Root>
);
```

## Key Features
- Keyboard navigation mimicking a single input field
- Auto-filling entire code on paste
- Password manager autofill support
- Input validation (numeric, alpha, alphanumeric)
- Auto-submit on completion
- Hidden input for form submission

## Component API

### OneTimePasswordField.Root

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `autoComplete` | "off" \| "one-time-code" | "one-time-code" | Input autocomplete behavior |
| `autoFocus` | boolean | - | Focus first input on load |
| `value` | string | - | Controlled value |
| `defaultValue` | string | - | Initial uncontrolled value |
| `onValueChange` | (value: string) => void | - | Value change handler |
| `autoSubmit` | boolean | false | Auto-submit form when filled |
| `onAutoSubmit` | (value: string) => void | - | Called when auto-submit triggered |
| `disabled` | boolean | false | Disable all inputs |
| `dir` | "ltr" \| "rtl" | "ltr" | Reading direction |
| `orientation` | "horizontal" \| "vertical" | "vertical" | Input orientation |
| `form` | string | - | Associated form ID |
| `name` | string | - | Input name for form submission |
| `placeholder` | string | - | Placeholder text for inputs |
| `readOnly` | boolean | false | Make inputs read-only |
| `sanitizeValue` | (value: string) => string | - | Custom value sanitization |
| `type` | "text" \| "password" | "text" | Input type |
| `validationType` | "none" \| "numeric" \| "alpha" \| "alphanumeric" | "numeric" | Input validation type |

**Data Attributes:** `[data-orientation]`: "vertical" or "horizontal"

### OneTimePasswordField.Input

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

**Data Attributes:** `[data-index]`: Character index in the field value

### OneTimePasswordField.HiddenInput

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

## Common Patterns

### Segmented Display
```jsx
<OneTimePasswordField.Root>
  <OneTimePasswordField.Input />
  <Separator.Root aria-hidden /> {/* Visual separator */}
  <OneTimePasswordField.Input />
  <Separator.Root aria-hidden />
  <OneTimePasswordField.Input />
  <Separator.Root aria-hidden />
  <OneTimePasswordField.Input />
  <OneTimePasswordField.HiddenInput />
</OneTimePasswordField.Root>
```

### Auto-Submit Form
```jsx
<form onSubmit={handleSubmit}>
  <OneTimePasswordField.Root name="otp" autoSubmit>
    {/* Generate inputs based on expected code length */}
    {Array.from({ length: 6 }).map((_, i) => (
      <OneTimePasswordField.Input key={i} />
    ))}
    <OneTimePasswordField.HiddenInput />
  </OneTimePasswordField.Root>
  <button type="submit">Verify</button>
</form>
```

### Controlled Value
```jsx
function Verify() {
  const [value, setValue] = React.useState("");
  
  return (
    <OneTimePasswordField.Root
      value={value}
      onValueChange={setValue}
      onAutoSubmit={handleVerification}
      autoSubmit
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <OneTimePasswordField.Input key={i} />
      ))}
    </OneTimePasswordField.Root>
  );
}
```

## Accessibility Notes

- Uses `role="group"` to indicate related input elements
- Behaves similar to a single input field with multiple cells
- Paste actions replace the entire value regardless of focus position
- Full keyboard navigation:
  - Tab/Shift+Tab: Navigate in/out of the field
  - Arrow keys: Move between individual inputs
  - Typing: Automatically advances focus to next input
  - Backspace: Clears current input and moves to previous
  - Delete: Clears current input and shifts later values back
  - Command+Backspace: Clears all inputs