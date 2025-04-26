# Date Picker Component
Created: 2025-04-24
Source: date-picker.mdx

## Overview
A date picker component that enables users to select dates from a calendar interface in a popover. Built by composing the `Popover` and `Calendar` components together.

## Features
- Single date selection
- Date range selection
- Date presets for quick selection
- Form integration
- Customizable appearance

## Installation
The Date Picker requires both the Popover and Calendar components:

```bash
# Install Popover component
npx shadcn@latest add popover

# Install Calendar component
npx shadcn@latest add calendar
```

## Usage Example

```tsx
"use client"

import * as React from "react"
import { format } from "date-fns"
import { Calendar as CalendarIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function DatePickerDemo() {
  const [date, setDate] = React.useState<Date>()

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-[280px] justify-start text-left font-normal",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "PPP") : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  )
}
```

## Variants

### Basic Date Picker
Simple date picker that allows selecting a single date from a calendar interface.

### Date Range Picker
Extends the basic date picker to allow selecting a range of dates.

```tsx
// Key differences for range implementation
const [date, setDate] = React.useState<DateRange | undefined>({
  from: new Date(2022, 0, 20),
  to: new Date(2022, 0, 25),
})

// In the Calendar component
<Calendar
  mode="range"
  selected={date}
  onSelect={setDate}
  numberOfMonths={2}
  initialFocus
/>
```

### Date Picker with Presets
Enhances the date picker with predefined date options for quick selection.

```tsx
// Example preset implementation
<PopoverContent className="w-auto p-0" align="start">
  <Select
    onValueChange={(value) =>
      setDate(
        value === "today"
          ? new Date()
          : value === "yesterday"
          ? addDays(new Date(), -1)
          : value === "last-week"
          ? addDays(new Date(), -7) 
          : undefined
      )
    }
  >
    <SelectTrigger>
      <SelectValue placeholder="Select" />
    </SelectTrigger>
    <SelectContent position="popper">
      <SelectItem value="today">Today</SelectItem>
      <SelectItem value="yesterday">Yesterday</SelectItem>
      <SelectItem value="last-week">Last week</SelectItem>
    </SelectContent>
  </Select>
  <Calendar
    mode="single"
    selected={date}
    onSelect={setDate}
    initialFocus
  />
</PopoverContent>
```

### Form Integration
The date picker can be integrated with form libraries like React Hook Form:

```tsx
// With React Hook Form integration
const form = useForm<FormValues>({
  defaultValues: {
    dob: new Date(),
  },
})

// In the form
<FormField
  control={form.control}
  name="dob"
  render={({ field }) => (
    <FormItem className="flex flex-col">
      <FormLabel>Date of birth</FormLabel>
      <Popover>
        <PopoverTrigger asChild>
          <FormControl>
            <Button
              variant={"outline"}
              className={cn(
                "w-[240px] pl-3 text-left font-normal",
                !field.value && "text-muted-foreground"
              )}
            >
              {field.value ? (
                format(field.value, "PPP")
              ) : (
                <span>Pick a date</span>
              )}
              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
            </Button>
          </FormControl>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={field.value}
            onSelect={field.onChange}
            disabled={(date) =>
              date > new Date() || date < new Date("1900-01-01")
            }
            initialFocus
          />
        </PopoverContent>
      </Popover>
      <FormDescription>
        Your date of birth is used to calculate your age.
      </FormDescription>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Calendar Props
The Calendar component (used within the DatePicker) supports these key props:

- `mode`: "single" | "multiple" | "range" - Selection mode
- `selected`: Date | Date[] | DateRange - Currently selected date(s)
- `onSelect`: Function to handle selection changes
- `disabled`: Function or array to disable specific dates
- `initialFocus`: Set focus on calendar when opened
- `numberOfMonths`: Number of months to display at once
- `fixedWeeks`: Force six weeks display per month
- `ISOWeek`: Use ISO week numbers

See the [React DayPicker](https://react-day-picker.js.org) documentation for more details and options.