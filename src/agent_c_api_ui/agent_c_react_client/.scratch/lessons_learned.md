# shadcn/ui Migration Lessons Learned

This document captures important lessons discovered during our shadcn/ui migration process. These should be applied to all future migration work.

## Key Lessons

1. **Verify Component Usage**: Before migrating any component, we must verify it's actually used in the application

2. **Isolate Theme Changes**: Be extremely careful with global CSS variables - test changes locally first

3. **Prioritize Active Components**: Focus on components that are actively used and visible to users

4. **Understand Component Relationships**: Map out how components connect to avoid unintended side effects

5. **Check for inline styles**: As we migrate each component we should be looking for inline styles that need moved to CSS

6. **Check for improper CSS variable usage**: Ensure components follow the themes

7. **Light and dark modes exist**: We need to be careful to preserve both themes

8. **Separate Styling from Structure**: Keep JSX focused on component structure and behavior by moving all styling to CSS files. Use semantic class names (like `messages-list-container`) instead of embedding styling utilities (like `flex-1 px-4`) directly in JSX. This improves readability, maintainability, and component reusability.

## Application Examples

### Example 1: Proper Separation of Concerns

```jsx
// GOOD: Semantic class name in JSX
<div className="messages-list-container">
  {children}
</div>

// CSS file
.messages-list-container {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: var(--background);
}
```

```jsx
// BAD: Styling utilities in JSX
<div className="flex flex-col p-4 bg-background">
  {children}
</div>
```

### Example 2: Theme Variables Usage

```css
/* GOOD: Using theme variables */
.tool-selection-indicator {
  background-color: hsl(var(--primary));
}

/* BAD: Hard-coded colors */
.tool-selection-indicator {
  background-color: #3b82f6;
}
```

### Example 3: Component Verification

```bash
# Before migration, search for imports and references
grep -r "import.*Sidebar" src/
grep -r "<Sidebar" src/
```

## Applying These Lessons

When approaching each component migration:

1. Verify the component is actually used in the application
2. Create a dedicated CSS file with semantic class names
3. Move all styling from JSX to CSS file
4. Use theme variables for colors, spacing, etc.
5. Test in both light and dark modes
6. Validate that both themes work correctly
7. Document any changes to component APIs