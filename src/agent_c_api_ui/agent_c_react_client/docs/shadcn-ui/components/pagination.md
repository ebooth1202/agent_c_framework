# Pagination Component

*Created: 2025-04-24 | Source: pagination.mdx*

## Overview

The Pagination component provides a set of interactive controls for navigating between pages of content. It includes previous and next links, page number links, and ellipsis indicators for skipped page ranges.

## Key Features

- Previous and next page navigation
- Page number links
- Ellipsis for large page ranges
- Customizable content structure
- Seamless integration with Next.js

## Installation

**CLI Method:**
```bash
npx shadcn@latest add pagination
```

**Manual Installation:**
1. Copy component source code to your project
2. Update import paths to match your project structure

## Component Structure

- `Pagination`: Main container component
- `PaginationContent`: Contains the pagination items
- `PaginationItem`: Wrapper for pagination elements
- `PaginationLink`: Link to a specific page number
- `PaginationPrevious`: Link to the previous page
- `PaginationNext`: Link to the next page
- `PaginationEllipsis`: Indicator for skipped page ranges

## Usage Example

```tsx
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

## Next.js Integration

To use the Next.js `<Link />` component, update the `pagination.tsx` file:

```tsx
import Link from "next/link"

type PaginationLinkProps = ... & React.ComponentProps<typeof Link>

const PaginationLink = ({...props }: ) => (
  <PaginationItem>
    <Link>
      // ...
    </Link>
  </PaginationItem>
)
```

## Common Use Cases

### Basic Pagination

```tsx
<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="/posts/page/1" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/posts/page/1">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/posts/page/2" isActive>2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/posts/page/3">3</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="/posts/page/3" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

### Extended Pagination with Ellipsis

```tsx
<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">8</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">9</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">10</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

### Dynamic Pagination

Implement pagination with dynamic page count:

```tsx
function DynamicPagination({ currentPage, totalPages }) {
  return (
    <Pagination>
      <PaginationContent>
        {currentPage > 1 && (
          <PaginationItem>
            <PaginationPrevious href={`/page/${currentPage - 1}`} />
          </PaginationItem>
        )}
        {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
          <PaginationItem key={page}>
            <PaginationLink 
              href={`/page/${page}`} 
              isActive={page === currentPage}
            >
              {page}
            </PaginationLink>
          </PaginationItem>
        ))}
        {currentPage < totalPages && (
          <PaginationItem>
            <PaginationNext href={`/page/${currentPage + 1}`} />
          </PaginationItem>
        )}
      </PaginationContent>
    </Pagination>
  )
}
```