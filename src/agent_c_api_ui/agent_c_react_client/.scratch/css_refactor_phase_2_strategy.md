# CSS Refactor Phase 2: Implementation Strategy

## Methodology Refinements

Based on lessons from Phase 1, we'll implement these refinements for Phase 2:

1. **Pattern Recognition**: Identify common patterns across components and create reusable class names
2. **Component Prefixing**: Use clear component prefixes for all classes (e.g., `layout-container`, `mobile-nav-dropdown`)
3. **CSS Comments**: Add detailed comments explaining the purpose and usage of each class
4. **Systematic Extraction**: Extract styles in logical groups (layout, typography, colors, interactions)

## CSS Implementation Patterns

### 1. Layout Component Pattern

```css
/* Layout component */
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  /* Header styles */
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-navigation {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.layout-nav-link {
  /* Base link styles */
}

.layout-nav-link:hover {
  /* Hover state */
}

.dark .layout-nav-link {
  /* Dark mode colors */
}
```

### 2. Navigation Component Pattern

```css
/* Mobile navigation */
.mobile-nav {
  position: relative;
}

.mobile-nav-toggle {
  /* Toggle button styles */
}

.mobile-nav-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 50;
  /* Other dropdown styles */
}

.mobile-nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mobile-nav-link {
  /* Link base styles */
}

.mobile-nav-link-active {
  /* Active link styles */
}
```

### 3. Card Component Pattern

```css
/* Config card component */
.config-card {
  /* Base card styles */
}

.config-card-header {
  /* Header styles */
}

.config-card-content {
  /* Content styles */
}

.config-card-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem;
}

.config-card-label {
  /* Label styles */
}

.config-card-value {
  /* Value styles */
}
```

## Common Element Patterns

### Badge Pattern

```css
.component-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.component-badge-primary {
  background-color: /* primary color */;
  color: /* text color */;
}

.dark .component-badge-primary {
  /* Dark mode colors */
}
```

### Icon Button Pattern

```css
.component-icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.component-icon-button:hover {
  background-color: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
}
```

## Implementation Examples

### Layout.jsx Example

Before:
```jsx
<div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex flex-col overflow-hidden">
  <header className="container mx-auto px-6 py-4 max-w-7xl flex items-center justify-between">
    {/* content */}
  </header>
  <main className="container mx-auto px-6 pt-1 pb-4 max-w-7xl text-gray-900 dark:text-gray-100 flex-1 flex flex-col overflow-hidden">
    {children}
  </main>
</div>
```

After:
```jsx
<div className="layout-container">
  <header className="layout-header">
    {/* content */}
  </header>
  <main className="layout-main">
    {children}
  </main>
</div>
```

With CSS:
```css
/* Layout component styles */
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-image: linear-gradient(to bottom, #f9fafb, #f3f4f6); /* from-gray-50 to-gray-100 */
}

.dark .layout-container {
  background-image: linear-gradient(to bottom, #111827, #1f2937); /* dark:from-gray-900 dark:to-gray-800 */
}

.layout-header {
  width: 100%;
  max-width: 80rem; /* max-w-7xl */
  margin-left: auto;
  margin-right: auto;
  padding: 1rem 1.5rem; /* px-6 py-4 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.layout-main {
  width: 100%;
  max-width: 80rem; /* max-w-7xl */
  margin-left: auto;
  margin-right: auto;
  padding: 0.25rem 1.5rem 1rem 1.5rem; /* pt-1 pb-4 px-6 */
  color: #111827; /* text-gray-900 */
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dark .layout-main {
  color: #f3f4f6; /* dark:text-gray-100 */
}
```

## Conversion Approach by Component Type

### 1. Layout Components
- Extract container styles (dimensions, positioning, backgrounds)
- Create classes for layout regions (header, main, footer)
- Define navigation item styling (links, buttons)

### 2. Interactive Components
- Define base, hover, focus, and active states
- Extract animation and transition properties
- Ensure accessible focus states are maintained

### 3. Card-based Components
- Define card containers and content areas
- Extract header, body, and footer styles
- Define spacing and typography consistently

### 4. Form Components
- Extract input field, label, and validation styling
- Define consistent focus and error states
- Maintain accessible form element styling

## Dark Mode Implementation

Continue with the established pattern of using the `.dark` class prefix:

```css
.component-element {
  /* Light mode styles */
  background-color: white;
  color: black;
}

.dark .component-element {
  /* Dark mode styles */
  background-color: #1f2937;
  color: white;
}
```

## Responsive Design Considerations

Ensure all extracted styles maintain responsive behavior:

```css
.component-container {
  width: 100%;
  padding: 1rem;
}

@media (min-width: 768px) {
  .component-container {
    padding: 2rem;
  }
}
```

## Animation Handling

Extract animations to CSS:

```css
.component-animated-element {
  transition: all 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.component-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
```

## Advanced Cases

### Conditional Styling
For elements with conditional class names, extract the base styling and leave only the conditional logic inline:

```jsx
// Before
<div className={`${isActive ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'} rounded p-2`}>

// After
<div className={`component-tab ${isActive ? 'component-tab-active' : ''}`}>
```

With CSS:
```css
.component-tab {
  border-radius: 0.25rem;
  padding: 0.5rem;
  background-color: #f3f4f6; /* bg-gray-100 */
  color: #1f2937; /* text-gray-800 */
}

.component-tab-active {
  background-color: #3b82f6; /* bg-blue-500 */
  color: white; /* text-white */
}
```