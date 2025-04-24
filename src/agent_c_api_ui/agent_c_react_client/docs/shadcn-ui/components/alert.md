---
Title: Alert Component
Created: 2025-04-24
Source: ui/docs/shadcn-ui/components/alert.mdx
---

# Alert

Displays a callout for user attention.

## Installation

### Option 1: Using CLI

```bash
npx shadcn@latest add alert
```

### Option 2: Manual Installation

Simply copy the component source code and update import paths to match your project structure.

## Usage

```tsx
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

<Alert>
  <Terminal className="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components and dependencies to your app using the cli.
  </AlertDescription>
</Alert>
```

## Variants

### Default Alert

Standard alert with icon, title, and description. Used for general information.

### Destructive Alert

Red-styled alert for warning or critical information. Typically used for destructive actions or error notifications.

Example:
```tsx
<Alert variant="destructive">
  <AlertTitle>Delete this item?</AlertTitle>
  <AlertDescription>
    This action cannot be undone.
  </AlertDescription>
</Alert>
```

## Components

- `Alert`: The container component
- `AlertTitle`: For the alert heading
- `AlertDescription`: For the alert body content

## Best Practices

- Include icons when appropriate to enhance visual recognition
- Use destructive variant sparingly for true warnings/errors
- Keep alert content concise and actionable