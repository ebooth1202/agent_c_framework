# Dialog Component

**Source:** Original from `shadcn-ui/components/dialog.mdx`  
**Created:** April 24, 2025  

## Overview
A window overlaid on either the primary window or another dialog window, rendering the content underneath inert. Dialog is a core UI component for displaying modal content.  

## Installation

### CLI Installation
```bash
npx shadcn@latest add dialog
```

### Manual Installation
1. Install dependencies:
```bash
npm install @radix-ui/react-dialog
```
2. Copy and paste the code from the component source
3. Update import paths to match your project setup

## Usage

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
```

```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you absolutely sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

## Examples

### Custom Close Button Example
A dialog with a custom close button implementation.

## Integration Notes

To activate the `Dialog` component from within a `Context Menu` or `Dropdown Menu`, you must encase the `Context Menu` or
`Dropdown Menu` component in the `Dialog` component.

```tsx
<Dialog>
  <ContextMenu>
    <ContextMenuTrigger>Right click</ContextMenuTrigger>
    <ContextMenuContent>
      <ContextMenuItem>Open</ContextMenuItem>
      <ContextMenuItem>Download</ContextMenuItem>
      <DialogTrigger asChild>
        <ContextMenuItem>
          <span>Delete</span>
        </ContextMenuItem>
      </DialogTrigger>
    </ContextMenuContent>
  </ContextMenu>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you absolutely sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone. Are you sure you want to permanently
        delete this file from our servers?
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button type="submit">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

## References
- Documentation: https://www.radix-ui.com/docs/primitives/components/dialog
- API Reference: https://www.radix-ui.com/docs/primitives/components/dialog#api-reference