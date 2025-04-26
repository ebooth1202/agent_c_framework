# Dialog

*Created: 2025-04-24*

A window overlaid on either the primary window or another dialog window, rendering the content underneath inert.

## Component API

### Root

Contains all parts of a dialog.

```jsx
<Dialog.Root>
  <Dialog.Trigger />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title />
      <Dialog.Description />
      <Dialog.Close />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

**Props:**
- `defaultOpen`: Initial open state (uncontrolled) - boolean
- `open`: Controlled open state - boolean
- `onOpenChange`: Event handler for open state changes - `(open: boolean) => void`
- `modal`: Controls modality (default: true) - boolean

### Trigger

The button that opens the dialog.

**Props:**
- `asChild`: Merges props with child element - boolean

**Data Attributes:**
- `[data-state]`: "open" | "closed"

### Portal

Portals the overlay and content parts into the `body`.

**Props:**
- `forceMount`: Forces mounting for animation control - boolean
- `container`: Specify container element (default: document.body) - HTMLElement

### Overlay

A layer that covers the inert portion of the view when dialog is open.

**Props:**
- `asChild`: Merges props with child element - boolean
- `forceMount`: Forces mounting for animation control - boolean

**Data Attributes:**
- `[data-state]`: "open" | "closed"

### Content

Contains content to be rendered in the open dialog.

**Props:**
- `asChild`: Merges props with child element - boolean
- `forceMount`: Forces mounting for animation control - boolean
- Event handlers: `onOpenAutoFocus`, `onCloseAutoFocus`, `onEscapeKeyDown`, `onPointerDownOutside`, `onInteractOutside`

**Data Attributes:**
- `[data-state]`: "open" | "closed"

### Close

The button that closes the dialog.

**Props:**
- `asChild`: Merges props with child element - boolean

### Title

An accessible title announced when dialog is opened.

**Props:**
- `asChild`: Merges props with child element - boolean

### Description

An optional accessible description announced when dialog is opened.

**Props:**
- `asChild`: Merges props with child element - boolean

## Accessibility

Adheres to the Dialog WAI-ARIA design pattern:
- Focus is automatically trapped within modal dialog
- Esc key closes the dialog
- Scroll is locked when modal
- Screen readers announce dialog title and description

**Keyboard Interactions:**
- Space/Enter: Opens/closes the dialog
- Tab: Moves focus to next focusable element
- Shift+Tab: Moves focus to previous focusable element
- Esc: Closes dialog and returns focus to trigger

## Usage Examples

### Basic Dialog

```jsx
<Dialog.Root>
  <Dialog.Trigger>Open Dialog</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="DialogOverlay" />
    <Dialog.Content className="DialogContent">
      <Dialog.Title>Dialog Title</Dialog.Title>
      <Dialog.Description>
        This is a description of the dialog's purpose.
      </Dialog.Description>
      <p>Dialog content goes here</p>
      <Dialog.Close>Close</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### Controlled Dialog with Form

```jsx
import * as React from "react";

export default () => {
  const [open, setOpen] = React.useState(false);
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    // Submit form data asynchronously
    await submitFormData();
    // Close dialog when done
    setOpen(false);
  };
  
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger>Open Form</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay />
        <Dialog.Content>
          <Dialog.Title>Submit Information</Dialog.Title>
          <form onSubmit={handleSubmit}>
            {/* Form fields here */}
            <button type="submit">Submit</button>
          </form>
          <Dialog.Close>Cancel</Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
```

### Scrollable Dialog

```jsx
<Dialog.Root>
  <Dialog.Trigger>Open Scrollable Dialog</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="ScrollableOverlay">
      <Dialog.Content className="ScrollableContent">
        <Dialog.Title>Terms and Conditions</Dialog.Title>
        <div className="ScrollableArea">
          {/* Long content here */}
        </div>
        <Dialog.Close>Accept</Dialog.Close>
      </Dialog.Content>
    </Dialog.Overlay>
  </Dialog.Portal>
</Dialog.Root>
```

```css
.ScrollableOverlay {
  background: rgba(0, 0, 0, 0.5);
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  overflow-y: auto;
}

.ScrollableContent {
  background: white;
  border-radius: 6px;
  padding: 20px;
  max-width: 500px;
  max-height: 85vh;
  margin: 20px;
}

.ScrollableArea {
  overflow-y: auto;
  max-height: 60vh;
}
```