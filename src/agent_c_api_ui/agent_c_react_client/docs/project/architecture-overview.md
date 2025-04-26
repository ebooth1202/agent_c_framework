# Agent C React UI: Project Architecture Overview

## Overview

This document provides a comprehensive overview of the Agent C React UI architecture, including the core technologies, component structure, state management approach, and key design patterns.

## Contents

- [Technology Stack](#technology-stack)
- [Application Structure](#application-structure)
- [Component Architecture](#component-architecture)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Theme System](#theme-system)

## Technology Stack

The Agent C React UI is built using modern web technologies:

- **React 18**: Core UI library using functional components and hooks
- **Vite**: Modern build tool for fast development and production optimization
- **React Router v7**: Client-side routing and navigation
- **shadcn/ui**: Component library system built on Radix UI primitives
- **Tailwind CSS**: Utility-first CSS framework integrated with shadcn/ui
- **Lucide React**: Icon library for consistent iconography

## Application Structure

The application follows a feature-based organization with logical separation of concerns:

```
src/
  components/     # UI components organized by feature
    chat_interface/  # Components for the chat feature
    rag_interface/   # Components for RAG functionality
    ui/              # shadcn/ui components
  config/         # Application configuration
  contexts/       # React context providers
  hooks/          # Custom React hooks
  lib/            # Utility functions and helpers
  pages/          # Page components for routing
  styles/         # CSS styles organized by scope
```

## Component Architecture

The application uses a component-based architecture with several key patterns:

### Core Structure

- **App.jsx**: Root component that sets up routing and context providers
- **Routes.jsx**: Defines application routes with lazy-loaded pages
- **Layout.jsx**: Common layout wrapper with navigation and footer

### Component Organization

Components are organized into several categories:

1. **Page Components**: Top-level components tied to routes (e.g., ChatPage, RAGPage)
2. **Feature Components**: Components related to specific features (e.g., ChatInterface, CollectionsManager)
3. **UI Components**: Reusable UI elements based on shadcn/ui (e.g., Button, Dialog)
4. **Layout Components**: Structural components (e.g., Layout, AppSidebar)

### Component Composition Pattern

The application uses composition over inheritance, with components composed from smaller, focused components that:

- Follow the single responsibility principle
- Use props for configuration
- Leverage React context for shared state
- Separate logical concerns from presentation

## State Management

The application uses a combination of state management approaches:

### Local Component State

- React's `useState` for component-specific state
- `useReducer` for more complex component state logic

### Application State

- **SessionContext**: Primary context provider managing:
  - Session state and authentication
  - Model configuration and parameters
  - Tool management
  - UI state (loading, streaming, etc.)

### Data Flow

- Props for parent-to-child communication
- Context for shared state across component trees
- Custom events for specific cross-component communication

## API Integration

The application communicates with the Agent C backend API:

- API endpoints configured in `config.js`
- Fetch API for data requests with async/await pattern
- Streaming responses handled with appropriate patterns
- File uploads managed with FormData

## Theme System

The application implements a theme system that supports light and dark modes:

- CSS variables defined in `:root` and `[data-theme="dark"]`
- Components styled using these variables for theme consistency
- Theme toggle functionality managed by ThemeProvider
- Responsive design with mobile-first approach

## Related Documentation

- [Getting Started Guide](./getting-started.md)
- [Component Documentation](../components/README.md)
- [Styling Guide](../style/styling-guide.md)