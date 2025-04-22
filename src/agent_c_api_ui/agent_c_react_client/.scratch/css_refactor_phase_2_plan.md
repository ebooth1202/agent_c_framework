# CSS Refactoring Phase 2 Plan

## Overview

After successfully completing Phase 1 (structure standardization), we'll now focus on Phase 2: reorganizing, consolidating, and optimizing our CSS styles. This phase will make the codebase more maintainable and reduce redundancy.

## Goals

1. Convert all remaining components to the new format
2. Identify and consolidate duplicate styles
3. Create a "Common" section for shared styles
4. Define CSS variables for consistent values
5. Add a comprehensive file header and table of contents

## Implementation Strategy

### Step 1: Finish Component Conversion

Convert all remaining components to the new format, focusing on 2-3 components per session:

1. **Group 1**: AgentConfigDisplay, AgentConfigHoverCard, MobileNav
2. **Group 2**: PersonaSelector, StatusBar, ToolCallDisplay
3. **Group 3**: ChatInputArea, FileItem, MediaMessage
4. **Group 4**: ModelParameterControls, AnimatedStatusIndicator, DragDropOverlay
5. **Group 5**: PageHeader, Sidebar, TokenUsageDisplay

### Step 2: Audit and Analysis

After converting a group of components:

1. Analyze for duplicate styles or patterns
2. Identify common values that could be CSS variables
3. Document findings in analysis files

### Step 3: Create Common Styles Section

Once all components are in the new format:

1. Create a "Common" section at the top of the file
2. Extract shared styles like buttons, inputs, cards
3. Update component-specific styles to use common classes where appropriate

### Step 4: Implement CSS Variables

1. Define variables for colors, spacing, typography, etc.
2. Update component styles to use the variables
3. Ensure dark mode support with variable overrides

### Step 5: Add File Structure

1. Create comprehensive file header with documentation
2. Add table of contents listing all components
3. Organize components in logical groups

## Tools and Methodology

1. Use `css_overview` to get a bird's-eye view of the CSS file
2. Use `css_get_component` to extract specific components
3. Use `css_get_style_source` to examine individual styles
4. Use `css_update_style` for targeted updates
5. Document progress in tracking file

## Testing and Verification

After each component group is updated:

1. Verify the CSS is syntactically valid
2. Test the affected components in the UI
3. Check both light and dark mode appearance

## Timeline

- **Session 1**: Group 1 conversion and analysis
- **Session 2**: Group 2 conversion and analysis
- **Session 3**: Group 3 conversion and analysis
- **Session 4**: Group 4 conversion and analysis
- **Session 5**: Group 5 conversion and analysis
- **Session 6**: Create common styles section
- **Session 7**: Implement CSS variables
- **Session 8**: Add file structure and final cleanup