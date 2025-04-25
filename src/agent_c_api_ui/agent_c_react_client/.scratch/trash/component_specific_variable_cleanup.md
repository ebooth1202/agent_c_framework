# Component-Specific CSS Variable Cleanup

## Overview

The goal of this task is to review and standardize all component-specific CSS variables in our variables.css file to ensure they follow consistent naming patterns and are properly organized.

## Current Component-Specific Variable Categories

### Message Types

#### Variables in Light Theme
```css
--thought-background: var(--color-amber-50);
--thought-foreground: var(--foreground);
--thought-border: var(--color-amber-400);
--thought-inline-code-bg: var(--color-amber-100);
--thought-inline-code-fg: var(--color-amber-900);

--tool-call-background: var(--card);
--tool-call-border: var(--color-blue-400);
--tool-call-header-background: var(--secondary);
--tool-call-header-hover: var(--color-blue-200);
--tool-call-title: var(--secondary-foreground);
--tool-call-icon: var(--primary);

--user-message-background: var(--primary);
--user-message-foreground: var(--primary-foreground);
--user-message-border: var(--color-blue-200);

--assistant-message-background: var(--secondary);
--assistant-message-foreground: var(--foreground);
--assistant-message-border: var(--color-blue-300);

--system-message-background: var(--muted);
--system-message-foreground: var(--muted-foreground);
--system-message-border: var(--border);
```

#### Variables in Dark Theme
```css
--thought-background: var(--secondary);
--thought-foreground: hsl(210 40% 98%);
--thought-border: var(--color-blue-700);
--thought-inline-code-bg: hsla(var(--accent), 0.3);
--thought-inline-code-fg: hsl(var(--accent-foreground));

--tool-call-background: var(--secondary);
--tool-call-border: var(--color-blue-700);
--tool-call-header-background: hsla(var(--color-blue-800), 0.5);
--tool-call-header-hover: hsla(var(--color-blue-700), 0.6);
--tool-call-title: hsl(var(--color-blue-300));
--tool-call-icon: hsl(var(--primary));

--user-message-background: var(--secondary);
--user-message-foreground: hsl(var(--secondary-foreground));
--user-message-border: var(--color-blue-700);

--assistant-message-background: var(--secondary);
--assistant-message-foreground: hsl(var(--secondary-foreground));
--assistant-message-border: var(--accent);

--system-message-background: var(--secondary);
--system-message-foreground: hsl(var(--secondary-foreground));
--system-message-border: var(--border);
```

### State Colors

#### Variables in Light Theme
```css
--success: var(--color-green-600);
--success-background: var(--color-green-100);
--success-foreground: hsl(0 0% 100%);

--warning: var(--color-amber-600);
--warning-background: var(--color-amber-100);
--warning-foreground: hsl(0 0% 100%);

--info: var(--primary);
--info-background: var(--secondary);
--info-foreground: var(--primary-foreground);
```

#### Variables in Dark Theme
```css
--success: var(--color-green-400);
--success-background: var(--color-green-900);
--success-foreground: var(--color-gray-950);

--warning: var(--color-amber-400);
--warning-background: var(--color-amber-900);
--warning-foreground: var(--color-gray-950);

--info: var(--primary);
--info-background: hsl(224 64% 33%);
--info-foreground: var(--background);
```

### Component-Specific Variables

```css
--sidebar-background: 210 40% 98%;     /* Gray-50 */
--sidebar-foreground: 221 39% 11%;     /* Gray-900 */
--sidebar-primary: 221 83% 53%;        /* Blue-600 */
--sidebar-primary-foreground: 0 0% 100%; /* White */
--sidebar-accent: 269 100% 95%;        /* Purple-100 */
--sidebar-accent-foreground: 273 67% 39%; /* Purple-800 */
--sidebar-border: 214 15% 91%;         /* Gray-200 */
--sidebar-ring: 221 83% 53%;           /* Blue-600 */

--card-padding-x: var(--spacing-4);
--card-padding-y: var(--spacing-3);
--card-background: hsl(var(--card));
--card-border-color: hsl(var(--border) / 0.2);
--card-border-radius: var(--radius);
--card-shadow: var(--shadow-md);

--button-height-sm: 2rem;   /* 32px */
--button-height-md: 2.5rem;  /* 40px */
--button-height-lg: 3rem;    /* 48px */

--input-height: 2.5rem;      /* 40px */
--input-padding-x: 0.75rem;  /* 12px */
--input-border-radius: var(--border-radius-md);

--badge-padding-x: 0.75rem;  /* 12px */
--badge-padding-y: 0.25rem;  /* 4px */
--badge-font-size: var(--font-size-xs);
--badge-border-radius: var(--border-radius-full);
```

## Issues to Address

1. **Inconsistent Variable Value References**:
   - Some variables reference hsl() values, others reference var(--color-*) values
   - Some variables reference other semantic variables, some reference raw values

2. **Inconsistent Format in Light vs Dark Mode**:
   - Some dark mode variables use direct hsl() syntax, others use var() references
   - Need to ensure consistent approach between light and dark mode

3. **Inconsistent Naming between Similar Components**:
   - Different message types use slightly different naming patterns
   - Tool call variables should match message type naming pattern

4. **Missing HSL Format for Component-Specific Variables**:
   - Sidebar variables are raw HSL values, should follow shadcn/ui format
   - Component variables should use consistent reference patterns

## Standardization Approach

1. **Message Type Variables**:
   - Keep current naming pattern (component-part)
   - Ensure all references use var(--color-*) format in light mode
   - Use hsl(var(--*)) format in dark mode consistently

2. **State Color Variables**:
   - Keep current naming pattern (state-part)
   - Standardize reference format to match message types

3. **Component-Specific Variables**:
   - For sidebar, update to hsl(var(--*)) format
   - For card, button, input, badge, keep current pattern but ensure references use proper format

4. **Documentation**:
   - Add clear comments indicating the purpose of each variable section
   - Document the standardized naming pattern for future additions