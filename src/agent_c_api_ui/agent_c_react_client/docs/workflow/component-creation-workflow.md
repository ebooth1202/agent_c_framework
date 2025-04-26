# Component Creation Workflow

## Overview

This document outlines the standardized workflow for creating new components in the Agent C React UI. Following these steps ensures consistency, maintainability, and proper integration with the existing component architecture.

## Contents
- [Component Planning](#component-planning)
- [Component Creation Steps](#component-creation-steps)
- [shadcn/ui Integration](#shadcnui-integration)
- [Component Testing](#component-testing)
- [Examples](#examples)

## Component Planning

Before creating a new component, consider the following:

### Component Purpose and Responsibility

1. **Single Responsibility**: Each component should have a clearly defined purpose
2. **Component Type**: Determine if the component is:
   - UI component (pure presentation)
   - Container component (with state/logic)
   - Layout component
   - Feature-specific component

### Component Hierarchy

1. **Parent/Child Relationships**: Where does this component fit in the component hierarchy?
2. **Composition**: Will this component be composed of other components?
3. **Context Requirements**: Does this component need access to context providers?

### State Management

1. **Local State**: What state should be maintained within the component?
2. **Props Interface**: What props should the component accept?
3. **Context Usage**: Should the component consume context?

## Component Creation Steps

Follow these steps to create a new component:

### 1. Create Component Files

Create the following files for your component:

```
src/components/[feature_area]/[ComponentName].jsx
src/styles/components/[component-name].css
```

For example, for a new `UserBadge` component in the chat interface:

```
src/components/chat_interface/UserBadge.jsx
src/styles/components/user-badge.css
```

### 2. Set Up Component Structure

Use this template for your component file:

```jsx
import React from 'react';

/**
 * UserBadge - Displays user information in a compact badge format
 * 
 * @param {Object} props
 * @param {string} props.username - User's display name
 * @param {string} props.avatarUrl - URL to user's avatar image
 * @param {string} props.status - User's status (online, offline, etc.)
 * @param {React.ReactNode} props.children - Optional children elements
 */
const UserBadge = ({ username, avatarUrl, status, children }) => {
  return (
    <div className="user-badge">
      {avatarUrl && (
        <div className="user-badge-avatar">
          <img src={avatarUrl} alt={username} />
        </div>
      )}
      
      <div className="user-badge-content">
        <div className="user-badge-username">{username}</div>
        {status && <div className="user-badge-status">{status}</div>}
        {children}
      </div>
    </div>
  );
};

export default UserBadge;
```

### 3. Create CSS File

Use this template for your CSS file:

```css
/* ===== COMPONENT: UserBadge ===== */
/* Description: Displays user information in a compact badge format */

/* UserBadge: Container */
.user-badge {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius);
  background-color: hsl(var(--muted));
}

/* UserBadge: Avatar */
.user-badge-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
}

.user-badge-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* UserBadge: Content */
.user-badge-content {
  display: flex;
  flex-direction: column;
}

.user-badge-username {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  color: hsl(var(--foreground));
}

.user-badge-status {
  font-size: var(--font-size-xs);
  color: hsl(var(--muted-foreground));
}
```

### 4. Import CSS into Component Styles

Add your component's CSS file to `src/styles/component-styles.css`:

```css
@import './components/user-badge.css';
```

### 5. Create Component Exports

If creating a set of related components, consider creating an index file for cleaner imports:

```jsx
// src/components/chat_interface/user/index.js
export { default as UserBadge } from './UserBadge';
export { default as UserCard } from './UserCard';
```

## shadcn/ui Integration

When creating components that use shadcn/ui:

### 1. Install Required shadcn/ui Components

Install any needed shadcn/ui components:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add avatar
```

### 2. Import and Use shadcn/ui Components

```jsx
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

const UserBadge = ({ username, avatarUrl, status, onLogout }) => {
  return (
    <div className="user-badge">
      <Avatar>
        <AvatarImage src={avatarUrl} alt={username} />
        <AvatarFallback>{username.charAt(0)}</AvatarFallback>
      </Avatar>
      
      <div className="user-badge-content">
        <div className="user-badge-username">{username}</div>
        {status && <div className="user-badge-status">{status}</div>}
      </div>
      
      <Button variant="ghost" size="sm" onClick={onLogout}>
        Logout
      </Button>
    </div>
  );
};
```

### 3. Extend shadcn/ui Components

To extend shadcn/ui components with custom styles:

```jsx
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const IconButton = React.forwardRef(({ className, icon, children, ...props }, ref) => (
  <Button
    ref={ref}
    className={cn("flex items-center gap-2", className)}
    {...props}
  >
    {icon}
    {children}
  </Button>
));
IconButton.displayName = "IconButton";

export { IconButton };
```

## Component Testing

Test your components to ensure they function correctly:

### 1. Manual Testing

- Test the component in isolation
- Test the component in context with its parent components
- Test with different props and states
- Test accessibility with keyboard navigation

### 2. Cross-Browser Testing

- Verify the component works in Chrome, Firefox, Safari, and Edge
- Check for layout issues or CSS incompatibilities

### 3. Responsive Testing

- Test at different viewport sizes
- Verify that the component adapts appropriately on mobile devices

## Examples

### Simple UI Component

```jsx
// src/components/ui/badge-button.jsx
import React from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * BadgeButton - A button with an attached badge counter
 */
const BadgeButton = React.forwardRef(({ 
  className, 
  count, 
  children, 
  badgeVariant = "default", 
  ...props 
}, ref) => (
  <div className="badge-button-container">
    <Button
      ref={ref}
      className={cn("badge-button", className)}
      {...props}
    >
      {children}
    </Button>
    {count > 0 && (
      <Badge variant={badgeVariant} className="badge-button-badge">
        {count}
      </Badge>
    )}
  </div>
));
BadgeButton.displayName = "BadgeButton";

export { BadgeButton };
```

```css
/* ===== COMPONENT: BadgeButton ===== */
/* Description: A button with an attached badge counter */

/* BadgeButton: Container */
.badge-button-container {
  position: relative;
  display: inline-block;
}

/* BadgeButton: Badge */
.badge-button-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: var(--font-size-xs);
  min-width: 20px;
  height: 20px;
  padding: 0 var(--space-1);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Feature Component

```jsx
// src/components/chat_interface/TypeIndicator.jsx
import React, { useEffect, useState } from 'react';
import { AnimatedDots } from "@/components/ui/animated-dots";

/**
 * TypeIndicator - Shows when the assistant is typing
 */
const TypeIndicator = ({ isTyping, typingText = "Assistant is typing" }) => {
  const [visible, setVisible] = useState(false);
  
  useEffect(() => {
    if (isTyping) {
      // Small delay before showing typing indicator
      const timer = setTimeout(() => setVisible(true), 500);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [isTyping]);
  
  if (!visible) return null;
  
  return (
    <div className="type-indicator">
      <div className="type-indicator-text">
        {typingText}
        <AnimatedDots />
      </div>
    </div>
  );
};

export default TypeIndicator;
```

```css
/* ===== COMPONENT: TypeIndicator ===== */
/* Description: Shows when the assistant is typing */

/* TypeIndicator: Container */
.type-indicator {
  padding: var(--space-2) var(--space-4);
  margin: var(--space-2) 0;
  border-radius: var(--radius);
  background-color: hsl(var(--muted));
  animation: fade-in 200ms ease-out;
}

/* TypeIndicator: Text */
.type-indicator-text {
  font-size: var(--font-size-sm);
  color: hsl(var(--muted-foreground));
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## Related Documentation

- [shadcn/ui Integration Guide](./shadcn-ui-integration.md)
- [Component Organization](../project/component-organization.md)
- [CSS Organization](../style/css-organization.md)