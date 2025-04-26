# Radix UI Themes Overview

*AI-optimized theme documentation*

Radix Themes is a component library built on top of Radix Primitives that provides a complete design system with sensible defaults while maintaining full customization capability. It offers a set of professionally designed, accessible components that work seamlessly together.

## Key Features

### Complete Theme Solution

Radix Themes provides a comprehensive set of styled components that work together as a cohesive system. The components are built on top of Radix Primitives, inheriting their accessibility and customization benefits, while adding consistent styling and behavior.

### Design Tokens System

Themes are built around a powerful design tokens system that controls colors, typography, spacing, and other visual aspects. This token-based approach ensures consistency across your interface while enabling straightforward customization.

### Light and Dark Mode

Every component comes with built-in support for both light and dark modes, with carefully designed color palettes that maintain proper contrast ratios for accessibility in both modes.

### Responsive by Default

Components are responsive by default, with appropriate behavior across different viewport sizes. The library includes responsive utilities for adjusting properties based on breakpoints.

## Installation

```bash
npm install @radix-ui/themes
```

## Basic Usage

```jsx
import { Theme, Button, Flex, Text } from '@radix-ui/themes';
import '@radix-ui/themes/styles.css';

function App() {
  return (
    <Theme appearance="light" scaling="100%" radius="medium">
      <Flex direction="column" gap="2" p="4">
        <Text size="5" weight="bold">Welcome to Radix Themes</Text>
        <Button size="3" color="jade">
          Get Started
        </Button>
      </Flex>
    </Theme>
  );
}
```

## Theme Configuration

The `Theme` component is the root provider for Radix Themes and accepts several props for customization:

```jsx
<Theme
  // Base appearance
  appearance="light" // or "dark"
  
  // Optional: Auto-switch based on system preference
  accentColor="jade" // Primary accent color
  grayColor="slate" // Base gray palette
  panelBackground="solid" // or "translucent"
  radius="medium" // Corner radius scale
  scaling="100%" // or "90%", "95%", "105%", "110%"
>
  {/* Your app content */}
</Theme>
```

### Nested Themes

You can nest `Theme` components to create sections with different theme settings:

```jsx
<Theme appearance="light">
  <Header />
  
  <Theme appearance="dark" accentColor="crimson">
    <DarkSection />
  </Theme>
  
  <Footer />
</Theme>
```

## Color System

Radix Themes includes a comprehensive color system with:

### Accent Colors

Accent colors are used for interactive elements, highlights, and important UI elements:

- `tomato`, `red`, `ruby`, `crimson`, `pink`, `plum`, `purple`, `violet`
- `iris`, `indigo`, `blue`, `cyan`, `teal`, `jade`, `green`, `grass`
- `bronze`, `gold`, `brown`, `orange`, `amber`

### Gray Scales

Gray scales serve as the foundation for UI elements:

- `gray`, `mauve`, `slate`, `sage`, `olive`, `sand`

### Using Colors

You can apply colors to components using the `color` prop:

```jsx
<Button color="blue">Blue Button</Button>
<Text color="crimson">Crimson text</Text>
<Card color="gray">Gray card</Card>
```

## Typography

Radix Themes provides a type system with consistent scales:

```jsx
<Text size="1">Size 1</Text>
<Text size="2">Size 2</Text>
<Text size="3">Size 3</Text>
<Text size="4">Size 4</Text>
<Text size="5">Size 5</Text>
<Text size="6">Size 6</Text>
<Text size="7">Size 7</Text>
<Text size="8">Size 8</Text>
<Text size="9">Size 9</Text>

<Heading size="1">Heading 1</Heading>
<Heading size="2">Heading 2</Heading>
<Heading size="3">Heading 3</Heading>
<Heading size="4">Heading 4</Heading>
<Heading size="5">Heading 5</Heading>
<Heading size="6">Heading 6</Heading>
<Heading size="7">Heading 7</Heading>
<Heading size="8">Heading 8</Heading>
<Heading size="9">Heading 9</Heading>
```

## Layout System

Radix Themes includes layout components for building consistent interfaces:

```jsx
<Flex direction="column" gap="3">
  <Text>Flex container with columns</Text>
  <Grid columns="3" gap="2">
    <Box height="7" background="blue">1</Box>
    <Box height="7" background="blue">2</Box>
    <Box height="7" background="blue">3</Box>
  </Grid>
</Flex>
```

## Responsive Props

Most component props accept responsive objects to adjust values at different breakpoints:

```jsx
<Flex 
  direction={{ initial: 'column', md: 'row' }}
  gap={{ initial: '1', xs: '2', sm: '3', md: '4' }}
>
  <Box width={{ initial: '100%', md: '50%' }}>Responsive box</Box>
</Flex>
```

Default breakpoints:
- `initial`: 0px and up
- `xs`: 520px and up
- `sm`: 768px and up
- `md`: 1024px and up
- `lg`: 1280px and up
- `xl`: 1640px and up

## Design System Customization

For deeper customization, you can extend the theme with your own design tokens using CSS variables:

```css
/* theme-config.css */
:root {
  --default-font-family: 'Inter, sans-serif';
  
  /* Custom colors */
  --custom-blue1: hsl(206, 100%, 50%);
  --custom-blue2: hsl(206, 100%, 60%);
  
  /* Override Radix theme tokens */
  --blue-light-a9: var(--custom-blue1);
  --blue-dark-a9: var(--custom-blue2);
}
```

Then import this CSS file in your application:

```jsx
import '@radix-ui/themes/styles.css';
import './theme-config.css';
```

## Using with Radix Primitives

Radix Themes components are built on top of Radix Primitives, providing styling while preserving the underlying accessibility and behavior:

```jsx
// Using the styled Dialog from Themes
import { Dialog, Flex, Text, Button } from '@radix-ui/themes';

function MyDialog() {
  return (
    <Dialog.Root>
      <Dialog.Trigger>
        <Button>Open Dialog</Button>
      </Dialog.Trigger>
      
      <Dialog.Content>
        <Dialog.Title>Dialog Title</Dialog.Title>
        <Dialog.Description>Dialog description here.</Dialog.Description>
        
        <Flex gap="3" mt="4" justify="end">
          <Dialog.Close>
            <Button variant="soft" color="gray">Cancel</Button>
          </Dialog.Close>
          <Dialog.Close>
            <Button>Save</Button>
          </Dialog.Close>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
}
```

For advanced customization needs, you can still use the unstyled primitives alongside Radix Themes.