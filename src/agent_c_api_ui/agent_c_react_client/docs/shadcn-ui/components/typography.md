# Typography

_Created: 2025-04-24 | Source: typography.mdx_

## Overview

A collection of standardized typography styles for headings, paragraphs, lists, and other text elements. Typography components provide consistent text formatting across an application.

## Key Features

- Consistent heading styles (h1, h2, h3, h4)
- Paragraph styling
- Blockquote formatting
- Table typography
- List formatting
- Inline code styling
- Special text styles (lead, large, small, muted)

## Installation

The typography styles are typically included as part of the base Tailwind CSS configuration in a Shadcn UI project. No separate installation is required.

## Component Styles

### Headings
- **h1**: Primary heading, largest text size
- **h2**: Secondary heading
- **h3**: Tertiary heading
- **h4**: Quaternary heading

### Block Elements
- **p**: Standard paragraph text
- **blockquote**: Stylized block quotation
- **table**: Formatted tabular data
- **list**: Ordered and unordered lists

### Inline Elements
- **Inline code**: Code snippets within text

### Special Text Styles
- **Lead**: Slightly larger, more prominent text often used for introductions
- **Large**: Emphasized larger text
- **Small**: De-emphasized smaller text
- **Muted**: Low-contrast text for less important information

## Usage

These typography styles are applied using CSS classes, typically through a combination of direct HTML elements and Tailwind utility classes.

```html
<!-- Heading examples -->
<h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">Heading 1</h1>
<h2 className="text-3xl font-semibold tracking-tight">Heading 2</h2>

<!-- Paragraph -->
<p className="leading-7 [&:not(:first-child)]:mt-6">Paragraph text</p>

<!-- Special styles -->
<p className="text-lg font-medium">Lead text</p>
<p className="text-sm font-medium text-muted-foreground">Muted text</p>
```

## Common Use Cases

- Document and article formatting
- UI headings and labels
- Content-heavy pages
- Blog posts and news articles
- Documentation
- Information hierarchies