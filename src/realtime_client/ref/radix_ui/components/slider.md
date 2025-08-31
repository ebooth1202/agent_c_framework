# Slider Component

**Purpose**: An input where the user selects a value from within a given range.

## Key Features

- Can be controlled or uncontrolled
- Supports multiple thumbs for range selection
- Supports minimum distance between thumbs
- Allows touch or click on track to update value
- Supports vertical and horizontal orientations
- Supports Right to Left direction
- Full keyboard navigation

## Installation

```bash
npm install @radix-ui/react-slider
```

## Component Anatomy

```jsx
import { Slider } from "radix-ui";

export default () => (
	<Slider.Root>
		<Slider.Track>
			<Slider.Range />
		</Slider.Track>
		<Slider.Thumb />
	</Slider.Root>
);
```

## API Reference

### Root

Contains all parts of a slider. Renders an `input` for each thumb when used within a form.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element
- `defaultValue` (number[]) - Initial value when uncontrolled
- `value` (number[]) - Controlled value, use with `onValueChange`
- `onValueChange` (function) - Handler when value changes during interaction
- `onValueCommit` (function) - Handler when value changes at the end of interaction
- `name` (string) - Form input name
- `disabled` (boolean, default: false) - Prevents user interaction
- `orientation` ("horizontal" | "vertical", default: "horizontal") - Slider orientation
- `dir` ("ltr" | "rtl") - Reading direction
- `inverted` (boolean, default: false) - Whether visually inverted
- `min` (number, default: 0) - Minimum value
- `max` (number, default: 100) - Maximum value
- `step` (number, default: 1) - Stepping interval
- `minStepsBetweenThumbs` (number, default: 0) - Minimum steps between multiple thumbs
- `form` (string) - Form ID to associate with

**Data Attributes:**
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

### Track

The track that contains the Slider.Range.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

### Range

The filled part of the track. Must be inside Slider.Track.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

### Thumb

A draggable thumb. Multiple thumbs can be rendered for range selection.

**Props:**
- `asChild` (boolean, default: false) - Merge props with child element

**Data Attributes:**
- `[data-disabled]`: Present when disabled
- `[data-orientation]`: "vertical" | "horizontal"

## Implementation Examples

### Vertical Orientation

```jsx
<Slider.Root
  defaultValue={[50]}
  orientation="vertical"
>
  <Slider.Track>
    <Slider.Range />
  </Slider.Track>
  <Slider.Thumb />
</Slider.Root>
```

### Range Slider

```jsx
<Slider.Root defaultValue={[25, 75]}>
  <Slider.Track>
    <Slider.Range />
  </Slider.Track>
  <Slider.Thumb />
  <Slider.Thumb />
</Slider.Root>
```

### Custom Step Size

```jsx
<Slider.Root defaultValue={[50]} step={10}>
  <Slider.Track>
    <Slider.Range />
  </Slider.Track>
  <Slider.Thumb />
</Slider.Root>
```

### Prevent Thumb Overlap

```jsx
<Slider.Root defaultValue={[25, 75]} step={10} minStepsBetweenThumbs={1}>
  <Slider.Track>
    <Slider.Range />
  </Slider.Track>
  <Slider.Thumb />
  <Slider.Thumb />
</Slider.Root>
```

## Accessibility

Adheres to the [Slider WAI-ARIA design pattern](https://www.w3.org/WAI/ARIA/apg/patterns/slider-multithumb).

### Keyboard Interactions

- **Arrow Right/Left**: Increment/decrement by step value (direction depends on orientation)
- **Arrow Up**: Increase value by step amount
- **Arrow Down**: Decrease value by step amount
- **Page Up**: Increase value by larger step
- **Page Down**: Decrease value by larger step
- **Shift + Arrow Up**: Increase value by larger step
- **Shift + Arrow Down**: Decrease value by larger step
- **Home**: Set value to minimum
- **End**: Set value to maximum

## Caveats

**Mouse Events**: Due to implementation limitations, mouse events (`onMouseDown`, `onMouseUp`) don't fire on the Root component. Use pointer events (`onPointerDown`, `onPointerUp`) instead, which work better across all devices anyway.