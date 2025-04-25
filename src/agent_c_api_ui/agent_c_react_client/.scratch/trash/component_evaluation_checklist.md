# Component Evaluation Checklist

Use this checklist when evaluating custom application components for proper shadcn/ui integration.

## Basic Information

- **Component Name**: 
- **File Location**: 
- **Component Purpose**: 
- **Uses shadcn/ui Components?**: Yes/No
- **Has Dedicated CSS File?**: Yes/No
- **CSS File Location**: 

## shadcn/ui Component Usage

- [ ] **Import Paths**: Component imports shadcn/ui components from correct paths
- [ ] **Component Composition**: Uses proper shadcn/ui component composition
- [ ] **Props Usage**: Uses component props correctly
- [ ] **Event Handling**: Implements event handlers according to documentation
- [ ] **Variants**: Uses variant props when applicable
- [ ] **Sizing**: Uses size props when applicable
- [ ] **Customization**: Uses className prop for customization
- [ ] **cn() Utility**: Uses cn() utility for className composition

## Styling Evaluation

- [ ] **Style Location**: Styles in dedicated CSS file (not inline)
- [ ] **CSS Organization**: CSS follows the component header format
- [ ] **Variable Usage**: Uses shadcn/ui CSS variables for theming
- [ ] **Specificity**: Avoids high specificity selectors and !important
- [ ] **Responsive Design**: Implements responsive design correctly
- [ ] **Dark Mode**: Works correctly in both light and dark modes
- [ ] **Custom Variables**: Any custom variables are necessary and well-named

## Accessibility 

- [ ] **Keyboard Navigation**: Component is keyboard navigable
- [ ] **Screen Reader**: Content is accessible to screen readers
- [ ] **Color Contrast**: Meets color contrast requirements
- [ ] **ARIA Attributes**: Uses appropriate ARIA attributes
- [ ] **Focus Management**: Manages focus correctly

## Performance & Optimization

- [ ] **Rendering Efficiency**: Avoids unnecessary re-renders
- [ ] **Bundle Size**: Doesn't import unnecessary dependencies
- [ ] **Event Handlers**: Properly memoized when needed
- [ ] **CSS Efficiency**: CSS is efficient and targeted

## Issues Identified

1. 
2. 
3. 

## Recommendations

1. 
2. 
3. 

## Migration Complexity

- **Complexity Rating**: (Low/Medium/High)
- **Estimated Effort**: (Hours)
- **Priority**: (Low/Medium/High)
- **Dependencies**: 

## Notes
