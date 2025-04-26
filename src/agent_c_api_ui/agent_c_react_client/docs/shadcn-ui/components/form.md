# Form Component
Created: 2025-04-24
Source: form.mdx

## Overview
The Form component is a wrapper around React Hook Form that provides accessible, type-safe form handling with Zod validation. It helps create well-structured, semantically correct, and accessible forms.

## Key Features
- Composable components for building forms
- Controlled form fields with FormField component
- Form validation using Zod
- Accessible form fields with proper ARIA attributes
- Unique ID generation with React.useId()
- Compatible with Radix UI components
- Flexible schema integration (Zod by default)
- Complete control over markup and styling

## Component Structure

```tsx
<Form>
  <FormField
    control={...}
    name="..."
    render={() => (
      <FormItem>
        <FormLabel />
        <FormControl>
          {/* Your form field */}
        </FormControl>
        <FormDescription />
        <FormMessage />
      </FormItem>
    )}
  />
</Form>
```

## Installation

```bash
npx shadcn@latest add form
```

Dependencies:
```bash
npm install @radix-ui/react-label @radix-ui/react-slot react-hook-form @hookform/resolvers zod
```

## Usage Guide

### 1. Create a Form Schema

```tsx
"use client"

import { z } from "zod"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
})
```

### 2. Define the Form

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
})

export function ProfileForm() {
  // 1. Define your form
  const form = useForm<z.infer<typeof formSchema>>({  
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
    },
  })

  // 2. Define submit handler
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values
    console.log(values)
  }
}
```

### 3. Build the Form UI

```tsx
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

export function ProfileForm() {
  // ... form definition from step 2

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

## Form Components

### Form
Main wrapper that provides form context.

### FormField
Component for creating controlled form fields with React Hook Form.

**Props:**
- `control`: Form control from React Hook Form
- `name`: Field name (must match schema)
- `render`: Function that renders the form field

### FormItem
Wrapper for form items that provides proper spacing and layout.

### FormLabel
Accessible label for form fields.

### FormControl
Wrapper that applies the correct aria attributes to form controls.

### FormDescription
Help text for form fields.

### FormMessage
Error message container for form validation errors.

## Integration with Other Components

The Form components work with various input components:

- Checkbox - For boolean inputs and multiple selections
- Date Picker - For date selection
- Input - For text and numeric inputs
- Radio Group - For single selection from multiple options
- Select - For dropdown selection
- Switch - For toggle inputs
- Textarea - For multiline text input
- Combobox - For searchable dropdown selection

## Advanced Usage

### Nested Objects

```tsx
const formSchema = z.object({
  profile: z.object({
    name: z.string(),
    bio: z.string(),
  }),
})

// In the form
<FormField
  control={form.control}
  name="profile.name"
  render={...}
/>
```

### Array Fields

```tsx
const formSchema = z.object({
  emails: z.array(z.string().email()),
})

// In the form
{fields.map((field, index) => (
  <FormField
    key={field.id}
    control={form.control}
    name={`emails.${index}`}
    render={...}
  />
))}
```

### Dynamic Validation

```tsx
const formSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})
```