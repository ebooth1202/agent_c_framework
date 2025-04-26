# Agent's Guide to Radix UI

*Created: April 24, 2025 - A concise reference for AI agents working with Radix UI*

## What is Radix UI?

Radix UI is a comprehensive, open-source UI component library focused on accessibility, customization, and developer experience. It provides a set of unstyled, composable components that serve as building blocks for creating high-quality web interfaces.

This guide provides a high-level overview of Radix UI with pointers to more detailed documentation for specific use cases.

## Key Features

- **Accessible**: Components follow WAI-ARIA design patterns ensuring accessibility
- **Unstyled**: Ships without predefined styles, giving complete customization freedom
- **Composable**: Components are broken down into logical parts that can be composed
- **Customizable**: Offers extensive styling options via CSS, CSS Modules, or Tailwind
- **Developer-friendly**: Consistent APIs, fully typed with TypeScript

## Core Concepts

### 1. Primitives vs. Themes

Radix UI offers two main packages:

- **Primitives**: Low-level, unstyled components (the foundation)
- **Themes**: Pre-styled components built on primitives with theming capabilities

### 2. Component Composition Pattern

Most Radix components follow a composition pattern using a `Root` component with nested subcomponents:

```jsx
<Dialog.Root>
  <Dialog.Trigger />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title />
      <Dialog.Description />
      <Dialog.Close />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### 3. Styling Approaches

Radix UI components can be styled using:

- [Plain CSS](/ui/docs/radix_ui/agent_context/styling/css.md)
- [CSS Modules](/ui/docs/radix_ui/agent_context/styling/css-modules.md)
- [Tailwind CSS](/ui/docs/radix_ui/agent_context/styling/tailwind.md)

## Component Categories

### 1. Layout and Structure

- [AspectRatio](/ui/docs/radix_ui/agent_context/components/aspect-ratio.md) - Maintains consistent width/height ratio
- [Collapsible](/ui/docs/radix_ui/agent_context/components/collapsible.md) - Expandable/collapsible content sections
- [Separator](/ui/docs/radix_ui/agent_context/components/separator.md) - Visual dividers between content
- [ScrollArea](/ui/docs/radix_ui/agent_context/components/scroll-area.md) - Custom scrollable containers

### 2. Navigation

- [NavigationMenu](/ui/docs/radix_ui/agent_context/components/navigation-menu.md) - Main navigation component
- [Tabs](/ui/docs/radix_ui/agent_context/components/tabs.md) - Tabbed interfaces for switching content views
- [ToggleGroup](/ui/docs/radix_ui/agent_context/components/toggle-group.md) - Set of two-state buttons
- [Toolbar](/ui/docs/radix_ui/agent_context/components/toolbar.md) - Container for grouping buttons/controls

### 3. Overlays and Popups

- [Dialog](/ui/docs/radix_ui/agent_context/components/dialog.md) - Modal dialog boxes
- [AlertDialog](/ui/docs/radix_ui/agent_context/components/alert-dialog.md) - Confirmation dialogs
- [HoverCard](/ui/docs/radix_ui/agent_context/components/hover-card.md) - Content cards that appear on hover
- [Popover](/ui/docs/radix_ui/agent_context/components/popover.md) - Positioned floating content
- [Tooltip](/ui/docs/radix_ui/agent_context/components/tooltip.md) - Short informational overlays

### 4. Menus and Selection

- [DropdownMenu](/ui/docs/radix_ui/agent_context/components/dropdown-menu.md) - Menu displayed on button click
- [ContextMenu](/ui/docs/radix_ui/agent_context/components/context-menu.md) - Menu displayed on right-click
- [Menubar](/ui/docs/radix_ui/agent_context/components/menubar.md) - Horizontal menu with dropdowns
- [Select](/ui/docs/radix_ui/agent_context/components/select.md) - Dropdown selection component

### 5. Form Controls

- [Form](/ui/docs/radix_ui/agent_context/components/form.md) - Form validation and submission
- [Checkbox](/ui/docs/radix_ui/agent_context/components/checkbox.md) - Toggle on/off selection
- [RadioGroup](/ui/docs/radix_ui/agent_context/components/radio-group.md) - Select one from multiple options
- [Switch](/ui/docs/radix_ui/agent_context/components/switch.md) - Toggle control
- [Slider](/ui/docs/radix_ui/agent_context/components/slider.md) - Select value from a range
- [Label](/ui/docs/radix_ui/agent_context/components/label.md) - Accessible label for form elements
- [OneTimePasswordField](/ui/docs/radix_ui/agent_context/components/one-time-password-field.md) - OTP input field

### 6. Feedback and Display

- [Accordion](/ui/docs/radix_ui/agent_context/components/accordion.md) - Expandable content sections
- [Avatar](/ui/docs/radix_ui/agent_context/components/avatar.md) - User/entity representation
- [Progress](/ui/docs/radix_ui/agent_context/components/progress.md) - Progress indicators
- [Toast](/ui/docs/radix_ui/agent_context/components/toast.md) - Temporary notifications

## Common Usage Patterns

### 1. State Management

Most Radix components can be used in either:

- **Uncontrolled mode**: Using `defaultValue` prop
  
  ```jsx
  <Accordion.Root type="single" defaultValue="item-1" collapsible>
    {/* Items */}
  </Accordion.Root>
  ```

- **Controlled mode**: Using `value` and `onValueChange` props
  
  ```jsx
  <Accordion.Root 
    type="single" 
    value={value} 
    onValueChange={setValue} 
    collapsible
  >
    {/* Items */}
  </Accordion.Root>
  ```

### 2. Accessibility Support

All components include proper ARIA attributes and keyboard interactions. Review the accessibility section in each component's documentation for specifics.

### 3. Animation Integration

Components provide data attributes (e.g., `data-state="open"` or `data-state="closed"`) and CSS variables that can be used for animations:

```css
.accordion-content[data-state="open"] {
  animation: slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1);
}

