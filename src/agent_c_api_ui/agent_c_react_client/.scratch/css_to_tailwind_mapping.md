# CSS to Tailwind/shadcn/ui Mapping

## Common CSS Patterns and Their Tailwind Equivalents

### Layout and Positioning

| CSS Pattern | Tailwind Equivalent | Notes |
|------------|---------------------|-------|
| `display: flex;` | `flex` | Basic flex container |
| `flex-direction: column;` | `flex-col` | Vertical flex layout |
| `justify-content: space-between;` | `justify-between` | Space items evenly |
| `justify-content: center;` | `justify-center` | Center items horizontally |
| `align-items: center;` | `items-center` | Center items vertically |
| `gap: var(--spacing-4);` | `gap-4` | Add space between flex/grid items |
| `max-width: var(--layout-max-width);` | `max-w-7xl` | Container max width |
| `margin-left: auto; margin-right: auto;` | `mx-auto` | Center block element |
| `position: relative;` | `relative` | Set relative positioning |
| `position: absolute;` | `absolute` | Set absolute positioning |
| `min-height: 100vh;` | `min-h-screen` | Minimum height of viewport |

### Spacing (Margins and Padding)

| CSS Variable | Tailwind Equivalent | Notes |
|-------------|---------------------|-------|
| `--spacing-1` (0.25rem) | `p-1`, `m-1` | 4px spacing |
| `--spacing-2` (0.5rem) | `p-2`, `m-2` | 8px spacing |
| `--spacing-3` (0.75rem) | `p-3`, `m-3` | 12px spacing |
| `--spacing-4` (1rem) | `p-4`, `m-4` | 16px spacing |
| `--spacing-5` (1.25rem) | `p-5`, `m-5` | 20px spacing |
| `--spacing-6` (1.5rem) | `p-6`, `m-6` | 24px spacing |
| `--spacing-8` (2rem) | `p-8`, `m-8` | 32px spacing |
| `--spacing-10` (2.5rem) | `p-10`, `m-10` | 40px spacing |
| `--spacing-12` (3rem) | `p-12`, `m-12` | 48px spacing |
| `--spacing-16` (4rem) | `p-16`, `m-16` | 64px spacing |

### Typography

| CSS Variable/Pattern | Tailwind Equivalent | Notes |
|---------------------|---------------------|-------|
| `--font-size-xs` (0.75rem) | `text-xs` | 12px font size |
| `--font-size-sm` (0.875rem) | `text-sm` | 14px font size |
| `--font-size-base` (1rem) | `text-base` | 16px font size |
| `--font-size-lg` (1.125rem) | `text-lg` | 18px font size |
| `--font-size-xl` (1.25rem) | `text-xl` | 20px font size |
| `--font-size-2xl` (1.5rem) | `text-2xl` | 24px font size |
| `--font-weight-normal` (400) | `font-normal` | Normal font weight |
| `--font-weight-medium` (500) | `font-medium` | Medium font weight |
| `--font-weight-semibold` (600) | `font-semibold` | Semibold font weight |
| `--font-weight-bold` (700) | `font-bold` | Bold font weight |
| `font-family: var(--font-sans)` | `font-sans` | Sans-serif font family |
| `font-family: var(--font-mono)` | `font-mono` | Monospace font family |

### Borders and Shadows

| CSS Variable/Pattern | Tailwind Equivalent | Notes |
|---------------------|---------------------|-------|
| `--border-radius-sm` (0.125rem) | `rounded-sm` | Small border radius |
| `--border-radius-md` (0.375rem) | `rounded-md` | Medium border radius |
| `--border-radius-lg` (0.5rem) | `rounded-lg` | Large border radius |
| `--border-radius-xl` (0.75rem) | `rounded-xl` | Extra large border radius |
| `--border-radius-2xl` (1rem) | `rounded-2xl` | 2x large border radius |
| `--border-radius-full` | `rounded-full` | Circular border radius |
| `border: var(--border-width-thin) solid var(--theme-border);` | `border border-border` | Default border |
| `--shadow-sm` | `shadow-sm` | Small shadow |
| `--shadow-md` | `shadow` | Medium shadow |
| `--shadow-lg` | `shadow-lg` | Large shadow |
| `--shadow-xl` | `shadow-xl` | Extra large shadow |

### Colors (Mapping to shadcn/ui variables)

