# Navigation Menu Component

**Purpose:** Provides a collection of links for website navigation with support for dropdown content, flexible layouts, and full keyboard navigation.

## Basic Usage

```jsx
import { NavigationMenu } from "radix-ui";

export default () => (
  <NavigationMenu.Root>
    <NavigationMenu.List>
      <NavigationMenu.Item>
        <NavigationMenu.Link href="/home" active>
          Home
        </NavigationMenu.Link>
      </NavigationMenu.Item>
      
      <NavigationMenu.Item>
        <NavigationMenu.Trigger>Products</NavigationMenu.Trigger>
        <NavigationMenu.Content>
          <ul>
            <li>
              <NavigationMenu.Link href="/products/1">Product 1</NavigationMenu.Link>
            </li>
            <li>
              <NavigationMenu.Link href="/products/2">Product 2</NavigationMenu.Link>
            </li>
          </ul>
        </NavigationMenu.Content>
      </NavigationMenu.Item>
    </NavigationMenu.List>
    
    <NavigationMenu.Viewport />
  </NavigationMenu.Root>
);
```

## Key Features
- Can be controlled or uncontrolled
- Flexible layout structure with managed tab focus
- Support for submenus
- Optional active item indicator
- Full keyboard navigation
- Customizable open/close timing
- Exposed CSS variables for advanced animations

## Component API

### NavigationMenu.Root

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `defaultValue` | string | - | Default active menu item (uncontrolled) |
| `value` | string | - | Controlled active menu item value |
| `onValueChange` | (value: string) => void | - | Active value change handler |
| `delayDuration` | number | 200 | Hover delay before opening content (ms) |
| `skipDelayDuration` | number | 300 | Time to skip delay when moving between triggers |
| `dir` | "ltr" \| "rtl" | - | Reading direction |
| `orientation` | "horizontal" \| "vertical" | "horizontal" | Menu orientation |

**Data Attributes:** `[data-orientation]`: "vertical" or "horizontal"

### NavigationMenu.Sub

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `defaultValue` | string | - | Default active submenu item (uncontrolled) |
| `value` | string | - | Controlled active submenu item value |
| `onValueChange` | (value: string) => void | - | Active submenu value change handler |
| `orientation` | "horizontal" \| "vertical" | "horizontal" | Submenu orientation |

**Data Attributes:** Same as Root

### NavigationMenu.List

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

**Data Attributes:** `[data-orientation]`: "vertical" or "horizontal"

### NavigationMenu.Item

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `value` | string | - | Unique identifier for item |

### NavigationMenu.Trigger

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |

**Data Attributes:** 
- `[data-state]`: "open" or "closed" 
- `[data-disabled]`: Present when disabled

### NavigationMenu.Content

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `onEscapeKeyDown` | (event: KeyboardEvent) => void | - | Escape key handler |
| `onPointerDownOutside` | (event: PointerDownOutsideEvent) => void | - | Pointer outside handler |
| `onFocusOutside` | (event: FocusOutsideEvent) => void | - | Focus outside handler |
| `onInteractOutside` | (event: React.FocusEvent \| MouseEvent \| TouchEvent) => void | - | Interaction outside handler |
| `forceMount` | boolean | - | Force content mounting |

**Data Attributes:**
- `[data-state]`: "open" or "closed"
- `[data-motion]`: "to-start", "to-end", "from-start", "from-end"
- `[data-orientation]`: "vertical" or "horizontal"

### NavigationMenu.Link

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `active` | boolean | false | Mark link as currently active page |
| `onSelect` | (event: Event) => void | - | Selection handler |

**Data Attributes:** `[data-active]`: Present when active

### NavigationMenu.Indicator

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `forceMount` | boolean | - | Force indicator mounting |

**Data Attributes:**
- `[data-state]`: "visible" or "hidden"
- `[data-orientation]`: "vertical" or "horizontal"

### NavigationMenu.Viewport

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `asChild` | boolean | false | Use child as rendered element |
| `forceMount` | boolean | - | Force viewport mounting |

**Data Attributes:**
- `[data-state]`: "open" or "closed"
- `[data-orientation]`: "vertical" or "horizontal"

**CSS Variables:**
- `--radix-navigation-menu-viewport-width`: Viewport width when visible/hidden
- `--radix-navigation-menu-viewport-height`: Viewport height when visible/hidden

## Common Patterns

### Vertical Orientation
```jsx
<NavigationMenu.Root orientation="vertical">
  {/* components */}
</NavigationMenu.Root>
```

### With Active Indicator
```jsx
// JSX
<NavigationMenu.List>
  {/* menu items */}
  <NavigationMenu.Indicator className="NavigationMenuIndicator" />
</NavigationMenu.List>

// CSS
.NavigationMenuIndicator {
  background-color: grey;
}
.NavigationMenuIndicator[data-orientation="horizontal"] {
  height: 3px;
  transition: width, transform, 250ms ease;
}
```

### With Submenus
```jsx
<NavigationMenu.Root>
  <NavigationMenu.List>
    <NavigationMenu.Item>
      <NavigationMenu.Trigger>Parent Item</NavigationMenu.Trigger>
      <NavigationMenu.Content>
        <NavigationMenu.Sub defaultValue="sub1">
          <NavigationMenu.List>
            <NavigationMenu.Item value="sub1">
              <NavigationMenu.Trigger>Submenu Item 1</NavigationMenu.Trigger>
              <NavigationMenu.Content>Content 1</NavigationMenu.Content>
            </NavigationMenu.Item>
            <NavigationMenu.Item value="sub2">
              <NavigationMenu.Trigger>Submenu Item 2</NavigationMenu.Trigger>
              <NavigationMenu.Content>Content 2</NavigationMenu.Content>
            </NavigationMenu.Item>
          </NavigationMenu.List>
        </NavigationMenu.Sub>
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  </NavigationMenu.List>
</NavigationMenu.Root>
```

### With Client-Side Routing
```jsx
// Custom Link component
const Link = ({ href, ...props }) => {
  const pathname = usePathname();
  const isActive = href === pathname;
  
  return (
    <NavigationMenu.Link asChild active={isActive}>
      <NextLink href={href} {...props} />
    </NavigationMenu.Link>
  );
};

// Usage
<NavigationMenu.Item>
  <Link href="/about">About</Link>
</NavigationMenu.Item>
```

### Advanced Animation
```css
/* Position content for animation */
.NavigationMenuContent {
  position: absolute;
  top: 0;
  left: 0;
  animation-duration: 250ms;
}

/* Use data-motion for direction-aware animations */
.NavigationMenuContent[data-motion="from-start"] {
  animation-name: enterFromLeft;
}
.NavigationMenuContent[data-motion="from-end"] {
  animation-name: enterFromRight;
}

/* Animate viewport size */
.NavigationMenuViewport {
  position: relative;
  width: var(--radix-navigation-menu-viewport-width);
  height: var(--radix-navigation-menu-viewport-height);
  transition: width, height, 250ms ease;
}
```

## Accessibility Notes
- Adheres to the `navigation` role requirements
- Use NavigationMenu.Link for all navigation links (including within content)
- Not to be confused with application menubar controls
- Supports keyboard navigation:
  - Tab: Move through focusable elements
  - Arrow keys: Navigate menu items
  - Space/Enter: Open/select items
  - Escape: Close and return to trigger