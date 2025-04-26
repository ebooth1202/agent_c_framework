# CSS Explorer Tools - Model Instructions

The CSS Explorer tools provide efficient ways to navigate, analyze, and manipulate CSS files with component-based structure. These tools are particularly useful for working with large CSS files without loading their entire content, saving tokens and improving efficiency.

## Available CSS Explorer Tools

### 1. `css_overview`

Provides a high-level overview of a CSS file's structure, identifying component sections and their styles.

**Parameters:**
- `path` (required): UNC-style path to the CSS file (e.g., `//WORKSPACE/path/to/file.css`)

**Example:**
```
css_overview(path="//workspace/styles/components.css")
```

**Returns:**
A markdown overview containing:
- File size (lines and characters)
- Number of components found
- List of component sections with line numbers and style counts

### 2. `css_get_component`

Retrieves detailed information about a specific component's styles from a CSS file.

**Parameters:**
- `path` (required): UNC-style path to the CSS file
- `component` (required): Name of the component to extract styles for

**Example:**
```
css_get_component(path="//workspace/styles/components.css", component="Button")
```

**Returns:**
A markdown document containing:
- Component details (name, line numbers)
- List of styles with selectors, descriptions, and formatted content

### 3. `css_update_style`

Updates a specific CSS class within a component section without rewriting the entire file.

**Parameters:**
- `path` (required): UNC-style path to the CSS file
- `component` (required): Name of the component containing the style
- `class_name` (required): Name of the CSS class to update (selector)
- `new_style` (required): New style definition including the selector and braces

**Example:**
```
css_update_style(
    path="//workspace/styles/components.css", 
    component="Button", 
    class_name=".btn-primary", 
    new_style=".btn-primary {\n  display: flex;\n  padding: 0.75rem;\n  background-color: blue;\n}"
)
```

**Returns:**
A markdown report of the update operation with component name, selector, and line numbers updated.

### 4. `css_get_component_source`

Retrieves the raw CSS source for a specific component, including its header comment and all styles.

**Parameters:**
- `path` (required): UNC-style path to the CSS file
- `component` (required): Name of the component to extract source for

**Example:**
```
css_get_component_source(path="//workspace/styles/components.css", component="Button")
```

**Returns:**
Raw CSS source code for the component including header comment and all styles.

### 5. `css_get_style_source`

Retrieves the raw CSS source for a specific style within a component, including its preceding comment.

**Parameters:**
- `path` (required): UNC-style path to the CSS file
- `component` (required): Name of the component containing the style
- `class_name` (required): Name of the CSS class to get source for (selector)

**Example:**
```
css_get_style_source(
    path="//workspace/styles/components.css", 
    component="Button", 
    class_name=".btn-primary"
)
```

**Returns:**
Raw CSS source code for the style including its preceding comment.

## Best Practices for Using CSS Explorer Tools

1. **Start with an overview**:
   - Use `css_overview` first to understand the structure of the CSS file
   - Note component names and their line ranges for further exploration

2. **Explore specific components**:
   - After identifying interesting components, use `css_get_component` to see all styles
   - This avoids loading the entire file when only certain components are relevant

3. **Examine raw source when needed**:
   - Use `css_get_component_source` when you need to see the exact formatting and comments
   - Use `css_get_style_source` when focusing on a specific selector and its comment

4. **Make targeted updates**:
   - Update individual styles using `css_update_style` instead of rewriting the entire file
   - Preserve the existing structure and comment patterns when creating new styles

5. **Handle errors gracefully**:
   - All tools return error messages when components or styles aren't found
   - Use these error messages to discover available components/styles

## Workflow Example

1. **Exploration phase**:
   ```
   # First get an overview of the CSS file
   css_overview(path="//workspace/styles/main.css")
   
   # Then examine a specific component of interest
   css_get_component(path="//workspace/styles/main.css", component="Button")
   ```

2. **Modification phase**:
   ```
   # Get the exact source for a style you want to modify
   css_get_style_source(
       path="//workspace/styles/main.css", 
       component="Button", 
       class_name=".btn-primary"
   )
   
   # Update the style with your changes
   css_update_style(
       path="//workspace/styles/main.css", 
       component="Button", 
       class_name=".btn-primary", 
       new_style=".btn-primary {\n  display: flex;\n  padding: 0.75rem;\n  background-color: #3b82f6;\n}"
   )
   ```

## Using CSS Explorer with Component-Based Design

These tools are optimized for CSS files that follow a component-based structure with:

1. Component sections marked with header comments:
   ```css
   /* ==============================
      Component Name Component Styles
      ============================== */
   ```

2. Individual styles with descriptive comments:
   ```css
   /* Description of the style */
   .selector {
     property: value;
   }
   ```

By maintaining this structure, you can efficiently navigate and modify large CSS files without the token overhead of loading entire files.