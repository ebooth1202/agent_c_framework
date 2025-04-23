# Inline Styles Extraction Plan

## Objective

Extract all inline styles from React components into proper CSS files, improving maintainability, reusability, and performance of the UI codebase.

## Current State Analysis

After initial analysis, we've discovered two main issues in the codebase:

1. **Inline Styles**: Many components use inline styles (via style={{}}) which makes maintenance difficult and prevents the advantages of CSS

2. **Style Duplication**: We've found duplication between `component-styles.css` and individual component CSS files, creating inconsistency and maintenance challenges

## Phased Approach

### Phase 1: Style Duplication Resolution

**Goal**: Resolve duplication between `component-styles.css` and individual component CSS files

**Target Components**:
- Layout
- Sidebar
- PageHeader
- MobileNav

**Tasks**:
1. Compare styles in `component-styles.css` vs individual component files
2. Transfer any unique styles from `component-styles.css` to component files
3. Remove duplicate sections from `component-styles.css`
4. Document CSS standards and best practices

### Phase 2: Chat Interface Components

**Goal**: Extract inline styles from chat interface components

**Target Components**:
- ChatInterface.jsx
- ChatInputArea.jsx
- MarkdownMessage.jsx
- MediaMessage.jsx
- ThoughtDisplay.jsx
- ToolCallDisplay.jsx
- ToolCallItem.jsx

**Tasks**:
1. Analyze inline styles in each component
2. Create/update appropriate CSS files in styles/components/
3. Replace inline styles with CSS classes
4. Test for visual consistency

### Phase 3: Auxiliary UI Components

**Goal**: Extract inline styles from auxiliary components

**Target Components**:
- PersonaSelector.jsx
- StatusBar.jsx
- AgentConfigDisplay.jsx
- AnimatedStatusIndicator.jsx
- CopyButton.jsx
- ModelParameterControls.jsx

**Tasks**:
1. Analyze inline styles in each component
2. Create/update appropriate CSS files
3. Replace inline styles with CSS classes
4. Test for visual consistency

### Phase 4: RAG Interface Components

**Goal**: Extract inline styles from RAG interface components

**Target Components**:
- CollectionsManager components
- Search components
- Upload components

**Tasks**:
1. Analyze inline styles in each component
2. Create/update appropriate CSS files
3. Replace inline styles with CSS classes
4. Test for visual consistency

## CSS Organization Standards

### File Structure

- **Common Styles**: `/styles/common/` - Base styles, variables, and utility classes
- **Component Styles**: `/styles/components/` - Component-specific styles

### Naming Conventions

- Follow component-based naming: `.component-element-variant`
- Use descriptive class names that reflect the component structure
- Use BEM-like methodology for complex components

### CSS Variables

- Use CSS variables for colors, spacing, transitions, etc.
- Keep variables in theme-appropriate files
- Ensure dark mode compatibility

## Implementation Guidelines

1. Create a CSS file for each component if one doesn't exist
2. Use comments to organize sections within CSS files
3. Ensure all styles support both light and dark modes
4. Test each component thoroughly after conversion
5. Maintain appropriate responsive behavior

## Success Criteria

1. Zero inline styles in React components
2. Consistent styling structure across the application
3. No visual regressions
4. Improved code maintainability
5. Documentation of CSS standards

## Testing Strategy

1. Visual comparison before/after each component change
2. Responsive testing across various viewport sizes
3. Dark mode testing
4. Browser compatibility testing