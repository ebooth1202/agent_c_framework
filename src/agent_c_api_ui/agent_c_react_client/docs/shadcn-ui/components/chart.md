# Chart

_Created: 2025-04-24 | Source: chart.mdx_

## Overview

Beautiful chart components built using Recharts. These components provide a flexible way to create various types of data visualizations in your application with consistent styling and theming.

## Key Features

- Built on Recharts library
- Customizable theming through CSS variables
- Support for light and dark mode
- Accessible chart components with keyboard navigation
- Built-in tooltip and legend components
- Supports various chart types (bar, line, area, etc.)

## Installation

**CLI Method:**
```bash
npx shadcn@latest add chart
```

**Required CSS Variables:**
Add the following to your CSS file:
```css
@layer base {
  :root {
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
    --chart-3: 197 37% 24%;
    --chart-4: 43 74% 66%;
    --chart-5: 27 87% 67%;
  }

  .dark {
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
    --chart-3: 30 80% 55%;
    --chart-4: 280 65% 60%;
    --chart-5: 340 75% 55%;
  }
}
```

**Manual Installation:**
1. Install dependencies:
   ```bash
   npm install recharts
   ```
2. Copy the component source code
3. Add the CSS variables to your stylesheet

## Component Structure

The chart system includes several key components:

- `ChartContainer`: Wrapper for chart components that handles theming and config
- `ChartTooltip`/`ChartTooltipContent`: Components for displaying data tooltips on hover
- `ChartLegend`/`ChartLegendContent`: Components for displaying a chart legend
- Standard Recharts components: BarChart, LineChart, CartesianGrid, XAxis, YAxis, etc.

## Usage

### Basic Chart Setup

```tsx
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

// Define chart data
const chartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  // ...
]

// Define chart config
const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
}

// Create chart component
export function MyChart() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="month"
          tickLine={false}
          tickMargin={10}
          axisLine={false}
          tickFormatter={(value) => value.slice(0, 3)}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
        <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
      </BarChart>
    </ChartContainer>
  )
}
```

## Chart Configuration

The `chartConfig` object provides a way to define labels, icons, and colors for chart elements:

```tsx
const chartConfig = {
  desktop: {
    label: "Desktop",            // Human-readable label
    icon: Monitor,              // Optional icon (Lucide icon)
    color: "hsl(var(--chart-1))", // Color value or CSS variable
    // OR theme object for light/dark mode
    theme: {
      light: "#2563eb",
      dark: "#dc2626",
    },
  },
  // Additional data keys...
}
```

## Theming

Colors can be defined using CSS variables (recommended) or direct color values:

```tsx
// Using CSS variables
color: "hsl(var(--chart-1))",

// Using direct color values
color: "#2563eb",
```

## Tooltip Customization

The tooltip can be customized with various props:

- `labelKey`: Config/data key for the tooltip label
- `nameKey`: Config/data key for the tooltip name
- `indicator`: Style for the tooltip indicator (`dot`, `line`, or `dashed`)
- `hideLabel`: Whether to hide the label
- `hideIndicator`: Whether to hide the indicator

## Accessibility

Add the `accessibilityLayer` prop to enable keyboard navigation and screen reader support:

```tsx
<LineChart accessibilityLayer />
```

## React 19/Next.js 15 Compatibility

If using with React 19 or Next.js 15, additional configuration may be required. Refer to the React 19 compatibility documentation.