# Theme Toggle Visibility Fix Implementation Plan

## Problem Analysis

The theme toggle buttons at the bottom of the sidebar remain visible even when the sidebar is minimized (collapsed into icon-only mode). This creates an inconsistent user experience, as other text elements are hidden in the collapsed state.

## Current Implementation

Currently, the theme toggle is implemented in `ThemeToggle.jsx` and placed within the `SidebarFooter` in `AppSidebar.jsx`. The toggle doesn't respond to the sidebar's collapsed state.

```jsx
// In AppSidebar.jsx
<SidebarFooter>
  <Separator className="my-2" />
  <div className="flex items-center justify-between px-2">
    <p className="text-xs text-muted-foreground sidebar-title">Agent C UI</p>
    <ThemeToggle />
  </div>
</SidebarFooter>
```

The `ThemeToggle` component isn't aware of the sidebar state and doesn't have conditional rendering based on it.

## Solution Approach

1. Pass the sidebar state to the ThemeToggle component
2. Conditionally render a simplified version when the sidebar is collapsed
3. Use CSS classes to handle visibility in different sidebar states

## Implementation Steps

### 1. Update ThemeToggle.jsx to accept sidebar state

```jsx
import React, { useContext } from 'react';
import { Sun, Moon, Laptop } from 'lucide-react';
import { Button } from './button';
import { SessionContext } from '../../contexts/SessionContext';
import { useSidebar } from './sidebar';

export function ThemeToggle({ className }) {
  const { theme, handleThemeChange } = useContext(SessionContext);
  const { state } = useSidebar(); // Get sidebar state
  const isCollapsed = state === 'collapsed';

  // If sidebar is collapsed, render only the active theme icon
  if (isCollapsed) {
    const ActiveIcon = {
      'light': Sun,
      'dark': Moon,
      'system': Laptop
    }[theme] || Sun;
    
    return (
      <div className={`theme-toggle theme-toggle-collapsed ${className}`}>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => {
            // Cycle through themes: light → dark → system → light
            const nextTheme = {
              'light': 'dark',
              'dark': 'system',
              'system': 'light'
            }[theme] || 'light';
            handleThemeChange(nextTheme);
          }}
          title={`Current: ${theme} theme. Click to change.`}
          className="theme-toggle-button-collapsed"
        >
          <ActiveIcon className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Toggle Theme</span>
        </Button>
      </div>
    );
  }

  // Regular expanded sidebar version
  return (
    <div className={`theme-toggle theme-toggle-expanded ${className} flex items-center space-x-1 border dark:border-gray-700 rounded-lg p-0.5 bg-white/10 dark:bg-gray-800/20 backdrop-blur-sm`}>
      <Button
        variant={theme === 'light' ? 'default' : 'secondary'}
        size="icon"
        onClick={() => handleThemeChange('light')}
        title="Light Mode"
        className="hover:bg-amber-100 dark:hover:bg-amber-900/30 hover:text-amber-600 dark:hover:text-amber-400 transition-colors text-gray-700 dark:text-gray-300"
      >
        <Sun className="h-[1.2rem] w-[1.2rem]" />
        <span className="sr-only">Light Mode</span>
      </Button>
      <Button
        variant={theme === 'dark' ? 'default' : 'secondary'}
        size="icon"
        onClick={() => handleThemeChange('dark')}
        title="Dark Mode"
        className="hover:bg-indigo-100 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-gray-700 dark:text-gray-300"
      >
        <Moon className="h-[1.2rem] w-[1.2rem]" />
        <span className="sr-only">Dark Mode</span>
      </Button>
      <Button
        variant={theme === 'system' ? 'default' : 'secondary'}
        size="icon"
        onClick={() => handleThemeChange('system')}
        title="System Theme"
        className="hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-gray-700 dark:text-gray-300"
      >
        <Laptop className="h-[1.2rem] w-[1.2rem]" />
        <span className="sr-only">System Theme</span>
      </Button>
    </div>
  );
}
```

### 2. Update AppSidebar.jsx

This update ensures that the footer elements properly respond to the sidebar state:

```jsx
<SidebarFooter>
  <Separator className="my-2" />
  <div className="flex items-center justify-between px-2">
    <p className="text-xs text-muted-foreground sidebar-title">Agent C UI</p>
    <ThemeToggle />
  </div>
</SidebarFooter>
```

### 3. Add CSS classes for the collapsed state

Create a new file `theme-toggle.css` in the components styles folder:

```css
/* ===== COMPONENT: ThemeToggle ===== */
/* Description: Theme toggle component that adapts to sidebar state */

/* ThemeToggle: Base styles */
.theme-toggle {
  transition: all 0.2s ease-in-out;
}

/* ThemeToggle: Collapsed state */
.theme-toggle-collapsed {
  display: flex;
  justify-content: center;
  width: 100%;
}

/* ThemeToggle: Collapsed button styles */
.theme-toggle-button-collapsed {
  color: hsl(var(--foreground));
  background-color: transparent;
}

.theme-toggle-button-collapsed:hover {
  background-color: hsl(var(--accent) / 0.3);
}

/* Dark mode adjustments */
.dark .theme-toggle-button-collapsed {
  color: hsl(var(--foreground) / 0.9);
}

.dark .theme-toggle-button-collapsed:hover {
  background-color: hsl(var(--accent) / 0.2);
}
```

### 4. Import the CSS in the main styles file

Ensure the new CSS file is imported in the appropriate location.

## Testing Criteria

1. The full theme toggle should be visible when the sidebar is expanded
2. Only a single icon (representing the current theme) should be visible when the sidebar is collapsed
3. Clicking the icon in collapsed mode should cycle through themes
4. The toggle should work correctly in both states
5. Verify proper behavior when switching between expanded and collapsed states
6. Test in light and dark modes

## Fallback Plan

If the conditional rendering approach causes any issues:

1. Use CSS-only approach to hide/show elements based on sidebar state
2. Simplify by just hiding the theme toggle completely in collapsed state (though this reduces functionality)