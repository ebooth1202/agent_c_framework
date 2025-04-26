# Table Component

*Created: 2025-04-24 | Source: table.mdx*

## Overview
A responsive table component for displaying structured data in rows and columns.

## Key Features
- Responsive design for different screen sizes
- Customizable layout with caption, headers, and body sections
- Can be integrated with TanStack Table for advanced features
- Consistent styling with the design system

## Installation

### CLI Method
```bash
npx shadcn@latest add table
```

### Manual Method
1. Copy the component source code to your project
2. Update import paths to match your project setup

## Component Structure
The Table component is composed of several sub-components:
- `Table`: The root container
- `TableCaption`: Optional descriptive text for the table
- `TableHeader`: Container for header row(s)
- `TableHead`: Individual header cell
- `TableBody`: Container for table data rows
- `TableRow`: A row within the table
- `TableCell`: Individual data cell

## Usage

### Basic Usage
```tsx
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

<Table>
  <TableCaption>A list of your recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead className="w-[100px]">Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Method</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">INV001</TableCell>
      <TableCell>Paid</TableCell>
      <TableCell>Credit Card</TableCell>
      <TableCell className="text-right">$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Advanced Data Tables
The Table component can be combined with TanStack Table (formerly React Table) to create advanced data tables with features like:
- Sorting
- Filtering
- Pagination
- Row selection

Refer to the Data Table component documentation for implementation details.

## Styling
- Use className props to customize width, alignment, and other styles
- Cells can be styled individually for responsive layouts

## Accessibility
- Uses semantic HTML table elements for screen reader compatibility
- Properly associates headers with data cells

## Related Components
- Data Table (advanced implementation with TanStack Table)

## Examples
See the Tasks demo for a comprehensive example of data tables.