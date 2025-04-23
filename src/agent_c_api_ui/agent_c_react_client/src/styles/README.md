# Agent C React Client CSS System

## Documentation Moved

The comprehensive CSS documentation has been moved to the `/docs/style/` directory at the root of the project for better visibility and accessibility.

Please refer to the following documentation:

- [CSS Architecture Overview](/docs/style/README.md)
- [CSS Style Guide](/docs/style/style-guide.md)
- [Common CSS Patterns](/docs/style/common-patterns.md)
- [Component-Specific Styling](/docs/style/component-styling.md)
- [Theme Consistency Guidelines](/docs/style/theme-consistency.md)

## Directory Structure

```
/styles
  /common            # Shared styles and utilities
    variables.css    # Global CSS variables for theming
    reset.css        # CSS reset and normalization
    typography.css   # Text styling and formatting
    layout.css       # Common layout patterns
    utilities.css    # Utility classes
    badges.css       # Badge styling patterns
    cards.css        # Card component patterns
    interactive.css  # Interactive element patterns
    tooltips.css     # Tooltip styling patterns
  /components        # Component-specific styles
    layout.css       # Layout component styles
    sidebar.css      # Sidebar component styles
    ... (other component files)
  main.css           # Main CSS entry point
  globals.css        # Global styles
  component-styles.css # Legacy file (being phased out)
```