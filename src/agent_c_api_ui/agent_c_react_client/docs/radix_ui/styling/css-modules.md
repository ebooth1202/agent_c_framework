# Styling Radix UI with CSS Modules

*AI-optimized styling reference documentation*

CSS Modules provide local scope for CSS classes, making them ideal for styling Radix UI components in larger applications. This approach offers the benefits of plain CSS with added scoping to prevent class name collisions.

## Basic Integration

### Component Structure

```jsx
// Dialog.jsx
import { Dialog } from "radix-ui";
import styles from "./Dialog.module.css";

export function DialogComponent() {
  return (
    <Dialog.Root>
      <Dialog.Trigger className={styles.trigger}>
        Open Dialog
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className={styles.overlay} />
        <Dialog.Content className={styles.content}>
          <Dialog.Title className={styles.title}>Dialog Title</Dialog.Title>
          <Dialog.Description className={styles.description}>
            This is a dialog built with Radix UI and styled with CSS Modules.
          </Dialog.Description>
          <Dialog.Close className={styles.closeButton}>Close</Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

### CSS Module

```css
/* Dialog.module.css */
.trigger {
  background-color: hsl(250, 80%, 50%);
  color: white;
  padding: 10px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.overlay {
  background-color: rgba(0, 0, 0, 0.5);
  position: fixed;
  inset: 0;
  animation: overlayShow 150ms cubic-bezier(0.16, 1, 0.3, 1);
}

.content {
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

.title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 10px;
}

.description {
  font-size: 16px;
  margin-bottom: 20px;
  color: hsl(240, 5%, 40%);
}

.closeButton {
  padding: 8px 16px;
  background-color: hsl(250, 80%, 50%);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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

## Composing Classes

CSS Modules allow for class composition, making it easy to share styles between components:

```css
/* base.module.css */
.primaryButton {
  background-color: hsl(250, 80%, 50%);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.primaryButton:hover {
  background-color: hsl(250, 80%, 45%);
}
```

```css
/* Dialog.module.css */
@import "./base.module.css";

.trigger {
  composes: primaryButton from "./base.module.css";
  font-size: 16px;
}

.closeButton {
  composes: primaryButton from "./base.module.css";
  font-size: 14px;
}
```

## Targeting Component States

Like with plain CSS, you can target Radix UI component states using CSS selectors and data attributes:

```css
/* Dropdown.module.css */
.trigger[data-state="open"] {
  background-color: hsl(250, 60%, 45%);
}

.item[data-highlighted] {
  background-color: hsl(250, 80%, 96%);
  outline: none;
}

.item[data-disabled] {
  color: hsl(0, 0%, 70%);
  pointer-events: none;
}
```

## Animation with CSS Variables

Radix UI exposes CSS variables for certain components that you can use in your animations:

```css
/* Accordion.module.css */
.content {
  overflow: hidden;
}

.content[data-state="open"] {
  animation: slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

.content[data-state="closed"] {
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

## Responsive Design

CSS Modules work well with responsive designs through standard media queries:

```css
/* Dialog.module.css */
.content {
  width: 90vw;
  max-width: 450px;
  padding: 25px;
}

@media (max-width: 640px) {
  .content {
    width: 100vw;
    border-radius: 0;
    padding: 16px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .description {
    font-size: 14px;
  }
}
```

## Naming Conventions

A common pattern with CSS Modules is to use camelCase for class names to match JavaScript naming conventions:

```jsx
import styles from "./Accordion.module.css";

<Accordion.Root className={styles.accordionRoot}>
  <Accordion.Item className={styles.accordionItem} value="item-1">
    <Accordion.Trigger className={styles.accordionTrigger}>
      Section 1
    </Accordion.Trigger>
    <Accordion.Content className={styles.accordionContent}>
      Content for section 1
    </Accordion.Content>
  </Accordion.Item>
</Accordion.Root>
```

## Global Styles

When needed, you can still include global styles in CSS Modules using the `:global` selector:

```css
/* theme.module.css */
:global(.radix-themes) {
  --primary-color: hsl(250, 80%, 50%);
  --background-color: white;
  --text-color: hsl(240, 5%, 20%);
}

.content {
  color: var(--text-color);
  background-color: var(--background-color);
}
```

## Best Practices

1. **One module per component**: Keep each component's styles in its own module file
2. **Use composition**: Share common styles through composition
3. **Consider specificity**: CSS Modules help with scoping, but be mindful of selector specificity
4. **Leverage data attributes**: Use Radix UI's data attributes for state-based styling
5. **Reusable variables**: For larger projects, consider a separate variables file with shared values