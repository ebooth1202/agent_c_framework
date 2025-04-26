# Breadcrumb

**Created:** April 24, 2025  
**Source:** breadcrumb.mdx

## Description

Displays the path to the current resource using a hierarchy of links. Breadcrumbs help users understand their current location in a hierarchical structure and navigate back to previous levels.

## Installation

### CLI Installation

```bash
npx shadcn@latest add breadcrumb
```

### Manual Installation

1. Copy the component code to your project's component directory
2. Update import paths to match your project structure

## Usage

### Import Statement

```tsx
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
```

### Basic Example

```tsx
<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/components">Components</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Breadcrumb</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

## Component Structure

- `Breadcrumb`: The root container component
- `BreadcrumbList`: Container for breadcrumb items
- `BreadcrumbItem`: Individual item in the breadcrumb path
- `BreadcrumbLink`: A link to a previous level in the hierarchy
- `BreadcrumbPage`: Represents the current page (usually the last item)
- `BreadcrumbSeparator`: Visual separator between breadcrumb items
- `BreadcrumbEllipsis`: Used to show a collapsed state for long breadcrumbs

## Examples

### Custom Separator

Use a custom component as children for `<BreadcrumbSeparator />` to create a custom separator:

```tsx
import { Slash } from "lucide-react"

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator>
      <Slash />
    </BreadcrumbSeparator>
    <BreadcrumbItem>
      <BreadcrumbLink href="/components">Components</BreadcrumbLink>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Dropdown Integration

You can compose `<BreadcrumbItem />` with a dropdown menu for advanced navigation:

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

<BreadcrumbItem>
  <DropdownMenu>
    <DropdownMenuTrigger className="flex items-center gap-1">
      Components
      <ChevronDownIcon />
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      <DropdownMenuItem>Documentation</DropdownMenuItem>
      <DropdownMenuItem>Themes</DropdownMenuItem>
      <DropdownMenuItem>GitHub</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</BreadcrumbItem>
```

### Collapsed State with Ellipsis

Use `<BreadcrumbEllipsis />` to show a collapsed state when the breadcrumb is too long:

```tsx
import { BreadcrumbEllipsis } from "@/components/ui/breadcrumb"

<Breadcrumb>
  <BreadcrumbList>
    {/* ... */}
    <BreadcrumbItem>
      <BreadcrumbEllipsis />
    </BreadcrumbItem>
    {/* ... */}
  </BreadcrumbList>
</Breadcrumb>
```

### Custom Link Component

To use a custom link component from your routing library, use the `asChild` prop on `<BreadcrumbLink />`:

```tsx
import { Link } from "next/link"

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink asChild>
        <Link href="/">Home</Link>
      </BreadcrumbLink>
    </BreadcrumbItem>
    {/* ... */}
  </BreadcrumbList>
</Breadcrumb>
```

## Responsive Design

Breadcrumbs can be made responsive by combining different components:
- Use dropdown menus for desktop displays
- Use drawers for mobile displays
- Use ellipsis for long paths

## Accessibility

The breadcrumb component follows the WAI-ARIA design pattern for breadcrumbs:
- Uses appropriate ARIA attributes for navigation
- Ensures proper focus management
- Provides clear indication of the current page