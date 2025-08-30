# Avatar Component

**Created:** 2025-04-24
**Source:** Radix UI Primitives

## Overview

Avatar is an image element with a fallback for representing the user. It handles loading states and provides a customizable fallback option.

## Key Features

- Automatic and manual control over when the image renders
- Fallback part accepts any children for custom placeholder content
- Optional delay for fallback rendering to avoid content flashing
- Composable with other components like Tooltip

## Installation

```bash
npm install @radix-ui/react-avatar
```

## Component Anatomy

```jsx
import { Avatar } from "radix-ui";

export default () => (
  <Avatar.Root>
    <Avatar.Image />
    <Avatar.Fallback />
  </Avatar.Root>
);
```

## API Reference

### Root

Container for all avatar parts.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |

### Image

The image to render. By default it only renders when loaded.

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `onLoadingStatusChange` | (status: "idle" \| "loading" \| "loaded" \| "error") => void | - | Callback for image loading status changes |

### Fallback

Element that renders when the image hasn't loaded (during loading or on error).

| Prop | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `asChild` | boolean | false | Use child as rendering root |
| `delayMs` | number | - | Delay rendering to avoid flashing for fast connections |

## Usage Examples

### Basic Avatar with Initials Fallback

```jsx
import { Avatar } from "radix-ui";

export default () => (
  <Avatar.Root className="AvatarRoot">
    <Avatar.Image
      className="AvatarImage"
      src="https://example.com/user-avatar.jpg"
      alt="User name"
    />
    <Avatar.Fallback className="AvatarFallback" delayMs={600}>
      JD
    </Avatar.Fallback>
  </Avatar.Root>
);
```

### Clickable Avatar with Tooltip

```jsx
import { Avatar, Tooltip } from "radix-ui";

export default () => (
  <Tooltip.Root>
    <Tooltip.Trigger>
      <Avatar.Root className="AvatarRoot">
        <Avatar.Image
          className="AvatarImage"
          src="https://example.com/user-avatar.jpg"
          alt="User name"
        />
        <Avatar.Fallback className="AvatarFallback">
          JD
        </Avatar.Fallback>
      </Avatar.Root>
    </Tooltip.Trigger>

    <Tooltip.Content side="top">
      John Doe
      <Tooltip.Arrow />
    </Tooltip.Content>
  </Tooltip.Root>
);
```

### With Custom Loading Status Control

```jsx
import { Avatar } from "radix-ui";
import { useState } from "react";

export default () => {
  const [status, setStatus] = useState("idle");
  
  return (
    <div>
      <div>Status: {status}</div>
      <Avatar.Root>
        <Avatar.Image
          src="https://example.com/user-avatar.jpg"
          onLoadingStatusChange={setStatus}
        />
        <Avatar.Fallback>
          {status === "loading" ? "Loading..." : "User"}
        </Avatar.Fallback>
      </Avatar.Root>
    </div>
  );
};
```