# ShadCN/UI and Radix UI Implementation Guide

This guide outlines the proper usage of shadcn/ui and Radix UI components within our application components. The components in `/components/ui` are correctly implemented - this guide focuses on how to properly use them in our custom application components.

## Core Principles

1. **Proper Component Import**
   - Always import shadcn/ui components from the `/components/ui` directory
   - Example: `import { Button } from "@/components/ui/button"`
   - Never import from `.scratch/backup` or other locations

2. **Tailwind vs. Custom CSS**
   - Use Tailwind classes for minor adjustments
   - Use separate CSS files for complex styling
   - Store CSS files in `src/styles/components/` following naming convention

3. **Theme Compatibility**
   - Use shadcn/ui CSS variables for theming
   - Examples: `var(--background)`, `var(--foreground)`, `var(--primary)`
   - Avoid hard-coded colors
   - Support both light and dark modes

4. **Component Composition**
   - Use shadcn/ui component composition patterns
   - Example: Card + CardHeader + CardContent instead of nested divs
   - Leverage existing patterns rather than recreating them

5. **Avoid Direct Modifications**
   - Don't modify shadcn/ui components directly
   - Use component props and className for customization
   - Use the `cn()` utility for className composition

## Using Common Components

### Button

```jsx
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Correct usage
function MyComponent({ className }) {
  return (
    <Button 
      variant="outline" // default, outline, secondary, ghost, link, destructive
      size="default" // default, sm, lg, icon
      className={cn("my-custom-class", className)}
      onClick={() => console.log("Clicked")}
    >
      Click Me
    </Button>
  );
}
```

### Card

```jsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// Correct usage
function MyCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Title</CardTitle>
        <CardDescription>Description</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Content goes here</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  );
}
```

### Dialog

```jsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

// Correct usage
function MyDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dialog Title</DialogTitle>
          <DialogDescription>Dialog description here.</DialogDescription>
        </DialogHeader>
        <div className="py-4">Dialog content goes here</div>
        <DialogFooter>
          <Button type="submit">Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

### Tabs

```jsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Correct usage
function MyTabs() {
  return (
    <Tabs defaultValue="account">
      <TabsList>
        <TabsTrigger value="account">Account</TabsTrigger>
        <TabsTrigger value="password">Password</TabsTrigger>
      </TabsList>
      <TabsContent value="account">Account content</TabsContent>
      <TabsContent value="password">Password content</TabsContent>
    </Tabs>
  );
}
```

## CSS File Structure

Each component should have a corresponding CSS file in `src/styles/components/` following this structure:

```css
/* ===== COMPONENT: ComponentName ===== */
/* Description: Brief description of component purpose */

/* ComponentName: Section description */
.component-specific-class {
  /* Use CSS variables for theming */
  background-color: var(--background);
  color: var(--foreground);
  /* Other styles */
}

/* ComponentName: Another section */
.another-class {
  /* styles */
}
```

## Theme Integration

### Using Theme Variables

Use shadcn/ui CSS variables for theming whenever possible:

```css
.my-component {
  /* Core theme variables */
  background-color: var(--background);
  color: var(--foreground);
  border: 1px solid var(--border);
  
  /* Accent colors */
  background-color: var(--primary);
  color: var(--primary-foreground);
  
  /* Semantic colors */
  background-color: var(--destructive);
  color: var(--destructive-foreground);
  
  /* Other variables */
  border-radius: var(--radius);
}
```

### Respecting Dark Mode

The application supports both light and dark modes. Ensure your components look good in both modes by using the theme variables instead of hard-coded colors.

### Theme Switching

The theme is controlled by the `theme-toggle.jsx` component, which uses the SessionContext to manage theme state.

## Best Practices

1. **Use Composition Over Customization**
   - Combine existing components rather than heavily styling a single component

2. **Keep JSX Clean**
   - Move complex styling to CSS files
   - Use semantic class names

3. **Consistent Pattern Usage**
   - Follow the established patterns for each component
   - Don't mix different approaches within the same component

4. **Progressive Enhancement**
   - Start with basic functionality first
   - Add interactivity and advanced styling incrementally
   - Test each enhancement step

5. **Accessibility Considerations**
   - shadcn/ui components are built with accessibility in mind
   - Maintain these accessibility features in your implementations
   - Use appropriate ARIA attributes when needed

## Common Anti-Patterns to Avoid

1. ❌ **Inline Styles**
   - Avoid `style={{}}` for anything beyond simple positioning
   - Use CSS files for complex styling

2. ❌ **Direct DOM Manipulation**
   - Avoid direct DOM manipulation with refs when possible
   - Use React's declarative approach

3. ❌ **Hard-Coded Colors**
   - Avoid hard-coded hex or RGB values
   - Use theme variables for color consistency

4. ❌ **!important Declarations**
   - Avoid using `!important` to override styles
   - Structure CSS selectors properly to handle specificity

5. ❌ **Non-Semantic Class Names**
   - Avoid class names like `.red-text` or `.big-margin`
   - Use semantic names like `.error-message` or `.section-spacing`