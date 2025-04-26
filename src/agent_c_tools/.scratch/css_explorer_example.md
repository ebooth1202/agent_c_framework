# CSS Explorer Tool Usage Examples

## Scanning a CSS File

This example scans a CSS file to identify all component sections and their styles.

```python
result = css_explorer-scan(path="//tools/.scratch/test_styles.css")
```

Expected output:

```markdown
# CSS Explorer: /tools/.scratch/test_styles.css

- File size: 145 lines, 4326 characters
- Components found: 3

## Component Sections:

- **Layout** (lines 11-31): 3 styles
- **ThoughtDisplay** (lines 33-52): 2 styles
- **Button** (lines 54-92): 4 styles
```

## Getting Component Details

This example gets detailed information about a specific component's styles.

```python
result = css_explorer-get_component(
    path="//tools/.scratch/test_styles.css", 
    component="Button"
)
```

Expected output:

```markdown
# Component: Button

- Location: lines 54-92
- Styles: 4

## Styles:

### .btn-primary
*Primary button*

Lines: 57-65

```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  background-color: #2563eb; /* bg-blue-600 */
  color: white;
  transition: background-color 150ms;
}
```

### .btn-primary:hover
*Primary button hover state*

Lines: 68-70

```css
.btn-primary:hover {
  background-color: #1d4ed8; /* bg-blue-700 */
}
```

...
```

## Updating a Specific Style

This example updates a specific style within a component section.

```python
new_style = ".btn-primary {\n  display: inline-flex;\n  align-items: center;\n  justify-content: center;\n  border-radius: 0.5rem;\n  padding: 0.75rem 1.25rem;\n  font-weight: 600;\n  background-color: #3b82f6; /* bg-blue-500 */\n  color: white;\n  transition: all 200ms;\n}"

result = css_explorer-update_style(
    path="//tools/.scratch/test_styles.css", 
    component="Button", 
    class_name=".btn-primary", 
    new_style=new_style
)
```

Expected output:

```markdown
# Style Update Successful

- Component: **Button**
- Selector: **.btn-primary**
- Lines updated: 57-65

```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  background-color: #3b82f6; /* bg-blue-500 */
  color: white;
  transition: all 200ms;
}
```
```

## Benefits

1. **Token Efficiency**: Instead of loading the entire 145-line CSS file (4326 characters), you can load just the Button component (38 lines, ~1000 characters) or even a single style (10 lines, ~300 characters).

2. **Targeted Updates**: When making changes, you only need to replace the specific style block rather than the entire file.

3. **Structural Understanding**: The tool helps you navigate the component structure of large CSS files without having to scan through them manually.