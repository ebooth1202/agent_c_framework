# Tooltip

_Created: 2025-04-24 | Source: tooltip.mdx_

## Overview

A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it. Tooltips provide contextual information without requiring user interaction.

## Key Features

- Displays informational text on hover/focus
- Automatically positions around the trigger element
- Built on Radix UI primitives for accessibility
- Supports custom content

## Installation

**CLI Method:**
```bash
npx shadcn@latest add tooltip
```

**Manual Installation:**
1. Install dependencies:
   ```bash
   npm install @radix-ui/react-tooltip
   ```
2. Copy the component source code
3. Update import paths for your project

## Component Structure

The tooltip system consists of several components:
- `TooltipProvider`: Provider component for global tooltip configuration
- `Tooltip`: Container component for tooltip functionality
- `TooltipTrigger`: The element that triggers the tooltip display
- `TooltipContent`: The actual content displayed in the tooltip

## Usage

```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>Hover</TooltipTrigger>
    <TooltipContent>
      <p>Add to library</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

## Common Use Cases

- Providing additional context for buttons with icon-only displays
- Explaining the purpose of form fields
- Clarifying abbreviated content
- Showing keyboard shortcuts
- Displaying additional information that doesn't fit in the UI

## Accessibility

Built on Radix UI's Tooltip primitive which ensures proper accessibility including:
- Appears on focus for keyboard navigation
- Proper ARIA attributes
- Screen reader announcements
- Dismissible with Escape key