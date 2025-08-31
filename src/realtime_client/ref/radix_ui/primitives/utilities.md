# Radix UI Utilities

*AI-optimized utility reference documentation*

Radix UI provides several utilities to help with common patterns and enhance the core primitives. These utilities handle specific concerns like portals, direction context, and composition.

## Slot

A utility for merging multiple components and forwarding props.

### Usage

```jsx
import { Slot } from "radix-ui";

// Merges props from SlotTrigger and Button
const SlotButton = ({ children, ...props }) => (
  <Slot {...props}>
    <button>{children}</button>
  </Slot>
);

// Usage:
<SlotButton onClick={() => console.log('clicked')}>Click me</SlotButton>
```

### API Reference

#### Slot
- **Purpose**: Merges its props with its immediate child's props
- **Use case**: When you want to compose components without introducing a new DOM node

## Portal

Renders a component into a DOM node that exists outside the DOM hierarchy of the parent component.

### Usage

```jsx
import { Portal } from "radix-ui";

<Portal>
  <div>This will be rendered outside the DOM hierarchy</div>
</Portal>

// With custom container
<Portal container={document.getElementById('my-portal-container')}>
  <div>This will be rendered in the specified container</div>
</Portal>
```

### API Reference

#### Portal
- `container`: HTMLElement - Optional element to render portal content into
- `forceMount`: boolean - Forces mounting when used with animation libraries

## Direction Provider

Provides a direction (RTL or LTR) context to descendant components.

### Usage

```jsx
import { DirectionProvider } from "radix-ui";

<DirectionProvider dir="rtl">
  {/* Components inside will inherit RTL direction */}
  <MyComponent />
</DirectionProvider>
```

### API Reference

#### DirectionProvider
- `dir`: "ltr" | "rtl" - The text direction

## Visually Hidden

Hides content visually while keeping it accessible to screen readers.

### Usage

```jsx
import { VisuallyHidden } from "radix-ui";

<button>
  <VisuallyHidden>Search</VisuallyHidden>
  <SearchIcon />
</button>
```

## Use Controllable State

A hook for managing both controlled and uncontrolled component states.

### Usage

```jsx
import { useControllableState } from "radix-ui";

function MyComponent({ value: valueProp, defaultValue, onChange }) {
  const [value, setValue] = useControllableState({
    prop: valueProp,
    defaultProp: defaultValue,
    onChange,
  });

  return (
    <button onClick={() => setValue(value + 1)}>
      Value: {value}
    </button>
  );
}
```

### API Reference

#### useControllableState
- `prop`: any - Controlled value
- `defaultProp`: any - Default value for uncontrolled state
- `onChange`: function - Callback for when value changes

## Primitive

A utility component used internally by Radix to create low-level UI primitives. This is used for creating DOM nodes with proper event handling.

## Composing Utilities

These utilities can be combined with Radix primitives for powerful compositions:

```jsx
import { Slot, VisuallyHidden, Dialog } from "radix-ui";

// Custom trigger that composes with Dialog.Trigger
const CustomTrigger = React.forwardRef((props, forwardedRef) => (
  <Dialog.Trigger asChild>
    <Slot {...props} ref={forwardedRef}>
      <button>
        <VisuallyHidden>Open dialog</VisuallyHidden>
        <OpenIcon />
      </button>
    </Slot>
  </Dialog.Trigger>
));
```