# Card Component

## Purpose

The `Card` component provides a container for content with a consistent design, elevation, and border. Cards are versatile UI elements used to group related information and actions.

## Import

```jsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
```

## Props

### Card

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the root element |

### CardHeader

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the element |

### CardTitle

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| as | React.ElementType | h3 | Element type to render the title as |
| ...props | any | | Additional props passed to the element |

### CardDescription

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the element |

### CardContent

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the element |

### CardFooter

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the element |

## Usage Example

```jsx
<Card>
  <CardHeader>
    <CardTitle>Recent Messages</CardTitle>
    <CardDescription>View your conversation history</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content with conversation details</p>
  </CardContent>
  <CardFooter>
    <Button>View All</Button>
  </CardFooter>
</Card>
```

## Variants

The Card component can be styled with different variants by applying CSS classes:

### Default Card

Standard card with subtle elevation and border.

```jsx
<Card>
  {/* Card content */}
</Card>
```

### Bordered Card

Card with emphasized border.

```jsx
<Card className="border-2 border-primary">
  {/* Card content */}
</Card>
```

### Transparent Card

Card without background color, useful for nested cards.

```jsx
<Card className="bg-transparent shadow-none">
  {/* Card content */}
</Card>
```

## Component Structure

The Card component is composed of several subcomponents to provide a consistent structure:

```jsx
<Card>                  {/* Outer container */}
  <CardHeader>         {/* Header section */}
    <CardTitle>        {/* Title element */}
    <CardDescription>  {/* Description element */}
  </CardHeader>
  <CardContent>        {/* Main content area */}
  <CardFooter>         {/* Footer section */}
</Card>
```

Each subcomponent is optional, allowing for flexible card layouts.

## Styling

The Card component uses CSS variables for consistent styling:

```css
.card {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.5rem 1.5rem 0 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.2;
}

.card-description {
  color: hsl(var(--muted-foreground));
  font-size: 0.875rem;
}

.card-content {
  padding: 1.5rem;
}

.card-footer {
  display: flex;
  align-items: center;
  padding: 0 1.5rem 1.5rem 1.5rem;
  gap: 0.5rem;
}
```

## Common Patterns

### Card Grid

Using cards in a responsive grid layout:

```jsx
<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
  <Card>
    {/* Card 1 content */}
  </Card>
  <Card>
    {/* Card 2 content */}
  </Card>
  <Card>
    {/* Card 3 content */}
  </Card>
</div>
```

### Interactive Card

Making entire cards clickable:

```jsx
<Link href="/details/1" className="block h-full">
  <Card className="h-full transition-colors hover:bg-muted/50">
    {/* Card content */}
  </Card>
</Link>
```

### Card with Icon

Including an icon in the card header:

```jsx
<Card>
  <CardHeader>
    <div className="flex items-center gap-2">
      <FileIcon className="h-4 w-4" />
      <CardTitle>Documents</CardTitle>
    </div>
    <CardDescription>Manage your files</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Card content */}
  </CardContent>
</Card>
```

## Accessibility

- Cards use background and border colors with sufficient contrast
- Card titles use proper heading hierarchy (`h3` by default)
- Interactive cards should have proper keyboard focus states
- When making a card interactive, ensure it has appropriate ARIA attributes

## Implementation Example

```jsx
import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef(({ className, as: Comp = "h3", ...props }, ref) => (
  <Comp
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
};
```

## Related Components

- [Button](./button.md)
- [Dialog](./dialog.md)
- [Sheet](./sheet.md)