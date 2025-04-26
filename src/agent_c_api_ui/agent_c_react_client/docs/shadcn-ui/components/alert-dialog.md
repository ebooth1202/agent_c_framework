# Alert Dialog

**Created:** April 24, 2025  
**Source:** alert-dialog.mdx

## Description

A modal dialog that interrupts the user with important content and expects a response.

## Installation

### CLI Installation

```bash
npx shadcn@latest add alert-dialog
```

### Manual Installation

1. Install the required dependencies:

```bash
npm install @radix-ui/react-alert-dialog
```

2. Copy the component code to your project's component directory
3. Update import paths to match your project structure

## Usage

### Import Statement

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
```

### Basic Example

```tsx
<AlertDialog>
  <AlertDialogTrigger>Open</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

## Component Structure

- `AlertDialog`: Root container component
- `AlertDialogTrigger`: Button that opens the dialog
- `AlertDialogContent`: Container for dialog content
- `AlertDialogHeader`: Header section of the dialog
- `AlertDialogTitle`: Title element
- `AlertDialogDescription`: Text description of the dialog action
- `AlertDialogFooter`: Footer containing action buttons
- `AlertDialogCancel`: Button to dismiss/cancel the dialog
- `AlertDialogAction`: Button to confirm/continue with the action