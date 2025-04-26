# Spun Pearl Color Palette Implementation Plan

## Colors in the Palette

1. Cold Purple: #aab0de - rgb(170, 176, 222)
2. Jagged Ice: #bbdae6 - rgb(187, 218, 230)
3. Link Water: #d4ecf3 - rgb(212, 236, 243)
4. Polar: #e7f7fa - rgb(231, 247, 250)
5. Twilight Blue: #f7ffff - rgb(247, 255, 255)

## Conversion to HSL Format

Since our CSS variables use HSL format, I need to convert the RGB values:

1. Cold Purple: hsl(234, 52%, 77%)
2. Jagged Ice: hsl(196, 47%, 82%)
3. Link Water: hsl(196, 64%, 89%)
4. Polar: hsl(187, 82%, 94%)
5. Twilight Blue: hsl(180, 100%, 99%)

## Mapping to Theme Variables

I'll map these colors to our theme variables in a way that creates a beautiful, harmonious light theme:

### Main Background Colors
- `--background`: Link Water (hsl(196, 64%, 89%)) - Main app background
- `--card`: Polar (hsl(187, 82%, 94%)) - Card backgrounds
- `--popover`: Twilight Blue (hsl(180, 100%, 99%)) - Popovers, dropdowns
- `--muted`: Jagged Ice (hsl(196, 47%, 82%)) - Muted elements
- `--accent`: Cold Purple (hsl(234, 52%, 77%)) - Accent elements

### Sidebar-specific
- `--sidebar-background`: Polar (hsl(187, 82%, 94%)) - Sidebar background
- `--sidebar-accent`: Cold Purple (hsl(234, 52%, 77%)) - Sidebar accents

### Message Backgrounds
- Update message backgrounds to complement the new palette while maintaining distinctiveness

### Borders
- Adjust border colors to be slightly darker versions of their corresponding backgrounds

## Changes to Make

1. Update the light mode theme variables in `variables.css`
2. Verify theme compatibility and transitions between light/dark modes
3. Test the new palette with all components

## Testing Plan

1. Verify the light mode has the correct Spun Pearl colors
2. Ensure dark mode is unaffected by these changes
3. Test theme switching to ensure smooth transitions
4. Check all components for color consistency
5. Verify text contrast for accessibility

## Implementation Complete

The Spun Pearl color palette has been successfully implemented for the light mode theme. The following changes were made:

### Main Background Colors
- Changed `--background` to Link Water (hsl(196, 64%, 89%))
- Changed `--card` to Polar (hsl(187, 82%, 94%))
- Changed `--popover` to Twilight Blue (hsl(180, 100%, 99%))
- Changed `--muted` to Jagged Ice (hsl(196, 47%, 82%))
- Changed `--accent` to Cold Purple (hsl(234, 52%, 77%))
- Updated related border and input colors to match the new palette

### Sidebar Colors
- Changed `--sidebar-background` to Polar (hsl(187, 82%, 94%))
- Changed `--sidebar-accent` to Cold Purple (hsl(234, 52%, 77%))
- Updated sidebar border color to match the new palette

### Message Backgrounds
- Updated assistant message background to Link Water
- Updated assistant message border to Cold Purple
- Updated thought message background to Polar
- Updated media message background to Polar
- Updated media message header to Jagged Ice
- Updated tool call background to Twilight Blue
- Updated tool call header to Jagged Ice

The dark mode theme remains unchanged, ensuring that users who prefer dark mode will still have a consistent experience.