# Chat Message Customization

## Overview

I've standardized the chat message bubbles and ensured each message type has its own set of dedicated color variables for both light and dark themes.

## Message Types and Variables

Each message type now has a dedicated set of variables:

### Assistant Message
- `--assistant-message-background`: Background color of the message bubble
- `--assistant-message-foreground`: Text color within the message
- `--assistant-message-border`: Border color of the message bubble
- `--assistant-message-hover`: Hover state background color

### User Message
- `--user-message-background`: Background color of the message bubble
- `--user-message-foreground`: Text color within the message
- `--user-message-border`: Border color of the message bubble
- `--user-message-hover`: Hover state background color

### System Message
- `--system-message-background`: Background color of the message bubble
- `--system-message-foreground`: Text color within the message
- `--system-message-border`: Border color of the message bubble
- `--system-message-hover`: Hover state background color

### Thought Message
- `--thought-background`: Background color of the message bubble
- `--thought-foreground`: Text color within the message
- `--thought-border`: Border color of the message bubble
- `--thought-hover`: Hover state background color
- `--thought-inline-code-bg`: Background color for inline code
- `--thought-inline-code-fg`: Text color for inline code

### Media Message
- `--media-message-background`: Background color of the message card
- `--media-message-foreground`: Text color within the message
- `--media-message-border`: Border color of the message card
- `--media-message-hover`: Hover state background color
- `--media-message-header-background`: Background color of the header
- `--media-message-header-hover`: Header hover background color
- `--media-message-header-icon`: Color of icons in the header
- `--media-message-header-title`: Color of the title text
- `--media-message-action-icon`: Color of action icons
- `--media-message-action-hover`: Hover color for action icons
- `--media-message-metadata-border`: Border color for metadata section
- `--media-message-metadata-color`: Text color for metadata

## Theming

These variables are defined separately for light and dark modes in the `variables.css` file. The dark mode specifically uses colors from the Cold Autumn Forest Grunge color palette:

### Cold Autumn Forest Grunge Palette (Dark Mode)

1. **Rangoon (#1a1914)** - rgb(26, 25, 20)
   - Main background color

2. **Rangitoto (#25241e)** - rgb(37, 36, 30)
   - Card and popover backgrounds

3. **Heavy Metal (#32352e)** - rgb(50, 53, 46)
   - Secondary and muted UI elements

4. **Kelp (#44442f)** - rgb(68, 68, 47)
   - Accent colors, rings, and interactive elements

5. **Mako (#3f4146)** - rgb(63, 65, 70)
   - Borders and contrasting elements

## Media Message Styling

The Media Message component has been updated to use dedicated variables for consistent styling with the Forest theme. The component now includes:

- Forest-toned background and text colors
- Olive-green accents for headers and icons
- Consistent border and hover states
- Proper variable usage throughout the component CSS

The DialogContent in the fullscreen view now properly uses the media message background variable to ensure consistent styling across all states.

## How to Customize

To customize the appearance of any message type:

1. Locate the appropriate section in `variables.css`
2. Modify the variable values for either light mode (`:root`) or dark mode (`.dark`)
3. All components will automatically reflect the new styling

This standardization makes it easy to create cohesive themes across the application while allowing each message type to have its own distinct visual identity.