# Alert Dialog Component

**Created:** 2025-04-24
**Source:** Radix UI Primitives

## Overview

Alert Dialog is a modal dialog that interrupts the user with important content and expects a response. Unlike regular dialogs, it's specifically designed for critical confirmations.

## Key Features

- Focus is automatically trapped within the dialog
- Can be controlled or uncontrolled
- Manages screen reader announcements with Title and Description components
- Esc key closes the component automatically
- Supports accessible keyboard navigation

## Installation

```bash
npm install @radix-ui/react-alert-dialog
```

## Component Anatomy

```jsx
import { AlertDialog } from "radix-ui";

export default () => (
  <AlertDialog.Root>
    <AlertDialog.Trigger />
    <AlertDialog.Portal>
      <AlertDialog.Overlay />
      <AlertDialog.Content>
        <AlertDialog.Title />
        <AlertDialog.Description />
        <AlertDialog.Cancel />
        <AlertDialog.Action />
      </AlertDialog.Content>
    </AlertDialog.Portal>
  </AlertDialog.Root>
);
```

## API Reference

### Root

Contains all parts of an alert dialog.

| Prop | Type | Description |
| ---- | ---- | ----------- |
| `defaultOpen` | boolean | The open state when initially rendered (uncontrolled) |
| `open` | boolean | The controlled open state (use with `onOpenChange`) |
| `onOpenChange` | (open: boolean) => void | Event handler for open state changes |

### Trigger

Button that opens the dialog.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

**Data Attributes:** `[data-state="open"|"closed"]`

### Portal

Portals overlay and content into the body.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `forceMount` | boolean | - | Force mounting for animation control |
| `container` | HTMLElement | document.body | Container element for portal |

### Overlay

Covers inert portion of the view when dialog is open.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `forceMount` | boolean | - | Force mounting for animation control |

**Data Attributes:** `[data-state="open"|"closed"]`

### Content

Contains content for the open dialog.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `forceMount` | boolean | - | Force mounting for animation control |
| `onOpenAutoFocus` | (event: Event) => void | - | Handler when focus moves to action after opening |
| `onCloseAutoFocus` | (event: Event) => void | - | Handler when focus moves to trigger after closing |
| `onEscapeKeyDown` | (event: KeyboardEvent) => void | - | Handler when escape key is pressed |

**Data Attributes:** `[data-state="open"|"closed"]`

### Cancel

Button that closes the dialog (visually distinct from Action).

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

### Action

Button that confirms and closes the dialog (visually distinct from Cancel).

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

### Title

Accessible name announced when dialog opens.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

### Description

Accessible description announced when dialog opens.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

## Usage Examples

### Controlled Dialog with Async Submit

```jsx
import * as React from "react";
import { AlertDialog } from "radix-ui";

const wait = () => new Promise((resolve) => setTimeout(resolve, 1000));

export default () => {
  const [open, setOpen] = React.useState(false);

  return (
    <AlertDialog.Root open={open} onOpenChange={setOpen}>
      <AlertDialog.Trigger>Open</AlertDialog.Trigger>
      <AlertDialog.Portal>
        <AlertDialog.Overlay />
        <AlertDialog.Content>
          <form
            onSubmit={(event) => {
              wait().then(() => setOpen(false));
              event.preventDefault();
            }}
          >
            {/* form inputs */}
            <button type="submit">Submit</button>
          </form>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
};
```

### Custom Portal Container

```jsx
export default () => {
  const [container, setContainer] = React.useState(null);
  return (
    <div>
      <AlertDialog.Root>
        <AlertDialog.Trigger />
        <AlertDialog.Portal container={container}>
          <AlertDialog.Overlay />
          <AlertDialog.Content>...</AlertDialog.Content>
        </AlertDialog.Portal>
      </AlertDialog.Root>

      <div ref={setContainer} />
    </div>
  );
};
```

## Accessibility

Implements the [Alert and Message Dialogs WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog).

### Keyboard Interactions

| Key | Action |
| --- | ------ |
| `Space` | Opens/closes the dialog |
| `Enter` | Opens/closes the dialog |
| `Tab` | Moves focus to next focusable element |
| `Shift + Tab` | Moves focus to previous focusable element |
| `Esc` | Closes dialog and moves focus to trigger |