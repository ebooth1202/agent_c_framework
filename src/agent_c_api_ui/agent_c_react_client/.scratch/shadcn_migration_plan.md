# ShadCN UI Migration Plan

## Current State Analysis

After examining the codebase, I've identified the following:

1. **Configuration Status**:
   - shadcn/ui is partially set up with `components.json` configured properly
   - Basic shadcn/ui components are already installed in `/src/components/ui/`
   - The tailwind.config.js is properly configured with shadcn/ui requirements
   - CSS variables are set up in globals.css

2. **Current Component Architecture**:
   - The application uses a mix of custom components with traditional CSS files
   - Some components are already using shadcn/ui primitives (like Button, Card)
   - Component-specific CSS is organized in the `/src/styles/components/` directory
   - Many components still use conventional class names instead of Tailwind utility classes

3. **Component Usage**:
   - The main application interface is divided into various specialized components
   - There's a clear organization for chat, RAG interface, and replay interface
   - Global layout components control the overall page structure

## Migration Strategy

I recommend a phased approach to migrate the application to shadcn/ui:

### Phase 1: CSS Extraction and Cleanup
1. Extract and document all custom CSS variables and styling patterns
2. Map existing custom component styles to equivalent Tailwind/shadcn/ui patterns
3. Identify components already using shadcn/ui primitives vs those that need migration

### Phase 2: Core Component Migration
1. Migrate foundational components first (layout, navigation, common UI elements)
2. Replace basic input controls with shadcn/ui equivalents (inputs, textareas, etc.)
3. Update container components with shadcn/ui cards, dialogs, etc.

### Phase 3: Specialized Component Migration
1. Migrate chat interface components
2. Migrate RAG interface components
3. Migrate replay interface components

### Phase 4: Theme Refinement and Polish
1. Ensure consistent theming across all components
2. Implement dark mode toggle and theme consistency
3. Address any UX inconsistencies introduced during migration

## Detailed Migration Steps

### Phase 1: CSS Extraction and Cleanup

1. **Inventory Existing Styles**:
   - Catalog all component-specific CSS files
   - Identify common patterns and variables
   - Document theming and dark mode implementation

2. **CSS to Tailwind Mapping**:
   - Create a mapping document for CSS classes to Tailwind equivalents
   - Identify custom styles that need to be preserved as CSS variables
   - Plan for gradual CSS file removal as components are migrated

3. **Component Dependency Analysis**:
   - Map component dependencies to understand migration order
   - Identify which shadcn/ui components are needed but not yet installed
   - Create a component migration priority list

### Phase 2: Core Component Migration

1. **Layout Components**:
   - Migrate `Layout.jsx`, `Sidebar.jsx`, and `PageHeader.jsx`
   - Implement shadcn/ui Sheet for mobile navigation
   - Update navigation components with shadcn/ui styling

2. **Form Controls**:
   - Replace custom inputs with shadcn/ui Input, Textarea, etc.
   - Update form validation to use shadcn/ui Form component
   - Implement consistent input styling using shadcn/ui patterns

3. **Feedback Components**:
   - Migrate loading indicators to shadcn/ui Skeleton/Loader
   - Update notifications to use shadcn/ui Toast
   - Implement modals using shadcn/ui Dialog

### Phase 3: Specialized Component Migration

1. **Chat Interface Components**:
   - Migrate message containers to use shadcn/ui Card
   - Update ChatInputArea with shadcn/ui Input and Button
   - Implement tool panels with shadcn/ui Collapsible

2. **RAG Interface Components**:
   - Update search interface with shadcn/ui input components
   - Migrate results display to use shadcn/ui components
   - Implement file upload with shadcn/ui patterns

3. **Replay Interface Components**:
   - Update timeline with shadcn/ui components
   - Migrate event display to shadcn/ui Card
   - Implement controls with shadcn/ui Button and other primitives

### Phase 4: Theme Refinement and Polish

1. **Theme Consistency**:
   - Ensure all components use shadcn/ui theming variables
   - Update any remaining custom colors to use the theme palette
   - Verify dark mode works correctly across all components

2. **Accessibility Review**:
   - Verify all migrated components maintain accessibility
   - Ensure proper keyboard navigation and focus management
   - Test with screen readers and other assistive technologies

3. **Performance Optimization**:
   - Remove unused CSS
   - Optimize Tailwind configuration
   - Ensure proper tree-shaking of unused components

## Implementation Plan

To make this migration manageable, we'll tackle one phase at a time, with each phase having specific task-oriented steps that can be tracked:

1. Start with CSS extraction and create a mapping document
2. Begin migrating foundational components
3. Move to form controls and input components
4. Tackle specialized components in order of complexity
5. Polish and finalize theme consistency

Let's start with Phase 1: CSS Extraction and Cleanup to build a solid foundation for the migration.