# CSS Common Patterns Documentation

This document provides detailed information about the common CSS patterns used throughout the Agent C React UI. These patterns provide consistent styling and functionality across all components.

## Table of Contents

1. [Badges](#badges)
2. [Cards](#cards)
3. [Interactive Elements](#interactive-elements)
4. [Layout](#layout)
5. [Reset](#reset)
6. [Tooltips](#tooltips)
7. [Typography](#typography)
8. [Utilities](#utilities)
9. [Variables](#variables)

## Badges

**File:** `styles/common/badges.css`

Provides standard badge components for statuses, labels, and indicators.

### Base Badge

```css
.badge { /* styling properties */ }
```

The base badge class provides default styling for all badge variants including flex display, alignment, border, padding, and font properties.

### Badge Variants

- **Primary**: `.badge-primary` - Blue-themed badges for primary information
- **Success**: `.badge-success` - Green-themed badges for success states
- **Warning**: `.badge-warning` - Amber-themed badges for warnings
- **Info**: `.badge-info` - Purple-themed badges for informational content
- **Disabled**: `.badge-disabled` - Gray-themed badges for disabled states

### Usage Example

```html
<span class="badge badge-success">Completed</span>
```

### Dark Mode Support

Each badge variant includes dark mode styles that automatically apply when the `.dark` class is present on an ancestor element.

---

## Cards

**File:** `styles/common/cards.css`

Provides card components for grouping related content visually.

### Base Card

```css
.card { /* styling properties */ }
```

The basic card component with background, border radius, border, and padding.

### Card Variants

- **Interactive Card**: `.card-interactive` - Cards with hover effects
- **Info Card**: `.info-card` - Used for tooltips and popovers
- **Card With Hover Reveal**: `.card-with-hover-reveal` - Cards with elements that appear on hover

### Card Structure Components

- **Card Header**: `.card-header` - Top section of a card, usually containing a title
- **Card Footer**: `.card-footer` - Bottom section of a card, usually containing actions

### Usage Example

```html
<div class="card">
  <div class="card-header">Card Title</div>
  <p>Card content goes here...</p>
  <div class="card-footer">Card actions</div>
</div>
```

### Dark Mode Support

Cards include dark mode variants that automatically apply when the `.dark` class is present on an ancestor element.

---

## Interactive Elements

**File:** `styles/common/interactive.css`

Provides styling for buttons, links, and other interactive UI elements.

### Base Interactive Element

```css
.interactive { /* styling properties */ }
```

Provides hover transition effect and cursor pointer for interactive elements.

### Interactive Element Variants

- **Copy Button**: `.copy-button` - Standardized button for copy functionality
- **Icon Button**: `.icon-button` - Button that primarily displays an icon
- **Hover Reveal Container**: `.hover-reveal-container` - Container where child elements appear on hover

### Usage Example

```html
<button class="copy-button">Copy</button>

<div class="hover-reveal-container">
  <div>Always visible content</div>
  <div class="hover-reveal">Appears on hover</div>
</div>
```

### Dark Mode Support

Interactive elements include dark mode variants for consistent appearance in both light and dark themes.

---

## Layout

**File:** `styles/common/layout.css`

Provides utility classes for common layout patterns and spacing.

### Flexbox Utilities

- **Flex Container**: `.flex` - Sets display: flex
- **Direction**: `.flex-col`, `.flex-row` - Sets flex direction
- **Alignment**: `.items-center`, `.items-start`, `.items-end` - Aligns items on cross axis
- **Justification**: `.justify-center`, `.justify-between`, etc. - Aligns items on main axis
- **Wrapping**: `.flex-wrap`, `.flex-nowrap` - Controls flex wrapping behavior
- **Spacing**: `.gap-1`, `.gap-2`, etc. - Sets gap between flex items
- **Growth**: `.flex-1`, `.flex-grow`, `.flex-shrink-0` - Controls how items grow/shrink

### Grid Utilities

- **Grid Container**: `.grid` - Sets display: grid
- **Columns**: `.grid-cols-1`, `.grid-cols-2`, etc. - Sets grid template columns

### Spacing Utilities

- **Padding**: `.p-1`, `.p-2`, etc. - Sets padding on all sides
- **Horizontal Padding**: `.px-1`, `.px-2`, etc. - Sets left and right padding
- **Vertical Padding**: `.py-1`, `.py-2`, etc. - Sets top and bottom padding
- **Margin**: `.m-1`, `.m-2`, etc. - Sets margin on all sides
- **Auto Margins**: `.mx-auto`, `.my-auto` - Centers elements horizontally or vertically

### Dimension Utilities

- **Width**: `.w-full` - 100% width
- **Height**: `.h-full` - 100% height
- **Min Height**: `.min-h-screen` - Minimum height of 100vh

### Position Utilities

- **Position Types**: `.relative`, `.absolute`, `.fixed`, `.sticky`
- **Positioning**: `.top-0`, `.right-0`, `.bottom-0`, `.left-0`, `.inset-0`

### Container

- `.container` - Standard container with responsive max-width at different breakpoints

### Usage Example

```html
<div class="flex items-center justify-between gap-2 p-2">
  <div>Left Content</div>
  <div>Right Content</div>
</div>
```

---

## Reset

**File:** `styles/common/reset.css`

Provides CSS reset and base styles to normalize rendering across browsers.

### Features

- Removes default margins, paddings, and borders
- Standardizes box-sizing
- Normalizes font rendering
- Sets base font family and size
- Standardizes form elements

---

## Tooltips

**File:** `styles/common/tooltips.css`

Provides styling for tooltips, popovers, and hover cards.

### Base Tooltip

```css
.tooltip { /* styling properties */ }
```

Provides styling for small tooltip components that appear on hover or focus.

### Popover

```css
.popover { /* styling properties */ }
```

Larger tooltip-like components that can contain more complex content.

### Animations

- **Popover Animation**: `.popover-animated` - Adds an entry animation for popovers

### Usage Example

```html
<div class="tooltip">This is a tooltip</div>

<div class="popover popover-animated">
  <div class="p-2">Popover content goes here</div>
</div>
```

### Dark Mode Support

Tooltips and popovers include dark mode variants for consistent appearance in both themes.

---

## Typography

**File:** `styles/common/typography.css`

Provides typography styles for consistent text rendering throughout the application.

### Headings

- **H1 - H6**: Semantic heading styles
- **.h1 - .h6**: Classes to apply heading styles to non-heading elements

### Text Sizes

- **.text-base**: Base font size (16px)
- **.text-sm**: Small text (14px)
- **.text-xs**: Extra small text (12px)
- **.text-lg**: Large text (18px)
- **.text-xl**: Extra large text (20px)

### Text Colors

- **.text-primary**: Primary text color
- **.text-secondary**: Secondary text color
- **.text-accent**: Accent text color
- **.text-muted**: Reduced opacity text for less emphasis

### Font Weights

- **.font-normal**: Normal weight (400)
- **.font-medium**: Medium weight (500)
- **.font-semibold**: Semi-bold weight (600)
- **.font-bold**: Bold weight (700)

### Special Text Styles

- **.mono**: Monospace font for code or technical text

### Text Alignment

- **.text-left**: Left-aligned text
- **.text-center**: Center-aligned text
- **.text-right**: Right-aligned text

### Text Overflow

- **.truncate**: Truncates text with ellipsis when it overflows
- **.break-words**: Breaks long words to prevent overflow

### Usage Example

```html
<h1 class="text-primary">Page Title</h1>
<p class="text-sm text-muted">This is a small muted paragraph.</p>
<span class="mono font-semibold">console.log('Hello');</span>
```

---

## Utilities

**File:** `styles/common/utilities.css`

Provides general utility classes for common styling needs.

### Display Utilities

- **.block**, **.inline**, **.inline-block** - Control display type
- **.hidden** - Hide an element
- **.overflow-hidden**, **.overflow-auto** - Control overflow behavior

### Visibility Utilities

- **.visible**, **.invisible** - Control visibility
- **.opacity-0**, **.opacity-50**, **.opacity-100** - Control opacity

### Background and Border Utilities

- **.rounded**, **.rounded-sm**, **.rounded-lg** - Border radius utilities
- **.border**, **.border-0** - Border utilities

### Shadow Utilities

- **.shadow**, **.shadow-md**, **.shadow-lg** - Box shadow utilities

### Transition Utilities

- **.transition** - Adds standard transition
- **.transition-color**, **.transition-transform** - Specific property transitions

### Usage Example

```html
<div class="rounded shadow-lg overflow-hidden">Content with rounded corners, shadow, and hidden overflow</div>
```

---

## Variables

**File:** `styles/common/variables.css`

Defines global CSS variables used throughout the application.

### Color Variables

- **Base Colors**: Primary, secondary, accent colors in HSL format
- **Gray Scale**: Shades of gray for backgrounds, text, and borders
- **Functional Colors**: Success, warning, error, and info colors

### Typography Variables

- **Font Families**: Sans-serif and monospace font stacks
- **Font Sizes**: Standard text sizes from xs to 2xl
- **Font Weights**: Weight values for different text styles
- **Line Heights**: Standard line heights for various text styles

### Spacing Variables

- **Spacing Scale**: Consistent spacing values (0.25rem to 4rem)

### Border Variables

- **Border Widths**: Standard border width values
- **Border Radii**: Rounded corner values from small to full

### Shadow Variables

- **Box Shadows**: Shadow values from subtle to prominent

### Transition Variables

- **Transition Timing**: Standard transition durations and easing functions

### Z-Index Variables

- **Z-Index Scale**: Standardized z-index values for layering elements

### Component-Specific Variables

- **Card Variables**: Specific styling for card components
- **Badge Variables**: Specific styling for badge components
- **Button Variables**: Specific styling for button components

### Usage Example

```css
.my-component {
  color: hsl(var(--color-primary));
  padding: var(--spacing-2);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  transition: var(--transition-hover);
}
```

### Dark Mode Variables

Many variables have light and dark mode variants that are automatically applied when the `.dark` class is present on an ancestor element.

---

## Best Practices for Using Common Patterns

1. **Prefer Common Patterns Over Custom Styles**: Use these common patterns whenever possible instead of creating custom styles that duplicate functionality.

2. **Combine Multiple Classes**: These patterns are designed to be combined, allowing you to build complex layouts with simple HTML.

3. **Use Variables from variables.css**: When creating new styles, use the CSS variables defined in variables.css to maintain consistency.

4. **Dark Mode Consistency**: Common patterns include dark mode variants that automatically apply with the `.dark` class.

5. **Responsive Design**: Use the responsive utilities and container classes to create layouts that work across different screen sizes.