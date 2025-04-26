# Radix UI Theme Configuration

*AI-optimized theme configuration reference*

Radix Themes provides extensive configuration options through a combination of component props, CSS variables, and design tokens. This reference covers the various ways to customize the theming system to match your design requirements.

## Theme Component Configuration

The `Theme` component is the foundation of the theming system and accepts several configuration props.

### Basic Configuration

```jsx
import { Theme } from '@radix-ui/themes';
import '@radix-ui/themes/styles.css';

function App() {
  return (
    <Theme
      appearance="light"
      accentColor="cyan"
      grayColor="slate"
      radius="medium"
      scaling="100%"
    >
      {/* Your app content */}
    </Theme>
  );
}
```

### Configuration Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `appearance` | `"light" \| "dark" \| "inherit"` | `"light"` | Base theme appearance |
| `accentColor` | `"tomato" \| "red" \| "ruby" \| "crimson" \| "pink" \| "plum" \| "purple" \| "violet" \| "iris" \| "indigo" \| "blue" \| "cyan" \| "teal" \| "jade" \| "green" \| "grass" \| "brown" \| "orange" \| "amber" \| "yellow" \| "gold" \| "bronze"` | `"indigo"` | Primary accent color |
| `grayColor` | `"gray" \| "mauve" \| "slate" \| "sage" \| "olive" \| "sand"` | `"gray"` | Base gray scale |
| `panelBackground` | `"solid" \| "translucent"` | `"solid"` | Background style for panels and cards |
| `radius` | `"none" \| "small" \| "medium" \| "large" \| "full"` | `"medium"` | Border radius scale |
| `scaling` | `"90%" \| "95%" \| "100%" \| "105%" \| "110%"` | `"100%"` | Global size scaling |

### Dark Mode Implementation

#### Basic Dark Mode

```jsx
import { Theme } from '@radix-ui/themes';
import { useEffect, useState } from 'react';

function App() {
  const [appearance, setAppearance] = useState('light');
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setAppearance(mediaQuery.matches ? 'dark' : 'light');
    
    const handler = (event) => {
      setAppearance(event.matches ? 'dark' : 'light');
    };
    
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  return (
    <Theme appearance={appearance}>
      {/* App content */}
    </Theme>
  );
}
```

#### Using CSS for Dark Mode

Alternatively, you can use CSS to handle the theme switching:

```css
/* In your CSS file */
:root {
  --app-theme: light;
}

@media (prefers-color-scheme: dark) {
  :root {
    --app-theme: dark;
  }
}
```

```jsx
<Theme appearance="var(--app-theme)">
  {/* App content */}
</Theme>
```

## Theme Extension with CSS Variables

Radix Themes uses CSS variables for all design tokens, which you can override to extend or modify the theme.

### Overriding Color Tokens

```css
/* In your CSS file */
:root {
  /* Override blue accent in light mode */
  --blue-1: hsl(212, 100%, 98%);
  --blue-2: hsl(210, 100%, 96%);
  --blue-3: hsl(209, 100%, 94%);
  --blue-4: hsl(210, 98%, 90%);
  --blue-5: hsl(209, 95%, 84%);
  --blue-6: hsl(209, 91%, 75%);
  --blue-7: hsl(208, 85%, 65%);
  --blue-8: hsl(207, 86%, 55%);
  --blue-9: hsl(206, 100%, 50%);
  --blue-10: hsl(208, 100%, 47%);
  --blue-11: hsl(212, 100%, 35%);
  --blue-12: hsl(213, 100%, 25%);
  
  /* Alpha variants */
  --blue-a1: hsla(212, 100%, 50%, 0.02);
  --blue-a2: hsla(210, 100%, 50%, 0.04);
  /* ... etc */
}

:root.dark {
  /* Override blue accent in dark mode */
  --blue-1: hsl(212, 35%, 9%);
  --blue-2: hsl(216, 50%, 11%);
  /* ... etc */
}
```

### Modifying Typography

```css
:root {
  /* Override base font */
  --default-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* Modify heading font */
  --heading-font-family: 'Montserrat', var(--default-font-family);
  
  /* Override font sizes */
  --font-size-1: 12px;
  --font-size-2: 14px;
  --font-size-3: 16px;
  --font-size-4: 18px;
  --font-size-5: 20px;
  --font-size-6: 24px;
  --font-size-7: 30px;
  --font-size-8: 36px;
  --font-size-9: 48px;
  
  /* Adjust line heights */
  --line-height-1: 16px;
  --line-height-2: 20px;
  --line-height-3: 24px;
  --line-height-4: 26px;
  --line-height-5: 28px;
  --line-height-6: 30px;
  --line-height-7: 36px;
  --line-height-8: 40px;
  --line-height-9: 52px;
}
```

### Customizing Spacing

```css
:root {
  /* Space scale (used for margin, padding, gap) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;
  --space-8: 48px;
  --space-9: 64px;
}
```

### Modifying Border Radius

