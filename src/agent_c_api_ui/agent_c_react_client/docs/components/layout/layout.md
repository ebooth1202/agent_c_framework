# Layout Component

## Purpose

The Layout component serves as the main structural container for the application, providing a consistent UI framework with a sidebar and content area. It handles the overall page structure and responsive behavior.

## Import

```jsx
import Layout from "@/components/Layout";
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| children | ReactNode | required | The main content to render in the layout |
| title | string | undefined | Page title for the header (currently unused) |
| headerActions | ReactNode | undefined | Actions to display in the header (currently unused) |
| showHeader | boolean | true | Whether to show the page header (currently unused) |
| className | string | undefined | Additional CSS classes to apply to the main content area |

## Usage Example

```jsx
<Layout title="Dashboard">
  <div>Your page content here</div>
</Layout>
```

## Component Structure

The Layout component consists of:

1. **AppSidebar**: Wraps the entire layout and provides the sidebar navigation
2. **Main Content Area**: Flexible container for page content

The component detects the current route and applies different styling for the home page versus other pages.

## Styling

The Layout component uses CSS classes defined in `src/styles/components/layout.css`:

- `.layout-main`: Base styles for the main content area
- `.layout-main-home`: Specific styles for the home page (removes padding)
- `.layout-main-page`: Styles for regular pages (adds max-width, padding, and scrolling)

Key styling features:

- Responsive padding using clamp function
- Support for dynamic viewport height (dvh) with fallback
- Transition effects for smooth style changes
- Automatic handling of overflow content

## Responsive Behavior

The Layout adjusts based on screen size through the AppSidebar component, which handles the responsive behavior of the sidebar (collapsing on mobile, etc.).

The main content area uses:

- A maximum width constraint (2000px) to prevent excessive stretching on large screens
- Responsive padding that scales with viewport size
- Dynamic height calculation to account for the header

## Related Components

- [AppSidebar](./app-sidebar.md) - The sidebar navigation that wraps the Layout
- [PageHeader](./page-header.md) - Optional header component for page titles