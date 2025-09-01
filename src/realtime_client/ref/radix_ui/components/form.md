# Form Component

A component for collecting information from users with built-in validation functionality. It's built on top of the native browser constraint validation API.

## Usage

```jsx
import { Form } from "radix-ui";

export default () => (
  <Form.Root>
    <Form.Field name="email">
      <Form.Label>Email</Form.Label>
      <Form.Control type="email" required />
      <Form.Message match="valueMissing">Please enter your email</Form.Message>
      <Form.Message match="typeMismatch">Please provide a valid email</Form.Message>
    </Form.Field>
    <Form.Submit>Submit</Form.Submit>
  </Form.Root>
);
```

## Key Features

- Built-in validation using native browser constraint validation API
- Custom validation support
- Full message customization
- Accessible validation messages
- Client-side and server-side validation support
- Fully managed focus handling

## API Reference

### Form.Root

Contains all parts of a form.

**Props:**
- `asChild` (boolean): Changes default element to child element
- `onClearServerErrors` (function): Event handler for clearing server errors on form submission/reset

### Form.Field

Wrapper for form fields that handles id/name and label accessibility.

**Props:**
- `asChild` (boolean): Changes default element to child element
- `name` (string, required): Field name passed to control and used for validation message matching
- `serverInvalid` (boolean): Marks field as invalid on server

**Data Attributes:**
- `[data-invalid]`: Present when field is invalid
- `[data-valid]`: Present when field is valid

### Form.Label

Label element automatically connected to control when nested in a Field.

**Props:**
- `asChild` (boolean): Changes default element to child element

**Data Attributes:**
- `[data-invalid]`: Present when field is invalid
- `[data-valid]`: Present when field is valid

### Form.Control

Input control element automatically wired when nested in a Field.

**Props:**
- `asChild` (boolean): Changes default element to child element

**Data Attributes:**
- `[data-invalid]`: Present when field is invalid
- `[data-valid]`: Present when field is valid

### Form.Message

Validation message with accessibility features.

**Props:**
- `asChild` (boolean): Changes default element to child element
- `match`: Condition for message visibility - can be standard validation type or custom function:
  - Standard types: 'badInput', 'patternMismatch', 'rangeOverflow', 'rangeUnderflow', 'stepMismatch', 'tooLong', 'tooShort', 'typeMismatch', 'valid', 'valueMissing'
  - Custom function: `(value: string, formData: FormData) => boolean`
  - Async function: `(value: string, formData: FormData) => Promise<boolean>`
- `forceMatch` (boolean): Forces message visibility for server-side validation
- `name` (string): Target field name when rendering outside Form.Field

### Form.ValidityState

Access a field's ValidityState for custom rendering.

**Props:**
- `children` (function): Render function receiving validity state
- `name` (string): Target field name when rendering outside Form.Field

### Form.Submit

Form submit button.

**Props:**
- `asChild` (boolean): Changes default element to child element

## Key Patterns

### Component Composition

```jsx
<Form.Field name="country">
  <Form.Label>Country</Form.Label>
  <Form.Control asChild>
    <select>
      <option value="uk">United Kingdom</option>
      {/* ... */}
    </select>
  </Form.Control>
</Form.Field>
```

### Custom Validation

```jsx
<Form.Field name="name">
  <Form.Label>Full name</Form.Label>
  <Form.Control />
  <Form.Message match={(value) => value !== "John"}>
    Only John is allowed.
  </Form.Message>
</Form.Field>
```

### Styling Based on Validity

```css
.FormLabel[data-invalid] {
  color: red;
}
.FormLabel[data-valid] {
  color: green;
}
```

### Server-Side Validation

```jsx
<Form.Root
  onSubmit={(event) => {
    // Form handling logic
    event.preventDefault();
  }}
  onClearServerErrors={() => setServerErrors({ email: false, password: false })}
>
  <Form.Field name="email" serverInvalid={serverErrors.email}>
    <Form.Label>Email address</Form.Label>
    <Form.Control type="email" required />
    <Form.Message match="typeMismatch" forceMatch={serverErrors.email}>
      Please provide a valid email.
    </Form.Message>
  </Form.Field>
  {/* ... */}
</Form.Root>
```

## Accessibility

- Label/control association via Form.Field's name
- Automatic association of error messages with controls
- Focus moves to first invalid control on validation failure