# Button Component

## Purpose

The Button component is a versatile, reusable button element that supports multiple variants and sizes. It serves as the primary interactive control throughout the application, providing consistent styling and behavior for clickable actions.

## Import

```jsx
import { Button } from "@/components/ui/button";
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | string | "default" | Visual style variation: "default", "destructive", "outline", "secondary", "ghost", or "link" |
| size | string | "default" | Size variation: "default", "sm", "lg", or "icon" |
| asChild | boolean | false | When true, button behavior is applied to child element instead of rendering a button |
| className | string | undefined | Additional CSS classes to apply |
| children | ReactNode | required | Content to render inside the button |
| ...props | any | - | All other props are passed to the underlying button element |

## Variants

- `default`: Primary action button with solid background
- `destructive`: Used for destructive actions (like delete)
- `outline`: Button with a border and transparent background
- `secondary`: Alternative style for secondary actions
- `ghost`: Minimal button with no background until hovered
- `link`: Appears as a text link rather than a button

## Sizes

- `default`: Standard button size (h-9, px-4, py-2)
- `sm`: Small button (h-8, px-3, text-xs)
- `lg`: Large button (h-10, px-8)
- `icon`: Square button designed for containing just an icon (h-9, w-9)

## Usage Examples

### Basic Button

```jsx
<Button>Click Me</Button>
```

### Button Variants

```jsx
<Button variant="default">Default Button</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>
```

### Button Sizes

```jsx
<Button size="default">Default Size</Button>
<Button size="sm">Small Button</Button>
<Button size="lg">Large Button</Button>
<Button size="icon"><Icon /></Button>
```

### With Icon

```jsx
import { PlusIcon } from "lucide-react";

<Button>
  <PlusIcon />
  Add Item
</Button>
```

### As Child

```jsx
<Button asChild>
  <a href="/dashboard">Dashboard</a>
</Button>
```

## Styling

The Button component uses Tailwind CSS classes through the `class-variance-authority` package to handle variants and sizes. It also uses the `cn` utility for merging classnames.

The component wraps styling with transitions for hover and focus states, and includes special handling for SVG icons to ensure consistent sizing and pointer events.

Key styling features:

- Icons inside buttons are automatically sized (size-4) and prevented from capturing pointer events
- Focus states use ring styling for accessibility
- Disabled state reduces opacity and prevents pointer events
- Each variant has unique color combinations that respect the application's theme variables

## Related Components

- [IconButton](./icon-button.md) - Specialized button for icon-only interactions
- [LinkButton](./link-button.md) - Button styled as a link