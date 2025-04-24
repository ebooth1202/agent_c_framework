# Aspect Ratio Component

**Created:** 2025-04-24
**Source:** Radix UI Primitives

## Overview

Aspect Ratio is a utility component that displays content within a desired ratio, maintaining consistent proportions across different viewport sizes.

## Key Features

- Accepts any custom ratio
- Preserves aspect ratio across viewport changes
- Simple implementation for consistent UI proportions

## Installation

```bash
npm install @radix-ui/react-aspect-ratio
```

## Component Anatomy

```jsx
import { AspectRatio } from "radix-ui";

export default () => <AspectRatio.Root />;
```

## API Reference

### Root

Contains the content you want to constrain to a given ratio.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `ratio` | number | 1 | The desired ratio (width/height) |

## Usage Examples

### Image with 16:9 Aspect Ratio

```jsx
import { AspectRatio } from "radix-ui";

export default () => (
  <div style={{ width: '300px', maxWidth: '100%' }}>
    <AspectRatio.Root ratio={16/9}>
      <img
        src="image.jpg"
        alt="Example"
        style={{
          objectFit: 'cover',
          width: '100%',
          height: '100%',
        }}
      />
    </AspectRatio.Root>
  </div>
);
```

### Video Player with 4:3 Aspect Ratio

```jsx
import { AspectRatio } from "radix-ui";

export default () => (
  <div style={{ maxWidth: '400px' }}>
    <AspectRatio.Root ratio={4/3}>
      <video
        src="video.mp4"
        controls
        style={{
          objectFit: 'cover',
          width: '100%',
          height: '100%',
        }}
      />
    </AspectRatio.Root>
  </div>
);
```