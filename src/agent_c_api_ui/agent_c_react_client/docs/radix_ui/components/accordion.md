# Accordion

*AI-optimized component reference*

An accordion is a vertically stacked set of interactive headings that each reveal a section of content.

## Usage

```jsx
import { Accordion } from "radix-ui";

export default function AccordionExample() {
  return (
    <Accordion.Root type="single" defaultValue="item-1" collapsible>
      <Accordion.Item value="item-1">
        <Accordion.Trigger>Is it accessible?</Accordion.Trigger>
        <Accordion.Content>
          Yes. It adheres to the WAI-ARIA design pattern.
        </Accordion.Content>
      </Accordion.Item>

      <Accordion.Item value="item-2">
        <Accordion.Trigger>Is it unstyled?</Accordion.Trigger>
        <Accordion.Content>
          Yes. It's unstyled by default, giving you freedom over the look and feel.
        </Accordion.Content>
      </Accordion.Item>
      
      <Accordion.Item value="item-3">
        <Accordion.Trigger>Can it be animated?</Accordion.Trigger>
        <Accordion.Content>
          Yes! You can animate the Accordion with CSS or JavaScript.
        </Accordion.Content>
      </Accordion.Item>
    </Accordion.Root>
  );
}
```

## API Reference

### Root

The main accordion container.

**Props**:

- `type`: `"single" | "multiple"` - Determines whether one or multiple items can be opened at the same time.
- `value`: `string` - The controlled value of the opened item(s). Must be used with `onValueChange`.
- `defaultValue`: `string` - The initial value of the opened item(s). Used for uncontrolled components.
- `onValueChange`: `(value: string) => void` - Callback called when the value changes.
- `collapsible`: `boolean` - When `type="single"`, allows closing content by clicking trigger of open item.
- `orientation`: `"vertical" | "horizontal"` - The orientation of the accordion. Default is `"vertical"`.
- `dir`: `"ltr" | "rtl"` - The reading direction of the accordion. Default is `"ltr"`.
- `disabled`: `boolean` - When `true`, prevents user interaction for all items.

### Item

An accordion item contains a trigger and content.

**Props**:

- `value`: `string` (required) - A unique value for the item.
- `disabled`: `boolean` - When `true`, prevents user interaction for this specific item.

**Data Attributes**:

- `[data-state]`: `"open" | "closed"` - The open/closed state of the item.
- `[data-disabled]`: Present when the item is disabled.
- `[data-orientation]`: `"vertical" | "horizontal"` - The orientation of the accordion.

### Trigger

The button that toggles the accordion item.

**Props**:

- Standard button attributes.

**Data Attributes**:

- `[data-state]`: `"open" | "closed"` - The open/closed state of the item.
- `[data-disabled]`: Present when the item is disabled.
- `[data-orientation]`: `"vertical" | "horizontal"` - The orientation of the accordion.

### Content

The content shown when the accordion item is open.

**Props**:

- `forceMount`: `boolean` - Forces mounting when used with React animation libraries.

**Data Attributes**:

- `[data-state]`: `"open" | "closed"` - The open/closed state of the item.
- `[data-disabled]`: Present when the item is disabled.
- `[data-orientation]`: `"vertical" | "horizontal"` - The orientation of the accordion.

**CSS Variables**:

- `--radix-accordion-content-height`: The dynamic height of the content when open.
- `--radix-accordion-content-width`: The dynamic width of the content when open (only when `orientation="horizontal"`).

## Styling

### Basic Styling

```css
/* In your CSS file */
.accordion-root {
  border-radius: 6px;
  width: 300px;
  background-color: var(--mauve-6);
}

.accordion-item {
  overflow: hidden;
  margin-top: 1px;
}

.accordion-item:first-child {
  margin-top: 0;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.accordion-item:last-child {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.accordion-trigger {
  font-family: inherit;
  background-color: transparent;
  padding: 0 20px;
  height: 45px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 15px;
  line-height: 1;
  color: var(--violet-11);
  box-shadow: 0 1px 0 var(--mauve-6);
  background-color: white;
}

.accordion-trigger:hover {
  background-color: var(--mauve-2);
}

.accordion-content {
  overflow: hidden;
  font-size: 15px;
  color: var(--mauve-11);
  background-color: var(--mauve-2);
}

.accordion-content[data-state="open"] {
  animation: slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

.accordion-content[data-state="closed"] {
  animation: slideUp 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

.accordion-content-text {
  padding: 15px 20px;
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

### Using with Component Libraries

#### Tailwind CSS Example

```jsx
<Accordion.Root 
  type="single" 
  defaultValue="item-1" 
  collapsible 
  className="w-full max-w-md bg-white rounded-md shadow-md"
