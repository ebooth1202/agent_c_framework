# Core shadcn/ui Components Standardization Guide

## Overview

This guide outlines the standard implementation and usage patterns for core shadcn/ui components in our application. These components serve as the foundation for our UI and should be used consistently throughout the codebase.

## General Principles

1. **Follow shadcn/ui Patterns**: All components should follow the official shadcn/ui implementation patterns.
2. **Use Tailwind Classes**: Use Tailwind utility classes for styling when possible.
3. **Leverage CSS Variables**: Use shadcn/ui theme variables instead of hard-coded values.
4. **Consistent Imports**: Import components directly from `@/components/ui/[component]`.
5. **Theme Integration**: Don't manually implement dark mode; use the theme variables.

## Component Standards

### Checkbox

**Standard Import**:
```jsx
import { Checkbox } from "@/components/ui/checkbox";
```

**Usage**:
```jsx
<Checkbox 
  checked={isChecked} 
  onCheckedChange={setIsChecked} 
  id="terms"
/>
<label 
  htmlFor="terms"
  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
>
  Accept terms and conditions
</label>
```

**Best Practices**:
- Always associate the checkbox with a label using the `id` and `htmlFor` attributes
- Use the `checked` and `onCheckedChange` props for controlled components
- Use `defaultChecked` for uncontrolled components

### Select

**Standard Import**:
```jsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
```

**Usage**:
```jsx
<Select onValueChange={setValue} defaultValue={defaultValue}>
  <SelectTrigger className="w-full">
    <SelectValue placeholder="Select an option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
    <SelectItem value="option3">Option 3</SelectItem>
  </SelectContent>
</Select>
```

**Best Practices**:
- Use `onValueChange` for handling selection changes
- Provide a clear placeholder in `SelectValue`
- Ensure the `value` prop is unique for each `SelectItem`
- Use `SelectGroup` and `SelectLabel` for organized groups of options

### Tabs

**Standard Import**:
```jsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
```

**Usage**:
```jsx
<Tabs defaultValue="tab1" className="w-full">
  <TabsList className="grid grid-cols-2">
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">
    Content for tab 1
  </TabsContent>
  <TabsContent value="tab2">
    Content for tab 2
  </TabsContent>
</Tabs>
```

**Best Practices**:
- Each `TabsTrigger` must have a corresponding `TabsContent` with matching `value`
- Use the `defaultValue` prop to specify the initially selected tab
- Use `className="grid grid-cols-[n]"` on `TabsList` for equal-width tabs
- Ensure tab content is accessible and properly labeled

### Toast/Toaster

**Standard Import for useToast hook**:
```jsx
import { useToast } from "@/hooks/use-toast";
```

**Usage**:
```jsx
const { toast } = useToast();

const showToast = () => {
  toast({
    title: "Success",
    description: "Your action was completed successfully.",
    variant: "default", // or "destructive"
  });
};
```

**Toaster Component (already added to the layout)**:
```jsx
import { Toaster } from "@/components/ui/toaster";

// In your layout component
<Toaster />
```

**Best Practices**:
- Import `useToast` from `@/hooks/use-toast`, not from UI components
- Include a title and description for better accessibility
- Use the appropriate variant based on the message type
- Only include the `Toaster` component once in your application layout

### Tooltip

**Standard Import**:
```jsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
```

**Usage**:
```jsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline" size="icon">
        <InfoIcon className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Additional information</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

**Best Practices**:
- Always wrap tooltips with `TooltipProvider`
- Use `asChild` on `TooltipTrigger` when wrapping an existing component
- Keep tooltip content concise and helpful
- Position tooltips with `side` and `align` props when necessary
- For multiple tooltips in a component, wrap the entire component with a single `TooltipProvider`

## Integration with Theme

All shadcn/ui components automatically adapt to light and dark themes using CSS variables defined in our theme configuration. Key variables to be aware of:

- `--background` / `--foreground`: Base background and text colors
- `--card` / `--card-foreground`: Card component colors
- `--popover` / `--popover-foreground`: Popover and dropdown colors
- `--primary` / `--primary-foreground`: Primary action colors
- `--secondary` / `--secondary-foreground`: Secondary action colors
- `--muted` / `--muted-foreground`: Subdued element colors
- `--accent` / `--accent-foreground`: Accent colors for highlights
- `--destructive` / `--destructive-foreground`: Error/danger colors
- `--border`: Border colors
- `--input`: Input field colors
- `--ring`: Focus ring colors

When customizing components, use these variables instead of hard-coded colors to ensure proper theme support.

## Common Issues and Solutions

1. **Manual Dark Mode**: Remove any `.dark` class selectors in CSS and use theme variables instead
2. **Inconsistent Styling**: Use Tailwind classes consistently across components
3. **Import Issues**: Ensure imports come from the correct paths
4. **Performance**: Use the components as intended to avoid unnecessary re-renders
5. **Accessibility**: Follow accessibility guidelines (labels, ARIA attributes, etc.)

## Testing and Verification

When implementing or modifying components, verify:

1. Proper light and dark mode rendering
2. Correct component behavior in all states
3. Proper integration with surrounding components
4. Accessibility compliance
5. Responsive behavior on different screen sizes