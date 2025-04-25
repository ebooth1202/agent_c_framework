# CSS Variable Standardization Plan

## Overview

This document outlines the step-by-step plan for standardizing our CSS variables to properly align with shadcn/ui's theming system. By following this plan, we'll ensure consistent styling across all components and prepare the application for future shadcn/ui component adoption.

## Goals

1. Standardize CSS variable naming and usage
2. Improve theme consistency between light and dark modes
3. Simplify component styling by leveraging shadcn/ui's theme variables
4. Ensure all components work correctly with theme switching

## Phase 1: Preparation

### 1.1 Create CSS Variable Inventory

- [x] Document all current CSS variables in the application
- [x] Map existing variables to shadcn/ui equivalents where possible
- [x] Identify component-specific variables that need to be preserved

### 1.2 Define Variable Update Strategy

- [x] Create transition plan for variable updates
- [x] Determine backward compatibility approach
- [x] Document usage patterns for component-specific variables

## Phase 2: Implementation

### 2.1 Update Root Variables

- [x] Update `variables.css` with shadcn/ui variable structure
- [x] Add translation layer for backward compatibility
- [x] Verify theme switching still works correctly

### 2.2 Component Updates (Batch 1 - Core Components)

- [x] Update `layout.css` (already using shadcn/ui format)
- [x] Update `cards.css` 
- [x] Update `badges.css`
- [x] Update `interactive.css` (contains button styles)
- [x] Test with theme switching

### 2.3 Component Updates (Batch 2 - Chat Interface)

- [x] Update `chat-interface.css` (already using shadcn/ui format)
- [x] Update `messages-list.css` (already using Tailwind classes)
- [x] Check message type CSS files (already using Tailwind classes)
- [x] Update `tool-call-display.css`
- [x] Update `tool-call-item.css`
- [x] Test with theme switching

### 2.4 Component Updates (Batch 3 - File Handling)

- [x] Check `files-panel.css` (already using Tailwind classes)
- [x] Check `file-item.css` (already using Tailwind classes)
- [x] Check `file-upload-manager.css` (already using Tailwind classes)
- [x] Check `drag-drop-area.css` (already using Tailwind classes)
- [x] Check `drag-drop-overlay.css` (already using Tailwind classes)
- [x] Test with theme switching

### 2.5 Component Updates (Batch 4 - Remaining Components)

- [x] Update `markdown-message.css`
- [x] Update remaining component CSS files:
  - [x] agent-config-display.css (already using shadcn/ui format)
  - [x] agent-config-hover-card.css (already using shadcn/ui format)
  - [x] animated-status-indicator.css
  - [x] app-sidebar.css (already using shadcn/ui format) 
  - [x] chat-input-area.css (already minimal and doesn't need changes)
  - [x] collapsible-options.css (already using Radix data attributes correctly)
  - [x] media-message.css
  - [x] model-parameter-controls.css
  - [x] page-header.css (empty reference file)
  - [x] parameter-documentation.css
  - [x] persona-selector.css
  - [x] status-bar.css
  - [x] tool-call-item-integrated.css
  - [x] tool-call-item.css
- [x] Test with theme switching

## Phase 3: Cleanup and Verification

### 3.1 Remove Backwards Compatibility Layer

- [x] Remove legacy variable definitions after all components are updated
- [x] Verify no legacy variables are being used

### 3.2 Final Testing

- [x] Test all components in light mode
- [x] Test all components in dark mode
- [x] Test theme switching
- [x] Verify consistent styling across all components

### 3.3 Component-Specific Variable Cleanup

- [x] Review component-specific variables in variables.css
- [x] Standardize naming patterns and organization
- [x] Update variables.css with improved organization and comments
- [x] Enhance AnimatedStatusIndicator with standardized state variables
- [x] Document component-specific theme extensions

## Tracking

| Component CSS File | Current Status | Updated to shadcn/ui | Tested | Notes |
|-------------------|----------------|---------------------|--------|-------|
| `variables.css` | Updated | Yes | Yes | Improved organization and comments |
| `layout.css` | Updated | Yes | Yes | No changes needed, already compatible |
| `cards.css` | Updated | Yes | Yes | Updated to use shadcn/ui variables |
| `badges.css` | Updated | Yes | Yes | Updated to use shadcn/ui variables |
| `interactive.css` | Updated | Yes | Yes | Updated to use shadcn/ui variables |
| `chat-interface.css` | Updated | Yes | Yes | Already using shadcn/ui variables |
| `tool-selector.css` | Updated | Yes | Yes | Already using shadcn/ui variables |
| `files-panel.css` | Updated | Yes | Yes | Already using Tailwind classes |
| `animated-status-indicator.css` | Enhanced | Yes | Yes | Added state-specific colors |

## Potential Issues

1. Components with hardcoded colors or non-variable styling
2. Complex CSS selectors that may need refactoring
3. Custom component styles that don't map well to shadcn/ui variables
4. Dark mode inconsistencies when switching themes

## Best Practices

1. Use `hsl(var(--variable))` syntax for shadcn/ui variables
2. Use opacity modifiers with the format `hsl(var(--variable) / 0.5)` for transparency
3. Keep component-specific variables semantically named for clarity
4. Test each batch of changes before moving to the next batch
5. Use the browser inspector to verify CSS variable usage and values