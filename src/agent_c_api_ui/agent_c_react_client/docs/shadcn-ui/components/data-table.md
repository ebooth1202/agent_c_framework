# Data Table Component
Created: 2025-04-24
Source: data-table.mdx

## Overview
A flexible data table framework built using TanStack Table v8 for creating powerful tables and datagrids.

## Key Concepts
Data tables are designed to be **customizable** rather than a one-size-fits-all component. This document provides a guide for building your own data tables with various features.

## Features
- Core table functionality with row and column rendering
- Row actions via dropdown menus
- Pagination controls
- Column sorting
- Filtering capabilities
- Column visibility toggle
- Row selection with checkboxes

## Installation

```bash
# Install the table component
npx shadcn@latest add table

# Add TanStack Table dependency
npm install @tanstack/react-table
```

## Project Structure
Recommended file structure for implementing data tables:

```
app
└── data-section
    ├── columns.tsx    # Column definitions
    ├── data-table.tsx # DataTable component
    └── page.tsx       # Page that renders the table
```

## Usage Example

### 1. Define Column Structure
```tsx
// columns.tsx
"use client"

import { ColumnDef } from "@tanstack/react-table"

// Define your data type
export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "status",
    header: "Status",
  },
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "amount",
    header: "Amount",
  },
]
```

### 2. Create DataTable Component
```tsx
// data-table.tsx
"use client"

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

### 3. Render the Table
```tsx
// page.tsx
import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"

async function getData(): Promise<Payment[]> {
  // Fetch data from your API here
  return [
    {
      id: "728ed52f",
      amount: 100,
      status: "pending",
      email: "m@example.com",
    },
    // ...
  ]
}

export default async function DemoPage() {
  const data = await getData()

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  )
}
```

## Advanced Features

### Cell Formatting
Customize how cells are displayed with formatting logic:

```tsx
{
  accessorKey: "amount",
  header: () => <div className="text-right">Amount</div>,
  cell: ({ row }) => {
    const amount = parseFloat(row.getValue("amount"))
    const formatted = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)

    return <div className="text-right font-medium">{formatted}</div>
  },
}
```

### Row Actions
Add dropdown menus for row actions:

```tsx
{
  id: "actions",
  cell: ({ row }) => {
    const payment = row.original

    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0">
            <span className="sr-only">Open menu</span>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Actions</DropdownMenuLabel>
          <DropdownMenuItem
            onClick={() => navigator.clipboard.writeText(payment.id)}
          >
            Copy payment ID
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>View customer</DropdownMenuItem>
          <DropdownMenuItem>View payment details</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  },
}
```

### Pagination
Add pagination to your table:

```tsx
// In the useReactTable config
{
  getPaginationRowModel: getPaginationRowModel(),
}

// Pagination controls
<div className="flex items-center justify-end space-x-2 py-4">
  <Button
    variant="outline"
    size="sm"
    onClick={() => table.previousPage()}
    disabled={!table.getCanPreviousPage()}
  >
    Previous
  </Button>
  <Button
    variant="outline"
    size="sm"
    onClick={() => table.nextPage()}
    disabled={!table.getCanNextPage()}
  >
    Next
  </Button>
</div>
```

### Sorting
Make columns sortable:

```tsx
// In DataTable component
const [sorting, setSorting] = React.useState<SortingState>([])

// In useReactTable config
{
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
  state: {
    sorting,
  },
}

// In column definition
header: ({ column }) => {
  return (
    <Button
      variant="ghost"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
      Email
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  )
}
```

### Filtering
Add search functionality:

```tsx
// In DataTable component
const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

// In useReactTable config
{
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  state: {
    columnFilters,
  },
}

// Filter input
<Input
  placeholder="Filter emails..."
  value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
  onChange={(event) =>
    table.getColumn("email")?.setFilterValue(event.target.value)
  }
  className="max-w-sm"
/>
```

### Column Visibility
Toggle which columns are displayed:

```tsx
// In DataTable component
const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})

// In useReactTable config
{
  onColumnVisibilityChange: setColumnVisibility,
  state: {
    columnVisibility,
  },
}

// Column visibility dropdown
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Columns</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    {table
      .getAllColumns()
      .filter((column) => column.getCanHide())
      .map((column) => {
        return (
          <DropdownMenuCheckboxItem
            key={column.id}
            className="capitalize"
            checked={column.getIsVisible()}
            onCheckedChange={(value) =>
              column.toggleVisibility(!!value)
            }
          >
            {column.id}
          </DropdownMenuCheckboxItem>
        )
      })}
  </DropdownMenuContent>
</DropdownMenu>
```

### Row Selection
Add checkboxes for selecting rows:

```tsx
// Add select column
{
  id: "select",
  header: ({ table }) => (
    <Checkbox
      checked={
        table.getIsAllPageRowsSelected() ||
        (table.getIsSomePageRowsSelected() && "indeterminate")
      }
      onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
      aria-label="Select all"
    />
  ),
  cell: ({ row }) => (
    <Checkbox
      checked={row.getIsSelected()}
      onCheckedChange={(value) => row.toggleSelected(!!value)}
      aria-label="Select row"
    />
  ),
  enableSorting: false,
  enableHiding: false,
}

// In DataTable component
const [rowSelection, setRowSelection] = React.useState({})

// In useReactTable config
{
  onRowSelectionChange: setRowSelection,
  state: {
    rowSelection,
  },
}

// Display selected row count
<div className="flex-1 text-sm text-muted-foreground">
  {table.getFilteredSelectedRowModel().rows.length} of{" "}
  {table.getFilteredRowModel().rows.length} row(s) selected.
</div>
```

## Reusable Components
For more complex implementations, consider creating these reusable components:

1. **DataTableColumnHeader** - Makes columns sortable and hideable
2. **DataTablePagination** - Pagination controls with page size selection
3. **DataTableViewOptions** - Column visibility toggles