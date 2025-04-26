# Chat Bubble Variables Fix

## Problem
When we implemented the Spun Pearl color palette for the light mode background colors, it inadvertently affected the chat bubble styling. This happened because some of the chat bubble components were inheriting their colors from the same variables we updated for the UI backgrounds (like `--background` and `--card`).

## Solution
Updated the message-specific CSS variables to use distinct colors that don't depend on the UI background variables. This ensures that the chat bubbles remain visually distinct regardless of theme changes.

## Changes Made

### Assistant Message (Blue tones)
- Changed background from `hsl(196, 64%, 89%)` (Link Water) to `hsl(221, 83%, 95%)` (Light blue)
- Changed foreground color for better contrast
- Kept the same border color (Cold Purple)
- Adjusted hover state

### User Message (Blue tones)
- Kept the existing blue background
- Changed text color to white for better contrast
- Adjusted border and hover state

### System Message (Purple tones)
- No changes needed as these were already distinct

### Thought Message (Amber tones)
- Changed background from `hsl(187, 82%, 94%)` (Polar) to `hsl(48, 100%, 96%)` (Very light amber)
- Kept the same foreground and border colors

### Media Message (Gray tones)
- Changed background from Polar to a light gray
- Updated all related colors to create a cohesive gray scheme
- This distinguishes media messages from regular messages

### Tool Call (Cyan tones)
- Changed background from Twilight Blue to light cyan
- Created a distinct cyan color scheme for tool calls

## Benefits

1. Each message type now has its own distinct color scheme, making them easily distinguishable
2. The colors complement the Spun Pearl palette while remaining visually separate
3. All text colors have good contrast with their backgrounds for readability
4. Changes only affect the light mode theme, preserving the dark mode styling