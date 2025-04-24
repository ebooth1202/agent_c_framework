# Separator Component

**Purpose**: Visually or semantically separates content.

## Key Features

- Supports horizontal and vertical orientations
- Can be purely decorative or semantic
- Simple implementation with minimal API

## Installation

```bash
npm install @radix-ui/react-separator
```

## Component Anatomy

```jsx
import { Separator } from "radix-ui";

export default () => <Separator.Root />;
```

## API Reference

### Root

The separator element.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `orientation` ("horizontal" | "vertical", default: "horizontal") - The orientation of the separator
- `decorative` (boolean) - When true, indicates it's purely visual with no semantic meaning

**Data Attributes:**
- `[data-orientation]`: "vertical" | "horizontal"

## Accessibility

Adheres to the [`separator` role requirements](https://www.w3.org/TR/wai-aria-1.2/#separator).

When used semantically (not decorative), the component properly implements the separator role which helps screen readers identify boundaries between content sections.