# Component Organization

## Overview

This document explains how components in the Agent C React UI are organized, their relationships to each other, and best practices for component creation and management.

## Contents
- [Component Hierarchy](#component-hierarchy)
- [Component Relationships](#component-relationships)
- [Component Categories](#component-categories)
- [Best Practices](#best-practices)

## Component Hierarchy

The application follows a hierarchical component structure with clearly defined responsibilities at each level:

```
App
┣━━ ThemeProvider
┗━━ Layout
    ┣━━ AppSidebar
    ┃   ┣━━ Navigation items
    ┃   ┗━━ Theme Toggle
    ┣━━ PageHeader
    ┗━━ Page Content
        ┣━━ HomePage
        ┣━━ ChatPage
        ┃   ┗━━ ChatInterface
        ┃       ┣━━ PersonaSelector
        ┃       ┣━━ MessagesList
        ┃       ┃   ┗━━ MessageItem (multiple)
        ┃       ┃       ┣━━ UserMessage
        ┃       ┃       ┣━━ AssistantMessage
        ┃       ┃       ┣━━ SystemMessage
        ┃       ┃       ┗━━ ToolCallDisplay
        ┃       ┣━━ ChatInputArea
        ┃       ┗━━ FilesPanel
        ┣━━ RAGPage
        ┗━━ SettingsPage
```

## Component Relationships

### Context-Based Relationships

Components share data and state through React contexts:

1. **SessionContext**
   - Primary state management for chat interaction
   - Provides session state to `ChatInterface` and all child components
   - Manages model configuration, parameters, tools, and UI state

2. **ThemeContext**
   - Manages theme state (light/dark)
   - Used throughout the application for theme-aware components

3. **ToolCallContext**
   - Specialized context for tool call state management
   - Used by `ToolCallDisplay` and `ToolCallItem`

### Parent-Child Relationships

Key component relationships follow these patterns:

1. **Container Components**
   - `Layout`: Acts as the main container with consistent header and sidebar
   - `ChatInterface`: Container for chat functionality components
   - `FilesPanel`: Container for file-related components

2. **Composite Components**
   - `MessagesList`: Composes multiple `MessageItem` components
   - `ToolCallDisplay`: Composes multiple `ToolCallItem` components

3. **Provider Components**
   - `ThemeProvider`: Provides theme context
   - `SessionProvider`: Provides session state

## Component Categories

Components are organized into several categories:

### 1. UI Components

**Location**: `src/components/ui/`

These are foundational UI components based on shadcn/ui, which themselves are built on Radix UI primitives. They include:

- Button
- Card
- Dialog
- Select
- Checkbox
- Input
- etc.

### 2. Layout Components

**Location**: Root of `src/components/`

Components that define the application structure and layout:

- `Layout.jsx`: Main application layout
- `AppSidebar.jsx`: Application sidebar navigation
- `PageHeader.jsx`: Page header component

### 3. Feature-Specific Components

**Location**: In feature-specific directories

#### Chat Interface Components

**Location**: `src/components/chat_interface/`

Components specifically for the chat functionality:

- `ChatInterface.jsx`: Main chat component
- `MessagesList.jsx`: List of chat messages
- `MessageItem.jsx`: Individual message component
- `ChatInputArea.jsx`: Message input and controls
- etc.

#### RAG Interface Components

**Location**: `src/components/rag_interface/`

Components for Retrieval-Augmented Generation functionality:

- Collections management
- Document upload
- Search interface

#### Replay Interface Components

**Location**: `src/components/replay_interface/`

Components for session replay functionality.

## Best Practices

### Component Creation Guidelines

1. **Single Responsibility Principle**
   - Each component should have a single responsibility
   - Break down complex components into smaller, focused ones

2. **Component Naming**
   - Use PascalCase for component names
   - Names should clearly indicate the component's purpose
   - Prefix related components (e.g., `MessageItem`, `MessagesList`)

3. **File Organization**
   - One component per file (with exceptions for very small related components)
   - Group related components in meaningful directories
   - Use index files to simplify imports

4. **Props Management**
   - Use destructuring for props
   - Provide default values for optional props
   - Document props with comments
   - Use prop spreading cautiously

### Component Composition Patterns

1. **Composition over Inheritance**
   - Use component composition rather than inheritance
   - Create higher-order components or use render props for shared functionality

2. **Children Props**
   - Use `children` prop for component composition
   - Create "slot" patterns for more complex compositions

3. **Container/Presentational Pattern**
   - Separate data fetching and state management (containers) from rendering (presentational)
   - Keep presentational components pure

4. **Component Extensions**
   - Extend shadcn/ui components rather than modifying their source
   - Create wrapper components with additional functionality

### State Management

1. **Local vs. Global State**
   - Use local state for UI-specific concerns
   - Use context for shared state that spans components
   - Consider component co-location for related state

2. **State Initialization**
   - Initialize state with sensible defaults
   - Consider lazy initialization for expensive computations

3. **State Updates**
   - Use functional updates for state that depends on previous value
   - Batch related state updates

### Performance Considerations

1. **Memoization**
   - Use `React.memo` for pure functional components
   - Use `useMemo` for expensive computations
   - Use `useCallback` for functions passed as props

2. **Lazy Loading**
   - Lazy load components that aren't immediately needed
   - Use code splitting for large component trees

3. **Virtualization**
   - Use virtualization for long lists (e.g., `MessagesList`)

## Related Documentation

- [Project Architecture Overview](./architecture-overview.md)
- [Chat Interface Components](../components/chat-interface/README.md)
- [UI Components](../components/ui/README.md)