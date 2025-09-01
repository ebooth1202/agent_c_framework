# Progress Component

## Overview
Displays an indicator showing the completion progress of a task, typically displayed as a progress bar. This component provides assistive technology context about the current progress state.

## Key Features
- Provides accessible progress information for screen readers
- Supports custom value labeling
- Handles complete, indeterminate, and loading states

## Installation
```bash
npm install @radix-ui/react-progress
```

## Component Structure
```jsx
import { Progress } from "radix-ui";

export default () => (
  <Progress.Root>
    <Progress.Indicator />
  </Progress.Root>
);
```

## API Reference

### Root
Contains all of the progress parts.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |
| `value` | number \| null | - | The progress value |
| `max` | number | - | The maximum progress value |
| `getValueLabel` | (value: number, max: number) => string | - | Function to get accessible label text for current value |

**Data Attributes:**
- `[data-state]`: "complete", "indeterminate", or "loading"
- `[data-value]`: Current value
- `[data-max]`: Maximum value

### Indicator
Used to show the progress visually and make it accessible to assistive technologies.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Merges props with child element |

**Data Attributes:**
- `[data-state]`: "complete", "indeterminate", or "loading"
- `[data-value]`: Current value
- `[data-max]`: Maximum value

## Usage Example

### Basic Progress Bar
```jsx
import { Progress } from "radix-ui";
import "./styles.css";

export default () => {
  const [progress, setProgress] = React.useState(13);
  
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(66);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Progress.Root 
      className="ProgressRoot" 
      value={progress} 
      max={100}
    >
      <Progress.Indicator 
        className="ProgressIndicator" 
        style={{ transform: `translateX(-${100 - progress}%)` }} 
      />
    </Progress.Root>
  );
};
```

```css
.ProgressRoot {
  position: relative;
  overflow: hidden;
  background: var(--gray-5);
  border-radius: 99999px;
  width: 300px;
  height: 25px;
}

.ProgressIndicator {
  background-color: var(--blue-9);
  width: 100%;
  height: 100%;
  transition: transform 660ms cubic-bezier(0.65, 0, 0.35, 1);
}
```

### Indeterminate Progress
```jsx
import { Progress } from "radix-ui";
import "./styles.css";

export default () => (
  <Progress.Root className="ProgressRoot">
    <Progress.Indicator className="ProgressIndicator ProgressIndicator--indeterminate" />
  </Progress.Root>
);
```

```css
.ProgressRoot {
  position: relative;
  overflow: hidden;
  background: var(--gray-5);
  border-radius: 99999px;
  width: 300px;
  height: 25px;
}

.ProgressIndicator {
  background-color: var(--blue-9);
  width: 100%;
  height: 100%;
}

.ProgressIndicator--indeterminate {
  animation: indeterminate 1500ms infinite linear;
  transform-origin: 0% 50%;
}

@keyframes indeterminate {
  0% {
    transform: translateX(0%) scaleX(0);
  }
  40% {
    transform: translateX(0%) scaleX(0.4);
  }
  100% {
    transform: translateX(100%) scaleX(0.5);
  }
}
```

### With Custom Label
```jsx
import { Progress } from "radix-ui";
import "./styles.css";

export default () => {
  const [progress, setProgress] = React.useState(13);
  
  return (
    <Progress.Root 
      className="ProgressRoot" 
      value={progress} 
      max={100}
      getValueLabel={(value, max) => `${value} of ${max} tasks completed`}
    >
      <Progress.Indicator 
        className="ProgressIndicator" 
        style={{ transform: `translateX(-${100 - progress}%)` }} 
      />
    </Progress.Root>
  );
};
```

## Accessibility
- Adheres to the `progressbar` role requirements from WAI-ARIA
- Provides proper ARIA attributes for assistive technologies
- Custom value labels can be provided for more descriptive announcements