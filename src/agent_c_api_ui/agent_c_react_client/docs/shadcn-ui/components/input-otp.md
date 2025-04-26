# Input OTP Component

*Created: 2025-04-24 | Source: input-otp.mdx*

## Overview

Input OTP is an accessible one-time password component built on top of [input-otp](https://github.com/guilhermerodz/input-otp) by Guilherme Rodz. It provides a specialized input for entering verification codes with copy-paste functionality.

## Key Features

- Accessible one-time password input
- Copy-paste functionality across slots
- Customizable patterns (numeric, alphanumeric)
- Grouping and separator support
- Controlled and uncontrolled usage
- Form integration capabilities

## Installation

**CLI Method:**
```bash
npx shadcn@latest add input-otp
```

**Manual Installation:**
1. Install dependencies:
   ```bash
   npm install input-otp
   ```
2. Copy component source code to your project
3. Update import paths
4. Add required animations to tailwind.config.js:
   ```js
   module.exports = {
     theme: {
       extend: {
         keyframes: {
           "caret-blink": {
             "0%,70%,100%": { opacity: "1" },
             "20%,50%": { opacity: "0" },
           },
         },
         animation: {
           "caret-blink": "caret-blink 1.25s ease-out infinite",
         },
       },
     },
   }
   ```

## Component Structure

- `InputOTP`: Main container component
- `InputOTPGroup`: Groups slots together
- `InputOTPSlot`: Individual input field for each character
- `InputOTPSeparator`: Visual separator between groups

## Usage Example

```tsx
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp"

<InputOTP maxLength={6}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
    <InputOTPSlot index={2} />
  </InputOTPGroup>
  <InputOTPSeparator />
  <InputOTPGroup>
    <InputOTPSlot index={3} />
    <InputOTPSlot index={4} />
    <InputOTPSlot index={5} />
  </InputOTPGroup>
</InputOTP>
```

## Common Use Cases

### Custom Pattern

Use the `pattern` prop to define a custom pattern for the OTP input:

```tsx
import { REGEXP_ONLY_DIGITS_AND_CHARS } from "input-otp"

<InputOTP maxLength={6} pattern={REGEXP_ONLY_DIGITS_AND_CHARS}>
  {/* ... */}
</InputOTP>
```

### Custom Separator

Add separators between input groups:

```tsx
<InputOTP maxLength={4}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
  </InputOTPGroup>
  <InputOTPSeparator />
  <InputOTPGroup>
    <InputOTPSlot index={2} />
    <InputOTPSlot index={3} />
  </InputOTPGroup>
</InputOTP>
```

### Controlled Input

Use the `value` and `onChange` props to control the input:

```tsx
const [value, setValue] = React.useState('')

<InputOTP value={value} onChange={setValue} maxLength={6}>
  {/* ... */}
</InputOTP>
```

### Form Integration

Integrate with form libraries:

```tsx
<Form {...form}>
  <FormField
    control={form.control}
    name="pin"
    render={({ field }) => (
      <FormItem>
        <FormLabel>Pin</FormLabel>
        <FormControl>
          <InputOTP maxLength={6} {...field}>
            {/* ... */}
          </InputOTP>
        </FormControl>
        <FormMessage />
      </FormItem>
    )}
  />
</Form>
```

## Accessibility

- Fully keyboard navigable
- Screen reader friendly
- Clear focus states
- Supports disabled state

## Recent Changes

- **2024-03-19**: Updated component to use composition pattern instead of render props
- **2024-03-19**: Added disabled state styling