```css
:root {
  /* Radius scale */
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 6px;
  --radius-4: 8px;
  --radius-5: 12px;
  --radius-6: 16px;
  --radius-full: 9999px;
}
```

## Semantic Tokens

Radix Themes also provides semantic tokens that reference the base tokens, which you can override:

```css
:root {
  /* Override semantic tokens */
  --color-panel-solid: white;
  --color-panel-translucent: rgba(255, 255, 255, 0.8);
  --color-surface: var(--gray-2);
  --color-selection: var(--blue-a5);
  
  /* Text colors */
  --color-text-contrast: black;
  --color-text: var(--gray-12);
  --color-text-secondary: var(--gray-11);
  --color-text-tertiary: var(--gray-10);
  
  /* Border colors */
  --color-border: var(--gray-6);
  --color-border-hover: var(--gray-8);
}
```

## Creating a Custom Theme Layer

For more complex theming needs, you can create a separate theme layer:

```jsx
// themes.jsx
import { createThemeContract } from '@radix-ui/themes';

// Create your theme contract
const themeContract = createThemeContract({
  colors: {
    primary: '',
    secondary: '',
    accent: '',
    background: '',
    text: '',
  },
  fonts: {
    body: '',
    heading: '',
  },
  // etc.
});

// Light theme implementation
const lightTheme = {
  colors: {
    primary: 'hsl(206, 100%, 50%)',
    secondary: 'hsl(252, 78%, 60%)',
    accent: 'hsl(150, 60%, 54%)',
    background: 'white',
    text: 'hsl(220, 20%, 20%)',
  },
  fonts: {
    body: 'Inter, sans-serif',
    heading: 'Montserrat, sans-serif',
  },
  // etc.
};

// Dark theme implementation
const darkTheme = {
  colors: {
    primary: 'hsl(206, 100%, 65%)',
    secondary: 'hsl(252, 78%, 70%)',
    accent: 'hsl(150, 60%, 60%)',
    background: 'hsl(220, 20%, 10%)',
    text: 'hsl(220, 20%, 90%)',
  },
  fonts: {
    body: 'Inter, sans-serif',
    heading: 'Montserrat, sans-serif',
  },
  // etc.
};

export { themeContract, lightTheme, darkTheme };
```

## Theme Scaling

The `scaling` prop on the `Theme` component affects the overall size of elements by scaling all size-related values:

```jsx
// For smaller UIs
<Theme scaling="90%">
  {/* Content will be 90% of the default size */}
</Theme>

// For larger UIs
<Theme scaling="110%">
  {/* Content will be 110% of the default size */}
</Theme>
```

## Media Queries for Responsive Theming

You can combine CSS variables with media queries for responsive theming:

```css
:root {
  --radius-global: var(--radius-3);
  --content-max-width: 1200px;
}

@media (max-width: 768px) {
  :root {
    --radius-global: var(--radius-2);
    --content-max-width: 100%;
  }
}

@media (max-width: 480px) {
  :root {
    --radius-global: var(--radius-1);
  }
}
```

## Using Theme Values in Custom Components

```jsx
import { styled } from '@stitches/react';

const CustomCard = styled('div', {
  backgroundColor: 'var(--color-panel-solid)',
  borderRadius: 'var(--radius-3)',
  border: '1px solid var(--color-border)',
  padding: 'var(--space-4)',
  color: 'var(--color-text)',
  fontFamily: 'var(--default-font-family)',
  boxShadow: 'var(--shadow-2)',
  
  '&:hover': {
    borderColor: 'var(--color-border-hover)',
    boxShadow: 'var(--shadow-3)',
  }
});
```

## Animation Tokens

Radix Themes includes animation tokens you can use and override:

```css
:root {
  /* Duration */
  --duration-0: 0ms;
  --duration-1: 100ms;
  --duration-2: 200ms;
  --duration-3: 300ms;
  --duration-4: 400ms;
  --duration-5: 500ms;
  
  /* Easing functions */
  --ease-1: cubic-bezier(0.25, 0, 0.5, 1);
  --ease-2: cubic-bezier(0.3, 0, 0.3, 1);
  --ease-3: cubic-bezier(0.3, 0, 0, 1);
  --ease-4: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-5: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

## Shadow Tokens

```css
:root {
  /* Box shadows */
  --shadow-1: 0px 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-2: 0px 1px 4px rgba(0, 0, 0, 0.06), 0px 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-3: 0px 2px 4px rgba(0, 0, 0, 0.06), 0px 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-4: 0px 2px 6px rgba(0, 0, 0, 0.06), 0px 8px 16px rgba(0, 0, 0, 0.1);
  --shadow-5: 0px 4px 8px rgba(0, 0, 0, 0.06), 0px 12px 24px rgba(0, 0, 0, 0.12);
  --shadow-6: 0px 8px 16px rgba(0, 0, 0, 0.06), 0px 20px 40px rgba(0, 0, 0, 0.14);
}
```