# Light Mode Improvement Plan

## Analysis

Based on the screenshot and code review, the following issues are apparent in the light mode:

1. **Background & Contrast Issues**:
   - The blue-tinted background (Link Water #d4ecf3) doesn't provide enough contrast with message bubbles
   - Multiple competing blue tones create visual noise
   - Tool call displays use yellow/amber tones that clash with the blue theme

2. **Visual Hierarchy Problems**:
   - Message bubbles don't stand out clearly from the background
   - Cards and containers lack sufficient depth/shadow
   - Border colors are too similar to background colors

3. **Color Scheme Inconsistency**:
   - Mix of blue, yellow, and purple tones without clear purpose
   - Insufficient contrast for text in some areas
   - Shadcn components don't fully integrate with the custom theme

## Improvement Approach

1. **Refined Color Palette**:
   - Create a more neutral base background (lighter, less saturated)
   - Use a consistent accent color for interactive elements
   - Ensure message bubbles have clear visual separation

2. **Enhanced Contrast & Readability**:
   - Strengthen borders and shadows for better component separation
   - Improve text contrast throughout the interface
   - Use more distinct colors for different message types

3. **Professional Polish**:
   - Apply subtle gradients and shadows for depth
   - Use a more coherent color story with intentional accent colors
   - Ensure tool displays are visually aligned with the rest of the UI

## Implementation Details

I'll modify the CSS variables in `variables.css` to create a cleaner, more professional light mode while keeping dark mode intact.

Key changes will include:

1. Lightening the background color and reducing saturation
2. Creating a more coherent color system with better contrast
3. Enhancing shadows and borders for better component separation
4. Refining the message type styles for clearer differentiation