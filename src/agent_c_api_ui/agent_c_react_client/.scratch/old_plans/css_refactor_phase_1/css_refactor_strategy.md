# CSS Refactoring Strategy

## Core Strategy

We're adopting a "strangler fig" approach to refactoring CSS. This strategy is named after a vine that gradually overtakes and replaces a host tree. In our context, we will:

1. Create a new CSS organization system alongside the current inline styles
2. Gradually migrate components one-by-one to the new system
3. Ensure each migration is visually identical before moving on
4. Eventually, all components will use the new system

## CSS Organization Approach

### File Structure

```
src/
  styles/
    globals.css (existing file)
    component-styles.css (new file for component-specific styles)
```

### CSS Organization Principles

1. **Component-Focused**: Each component gets its own section in the CSS file
2. **BEM-Inspired Naming**: Use component-element-modifier pattern (e.g., `thought-container`, `thought-content`)
3. **Dark Mode Support**: Use `.dark` class prefix for dark mode styles
4. **Tailwind Integration**: Use `@apply` directive for Tailwind utility classes where appropriate
5. **Direct CSS Properties**: Use standard CSS properties for complex styles like scrollbars
6. **CSS Variables**: Leverage theme variables from globals.css where possible

## Implementation Guidelines

### Step 1: Create the CSS File

Create a component-styles.css file in src/styles/ with the following structure:

```css
/* Component Styles */

/* ===== ThoughtDisplay ===== */
/* styles for ThoughtDisplay go here */

/* ===== MarkdownMessage ===== */
/* styles for MarkdownMessage go here */

/* etc. */
```

### Step 2: Import the CSS File

Import the new CSS file in the main entry point (likely src/main.jsx or similar):

```jsx
import './styles/globals.css';
import './styles/component-styles.css';
```

### Step 3: Refactor Components

For each component:

1. Identify all inline styles and Tailwind utility classes
2. Create appropriate CSS classes in component-styles.css
3. Replace inline styles with the new classes
4. Verify visual appearance is identical

## Refactoring Patterns

### Pattern 1: Inline style object

**Before**:
```jsx
<div 
  style={{
    scrollbarWidth: 'thin',
    scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
  }}
>
```

**After**:
```jsx
<div className="component-element">
```

With CSS:
```css
.component-element {
  scrollbar-width: thin;
  scrollbar-color: #d97706 #fef3c7;
}

.dark .component-element {
  scrollbar-color: #78350f #2c1a09;
}
```

### Pattern 2: Conditional Tailwind classes

**Before**:
```jsx
<div className="
  bg-amber-50 dark:bg-gray-700/70 
  text-amber-700/80 dark:text-amber-200/80 
  border border-amber-200 dark:border-amber-800
">
```

**After**:
```jsx
<div className="component-element">
```

With CSS:
```css
.component-element {
  background-color: #fffbeb; /* amber-50 */
  color: rgba(180, 83, 9, 0.8); /* amber-700/80 */
  border: 1px solid #fde68a; /* amber-200 */
}

.dark .component-element {
  background-color: rgba(55, 65, 81, 0.7); /* gray-700/70 */
  color: rgba(252, 211, 77, 0.8); /* amber-200/80 */
  border-color: #92400e; /* amber-800 */
}
```

### Pattern 3: Component overrides

**Before**:
```jsx
h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-3 mb-1" {...props} />
```

**After**:
```jsx
h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />
```

With CSS:
```css
.markdown-h1 {
  @apply text-2xl font-bold mt-3 mb-1;
}
```

## Testing Approach

1. **Visual Comparison**: Take screenshots before and after to verify appearance
2. **Interactive Testing**: Test all hover states, focus states, and animations
3. **Dark Mode Testing**: Verify appearance in both light and dark modes

## Potential Challenges

1. **CSS Specificity Issues**: May need to adjust specificity for proper styling
2. **Dynamic Styles**: Some styles may depend on JavaScript variables
3. **Third-Party Component Integration**: May need special handling for third-party components

## Success Criteria

The refactoring will be considered successful when:

1. All inline styles have been moved to CSS classes
2. Visual appearance is identical to the original
3. All interactive states work as expected
4. The codebase is more maintainable and consistent
5. The application passes all existing tests

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [CSS Custom Properties (Variables)](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [BEM Naming Convention](http://getbem.com/naming/)