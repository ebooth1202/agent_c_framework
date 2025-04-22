# CSS Common Patterns Extraction Draft

Based on the audit of our first 6 components, I've identified several UI patterns that appear in multiple components. Here's a draft plan for extracting these patterns into common style files.

## 1. Card Patterns

Many components use card-like containers. We should create common card styles in `/styles/common/cards.css`:

```css
/* ===== COMMON: Cards ===== */
/* Description: Reusable card components and variations */

/* Base card style */
.card {
  background-color: var(--card-background);
  border-radius: var(--card-border-radius);
  border: var(--border-width-thin) solid var(--card-border-color);
  box-shadow: var(--card-shadow);
  padding: var(--card-padding-y) var(--card-padding-x);
}

/* Card with hover effect */
.card-interactive {
  transition: var(--transition-hover);
}

.card-interactive:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

/* Info card - used for tooltips and popovers */
.info-card {
  background-color: var(--card-background);
  border-radius: var(--card-border-radius);
  border: var(--border-width-thin) solid var(--card-border-color);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-index-popover);
}

/* Card header */
.card-header {
  padding-bottom: var(--spacing-2);
  margin-bottom: var(--spacing-2);
  border-bottom: var(--border-width-thin) solid hsl(var(--color-gray-200));
}

.dark .card-header {
  border-bottom-color: hsl(var(--color-gray-700));
}

/* Card footer */
.card-footer {
  padding-top: var(--spacing-2);
  margin-top: var(--spacing-2);
  border-top: var(--border-width-thin) solid hsl(var(--color-gray-200));
}

.dark .card-footer {
  border-top-color: hsl(var(--color-gray-700));
}

/* Card with hover reveal */
.card-with-hover-reveal .hover-reveal {
  opacity: 0;
  transition: opacity var(--transition-hover);
}

.card-with-hover-reveal:hover .hover-reveal {
  opacity: 1;
}
```

## 2. Button and Interactive Elements

We should create a file for common interactive elements in `/styles/common/interactive.css`:

```css
/* ===== COMMON: Interactive Elements ===== */
/* Description: Buttons, links, and other interactive elements */

/* Base interactive element with hover effect */
.interactive {
  transition: var(--transition-hover);
  cursor: pointer;
}

/* Copy button - used in multiple components */
.copy-button {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-sm);
  transition: var(--transition-hover);
  background-color: hsl(var(--color-gray-800));
  color: white;
}

.copy-button:hover {
  background-color: hsl(var(--color-gray-700));
}

/* Icon button */
.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  color: hsl(var(--color-gray-500));
  transition: var(--transition-hover);
}

.icon-button:hover {
  color: hsl(var(--color-gray-900));
}

.dark .icon-button {
  color: hsl(var(--color-gray-400));
}

.dark .icon-button:hover {
  color: hsl(var(--color-gray-50));
}

/* Hover-reveal container */
.hover-reveal-container .hover-reveal {
  opacity: 0;
  transition: opacity var(--transition-hover);
}

.hover-reveal-container:hover .hover-reveal {
  opacity: 1;
}
```

## 3. Badges and Tags

We should create a file for badges and tags in `/styles/common/badges.css`:

