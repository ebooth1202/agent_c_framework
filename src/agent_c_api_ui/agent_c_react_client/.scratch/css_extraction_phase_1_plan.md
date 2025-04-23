# CSS Extraction - Phase 1 Detailed Plan

## Overview
This document provides a detailed breakdown of Phase 1 of the Inline Styles Extraction project, focusing on Core UI Components. This phase will establish patterns and practices for the remaining phases while addressing the most fundamental UI components first.

## Phase 1 Components
1. Layout Component (`src/components/Layout.jsx` → `src/styles/components/layout.css`)
2. Sidebar Component (`src/components/Sidebar.jsx` → `src/styles/components/sidebar.css`)
3. PageHeader Component (`src/components/PageHeader.jsx` → `src/styles/components/page-header.css`)
4. MobileNav Component (`src/components/MobileNav.jsx` → `src/styles/components/mobile-nav.css`)

## Process Detail for Each Component

For each component, we'll follow this standardized process:

### 1. Component Analysis
- Examine the component structure and functionality
- Identify all inline styles (style={...} props)
- Document conditional styling and state-dependent styles
- Note any dynamic values that will need CSS variables
- Identify any potential challenges (responsive behavior, state transitions, etc.)

### 2. CSS File Preparation
- Create new CSS file or update existing file with proper component header
- Define a clear naming strategy for classes following BEM-like principles
- Create base styles for the component
- Add state-specific styles with appropriate modifiers
- Implement responsive styling with media queries as needed

### 3. Component Refactoring
- Add import for CSS file if not already present
- Replace inline style objects with className references
- Use conditional classNames for state-dependent styling
- Utilize the cn() utility for complex className combinations
- Ensure all behavior is preserved after style extraction

### 4. Verification
- Visual comparison before and after changes
- Test responsive behavior at different screen sizes
- Verify proper styling across all states (hover, active, focused, etc.)
- Ensure functionality remains intact
- Document any visual or behavioral differences

## Component-Specific Details

### 1. Layout Component

#### Analysis Tasks
- Identify the overall layout structure (grid, flex, etc.)
- Note any conditional layout variations
- Document responsive behavior across breakpoints
- Identify any z-index stacking or positioning issues

#### CSS Implementation
- Create base layout container styles
- Define main content area styling
- Implement responsive adjustments
- Add any transition effects for layout changes

#### Refactoring Steps
- Import layout.css in Layout.jsx
- Replace inline styles with appropriate class names
- Use cn() for conditional classes if needed
- Update any child component style props as needed

#### Verification Criteria
- Maintain proper spacing and alignment
- Verify responsive behavior at all breakpoints
- Check for content overflow issues
- Ensure consistent rendering across pages

### 2. Sidebar Component

#### Analysis Tasks
- Identify navigation item styling patterns
- Document active/inactive state styling
- Note any conditional rendering or responsive behaviors
- Identify hover/focus states

#### CSS Implementation
- Create sidebar container styles
- Define navigation item styles (normal, active, hover)
- Implement mobile/responsive adjustments
- Add transition effects for state changes

#### Refactoring Steps
- Import sidebar.css in Sidebar.jsx
- Replace inline styles with class names
- Implement conditional classes for active states
- Update any SVG/icon styling

#### Verification Criteria
- Verify active state highlighting
- Check hover/focus behaviors
- Test mobile collapse/expand functionality
- Ensure consistent spacing and alignment

### 3. PageHeader Component

#### Analysis Tasks
- Identify header layout structure
- Document any title/subtitle styling
- Note responsive adjustments
- Identify any action button styling

#### CSS Implementation
- Create header container styles
- Define title/heading styles
- Implement responsive text sizing
- Style action buttons or controls

#### Refactoring Steps
- Import page-header.css in PageHeader.jsx
- Replace inline styles with class names
- Update any dynamic text styling
- Apply conditional classes for different header variations

#### Verification Criteria
- Maintain proper alignment and spacing
- Verify text truncation/wrapping behavior
- Check responsive sizing
- Ensure consistent appearance across pages

### 4. MobileNav Component

#### Analysis Tasks
- Identify mobile navigation patterns
- Document open/closed state styling
- Note any animation or transition effects
- Identify touch target sizing and accessibility concerns

#### CSS Implementation
- Create mobile nav container styles
- Define toggle button styling
- Implement menu open/closed states
- Add transition animations

#### Refactoring Steps
- Import mobile-nav.css in MobileNav.jsx
- Replace inline styles with class names
- Implement conditional classes for open/closed states
- Update any overlay or backdrop styling

#### Verification Criteria
- Verify open/close animation
- Check touch target sizes for accessibility
- Test overlay behavior
- Ensure consistent appearance and behavior across devices

## Testing Strategy

### Visual Regression Testing
- Screenshot components before changes
- Compare with screenshots after changes
- Document and resolve any visual discrepancies

### Responsive Testing
- Test at standard breakpoints (mobile, tablet, desktop)
- Verify behavior during window resizing
- Check orientation changes on mobile devices

### State Testing
- Verify all component states (normal, hover, active, disabled)
- Test transitions between states
- Ensure conditional rendering works correctly

## Deliverables

1. Updated component files with inline styles removed
2. New or updated CSS files with extracted styles
3. Documentation of any challenges or patterns discovered
4. Before/after screenshots for verification

## Dependencies

- Existing CSS structure and organization
- CSS variable definitions in globals.css
- cn() utility function from utils.ts
- Current responsive breakpoints

## Risk Management

### Potential Issues
- Dynamic styles calculated from props/state
- Responsive behavior differences
- Z-index stacking context changes
- Transition/animation disruptions

### Mitigation Strategies
- Use CSS variables for dynamic values
- Thoroughly test at all breakpoints
- Document z-index hierarchy
- Implement transitions gradually and test incrementally