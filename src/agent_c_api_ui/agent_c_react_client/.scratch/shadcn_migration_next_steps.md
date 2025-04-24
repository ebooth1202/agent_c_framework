# shadcn/ui Migration Next Steps

## Completed Components

We've successfully completed the migration of all primary user-facing components:

1. ✅ Layout (core structure)
2. ✅ StatusBar 
3. ✅ MessagesList (with improved scrolling)
4. ✅ ChatInputArea
5. ✅ CollapsibleOptions
6. ✅ MarkdownMessage
7. ✅ UserMessage

Additionally, we've resolved critical UI issues:

1. ✅ Fixed scroll-to-top functionality allowing users to reach the first message
2. ✅ Made tool selection indicators automatically scroll into view
3. ✅ Improved spacing consistency between different message types
4. ✅ Extracted inline styles to component CSS files
5. ✅ Fixed incorrect CSS variable usage

## Recommended Next Steps

### 1. Message Components

Complete the rest of the message-related components:

- AssistantMessage
- SystemMessage
- ThoughtDisplay
- ToolCallDisplay & ToolCallItem

These components are frequently viewed by users and would benefit from consistent styling.

### 2. Tool-Related Components

Focus on tool-related components:

- ToolSelector
- ToolCallManager
- FileUploadManager
- FilesPanel

### 3. CSS Structure Review

Conduct a thorough review of the CSS structure:

- Ensure all components follow the naming conventions
- Verify all styles are properly scoped to their components
- Check for any remaining inline styles
- Validate consistent use of CSS variables

### 4. Theme Consistency

Ensure theme consistency across all components:

- Verify all components work correctly in both light and dark mode
- Ensure proper use of CSS variables for theming
- Check for any hardcoded colors or styles

### 5. Documentation

Update documentation to reflect the new component structure:

- Create usage examples for the migrated components
- Document any custom extensions to shadcn/ui components
- Update style guides with consistent patterns