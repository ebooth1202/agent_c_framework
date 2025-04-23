# shadcn/ui Migration Strategy

## Overview

This document outlines the approach for migrating the Agent C React UI from traditional CSS to shadcn/ui components with Tailwind CSS. The migration will follow a phased approach, starting with core layout components and gradually moving to more specialized components.

## Migration Principles

1. **Progressive Enhancement**: Migrate one component at a time, ensuring full functionality before moving to the next
2. **Consistent Theming**: Maintain visual consistency by preserving the existing color scheme and design language
3. **Component Ownership**: Use shadcn/ui's approach of copying components into your project for full control
4. **Accessibility**: Leverage shadcn/ui's accessibility features built on Radix UI primitives
5. **Test-Driven**: Test each component before and after migration to ensure identical functionality

## Implementation Strategy

### Step 1: Prepare shadcn/ui Environment

1. **Install Missing Components**: Use the shadcn CLI to add required components
   ```bash
   npx shadcn-ui@latest add accordion avatar dropdown-menu form separator sheet context-menu
   ```

2. **Configure CSS Variables**: Review and update global variables to ensure compatibility
   - Preserve component-specific theme variables by adding them to globals.css
   - Ensure dark mode variables are properly configured

### Step 2: Component Migration Process

For each component, follow this process:

1. **Create New Component**: Create a new version of the component using shadcn/ui primitives
   - Start with minimal functionality and build up
   - Use the Tailwind CSS equivalents from the mapping document
   - Keep the same props interface for compatibility

2. **Implement Styling**:
   - Convert CSS classes to Tailwind utilities
   - Use shadcn/ui's `cn()` utility for class name merging
   - Preserve essential theme variables in globals.css

3. **Implement Functionality**:
   - Reimplement component behavior using shadcn/ui primitives
   - Use hooks and context the same way as the original component
   - Ensure event handlers work identically

4. **Test and Refine**:
   - Test the component in isolation
   - Verify visual appearance matches the original
   - Ensure all functionality works as expected
   - Verify accessibility features

5. **Integration**:
   - Replace the original component with the new one
   - Test the component in context
   - Fix any integration issues

6. **Clean Up**:
   - Remove the old CSS file once the migration is complete
   - Update imports in other components
   - Document any changes to the component API

### Step 3: Sidebar Component Migration Example

Here's how we'll approach migrating the Sidebar component:

1. **Create New Component**:
   ```jsx
   // src/components/ui/sidebar.jsx
   import * as React from "react";
   import { cn } from "@/lib/utils";
   import { ScrollArea } from "@/components/ui/scroll-area";
   import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
   import { Link } from "react-router-dom";

   const Sidebar = React.forwardRef(({ className, title, items, footer, ...props }, ref) => {
     const location = useLocation();

     return (
       <aside className={cn(
         "flex flex-col w-full max-w-64 bg-background border-r border-border overflow-y-auto h-full",
         className
       )} ref={ref} {...props}>
         {title && (
           <div className="p-4 text-lg font-semibold border-b border-border">
             {title}
           </div>
         )}
         
         <ScrollArea className="flex-1 py-4">
           <nav>
             <ul className="list-none p-0 m-0">
               {items.map((item, index) => (
                 <li key={index} className="mb-1">
                   {item.disabled ? (
                     <span className="flex items-center px-4 py-2 text-muted-foreground cursor-not-allowed border-l-3 border-transparent">
                       {item.icon && <span className="mr-2">{item.icon}</span>}
                       {item.label}
                     </span>
                   ) : (
                     <Link to={item.path} 
                       className={cn(
                         "flex items-center px-4 py-2 transition-colors border-l-3",
                         location.pathname === item.path
                           ? "text-primary bg-primary/10 font-medium border-l-primary"
                           : "text-muted-foreground hover:bg-accent hover:text-accent-foreground border-transparent"
                       )}
                     >
                       {item.icon && <span className="mr-2">{item.icon}</span>}
                       {item.label}
                     </Link>
                   )}
                 </li>
               ))}
             </ul>
           </nav>
         </ScrollArea>
         
         {footer && (
           <div className="p-4 border-t border-border text-sm">
             {footer}
           </div>
         )}
       </aside>
     );
   });
   Sidebar.displayName = "Sidebar";

   // Mobile Sidebar using Sheet
   const MobileSidebar = ({ items, title, footer, trigger }) => {
     return (
       <Sheet>
         <SheetTrigger asChild>
           {trigger}
         </SheetTrigger>
         <SheetContent side="left" className="p-0">
           <Sidebar items={items} title={title} footer={footer} />
         </SheetContent>
       </Sheet>
     );
   };

   export { Sidebar, MobileSidebar };
   ```

2. **Update Import in Layout Component**:
   ```jsx
   import { Sidebar, MobileSidebar } from "@/components/ui/sidebar";
   ```

3. **Use New Component**:
   ```jsx
   // Desktop view
   <Sidebar 
     title="Agent C"
     items={navigationItems}
     footer={<ThemeToggle />}
     className="hidden sm:flex"
   />
   
   // Mobile view
   <MobileSidebar
     title="Agent C"
     items={navigationItems}
     footer={<ThemeToggle />}
     trigger={<Button variant="ghost" size="icon"><Menu className="h-5 w-5" /></Button>}
   />
   ```

4. **Remove Old CSS File**:
   Once the new component is working, remove `src/styles/components/sidebar.css` and its import from main.css.

## Migration Order

Use the priority order from the component dependency map, starting with:

1. Sidebar.jsx
2. PageHeader.jsx
3. Layout.jsx
4. MobileNav.jsx

This will establish the core layout structure with shadcn/ui before moving to more specialized components.

## Testing Strategy

1. **Visual Comparison**: Before/after screenshots to ensure consistent appearance
2. **Functionality Testing**: Verify all features work identically
3. **Responsive Testing**: Ensure proper behavior across device sizes
4. **Dark Mode Testing**: Verify theme switching works correctly
5. **Accessibility Testing**: Verify a11y features are maintained or improved

## Rollback Plan

If issues are encountered during migration:

1. Keep original components and CSS files until migration is verified
2. Create a separate branch for each migration task
3. Be prepared to roll back individual component migrations if necessary

## Documentation

For each migrated component:

1. Update component documentation
2. Note any API changes
3. Document dependencies on shadcn/ui primitives
4. Add examples of Tailwind class usage for future reference

## Conclusion

Following this strategy will ensure a smooth, incremental migration to shadcn/ui while maintaining the existing functionality and design language of the Agent C React UI.