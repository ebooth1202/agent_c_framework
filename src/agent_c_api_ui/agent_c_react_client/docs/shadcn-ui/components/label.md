# Label Component

*Created: 2025-04-24 | Source: label.mdx*

## Overview

The Label component renders an accessible label that can be associated with form controls. It's built on top of Radix UI's Label primitive and provides proper accessibility for form controls.

## Key Features

- Accessible association with form controls
- Proper focus handling and screen reader support
- Consistent styling with other form components
- Lightweight implementation

## Installation

**CLI Method:**
```bash
npx shadcn@latest add label
```

**Manual Installation:**
1. Install required dependencies:
   ```bash
   npm install @radix-ui/react-label
   ```
2. Copy component source code to your project
3. Update import paths to match your project structure

## Component Structure

The Label component is a simple wrapper around Radix UI's Label primitive with additional styling applied.

## Usage Example

```tsx
import { Label } from "@/components/ui/label"

<Label htmlFor="email">Your email address</Label>
```

## Common Use Cases

### With Form Controls

```tsx
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="email">Email</Label>
  <Input type="email" id="email" placeholder="Enter your email" />
</div>
```

### With Required Fields

```tsx
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="username" required>
    Username <span className="text-red-500">*</span>
  </Label>
  <Input type="text" id="username" required />
</div>
```

### Disabled State

```tsx
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="disabled-input" disabled>
    Disabled Input
  </Label>
  <Input type="text" id="disabled-input" disabled />
</div>
```

## Accessibility

- Properly associates labels with form controls using the `htmlFor` attribute
- Enables screen readers to announce the label when the associated control is focused
- Clicking on the label focuses the associated control
- Supports the `disabled` state