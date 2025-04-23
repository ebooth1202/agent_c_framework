# Phase 2: Core Component Migration Plan

## Goals

- Migrate core layout components to shadcn/ui
- Establish patterns for component migration
- Create reusable shadcn/ui component variants
- Ensure consistent styling across migrated components

## Components to Migrate

1. **Sidebar.jsx**
   - Estimated complexity: Medium
   - shadcn/ui components needed: ScrollArea, Sheet (for mobile)
   - Special considerations: Mobile/desktop variants

2. **PageHeader.jsx**
   - Estimated complexity: Low
   - shadcn/ui components needed: None (just Tailwind)
   - Special considerations: Responsive layout

3. **Layout.jsx**
   - Estimated complexity: Medium
   - shadcn/ui components needed: Card (for content container)
   - Special considerations: Integration with Sidebar and PageHeader

4. **MobileNav.jsx**
   - Estimated complexity: Medium
   - shadcn/ui components needed: Sheet, Button
   - Special considerations: Animation and interaction

## Migration Steps for Each Component

### Step 1: Prepare Environment

1. Install missing shadcn/ui components:
   ```bash
   npx shadcn-ui@latest add sheet
   ```

2. Create component-specific CSS variables in `globals.css` if needed

### Step 2: Sidebar Migration

1. Create new shadcn/ui-based sidebar component:
   ```jsx
   // src/components/ui/sidebar.jsx
   ```

2. Update imports in Layout.jsx:
   ```jsx
   import { Sidebar, MobileSidebar } from "@/components/ui/sidebar";
   ```

3. Test sidebar functionality and appearance

4. Remove old sidebar.css file and update imports

### Step 3: PageHeader Migration

1. Create new shadcn/ui-based page header component:
   ```jsx
   // src/components/ui/page-header.jsx
   ```

2. Update imports in Layout.jsx:
   ```jsx
   import { PageHeader } from "@/components/ui/page-header";
   ```

3. Test page header functionality and appearance

4. Remove old page-header.css file and update imports

### Step 4: Layout Migration

1. Create new shadcn/ui-based layout component:
   ```jsx
   // src/components/ui/layout.jsx
   ```

2. Update imports in App.jsx or Routes.jsx:
   ```jsx
   import { Layout } from "@/components/ui/layout";
   ```

3. Test layout functionality and appearance

4. Remove old layout.css file and update imports

### Step 5: MobileNav Migration

1. Create new shadcn/ui-based mobile nav component (this might be merged with Sidebar as MobileSidebar):
   ```jsx
   // If separate: src/components/ui/mobile-nav.jsx
   ```

2. Update imports in Layout.jsx:
   ```jsx
   import { MobileNav } from "@/components/ui/mobile-nav";
   ```

3. Test mobile nav functionality and appearance

4. Remove old mobile-nav.css file and update imports

## Testing Plan

1. **Visual Testing**:
   - Compare screenshots before and after migration
   - Verify responsive behavior at multiple breakpoints
   - Check dark mode appearance

2. **Functional Testing**:
   - Verify navigation links work correctly
   - Test mobile navigation opening/closing
   - Ensure proper layout at all screen sizes

3. **Accessibility Testing**:
   - Test keyboard navigation
   - Verify proper ARIA attributes
   - Check color contrast

## Success Criteria

- All core layout components successfully migrated to shadcn/ui
- Visual appearance matches the original design
- All functionality works as expected
- No regressions in responsive behavior
- Dark mode works correctly
- CSS file size reduced through Tailwind utility classes

## Timeline

Estimated completion time for Phase 2: 3-4 days of development effort

- Sidebar: 1 day
- PageHeader: 0.5 day
- Layout: 1 day
- MobileNav: 0.5-1 day
- Testing and refinement: 1 day