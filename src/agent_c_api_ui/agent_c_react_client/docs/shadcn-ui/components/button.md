# Button Component

**Created**: April 24, 2025  
**Source**: components/button.mdx  
**Component Type**: UI Element  
**Featured**: Yes

## Description

Displays a button or a component that looks like a button.

## Installation

### CLI Method
```bash
npx shadcn@latest add button
```

### Manual Method

1. Install dependencies:
```bash
npm install @radix-ui/react-slot
```

2. Copy and paste the button component code into your project
3. Update import paths to match your project setup

## Usage

### Basic Usage
```tsx
import { Button } from "@/components/ui/button"

<Button variant="outline">Button</Button>
```

### As a Link

Option 1: Use the `buttonVariants` helper:
```tsx
import { buttonVariants } from "@/components/ui/button"

<Link className={buttonVariants({ variant: "outline" })}>Click here</Link>
```

Option 2: Use the `asChild` parameter:
```tsx
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

## Variants

### Primary
Default button style.

### Secondary
Alternative styling for secondary actions.

### Destructive
Highlights destructive actions (red styling).

### Outline
Button with an outline and transparent background.

### Ghost
Button with no background or border.

### Link
Button that appears as a link.

## Examples

### Icon Button
A button that only contains an icon.

### With Icon
A button with both text and an icon.

### Loading State
A button with a loading indicator.

### As Child
A button wrapping a custom Link component.

## Technical Notes

### Recent Changes

**2024-10-16**: Added classes for icons

Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to automatically style icons inside buttons.

Update to add these classes to the `cva` call in your button.tsx file:

```diff
const buttonVariants = cva(
  "inline-flex ... gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0"
)
```