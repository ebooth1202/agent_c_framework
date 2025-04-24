# Next Session Plan - ShadCN/Radix UI Implementation

## Session Goals

1. Fix critical issues with shadcn/ui components
2. Create detailed CSS variable mapping
3. Begin addressing theming inconsistencies

## Detailed Tasks

### 1. Fix ThemeToggle Component (High Priority)

- **Issue**: Currently imports from incorrect path (`.scratch/backup`)
- **Steps**:
  1. Check shadcn-ui documentation for correct theme-toggle implementation
  2. Fix import paths in the component
  3. Verify functionality in browser
  4. Ensure it works correctly with ThemeProvider

### 2. Create CSS Variable Mapping Reference

- **Purpose**: Help developers understand which variables to use and where
- **Steps**:
  1. Create comprehensive table mapping shadcn to custom variables
  2. Identify variables with no direct equivalent
  3. Document which components use which variable systems
  4. Create guidelines for variable usage moving forward

### 3. Fix CSS Import Structure

- **Issue**: Complex and potentially problematic import patterns
- **Steps**:
  1. Analyze main.css, component-styles.css, and import order
  2. Evaluate impact of Tailwind being imported after component styles
  3. Propose simplified import structure
  4. Test changes for visual regressions

### 4. Audit CollapsibleOptions Component

- **Purpose**: Example of addressing application component styling
- **Steps**:
  1. Identify inline styles that should be in CSS
  2. Check for custom classes that could use Tailwind
  3. Document changes needed
  4. Implement and test changes

### 5. Document Theming Conflicts

- **Purpose**: Create clear path for theming standardization
- **Steps**:
  1. Identify components using custom theme variables
  2. Document impact of migrating these to shadcn variables
  3. Create prioritized list for future migration

## Validation Criteria

- ThemeToggle component works correctly in light and dark modes
- CSS variable mapping document is comprehensive and clear
- Preliminary fixes don't introduce visual regressions
- We have a clear understanding of the scope of theming conflicts

## Resources Needed

- shadcn/ui documentation for reference
- Ability to test changes in both light and dark modes
- Access to see components in browser for visual verification