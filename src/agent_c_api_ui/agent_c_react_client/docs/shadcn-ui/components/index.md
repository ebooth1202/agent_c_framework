# shadcn/ui Components

**Created:** April 24, 2025  
**Purpose:** Index of available shadcn/ui components

## Overview
shadcn/ui provides a collection of accessible, reusable, and composable React components that are built with Radix UI and styled with Tailwind CSS. This index provides a quick reference to all available components.

## UI Components

### Inputs & Form Elements
- [Button](button.md) - Standard button component with variants
- [Checkbox](checkbox.md) - Toggle control for boolean values
- [Input](input.md) - Standard text input field
- [Select](select.md) - Dropdown selection component
- [Textarea](textarea.md) - Multi-line text input field

### Layout & Structure
- [Accordion](accordion.md) - Vertically stacked sections that can be expanded/collapsed
- [Card](card.md) - Container component for related content

### Feedback & Alerts
- [Alert](alert.md) - Displays important messages to the user
- [Dialog](dialog.md) - Modal window overlay for focused tasks

### Navigation
- [Dropdown Menu](dropdown-menu.md) - Menu triggered by a button

## Component Installation

All components can be added to your project using the shadcn CLI:

```bash
npx shadcn@latest add [component-name]
```

For example, to add the button component:

```bash
npx shadcn@latest add button
```

## Component Structure

Each component typically follows this pattern:
1. Installation instructions (CLI and manual)
2. Basic usage example
3. Examples of variants and use cases
4. API reference where applicable

## Notes

- Components are designed to be customized to your project's needs
- All components use Tailwind CSS for styling
- Most interactive components are built on Radix UI primitives