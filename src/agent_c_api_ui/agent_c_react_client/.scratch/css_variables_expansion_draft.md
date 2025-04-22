# CSS Variables Expansion Draft

After auditing the first 6 components, I've identified several categories of hardcoded values that should be converted to variables. Here's a proposal for expanding our variables.css file:

```css
/* ===== COMMON: CSS Variables ===== */
/* Description: Global CSS variables for consistent styling across the application */

:root {
  /* Colors - Base */
  --color-primary: 211 96% 62%;
  --color-primary-foreground: 0 0% 100%;
  
  --color-secondary: 217 91% 60%;
  --color-secondary-foreground: 0 0% 100%;
  
  --color-accent: 250 95% 76%;
  --color-accent-foreground: 0 0% 100%;
  
  --color-background: 224 71% 4%;
  --color-foreground: 0 0% 100%;
  
  /* Colors - UI Elements */
  --color-card: 222 47% 11%;
  --color-card-foreground: 0 0% 100%;
  
  --color-popover: 222 47% 11%;
  --color-popover-foreground: 0 0% 100%;
  
  --color-border: 217 33% 17%;
  --color-input: 217 33% 17%;
  
  /* Colors - State */
  --color-success: 142 71% 45%;
  --color-warning: 38 92% 50%;
  --color-error: 0 84% 60%;
  --color-info: 211 96% 62%;
  
  /* NEW: Colors - Gray Scale */
  --color-gray-50: 210 40% 98%;
  --color-gray-100: 214 32% 91%;
  --color-gray-200: 214 15% 91%;
  --color-gray-300: 212 10% 83%;
  --color-gray-400: 217 10% 65%;
  --color-gray-500: 220 9% 46%;
  --color-gray-600: 215 14% 34%;
  --color-gray-700: 217 19% 27%;
  --color-gray-800: 215 28% 17%;
  --color-gray-900: 221 39% 11%;
  --color-gray-950: 224 71% 4%;

  /* NEW: Colors - Blue Scale */
  --color-blue-50: 214 100% 97%;
  --color-blue-100: 214 95% 93%;
  --color-blue-200: 213 97% 87%;
  --color-blue-300: 212 96% 78%;
  --color-blue-400: 213 94% 68%;
  --color-blue-500: 217 91% 60%;
  --color-blue-600: 221 83% 53%;
  --color-blue-700: 224 76% 48%;
  --color-blue-800: 226 71% 40%;
  --color-blue-900: 224 64% 33%;
  
  /* NEW: Colors - Purple Scale */
  --color-purple-50: 270 100% 98%;
  --color-purple-100: 269 100% 95%;
  --color-purple-200: 268 100% 92%;
  --color-purple-300: 268 100% 87%;
  --color-purple-400: 270 95% 75%;
  --color-purple-500: 271 91% 65%;
  --color-purple-600: 271 81% 56%;
  --color-purple-700: 272 72% 47%;
  --color-purple-800: 273 67% 39%;
  --color-purple-900: 274 66% 32%;

  /* NEW: Colors - Green Scale */
  --color-green-50: 138 76% 97%;
  --color-green-100: 141 84% 93%;
  --color-green-200: 141 79% 85%;
  --color-green-300: 142 77% 73%;
  --color-green-400: 142 69% 58%;
  --color-green-500: 142 71% 45%;
  --color-green-600: 142 76% 36%;
  --color-green-700: 142 72% 29%;
  --color-green-800: 143 64% 24%;
  --color-green-900: 144 61% 20%;

  /* NEW: Colors - Amber Scale */
  --color-amber-50: 48 100% 96%;
  --color-amber-100: 48 96% 89%;
  --color-amber-200: 48 97% 77%;
  --color-amber-300: 46 97% 65%;
  --color-amber-400: 43 96% 56%;
  --color-amber-500: 38 92% 50%;
  --color-amber-600: 32 95% 44%;
  --color-amber-700: 26 90% 37%;
  --color-amber-800: 23 83% 31%;
  --color-amber-900: 22 78% 26%;
  
  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  --font-mono: 'JetBrains Mono', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  
  /* NEW: Font Sizes */
  --font-size-xs: 0.75rem;     /* 12px */
  --font-size-sm: 0.875rem;    /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg: 1.125rem;    /* 18px */
  --font-size-xl: 1.25rem;     /* 20px */
  --font-size-2xl: 1.5rem;     /* 24px */
  --font-size-3xl: 1.875rem;   /* 30px */
  --font-size-4xl: 2.25rem;    /* 36px */
  
  /* NEW: Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Spacing */
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
  
  /* Borders */
  --border-radius-sm: 0.125rem;  /* 2px */
  --border-radius-md: 0.375rem;  /* 6px */
  --border-radius-lg: 0.5rem;    /* 8px */
  --border-radius-xl: 0.75rem;   /* 12px */
  --border-radius-2xl: 1rem;     /* 16px */
  --border-radius-full: 9999px;  /* Fully rounded */
  
  /* NEW: Border Widths */
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 3px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
  
  /* NEW: Specific Transitions */
  --transition-hover: 200ms ease;
  --transition-fade: 200ms ease-out;
  --transition-slide: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Z-index layers */
  --z-index-dropdown: 10;
  --z-index-sticky: 20;
  --z-index-fixed: 30;
  --z-index-modal-backdrop: 40;
  --z-index-modal: 50;
  --z-index-popover: 60;
  --z-index-tooltip: 70;
  
  /* NEW: Component-specific variables */
  
  /* Layout Component */
  --layout-max-width: 80rem; /* 1280px */
  
  /* Card Components */
  --card-padding-x: var(--spacing-4);
  --card-padding-y: var(--spacing-3);
  --card-background: white;
  --card-border-color: hsl(var(--color-border) / 0.2);
  --card-border-radius: var(--border-radius-lg);
  --card-shadow: var(--shadow-md);
  
  /* Button Components */
  --button-height-sm: 2rem;   /* 32px */
  --button-height-md: 2.5rem;  /* 40px */
  --button-height-lg: 3rem;    /* 48px */
  
  /* Input Components */
  --input-height: 2.5rem;      /* 40px */
  --input-padding-x: 0.75rem;  /* 12px */
  --input-border-radius: var(--border-radius-md);
  
  /* Badge Components */
  --badge-padding-x: 0.75rem;  /* 12px */
  --badge-padding-y: 0.25rem;  /* 4px */
  --badge-font-size: var(--font-size-xs);
  --badge-border-radius: var(--border-radius-full);
}
```

