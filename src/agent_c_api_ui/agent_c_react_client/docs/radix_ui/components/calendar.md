# Calendar Component

*Created: April 24, 2025 from source file calendar.mdx*

## Overview
A date field component that allows users to enter and edit dates. Built on top of React DayPicker.

## Key Features
- Calendar date picker with month navigation
- Single date selection mode
- Customizable styling and border options
- Integration with form components

## Installation

```bash
npm install react-day-picker@8.10.1 date-fns
```

Note: The Calendar component requires the Button component as a dependency.

## Usage Example

```tsx
import { Calendar } from "@/components/ui/calendar"

const [date, setDate] = React.useState<Date | undefined>(new Date())

return (
  <Calendar
    mode="single"
    selected={date}
    onSelect={setDate}
    className="rounded-md border"
  />
)
```

## Component Structure
The Calendar component relies on React DayPicker for calendar functionality and supports various selection modes, including:
- Single date selection
- Multiple date selection
- Range selection

## Common Use Cases
- Date input fields in forms
- Date selection for scheduling
- Date range selection for reporting
- As part of a more complex Date Picker component

## Recent Changes
- 11-03-2024: Changed the color of the `day_outside` class to improve contrast

## Related Components
- Date Picker (built using Calendar)