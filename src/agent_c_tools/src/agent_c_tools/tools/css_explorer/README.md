# CSS Explorer Tool

## Overview

The CSS Explorer tool helps agents efficiently work with large CSS files by:

1. **Scanning CSS files** to identify component sections and their styles
2. **Exploring specific components** without loading entire files
3. **Updating individual styles** with precision

This tool is especially useful when working with large component-based CSS files (1000+ lines) where loading the entire file would be inefficient for token usage.

## Features

- **Token-efficient exploration**: Only load the parts of CSS files that are needed
- **Component-based navigation**: Access CSS by logical component structure
- **Targeted updates**: Modify specific styles without rewriting entire files
- **Markdown output**: Human-readable output that minimizes token usage

## File Structure Requirements

The tool works best with CSS files that use a consistent component-based structure with clear section comments:

```css
/* ==============================
   Component Name Component Styles
   ============================== */

/* Style description */
.component-class {
  property: value;
}
```

## Usage Examples

### Scanning a CSS File

```python
css_explorer-scan(path="//workspace/styles/main.css")
```

Returns a Markdown overview of components and their locations.

### Getting Component Details

```python
css_explorer-get_component(path="//workspace/styles/main.css", component="Button")
```

Returns a detailed Markdown view of all styles in the Button component section.

### Updating a Style

```python
new_style = ".btn-primary {\n  background-color: #3b82f6;\n  color: white;\n  padding: 0.5rem 1rem;\n}"

css_explorer-update_style(
    path="//workspace/styles/main.css", 
    component="Button", 
    class_name=".btn-primary", 
    new_style=new_style
)
```

Updates just the `.btn-primary` style within the Button component section.