>
  <Accordion.Item 
    value="item-1"
    className="border-b border-gray-200"
  >
    <Accordion.Trigger className="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50 data-[state=open]:bg-gray-50">
      <span>Section 1</span>
      <ChevronDownIcon className="h-5 w-5 transition-transform data-[state=open]:rotate-180" />
    </Accordion.Trigger>
    <Accordion.Content className="overflow-hidden data-[state=closed]:animate-slideUp data-[state=open]:animate-slideDown">
      <div className="px-4 py-3 text-gray-700">
        Content for section 1
      </div>
    </Accordion.Content>
  </Accordion.Item>
  {/* Additional items... */}
</Accordion.Root>
```

## Accessibility

Accordion adheres to the [WAI-ARIA Accordion Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/).

### Keyboard Interactions

- `Space`: When focus is on the `Accordion.Trigger`, opens/closes the corresponding item.
- `Enter`: When focus is on the `Accordion.Trigger`, opens/closes the corresponding item.
- `Tab`: Moves focus to the next focusable element.
- `Shift + Tab`: Moves focus to the previous focusable element.
- `Down Arrow`: When `orientation` is `vertical` and focus is on a `Trigger`, moves focus to the next `Trigger`.
- `Up Arrow`: When `orientation` is `vertical` and focus is on a `Trigger`, moves focus to the previous `Trigger`.
- `Right Arrow`: When `orientation` is `horizontal` and focus is on a `Trigger`, moves focus to the next `Trigger`.
- `Left Arrow`: When `orientation` is `horizontal` and focus is on a `Trigger`, moves focus to the previous `Trigger`.
- `Home`: When focus is on a `Trigger`, moves focus to the first `Trigger`.
- `End`: When focus is on a `Trigger`, moves focus to the last `Trigger`.

## Examples

### Multiple items open

```jsx
<Accordion.Root type="multiple" defaultValue={["item-1", "item-2"]}>
  <Accordion.Item value="item-1">
    <Accordion.Trigger>Section 1</Accordion.Trigger>
    <Accordion.Content>Content 1</Accordion.Content>
  </Accordion.Item>
  <Accordion.Item value="item-2">
    <Accordion.Trigger>Section 2</Accordion.Trigger>
    <Accordion.Content>Content 2</Accordion.Content>
  </Accordion.Item>
</Accordion.Root>
```

### Controlled accordion

```jsx
import { useState } from "react";

function ControlledAccordion() {
  const [value, setValue] = useState("item-1");
  
  return (
    <Accordion.Root 
      type="single" 
      value={value} 
      onValueChange={setValue}
      collapsible
    >
      <Accordion.Item value="item-1">
        <Accordion.Trigger>Section 1</Accordion.Trigger>
        <Accordion.Content>Content 1</Accordion.Content>
      </Accordion.Item>
      <Accordion.Item value="item-2">
        <Accordion.Trigger>Section 2</Accordion.Trigger>
        <Accordion.Content>Content 2</Accordion.Content>
      </Accordion.Item>
    </Accordion.Root>
  );
}
```

### Horizontal orientation

```jsx
<Accordion.Root 
  type="single" 
  orientation="horizontal" 
  defaultValue="item-1"
  className="flex"
>
  <Accordion.Item value="item-1" className="flex">
    <Accordion.Trigger>Section 1</Accordion.Trigger>
    <Accordion.Content>Content 1</Accordion.Content>
  </Accordion.Item>
  <Accordion.Item value="item-2" className="flex">
    <Accordion.Trigger>Section 2</Accordion.Trigger>
    <Accordion.Content>Content 2</Accordion.Content>
  </Accordion.Item>
</Accordion.Root>
```