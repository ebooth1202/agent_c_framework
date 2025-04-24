# CSS Variable Mapping: shadcn/ui vs. Custom

This document maps the shadcn/ui CSS variables to our custom CSS variables for theming consolidation.

## Core Theme Variables

| shadcn/ui Variable | Custom Variable | Notes |
|-------------------|----------------|-------|
| `--background` | `--theme-background` | Main background color |
| `--foreground` | `--theme-foreground` | Main text color |
| `--card` | `--theme-card` | Card background color |
| `--card-foreground` | `--theme-card-foreground` | Card text color |
| `--popover` | `--theme-popover` | Popover background color |
| `--popover-foreground` | `--theme-popover-foreground` | Popover text color |
| `--primary` | `--theme-primary` | Primary action color |
| `--primary-foreground` | `--theme-primary-foreground` | Primary action text color |
| `--secondary` | `--theme-secondary` | Secondary action color |
| `--secondary-foreground` | `--theme-secondary-foreground` | Secondary action text color |
| `--muted` | `--theme-muted` | Muted background color |
| `--muted-foreground` | `--theme-muted-foreground` | Muted text color |
| `--accent` | `--theme-accent` | Accent color |
| `--accent-foreground` | `--theme-accent-foreground` | Accent text color |
| `--destructive` | `--theme-error` | Error/destructive color |
| `--destructive-foreground` | `--theme-error-foreground` | Error/destructive text color |
| `--border` | `--theme-border` | Border color |
| `--input` | `--theme-input` | Input border color |
| `--ring` | N/A | Focus ring color (no direct equivalent) |
| `--radius` | `--border-radius-lg` | Border radius |

## Additional Custom Variables

Our custom variables include additional semantic categories not present in shadcn/ui:

1. **State Colors**:
   - `--theme-success`, `--theme-success-background`, `--theme-success-foreground`
   - `--theme-warning`, `--theme-warning-background`, `--theme-warning-foreground`
   - `--theme-info`, `--theme-info-background`, `--theme-info-foreground`

2. **Component-specific Colors**:
   - `--theme-thought-background`, `--theme-thought-foreground`, `--theme-thought-border`
   - `--theme-tool-call-background`, `--theme-tool-call-border`, etc.
   - `--theme-user-message-background`, `--theme-assistant-message-background`, etc.

3. **Typography, Spacing, and Other Design Tokens**:
   - Font families, sizes, weights
   - Spacing values
   - Shadow values
   - Z-index values

## Transition Plan

For our transition strategy:

1. First, ensure all shadcn/ui components use their native variables
2. For custom components, gradually transition from custom variables to shadcn/ui variables
3. Keep component-specific variables that don't have shadcn/ui equivalents
4. Potentially extend the shadcn/ui theme with our additional semantic variables using the same naming convention