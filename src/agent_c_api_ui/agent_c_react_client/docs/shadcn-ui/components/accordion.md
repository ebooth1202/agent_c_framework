---
Title: Accordion Component
Created: 2025-04-24
Source: ui/docs/shadcn-ui/components/accordion.mdx
---

# Accordion

A vertically stacked set of interactive headings that each reveal a section of content.

## API Reference

Based on Radix UI Accordion primitive
Links: 
- Documentation: https://www.radix-ui.com/docs/primitives/components/accordion
- API Reference: https://www.radix-ui.com/docs/primitives/components/accordion#api-reference

## Installation

### Option 1: Using CLI

```bash
npx shadcn@latest add accordion
```

### Option 2: Manual Installation

1. Install dependencies:
   ```bash
   npm install @radix-ui/react-accordion
   ```

2. Add the required animations to `tailwind.config.js`:
   ```js
   /** @type {import('tailwindcss').Config} */
   module.exports = {
     theme: {
       extend: {
         keyframes: {
           "accordion-down": {
             from: { height: "0" },
             to: { height: "var(--radix-accordion-content-height)" },
           },
           "accordion-up": {
             from: { height: "var(--radix-accordion-content-height)" },
             to: { height: "0" },
           },
         },
         animation: {
           "accordion-down": "accordion-down 0.2s ease-out",
           "accordion-up": "accordion-up 0.2s ease-out",
         },
       },
     },
   }
   ```

## Usage

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

## Key Features

- WAI-ARIA compliant for accessibility
- Supports single or multiple expanded items
- Collapsible option available
- Smooth animations for expand/collapse