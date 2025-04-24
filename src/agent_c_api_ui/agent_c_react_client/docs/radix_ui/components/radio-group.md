# RadioGroup Component

## Overview
A set of checkable buttons—known as radio buttons—where no more than one of the buttons can be checked at a time. This component follows the WAI-ARIA Radio Group pattern and manages keyboard navigation and selection states.

## Key Features
- Full keyboard navigation with arrow keys
- Supports horizontal and vertical orientation
- Can be controlled or uncontrolled
- Implements roving tabindex for proper focus management
- Form-compatible for submission

## Installation
```bash
npm install @radix-ui/react-radio-group
```

## Component Structure
```jsx
import { RadioGroup } from "radix-ui";

export default () => (
  <RadioGroup.Root>
    <RadioGroup.Item>
      <RadioGroup.Indicator />
    </RadioGroup.Item>
  </RadioGroup.Root>
);
```

## API Reference

### Root
Contains all the parts of a radio group.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `defaultValue` | string | - | Initial checked value (uncontrolled) |
| `value` | string | - | Controlled checked value |
| `onValueChange` | (value: string) => void | - | Event handler for value changes |
| `disabled` | boolean | - | When true, prevents interaction with all items |
| `name` | string | - | Form name for the radio group |
| `required` | boolean | - | When true, requires a selection before form submission |
| `orientation` | "horizontal" \| "vertical" | - | Orientation of the component |
| `dir` | "ltr" \| "rtl" | - | Reading direction of the radio group |
| `loop` | boolean | true | Whether keyboard navigation should loop from last to first |

**Data Attributes:**
- `[data-disabled]`: Present when disabled

### Item
An individual radio button that can be checked.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `value` | string | - | The value for this item when selected |
| `disabled` | boolean | - | When true, prevents interaction with this item |
| `required` | boolean | - | When true, requires selection before form submission |

**Data Attributes:**
- `[data-state]`: "checked" or "unchecked"
- `[data-disabled]`: Present when disabled

### Indicator
Renders when the radio item is checked. Can be styled directly or used as a wrapper for an icon.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `forceMount` | boolean | - | Forces mounting for animation control |

**Data Attributes:**
- `[data-state]`: "checked" or "unchecked"
- `[data-disabled]`: Present when disabled

## Usage Examples

### Basic Radio Group
```jsx
import { RadioGroup } from "radix-ui";
import "./styles.css";

export default () => (
  <form>
    <RadioGroup.Root 
      className="RadioGroupRoot" 
      defaultValue="default"
      aria-label="View density"
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <RadioGroup.Item className="RadioGroupItem" value="default" id="r1">
          <RadioGroup.Indicator className="RadioGroupIndicator" />
        </RadioGroup.Item>
        <label className="Label" htmlFor="r1">Default</label>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <RadioGroup.Item className="RadioGroupItem" value="comfortable" id="r2">
          <RadioGroup.Indicator className="RadioGroupIndicator" />
        </RadioGroup.Item>
        <label className="Label" htmlFor="r2">Comfortable</label>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <RadioGroup.Item className="RadioGroupItem" value="compact" id="r3">
          <RadioGroup.Indicator className="RadioGroupIndicator" />
        </RadioGroup.Item>
        <label className="Label" htmlFor="r3">Compact</label>
      </div>
    </RadioGroup.Root>
  </form>
);
```

```css
.RadioGroupRoot {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.RadioGroupItem {
  background-color: white;
  width: 25px;
  height: 25px;
  border-radius: 100%;
  box-shadow: 0 2px 10px var(--blackA7);
}

.RadioGroupItem:hover {
  background-color: var(--violet3);
}

.RadioGroupItem:focus {
  box-shadow: 0 0 0 2px black;
}

.RadioGroupIndicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: relative;
}

.RadioGroupIndicator::after {
  content: '';
  display: block;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background-color: var(--violet11);
}

.Label {
  color: white;
  font-size: 15px;
  line-height: 1;
  padding-left: 15px;
}
```

### Horizontal Orientation
```jsx
import { RadioGroup } from "radix-ui";

export default () => (
  <RadioGroup.Root 
    className="RadioGroupRoot" 
    defaultValue="default"
    orientation="horizontal"
    aria-label="View density"
  >
    {/* Radio items */}
  </RadioGroup.Root>
);
```

### Controlled Value
```jsx
import React from 'react';
import { RadioGroup } from "radix-ui";

export default () => {
  const [value, setValue] = React.useState('default');
  
  return (
    <RadioGroup.Root 
      className="RadioGroupRoot" 
      value={value}
      onValueChange={setValue}
      aria-label="View density"
    >
      {/* Radio items */}
    </RadioGroup.Root>
  );
};
```

## Accessibility

- Adheres to the [Radio Group WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/radio)
- Uses roving tabindex to manage focus movement among radio items
- Keyboard navigation follows established patterns for radio groups

### Keyboard Interactions

| Key | Action |
| --- | ------ |
| Tab | Moves focus to either the checked radio item or the first radio item |
| Space | When focus is on an unchecked radio item, checks it |
| ArrowDown | Moves focus and checks the next radio item |
| ArrowRight | Moves focus and checks the next radio item |
| ArrowUp | Moves focus and checks the previous radio item |
| ArrowLeft | Moves focus and checks the previous radio item |