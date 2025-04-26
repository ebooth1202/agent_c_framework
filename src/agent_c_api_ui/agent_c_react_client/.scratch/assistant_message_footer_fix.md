# Assistant Message Footer Improvements

## Issues Addressed

1. **Token Text Readability**
   - Increased contrast by changing color from muted foreground to regular foreground with slight opacity
   - Added font weight (500) to make text more legible
   - Added a special class for numerical values with even higher contrast (600 weight)

2. **Tool Calls Button Alignment and Visibility**
   - Increased button width from 110px to 130px to prevent text from being cut off
   - Added more padding inside the button for better visibility
   - Changed button style to use primary color for better contrast
   - Adjusted the margin to ensure proper alignment with token display
   - Made the arrow indicator larger and bold for better visibility

3. **Footer Layout and Spacing**
   - Increased the gap between elements from 0.5rem to 1rem
   - Added justify-content: space-between to distribute elements better
   - Increased minimum height from 2.5rem to 2.75rem for more breathing room
   - Improved scrollbar styling for better horizontal scrolling experience
   - Adjusted padding to ensure consistent spacing

## Mobile Improvements

- Maintained consistent height on mobile devices
- Ensured button remains properly sized (110px min-width) on mobile
- Added additional padding on mobile for better touch interactions
- Adjusted font sizes slightly for mobile readability

## Visual Enhancements

- Added subtle scrollbar styling that only appears when needed
- Improved hover states for token statistics
- Enhanced overall visual hierarchy between token numbers and labels
- Made sure the Tool Calls button stands out while maintaining a cohesive look

These changes should significantly improve the readability and usability of the assistant message footer while ensuring the tool calls button is properly displayed and aligned with the token usage statistics.