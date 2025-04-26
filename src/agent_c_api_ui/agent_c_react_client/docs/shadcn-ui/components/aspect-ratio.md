# Aspect Ratio

**Created:** April 24, 2025  
**Source:** aspect-ratio.mdx

## Description

Displays content within a desired ratio, ensuring elements like images maintain a consistent proportional size regardless of their container width.

## Installation

### CLI Installation

```bash
npx shadcn@latest add aspect-ratio
```

### Manual Installation

1. Install the required dependencies:

```bash
npm install @radix-ui/react-aspect-ratio
```

2. Copy the component code to your project's component directory
3. Update import paths to match your project structure

## Usage

### Import Statement

```tsx
import Image from "next/image"
import { AspectRatio } from "@/components/ui/aspect-ratio"
```

### Basic Example

```tsx
<div className="w-[450px]">
  <AspectRatio ratio={16 / 9}>
    <Image src="..." alt="Image" className="rounded-md object-cover" />
  </AspectRatio>
</div>
```

## Component Properties

- `ratio`: Number specifying the aspect ratio (width/height). In the example above, 16/9 creates a 16:9 aspect ratio.

## Use Cases

- Maintaining consistent image ratios in responsive layouts
- Creating uniform cards or media containers
- Preventing layout shifts when loading images or media
- Implementing responsive video embeds