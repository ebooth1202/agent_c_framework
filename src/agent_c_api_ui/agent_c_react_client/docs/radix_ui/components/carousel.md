# Carousel Component

*Created: April 24, 2025 from source file carousel.mdx*

## Overview
A carousel component with motion and swipe capabilities built using Embla Carousel library.

## Key Features
- Horizontal and vertical orientation options
- Customizable item sizes and spacing
- Navigation controls (previous/next buttons)
- Plugin support (autoplay, etc.)
- Responsive design options
- API for programmatic control

## Installation

```bash
npm install embla-carousel-react
```

## Usage Example

```tsx
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

<Carousel>
  <CarouselContent>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
  </CarouselContent>
  <CarouselPrevious />
  <CarouselNext />
</Carousel>
```

## Component Structure
The Carousel component consists of several sub-components:
- `Carousel`: The main container
- `CarouselContent`: Wrapper for carousel items
- `CarouselItem`: Individual carousel slides
- `CarouselPrevious`: Previous button navigation
- `CarouselNext`: Next button navigation

## Configuration Options

### Item Sizing
Use the `basis` utility class to control item width:
```tsx
<CarouselItem className="basis-1/3">...</CarouselItem> // 33% width
<CarouselItem className="md:basis-1/2 lg:basis-1/3">...</CarouselItem> // Responsive
```

### Spacing
Use padding-left on items and negative margin-left on content:
```tsx
<CarouselContent className="-ml-4">
  <CarouselItem className="pl-4">...</CarouselItem>
</CarouselContent>
```

### Orientation
Set the carousel direction:
```tsx
<Carousel orientation="vertical | horizontal">
```

### Options
Pass Embla Carousel options:
```tsx
<Carousel
  opts={{
    align: "start",
    loop: true,
  }}
>
```

## API Access
Access the carousel API for programmatic control:

```tsx
import { type CarouselApi } from "@/components/ui/carousel"

const [api, setApi] = React.useState<CarouselApi>()

return (
  <Carousel setApi={setApi}>
    {/* Items */}
  </Carousel>
)
```

## Plugin Support
Add plugins like autoplay:

```tsx
import Autoplay from "embla-carousel-autoplay"

<Carousel
  plugins={[
    Autoplay({
      delay: 2000,
    }),
  ]}
>
```

## Common Use Cases
- Image galleries
- Product showcases
- Testimonial displays
- Feature highlights
- Content sliders