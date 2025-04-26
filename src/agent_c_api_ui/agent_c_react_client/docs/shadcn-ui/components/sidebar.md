# Sidebar Component

*Created: 2025-04-24 | Source: sidebar.mdx*

## Overview

Sidebar is a composable, themeable, and customizable component for creating application sidebars. It provides a comprehensive solution for building complex sidebar interfaces with collapsible sections, navigation menus, and responsive behavior.

## Key Features

- Multiple sidebar variants (standard, floating, inset)
- Collapsible modes (offcanvas, icon, none)
- Responsive design with mobile support
- Sticky header and footer sections
- Scrollable content area
- Composable menu system
- Keyboard shortcut support
- Persistence via cookies
- Custom theming capabilities

## Installation

**CLI Method:**
```bash
npx shadcn@latest add sidebar
```

**Manual Installation:**
1. Copy the sidebar component code to your project
2. Update import paths to match your project structure
3. Add required CSS variables to your stylesheet:
   ```css
   @layer base {
     :root {
       --sidebar-background: 0 0% 98%;
       --sidebar-foreground: 240 5.3% 26.1%;
       --sidebar-primary: 240 5.9% 10%;
       --sidebar-primary-foreground: 0 0% 98%;
       --sidebar-accent: 240 4.8% 95.9%;
       --sidebar-accent-foreground: 240 5.9% 10%;
       --sidebar-border: 220 13% 91%;
       --sidebar-ring: 217.2 91.2% 59.8%;
     }
     .dark {
       --sidebar-background: 240 5.9% 10%;
       --sidebar-foreground: 240 4.8% 95.9%;
       --sidebar-primary: 224.3 76.3% 48%;
       --sidebar-primary-foreground: 0 0% 100%;
       --sidebar-accent: 240 3.7% 15.9%;
       --sidebar-accent-foreground: 240 4.8% 95.9%;
       --sidebar-border: 240 3.7% 15.9%;
       --sidebar-ring: 217.2 91.2% 59.8%;
     }
   }
   ```
4. Add Sidebar tailwind config to `tailwind.config.js`:
   ```js
   sidebar: {
     DEFAULT: 'hsl(var(--sidebar-background))',
     foreground: 'hsl(var(--sidebar-foreground))',
     primary: 'hsl(var(--sidebar-primary))',
     'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
     accent: 'hsl(var(--sidebar-accent))',
     'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
     border: 'hsl(var(--sidebar-border))',
     ring: 'hsl(var(--sidebar-ring))',
   }
   ```

## Component Structure

The Sidebar component is composed of several parts:

- `SidebarProvider` - Context provider for sidebar state
- `Sidebar` - Main container component
- `SidebarHeader` - Sticky header section
- `SidebarFooter` - Sticky footer section
- `SidebarContent` - Scrollable content area
- `SidebarGroup` - Section within content
- `SidebarMenu` - Navigation menu system
- `SidebarTrigger` - Toggle button for sidebar
- `SidebarRail` - Optional rail for toggling

## Basic Usage

```tsx
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main>
        <SidebarTrigger />
        {children}
      </main>
    </SidebarProvider>
  )
}
```

```tsx
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
```

## SidebarProvider

The `SidebarProvider` handles the sidebar state and provides context to all sidebar components.

**Props:**
- `defaultOpen` (boolean) - Default open state
- `open` (boolean) - Controlled open state
- `onOpenChange` (function) - Callback for open state changes

Customize sidebar width with CSS variables:
```tsx
<SidebarProvider
  style={{
    "--sidebar-width": "20rem",
    "--sidebar-width-mobile": "20rem",
  }}
>
  <Sidebar />
</SidebarProvider>
```

## Persisted State

The sidebar state can be persisted using cookies:

```tsx
import { cookies } from "next/headers"

export async function Layout({ children }) {
  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get("sidebar_state")?.value === "true"

  return (
    <SidebarProvider defaultOpen={defaultOpen}>
      {/* ... */}
    </SidebarProvider>
  )
}
```

## Sidebar Props

- `side`: "left" | "right" - The side of the sidebar
- `variant`: "sidebar" | "floating" | "inset" - The variant of the sidebar
- `collapsible`: "offcanvas" | "icon" | "none" - Collapsible behavior

## useSidebar Hook

Control the sidebar programmatically:

```tsx
const {
  state,           // "expanded" | "collapsed"
  open,            // boolean
  setOpen,         // (open: boolean) => void
  openMobile,      // boolean
  setOpenMobile,   // (open: boolean) => void
  isMobile,        // boolean
  toggleSidebar,   // () => void
} = useSidebar()
```

## Advanced Features

### Collapsible SidebarGroup

```tsx
<Collapsible defaultOpen className="group/collapsible">
  <SidebarGroup>
    <SidebarGroupLabel asChild>
      <CollapsibleTrigger>
        Help
        <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
      </CollapsibleTrigger>
    </SidebarGroupLabel>
    <CollapsibleContent>
      <SidebarGroupContent />
    </CollapsibleContent>
  </SidebarGroup>
</Collapsible>
```

### SidebarGroupAction

```tsx
<SidebarGroup>
  <SidebarGroupLabel>Projects</SidebarGroupLabel>
  <SidebarGroupAction title="Add Project">
    <Plus /> <span className="sr-only">Add Project</span>
  </SidebarGroupAction>
  <SidebarGroupContent />
</SidebarGroup>
```

### SidebarMenu with Submenu

```tsx
<SidebarMenuItem>
  <SidebarMenuButton />
  <SidebarMenuSub>
    <SidebarMenuSubItem>
      <SidebarMenuSubButton />
    </SidebarMenuSubItem>
  </SidebarMenuSub>
</SidebarMenuItem>
```

### Data Fetching

With React Server Components:

```tsx
function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Projects</SidebarGroupLabel>
          <SidebarGroupContent>
            <React.Suspense fallback={<NavProjectsSkeleton />}>
              <NavProjects />
            </React.Suspense>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
```

## Controlled Sidebar

```tsx
export function AppSidebar() {
  const [open, setOpen] = React.useState(false)

  return (
    <SidebarProvider open={open} onOpenChange={setOpen}>
      <Sidebar />
    </SidebarProvider>
  )
}
```

## Styling Tips

- Hide elements in icon mode: `className="group-data-[collapsible=icon]:hidden"`
- Show menu action when button is active: `className="peer-data-[active=true]/menu-button:opacity-100"`