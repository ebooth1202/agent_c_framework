# Avatar

**Created:** April 24, 2025  
**Source:** avatar.mdx

## Description

An image element with a fallback for representing the user. The avatar component displays a user's profile picture with a text fallback when the image isn't available.

## Installation

### CLI Installation

```bash
npx shadcn@latest add avatar
```

### Manual Installation

1. Install the required dependencies:

```bash
npm install @radix-ui/react-avatar
```

2. Copy the component code to your project's component directory
3. Update import paths to match your project structure

## Usage

### Import Statement

```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
```

### Basic Example

```tsx
<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
```

## Component Structure

- `Avatar`: The root container component
- `AvatarImage`: The image component that displays the user's picture
- `AvatarFallback`: Renders when the image fails to load, typically showing initials or an icon

## Common Use Cases

- User profile pictures in headers, comments, or user lists
- Team member displays
- Chat or messaging interfaces
- Author attribution in content

## Accessibility

Ensure the `AvatarImage` component has an appropriate `alt` attribute for screen readers when the image represents meaningful content.