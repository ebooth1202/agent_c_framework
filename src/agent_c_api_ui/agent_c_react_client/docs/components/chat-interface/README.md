# Chat Interface Components

This directory contains documentation for the components that make up the chat interface in the Agent C React UI.

## Core Components

- [ChatInterface](./chat-interface.md) - The main container component for the chat functionality
- [MessagesList](./messages-list.md) - Component for displaying the list of messages

## Purpose

The chat interface is the primary way users interact with Agent C. It provides a conversational interface where users can send messages, upload files, and see responses from the AI assistant. The components in this section handle everything from message display to input handling and tool interactions.

## Component Relationships

The chat interface follows a hierarchical structure:

```
ChatInterface
u2523u2501u2501 PersonaSelector
u2523u2501u2501 MessagesList
u2503   u2517u2501u2501 MessageItem (multiple)
u2503       u2523u2501u2501 UserMessage
u2503       u2523u2501u2501 AssistantMessage
u2503       u2523u2501u2501 SystemMessage
u2503       u2517u2501u2501 ToolCallDisplay
u2523u2501u2501 ChatInputArea
u2523u2501u2501 FilesPanel
u2503   u2517u2501u2501 FileItem (multiple)
u2523u2501u2501 ToolSelector
u2517u2501u2501 StatusBar
```

## Features

The chat interface components collectively provide the following features:

- Real-time message streaming
- File uploads and attachments
- Tool selection and execution
- Persona/model selection
- Markdown message rendering
- Copy and export functionality
- Status indicators and notifications

## State Management

State in the chat interface is managed through a combination of:

- React Context for global state (SessionContext)
- Component-level state for UI-specific concerns
- Props for passing data down the component tree

## CSS Organization

Each component has its own CSS file in `src/styles/components/`, following the naming convention of kebab-case (e.g., `chat-interface.css`, `messages-list.css`).