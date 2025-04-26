# Toast Component

**Purpose**: A succinct message that is displayed temporarily.

## Key Features

- Automatically closes after a configurable duration
- Pauses closing on hover, focus, and window blur
- Supports keyboard hotkey to jump to toast viewport
- Supports closing via swipe gesture
- Exposes CSS variables for swipe animations
- Can be controlled or uncontrolled
- Accessibility considerations for screen readers

## Installation

```bash
npm install @radix-ui/react-toast
```

## Component Anatomy

```jsx
import { Toast } from "radix-ui";

export default () => (
	<Toast.Provider>
		<Toast.Root>
			<Toast.Title />
			<Toast.Description />
			<Toast.Action />
			<Toast.Close />
		</Toast.Root>

		<Toast.Viewport />
	</Toast.Provider>
);
```

## API Reference

### Provider

The provider that wraps your toasts and toast viewport. Usually wraps the application.

**Props:**
- `duration` (number, default: 5000) - Milliseconds before auto-closing each toast
- `label` (string, default: "Notification") - Accessible label for screen readers
- `swipeDirection` ("right" | "left" | "up" | "down", default: "right") - Direction of swipe gesture to close
- `swipeThreshold` (number, default: 50) - Swipe distance in pixels required to trigger close

### Viewport

The fixed area where toasts appear. Users can jump to it using a hotkey.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `hotkey` (string[], default: ["F8"]) - Keyboard shortcut to focus the viewport
- `label` (string, default: "Notifications ({hotkey})") - Accessible label with hotkey placeholder

### Root

The toast component that automatically closes.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `type` ("foreground" | "background", default: "foreground") - Accessibility sensitivity level
- `duration` (number) - Override auto-close time from provider
- `defaultOpen` (boolean, default: true) - Initial open state when uncontrolled
- `open` (boolean) - Controlled open state, use with `onOpenChange`
- `onOpenChange` (function) - Handler when open state changes
- `onEscapeKeyDown` (function) - Handler for escape key press
- `onPause` (function) - Handler when dismiss timer pauses
- `onResume` (function) - Handler when dismiss timer resumes
- `onSwipeStart`, `onSwipeMove`, `onSwipeEnd`, `onSwipeCancel` (function) - Swipe gesture handlers
- `forceMount` (boolean) - Forces mounting for animation control

**Data Attributes:**
- `[data-state]`: "open" | "closed"
- `[data-swipe]`: "start" | "move" | "cancel" | "end"
- `[data-swipe-direction]`: "up" | "down" | "left" | "right"

**CSS Variables:**
- `--radix-toast-swipe-move-x` - Horizontal offset during swipe
- `--radix-toast-swipe-move-y` - Vertical offset during swipe
- `--radix-toast-swipe-end-x` - Final horizontal position after swipe
- `--radix-toast-swipe-end-y` - Final vertical position after swipe

### Title

An optional title for the toast.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Description

The toast message content.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

### Action

An action button that is safe to ignore.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `altText` (string, required) - Description of alternative ways to perform the action for screen readers

### Close

A button to dismiss the toast.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

## Implementation Examples

### Custom Hotkey

```jsx
<Toast.Provider>
  {/* ... */}
  <Toast.Viewport hotkey={["altKey", "KeyT"]} />
</Toast.Provider>
```

### Custom Duration

```jsx
<Toast.Root duration={3000}>
  <Toast.Description>Saved!</Toast.Description>
</Toast.Root>
```

### Animating Swipe Gesture

```jsx
// JSX
<Toast.Provider swipeDirection="right">
  <Toast.Root className="ToastRoot">...</Toast.Root>
  <Toast.Viewport />
</Toast.Provider>

// CSS
.ToastRoot[data-swipe="move"] {
  transform: translateX(var(--radix-toast-swipe-move-x));
}
.ToastRoot[data-swipe="cancel"] {
  transform: translateX(0);
  transition: transform 200ms ease-out;
}
.ToastRoot[data-swipe="end"] {
  animation: slideRight 100ms ease-out;
}
```

## Accessibility

Adheres to the [`aria-live` requirements](https://www.w3.org/TR/wai-aria/#aria-live).

### Toast Sensitivity Types

- **Foreground** (`type="foreground"`): Announced immediately by screen readers, best for user-initiated actions
- **Background** (`type="background"`): Announced at the next opportunity, best for background notifications

### Alternative Actions

Use `altText` on `Action` to provide screen reader users with alternative ways to perform the action:

```jsx
<Toast.Root type="foreground" duration={10000}>
  <Toast.Description>File removed successfully.</Toast.Description>
  <Toast.Action altText="Undo (Alt+U)">
    Undo <kbd>Alt</kbd>+<kbd>U</kbd>
  </Toast.Action>
  <Toast.Close>Dismiss</Toast.Close>
</Toast.Root>
```

### Keyboard Interactions

- **F8**: Focus toasts viewport
- **Tab/Shift+Tab**: Navigate focusable elements
- **Space/Enter**: When focused on Action or Close, activates the button
- **Esc**: Close the toast when focused