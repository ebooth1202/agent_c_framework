# Dialog Component

## Purpose

The `Dialog` component displays content in a modal overlay, requiring user interaction before returning to the main interface. It's used for important information, confirmations, forms, and other content that requires focus.

## Import

```jsx
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
```

## Props

### Dialog

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| open | boolean | undefined | Controls the open state of the dialog |
| onOpenChange | function | undefined | Callback when open state changes |
| modal | boolean | true | Whether the dialog behaves as a modal |
| ...props | any | | Additional props passed to Radix Dialog |

### DialogTrigger

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| asChild | boolean | false | Use the provided child as the trigger element |
| ...props | any | | Additional props passed to Radix DialogTrigger |

### DialogContent

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| children | React.ReactNode | | Dialog content |
| onEscapeKeyDown | function | | Callback when escape key is pressed |
| onPointerDownOutside | function | | Callback when clicking outside dialog |
| onInteractOutside | function | | Callback when interacting outside dialog |
| ...props | any | | Additional props passed to Radix DialogContent |

### DialogHeader, DialogFooter, DialogTitle, DialogDescription, DialogClose

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| className | string | | Additional CSS classes |
| ...props | any | | Additional props passed to the element |

## Usage Example

### Basic Dialog

```jsx
<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Authentication Required</DialogTitle>
      <DialogDescription>
        Please enter your credentials to continue.
      </DialogDescription>
    </DialogHeader>
    <div className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="username" className="text-right">Username</Label>
        <Input id="username" className="col-span-3" />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="password" className="text-right">Password</Label>
        <Input id="password" type="password" className="col-span-3" />
      </div>
    </div>
    <DialogFooter>
      <Button type="submit">Login</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Controlled Dialog

```jsx
import { useState } from "react";

function ControlledDialog() {
  const [open, setOpen] = useState(false);
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Open Controlled Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Controlled Dialog</DialogTitle>
          <DialogDescription>
            This dialog's open state is controlled programmatically.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <p>Dialog content</p>
        </div>
        <DialogFooter>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

## Component Structure

The Dialog component is composed of several subcomponents:

```jsx
<Dialog>                 {/* Provider component */}
  <DialogTrigger>       {/* Element that opens the dialog */}
  <DialogContent>       {/* Container for dialog content */}
    <DialogHeader>      {/* Header section */}
      <DialogTitle>     {/* Dialog title */}
      <DialogDescription> {/* Extended description */}
    </DialogHeader>
    {/* Custom content */}
    <DialogFooter>      {/* Footer section, typically for actions */}
      <DialogClose>     {/* Element that closes the dialog */}
    </DialogFooter>
  </DialogContent>
</Dialog>
```

## Variants and Use Cases

### Confirmation Dialog

For confirming user actions:

```jsx
<Dialog>
  <DialogTrigger asChild>
    <Button variant="destructive">Delete Item</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Deletion</DialogTitle>
      <DialogDescription>
        Are you sure you want to delete this item? This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">Cancel</Button>
      </DialogClose>
      <Button variant="destructive" onClick={handleDelete}>Delete</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Form Dialog

For collecting user input:

```jsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Create New</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Create New Item</DialogTitle>
      <DialogDescription>
        Fill out the form below to create a new item.
      </DialogDescription>
    </DialogHeader>
    <form onSubmit={handleSubmit}>
      <div className="grid gap-4 py-4">
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="name" className="text-right">Name</Label>
          <Input id="name" className="col-span-3" />
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="description" className="text-right">Description</Label>
          <Textarea id="description" className="col-span-3" />
        </div>
      </div>
      <DialogFooter>
        <Button type="submit">Create</Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

## Styling

The Dialog component uses CSS variables for consistent styling:

```css
.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  animation: fade-in 150ms cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 50;
}

.dialog-content {
  background-color: hsl(var(--background));
  border-radius: var(--radius);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90vw;
  max-width: 450px;
  max-height: 85vh;
  padding: 1.5rem;
  z-index: 50;
  animation: fade-in-scale 150ms cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: center;
}

.dialog-title {
  font-weight: 600;
  font-size: 1.25rem;
}

.dialog-description {
  color: hsl(var(--muted-foreground));
  font-size: 0.875rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
```

## Animation

The Dialog includes entrance and exit animations:

```css
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fade-in-scale {
  from { opacity: 0; transform: translate(-50%, -48%) scale(0.96); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fade-out-scale {
  from { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  to { opacity: 0; transform: translate(-50%, -48%) scale(0.96); }
}
```

## Accessibility

The Dialog component follows accessibility best practices:

- Uses `role="dialog"` and `aria-modal="true"`
- Manages focus when the dialog opens and closes
- Supports keyboard navigation (Escape to close)
- Uses proper heading hierarchy with `DialogTitle`
- Provides descriptive content with `DialogDescription`
- Traps focus within the dialog when open

## Implementation Example

```jsx
import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogClose = DialogPrimitive.Close;

const DialogPortal = DialogPrimitive.Portal;

const DialogOverlay = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
));
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName;

const DialogContent = React.forwardRef(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
));
DialogContent.displayName = DialogPrimitive.Content.displayName;

const DialogHeader = ({
  className,
  ...props
}) => (
  <div
    className={cn("flex flex-col space-y-1.5 text-center sm:text-left", className)}
    {...props}
  />
);
DialogHeader.displayName = "DialogHeader";

const DialogFooter = ({
  className,
  ...props
}) => (
  <div
    className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2", className)}
    {...props}
  />
);
DialogFooter.displayName = "DialogFooter";

const DialogTitle = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn("text-lg font-semibold leading-none tracking-tight", className)}
    {...props}
  />
));
DialogTitle.displayName = DialogPrimitive.Title.displayName;

const DialogDescription = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
));
DialogDescription.displayName = DialogPrimitive.Description.displayName;

export {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
};
```

## Related Components

- [Sheet](./sheet.md)
- [Card](./card.md)
- [AlertDialog](./alert-dialog.md)