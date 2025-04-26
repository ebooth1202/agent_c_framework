# Skeleton Component

*Created: May 2, 2023 from skeleton.mdx*

## Overview
A skeleton component used to show a placeholder while content is loading. It provides visual feedback to users during data fetching or processing operations.

## Key Features
- Visual placeholder for loading states
- Customizable dimensions and shape
- Simple implementation with minimal dependencies
- Helps maintain layout stability during loading
- Reduces perceived loading time

## Installation

### CLI Installation
```bash
npx shadcn@latest add skeleton
```

### Manual Installation
1. Copy the component code into your project
2. Import the component:
```tsx
import { Skeleton } from "@/components/ui/skeleton"
```

## Component Structure
The Skeleton component is a simple div with pulsing animation styles applied. Its appearance can be customized through className props to match the dimensions and shape of the content being loaded.

## Usage

### Basic Usage
```tsx
<Skeleton className="w-[100px] h-[20px] rounded-full" />
```

### Card Loading State Example
```tsx
<div className="flex flex-col space-y-3">
  <Skeleton className="h-[125px] w-[250px] rounded-xl" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

### Profile Loading Example
```tsx
<div className="flex items-center space-x-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

## Common Use Cases
- User profile placeholders
- Card layouts during content loading
- Table rows while data is being fetched
- Image placeholders
- Text content placeholders
- Form field placeholders during auto-fill
- Dashboard widget loading states

## Accessibility
- Should be replaced with actual content as soon as it's available
- Consider adding appropriate ARIA attributes when using in complex loading scenarios
- Use in conjunction with proper loading announcements for screen readers