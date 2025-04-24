# Sheet Component

*Created: May 2, 2023 from sheet.mdx*

## Overview
A sheet component extends the Dialog component to display content that complements the main content of the screen. It slides in from the edge of the screen (top, right, bottom, or left) and is commonly used for navigation menus, filters, or property panels.

## Key Features
- Slides in from any edge of the screen (top, right, bottom, left)
- Backdrop overlay that dims the main content
- Dismissible via close button, clicking outside, or pressing Escape key
- Customizable width/height
- Built on Radix UI Dialog primitives

## Installation

### CLI Installation
```bash
npx shadcn@latest add sheet
```

### Manual Installation
1. Install dependencies:
```bash
npm install @radix-ui/react-dialog
```

2. Import the component:
```tsx
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
```

## Component Structure
The Sheet component is composed of multiple parts:
- `Sheet`: The root container component
- `SheetTrigger`: The button that opens the sheet
- `SheetContent`: The container for the sheet content
- `SheetHeader`: Optional header section
- `SheetTitle`: Title element within the header
- `SheetDescription`: Description text within the header
- `SheetFooter`: Optional footer section
- `SheetClose`: Button to close the sheet

## Usage

### Basic Usage
```tsx
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Are you absolutely sure?</SheetTitle>
      <SheetDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

### Positioning with Side Prop
Use the `side` property to specify which edge the sheet appears from:

```tsx
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent side="left">
    {/* Left side panel content */}
  </SheetContent>
</Sheet>
```

Available side values: `top`, `right`, `bottom`, `left`

### Custom Sizing
Adjust the sheet size using CSS classes:

```tsx
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent className="w-[400px] sm:w-[540px]">
    <SheetHeader>
      <SheetTitle>Sheet Title</SheetTitle>
      <SheetDescription>Sheet description text here.</SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

## Common Use Cases
- Mobile navigation menus
- Filter panels
- Property inspectors
- Form entry panels
- Settings panels
- Shopping carts
- User profile details

## Accessibility
- Focus is trapped within the sheet when open
- Supports keyboard navigation
- Closes on Escape key press
- Implements proper ARIA attributes
- Screen reader announcements for sheet state