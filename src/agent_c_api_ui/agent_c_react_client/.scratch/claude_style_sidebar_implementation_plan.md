# Claude-Style Sidebar Implementation Plan

## Overview

This plan details how to modify our current sidebar implementation to match the Claude UI style shown in the image. The key difference is that Claude has a two-level sidebar:

1. A narrow sidebar with only icons that's always visible
2. An expanded sidebar with text labels that can be toggled

Our current implementation has an offcanvas sidebar that completely hides when collapsed.

## Current Implementation

- SidebarProvider manages open/closed state
- Sidebar component handles rendering the sidebar
- When collapsed, the sidebar is completely hidden (offcanvas mode)
- A floating toggle button appears when the sidebar is hidden

## Required Changes

### 1. Modify the Sidebar Component

- Change the collapsible mode from "offcanvas" to "icon" by default
- Adjust the width variables: 
  - Default width for expanded view: `--sidebar-width` (currently 16rem)
  - Width for icon-only view: `--sidebar-width-icon` (currently 3rem)
- Ensure the sidebar is always visible, even in collapsed state

### 2. Update AppSidebar Component

- Modify the AppSidebar component to use the new collapsible mode
- Update the sidebar layout to accommodate the always-visible icon sidebar
- Add proper icon display for collapsed state

### 3. CSS Modifications

- Update app-sidebar.css to accommodate the new layout
- Modify sidebar-toggle.css to adapt to the new behavior
- Ensure proper transitions between states

### 4. Layout Adjustments

- Update the layout component to handle the new sidebar width calculations
- Ensure content properly adjusts when sidebar changes state

## Implementation Steps

1. Update the SidebarProvider in AppSidebar.jsx to use "icon" collapsible mode
2. Modify the sidebar component CSS classes for proper display
3. Update the nav links to ensure they display properly in both modes
4. Update the floating toggle behavior
5. Test the implementation in different screen sizes
6. Ensure proper responsive behavior on mobile

## Considerations

- Mobile behavior should remain similar to current (sheet overlay)
- Animation smoothness between states
- Ensure proper accessibility
- Content adjustment to prevent layout shifts