@keyframes slideDown {
  from { height: 0; }
  to { height: var(--radix-accordion-content-height); }
}
```

## Theming System

Radix UI offers a theming system with:

- [Theme Overview](/ui/docs/radix_ui/agent_context/themes/overview.md) - Core theming concepts
- [Theme Configuration](/ui/docs/radix_ui/agent_context/themes/configuration.md) - Customizing themes

The theming system supports:

- Light and dark modes
- Custom color scales
- Responsive scaling
- Accessible color contrasts

## Color System

Radix Colors provides a carefully designed color system:

- [Colors Overview](/ui/docs/radix_ui/agent_context/colors/overview.md) - Color system introduction
- [Color Palette](/ui/docs/radix_ui/agent_context/colors/palette.md) - Color scales and their usage

## Best Practices

1. **Use composition patterns** - Take advantage of the component part system
2. **Leverage data attributes** - Use `data-state` and other attributes for styling
3. **Maintain accessibility** - Don't override accessibility features
4. **Choose appropriate styling** - Select a consistent styling approach
5. **Implement proper animations** - Use provided CSS variables for smooth transitions

## Getting Started Example

```jsx
import * as Accordion from '@radix-ui/react-accordion';
import './styles.css';

export default function App() {
  return (
    <Accordion.Root type="single" defaultValue="item-1" collapsible>
      <Accordion.Item value="item-1">
        <Accordion.Trigger>What is Radix UI?</Accordion.Trigger>
        <Accordion.Content>
          Radix UI is a low-level UI component library with a focus on 
          accessibility, customization and developer experience.
        </Accordion.Content>
      </Accordion.Item>

      <Accordion.Item value="item-2">
        <Accordion.Trigger>Is it accessible?</Accordion.Trigger>
        <Accordion.Content>
          Yes. It adheres to the WAI-ARIA design patterns.
        </Accordion.Content>
      </Accordion.Item>
    </Accordion.Root>
  );
}
```

## Further Resources

- [Complete Components List](/ui/docs/radix_ui/agent_context/components/index.md)
- [Primitives Overview](/ui/docs/radix_ui/agent_context/primitives/overview.md)
- [Styling Guide](/ui/docs/radix_ui/agent_context/styling/index.md)

---

This guide provides a high-level overview of Radix UI. For detailed information on specific components or features, follow the links to the corresponding documentation sections.