| Current CSS Variable | shadcn/ui Equivalent | Notes |
|----------------------|----------------------|-------|
| `--theme-background` | `bg-background` | Background color |
| `--theme-foreground` | `text-foreground` | Text color |
| `--theme-card` | `bg-card` | Card background |
| `--theme-card-foreground` | `text-card-foreground` | Card text color |
| `--theme-primary` | `bg-primary` | Primary action color |
| `--theme-primary-foreground` | `text-primary-foreground` | Primary action text |
| `--theme-secondary` | `bg-secondary` | Secondary color |
| `--theme-secondary-foreground` | `text-secondary-foreground` | Secondary text |
| `--theme-muted` | `bg-muted` | Muted background |
| `--theme-muted-foreground` | `text-muted-foreground` | Muted text |
| `--theme-accent` | `bg-accent` | Accent color |
| `--theme-accent-foreground` | `text-accent-foreground` | Accent text |
| `--theme-destructive` | `bg-destructive` | Destructive action color |
| `--theme-destructive-foreground` | `text-destructive-foreground` | Destructive text |
| `--theme-border` | `border-border` | Border color |
| `--theme-input` | `border-input` | Input border color |

### Component-Specific Patterns

#### Card Pattern
```css
.custom-card {
  max-width: var(--layout-max-width);
  padding: var(--card-padding-y) var(--card-padding-x);
  background-color: var(--card-background);
  border: var(--border-width-thin) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  box-shadow: var(--card-shadow);
}
```

**Tailwind/shadcn Equivalent:**
```jsx
<Card className="max-w-7xl p-4 shadow-md">
  <CardContent>
    {/* Content here */}
  </CardContent>
</Card>
```

#### Button Pattern
```css
.custom-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: white;
  background-color: var(--theme-primary);
  border-radius: var(--border-radius-md);
  transition: background-color var(--transition-hover);
}

.custom-button:hover {
  background-color: rgba(var(--theme-primary), 0.9);
}
```

**Tailwind/shadcn Equivalent:**
```jsx
<Button variant="default" size="default">
  Button Text
</Button>
```

#### Input Pattern
```css
.custom-input {
  width: 100%;
  height: var(--input-height);
  padding: 0 var(--input-padding-x);
  font-size: var(--font-size-base);
  color: var(--theme-foreground);
  background-color: white;
  border: 1px solid var(--theme-input);
  border-radius: var(--input-border-radius);
  transition: border-color var(--transition-hover);
}

.custom-input:focus {
  outline: none;
  border-color: var(--theme-primary);
  box-shadow: 0 0 0 2px rgba(var(--theme-primary), 0.2);
}
```

**Tailwind/shadcn Equivalent:**
```jsx
<Input className="w-full" />
```

## Transition and Animation

| CSS Variable/Pattern | Tailwind Equivalent | Notes |
|---------------------|---------------------|-------|
| `transition: var(--transition-hover);` | `transition-colors` | Color transition |
| `transition: var(--transition-normal);` | `transition duration-200` | Standard transition |
| `transition: var(--transition-slow);` | `transition duration-300` | Slow transition |

## Responsive Patterns

| CSS Pattern | Tailwind Equivalent | Notes |
|------------|---------------------|-------|
| `@media (min-width: 640px) { ... }` | `sm:...` | Small screens and up |
| `@media (min-width: 768px) { ... }` | `md:...` | Medium screens and up |
| `@media (min-width: 1024px) { ... }` | `lg:...` | Large screens and up |
| `@media (min-width: 1280px) { ... }` | `xl:...` | Extra large screens and up |
| `@media (min-width: 1536px) { ... }` | `2xl:...` | 2x large screens and up |

## Dark Mode

Instead of separate dark mode CSS classes with overrides, use Tailwind's dark mode modifier:

```jsx
<div className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white">
  Content with automatic dark mode support
</div>
```

## Component-Specific CSS Variables to Preserve

These CSS variables should be preserved as they serve specific purposes for component styling that are not directly available in Tailwind:

1. Tool call-specific variables:
   - `--theme-tool-call-background`
   - `--theme-tool-call-border`
   - `--theme-tool-call-header-background`
   - `--theme-tool-call-header-hover`
   - `--theme-tool-call-title`
   - `--theme-tool-call-icon`

2. Message-specific variables:
   - `--theme-user-message-background`
   - `--theme-user-message-foreground`
   - `--theme-user-message-border`
   - `--theme-assistant-message-background`
   - `--theme-assistant-message-foreground`
   - `--theme-assistant-message-border`
   - `--theme-system-message-background`
   - `--theme-system-message-foreground`
   - `--theme-system-message-border`
   - `--theme-thought-background`
   - `--theme-thought-foreground`
   - `--theme-thought-border`

These should be added to the globals.css file with the other shadcn/ui variables to ensure consistent theming.