## Implementation Strategy

1. Update variables.css with these expanded variables

2. For component CSS files, implement the following substitutions:

### Text Colors
- Replace `#111827` with `hsl(var(--color-gray-900))`
- Replace `#f9fafb` with `hsl(var(--color-gray-50))`
- Replace `#4b5563` with `hsl(var(--color-gray-600))`
- Replace `#6b7280` with `hsl(var(--color-gray-500))`
- Replace `#9ca3af` with `hsl(var(--color-gray-400))`

### UI Element Colors
- Replace `white` with `var(--card-background)` for card backgrounds
- Replace `#f3f4f6` with `hsl(var(--color-gray-100))`
- Replace `#1f2937` with `hsl(var(--color-gray-800))`
- Replace `#374151` with `hsl(var(--color-gray-700))`
- Replace `#e5e7eb` with `hsl(var(--color-gray-200))`

### Spacing
- Replace `0.25rem` with `var(--spacing-1)`
- Replace `0.5rem` with `var(--spacing-2)`
- Replace `0.75rem` with `var(--spacing-3)`
- Replace `1rem` with `var(--spacing-4)`
- Replace `1.5rem` with `var(--spacing-6)`

### Typography
- Replace `0.75rem` with `var(--font-size-xs)`
- Replace `0.875rem` with `var(--font-size-sm)`
- Replace `1rem` with `var(--font-size-base)`
- Replace `1.25rem` with `var(--font-size-xl)`
- Replace `1.5rem` with `var(--font-size-2xl)`

### Transitions
- Replace `0.2s ease` with `var(--transition-hover)`

## Next Steps

1. Update variables.css with expanded variables
2. Create a common-elements.css file for shared UI patterns
3. Begin updating component CSS files systematically
4. Test and validate changes