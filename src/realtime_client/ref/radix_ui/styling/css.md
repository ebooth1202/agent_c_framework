# Styling Radix UI with CSS

*AI-optimized styling reference documentation*

Radix UI components ship unstyled, allowing you to apply styles using plain CSS. This approach is simple, performant, and works with any project setup.

## Basic Styling

### CSS File Approach

The most straightforward method is to create a separate CSS file and import it:

```jsx
// Component.jsx
import { Accordion } from "radix-ui";
import "./styles.css";

export default () => (
  <Accordion.Root className="accordion-root">
    <Accordion.Item className="accordion-item" value="item-1">
      <Accordion.Trigger className="accordion-trigger">
        Section 1
      </Accordion.Trigger>
      <Accordion.Content className="accordion-content">
        Content for section 1
      </Accordion.Content>
    </Accordion.Item>
  </Accordion.Root>
);
```

```css
/* styles.css */
.accordion-root {
  border-radius: 6px;
  width: 300px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.accordion-item {
  border-bottom: 1px solid #eee;
}

.accordion-trigger {
  width: 100%;
  padding: 10px 15px;
  text-align: left;
  background: none;
  border: none;
  font-size: 16px;
}

.accordion-content {
  padding: 15px;
  overflow: hidden;
}

/* Animation using custom property exposed by Radix UI */
.accordion-content[data-state="open"] {
  animation: slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

.accordion-content[data-state="closed"] {
  animation: slideUp 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

@keyframes slideDown {
  from {
    height: 0;
  }
  to {
    height: var(--radix-accordion-content-height);
  }
}

@keyframes slideUp {
  from {
    height: var(--radix-accordion-content-height);
  }
  to {
    height: 0;
  }
}
```

## Data Attributes

Radix components expose various data attributes to target different states:

### Common Data Attributes

- `data-state`: Used for styling based on component state
  - Common values: `open`/`closed`, `checked`/`unchecked`, `active`/`inactive`
- `data-disabled`: Present when a component is disabled
- `data-highlighted`: For items that are currently highlighted/focused in menus
- `data-orientation`: Indicates `horizontal` or `vertical` orientation
- `data-side` and `data-align`: For positioning components like popovers and tooltips

```css
/* Styling a button based on state */
.dropdown-trigger[data-state="open"] {
  background-color: #f3f4f6;
}

/* Styling a menu item when highlighted */
.dropdown-item[data-highlighted] {
  background-color: #e5e7eb;
  outline: none;
}

/* Styling disabled items */
.accordion-trigger[data-disabled] {
  color: #9ca3af;
  cursor: not-allowed;
}
```

## CSS Variables

Some Radix components expose CSS custom properties (variables) for advanced styling:

### Available CSS Variables

- `--radix-accordion-content-height`: In `Accordion.Content`, represents content height
- `--radix-collapsible-content-height`: In `Collapsible.Content`, represents content height
- `--radix-popper-available-width`: Available width for popper elements
- `--radix-popper-available-height`: Available height for popper elements
- `--radix-tooltip-content-available-width`: Available width for tooltip content
- `--radix-tooltip-content-available-height`: Available height for tooltip content

```css
/* Use custom properties for animations */
.accordion-content {
  overflow: hidden;
  height: var(--radix-accordion-content-height);
  transition: height 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

/* Size constraints using custom properties */
.popover-content {
  max-width: var(--radix-popper-available-width);
  max-height: var(--radix-popper-available-height);
  overflow: auto;
}
```

## Animation Examples

### Accordion Animation

```css
.accordion-content {
  overflow: hidden;
}

.accordion-content[data-state="open"] {
  animation: slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

.accordion-content[data-state="closed"] {
  animation: slideUp 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

@keyframes slideDown {
  from { height: 0; }
  to { height: var(--radix-accordion-content-height); }
}

@keyframes slideUp {
  from { height: var(--radix-accordion-content-height); }
  to { height: 0; }
}
```

### Dialog Animation

```css
.dialog-overlay {
  background-color: rgba(0, 0, 0, 0.5);
  position: fixed;
  inset: 0;
  animation: overlayShow 150ms cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-content {
  background-color: white;
  border-radius: 6px;
  box-shadow: 0px 10px 38px -10px rgba(22, 23, 24, 0.35);
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90vw;
  max-width: 450px;
  max-height: 85vh;
  padding: 25px;
  animation: contentShow 150ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes overlayShow {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes contentShow {
  from {
    opacity: 0;
    transform: translate(-50%, -48%) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
```

## Media Queries

Radix components work well with responsive styling using standard CSS media queries:

```css
.dialog-content {
  width: 90vw;
  max-width: 450px;
}

@media (max-width: 640px) {
  .dialog-content {
    width: 100vw;
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
}
```

## CSS Reset Recommendations

When working with Radix UI components, consider these CSS resets:

```css
button {
  all: unset; /* Remove default button styling */
}

/* For components that should still show a focus ring for accessibility */
*:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}

/* Hide elements from screen but keep them available for screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```