```css
/* ===== COMMON: Badges and Tags ===== */
/* Description: Badge components for statuses, labels, and indicators */

/* Base badge */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  font-weight: var(--font-weight-medium);
  border: var(--border-width-thin) solid;
  border-radius: var(--badge-border-radius);
  padding: var(--badge-padding-y) var(--badge-padding-x);
  font-size: var(--badge-font-size);
  white-space: nowrap;
}

/* Badge variants */

/* Primary badge */
.badge-primary {
  background-color: hsl(var(--color-blue-50));
  color: hsl(var(--color-blue-700));
  border-color: hsl(var(--color-blue-200));
}

.dark .badge-primary {
  background-color: hsla(var(--color-blue-900), 0.3);
  color: hsl(var(--color-blue-300));
  border-color: hsla(var(--color-blue-800), 0.3);
}

/* Success badge */
.badge-success {
  background-color: hsl(var(--color-green-50));
  color: hsl(var(--color-green-700));
  border-color: hsl(var(--color-green-200));
}

.dark .badge-success {
  background-color: hsla(var(--color-green-900), 0.3);
  color: hsl(var(--color-green-300));
  border-color: hsla(var(--color-green-800), 0.3);
}

/* Warning badge */
.badge-warning {
  background-color: hsl(var(--color-amber-50));
  color: hsl(var(--color-amber-700));
  border-color: hsl(var(--color-amber-200));
}

.dark .badge-warning {
  background-color: hsla(var(--color-amber-900), 0.3);
  color: hsl(var(--color-amber-300));
  border-color: hsla(var(--color-amber-800), 0.3);
}

/* Info badge */
.badge-info {
  background-color: hsl(var(--color-purple-50));
  color: hsl(var(--color-purple-700));
  border-color: hsl(var(--color-purple-200));
}

.dark .badge-info {
  background-color: hsla(var(--color-purple-900), 0.3);
  color: hsl(var(--color-purple-300));
  border-color: hsla(var(--color-purple-800), 0.3);
}

/* Disabled badge */
.badge-disabled {
  background-color: hsl(var(--color-gray-100));
  color: hsl(var(--color-gray-500));
  border-color: hsl(var(--color-gray-200));
}

.dark .badge-disabled {
  background-color: hsla(var(--color-gray-700), 0.3);
  color: hsl(var(--color-gray-400));
  border-color: hsla(var(--color-gray-700), 0.4);
}
```

## 4. Tooltips and Popovers

We should create a file for tooltips and popovers in `/styles/common/tooltips.css`:

```css
/* ===== COMMON: Tooltips and Popovers ===== */
/* Description: Tooltip, popover, and hover card components */

/* Base tooltip */
.tooltip {
  position: relative;
  z-index: var(--z-index-tooltip);
  max-width: 20rem;
  background-color: var(--card-background);
  border: var(--border-width-thin) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.dark .tooltip {
  background-color: hsl(var(--color-gray-800));
  border-color: hsl(var(--color-gray-700));
}

/* Popover - similar to tooltip but larger */
.popover {
  position: relative;
  z-index: var(--z-index-popover);
  background-color: var(--card-background);
  border: var(--border-width-thin) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  box-shadow: var(--shadow-lg);
}

.dark .popover {
  background-color: hsl(var(--color-gray-800));
  border-color: hsl(var(--color-gray-700));
}

/* Popover animation */
@keyframes popoverAnimation {
  from {
    opacity: 0;
    transform: translateY(-0.5rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popover-animated {
  animation: popoverAnimation var(--transition-fade);
}
```

## 5. Layout Utilities

We should update `/styles/common/layout.css` with more layout utilities:

```css
/* ===== COMMON: Layout ===== */
/* Description: Common layout patterns and utilities */

/* Container with max width and centered */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.container-sm {
  max-width: 640px;
}

.container-md {
  max-width: 768px;
}

.container-lg {
  max-width: 1024px;
}

.container-xl {
  max-width: 1280px;
}

/* Flex layouts */
.flex-row {
  display: flex;
  flex-direction: row;
}

.flex-col {
  display: flex;
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-1 {
  gap: var(--spacing-1);
}

.gap-2 {
  gap: var(--spacing-2);
}

.gap-3 {
  gap: var(--spacing-3);
}

.gap-4 {
  gap: var(--spacing-4);
}

/* Grids */
.grid-2-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.grid-3-cols {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
}
```

## Implementation Strategy

1. Create the common CSS files described above

2. Update main.css to import these new common files

3. Begin refactoring components to use these common patterns:

   - Replace component-specific card styles with `.card` and its variants
   - Replace copy buttons with the common `.copy-button` class
   - Replace badges with the common `.badge` and its variants
   - Replace tooltips with the common `.tooltip` class
   - Replace layout patterns with common layout utilities

4. For example, refactor AgentConfigHoverCard from:

```css
.agent-config-hover-card-content {
  width: 24rem;
  padding: 0;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 50;
}
```

To:

```css
.agent-config-hover-card-content {
  width: 24rem;
  padding: 0;
  z-index: var(--z-index-popover);
}

/* Add the .popover class to the component's JSX */
```

5. Document all common patterns in a style guide for future reference

## Next Steps

1. Create the new common CSS files
2. Update main.css to import these files
3. Begin refactoring the first component (Layout) to use common patterns
4. Test and validate the changes