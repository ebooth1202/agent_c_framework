# Select Component

**Source:** Original from `shadcn-ui/components/select.mdx`  
**Created:** April 24, 2025  

## Overview
Displays a list of options for the user to pick from—triggered by a button. The select component is a core form element for allowing users to choose from predefined options.

## Installation

### CLI Installation
```bash
npx shadcn@latest add select
```

### Manual Installation
1. Install dependencies:
```bash
npm install @radix-ui/react-select
```
2. Copy and paste the code from the component source
3. Update import paths to match your project setup

## Usage

```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
```

```tsx
<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Theme" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="light">Light</SelectItem>
    <SelectItem value="dark">Dark</SelectItem>
    <SelectItem value="system">System</SelectItem>
  </SelectContent>
</Select>
```

## Examples

### Scrollable
A select component with a scrollable list of options for handling large option sets.

### Form Integration
An example showing how to integrate the Select component with form handling.

## References
- Documentation: https://www.radix-ui.com/docs/primitives/components/select
- API Reference: https://www.radix-ui.com/docs/primitives/components/select#api-reference