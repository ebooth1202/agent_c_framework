# Component Dependency Map

## Core Layout Components

```
Layout.jsx
├─ PageHeader.jsx
├─ Sidebar.jsx
└─ MobileNav.jsx
```

## Chat Interface Components

```
ChatInterface.jsx
├─ MessagesList.jsx
│  ├─ MessageItem.jsx
│  │  ├─ UserMessage.jsx
│  │  ├─ AssistantMessage.jsx
│  │  │  ├─ ToolCallDisplay.jsx
│  │  │  │  └─ ToolCallItem.jsx
│  │  │  ├─ ThoughtDisplay.jsx
│  │  │  └─ TokenUsageDisplay.jsx
│  │  ├─ SystemMessage.jsx
│  │  └─ MediaMessage.jsx
│  └─ MarkdownMessage.jsx
├─ StatusBar.jsx
├─ ChatInputArea.jsx
├─ CollapsibleOptions.jsx
│  ├─ PersonaSelector.jsx
│  ├─ ModelParameterControls.jsx
│  └─ ToolSelector.jsx
├─ FileUploadManager.jsx
│  └─ FileItem.jsx
└─ DragDropArea.jsx
```

## RAG Interface Components

```
CollectionsManager.jsx
SearchContainer.jsx
├─ SearchForm.jsx
└─ SearchResults.jsx
UploadContainer.jsx
```

## Replay Interface Components

```
ReplayPage.jsx
├─ EnhancedChatEventReplay.jsx
├─ EventDisplay.jsx
├─ ModelCardDisplay.jsx
└─ SystemPromptDisplay.jsx
```

## Component Migration Priority

Based on the component analysis and dependency relationships, here's the recommended migration order:

### Phase 1: Core Layout Components
1. **Sidebar.jsx** - Navigation component used throughout the app
2. **PageHeader.jsx** - Header component used on all pages
3. **Layout.jsx** - Main layout wrapper that includes the above
4. **MobileNav.jsx** - Mobile navigation component

### Phase 2: Form and Input Components
1. **ChatInputArea.jsx** - Main input area for the chat interface
2. **ModelParameterControls.jsx** - Controls for model parameters
3. **PersonaSelector.jsx** - Selection component for personas
4. **FileUploadManager.jsx** - File upload functionality

### Phase 3: Message Components
1. **UserMessage.jsx** - User message bubble
2. **SystemMessage.jsx** - System message component
3. **AssistantMessage.jsx** - Assistant message component
4. **MarkdownMessage.jsx** - Markdown rendering component

### Phase 4: Tool-Related Components
1. **ToolCallItem.jsx** - Individual tool call display
2. **ToolCallDisplay.jsx** - Container for tool calls
3. **ThoughtDisplay.jsx** - Display for AI thinking process

### Phase 5: Complex Interactive Components
1. **CollapsibleOptions.jsx** - Options panel with complex state
2. **StatusBar.jsx** - Status information display
3. **TokenUsageDisplay.jsx** - Token usage visualization

### Phase 6: RAG and Replay Components
1. **SearchForm.jsx** - Form for search functionality
2. **SearchResults.jsx** - Results display component
3. **ReplayPage.jsx** and subcomponents - Replay interface components

## Component shadcn/ui Mapping

Here's how current components map to shadcn/ui components:

| Current Component | shadcn/ui Components Needed |
|-------------------|----------------------------|
| Sidebar.jsx | Sheet (mobile), ScrollArea |
| PageHeader.jsx | NavigationMenu |
| ChatInputArea.jsx | Textarea, Button |
| ModelParameterControls.jsx | Slider, Form, Select |
| PersonaSelector.jsx | Select, RadioGroup |
| CollapsibleOptions.jsx | Collapsible, Accordion |
| ToolCallDisplay.jsx | Collapsible, Badge |
| FileUploadManager.jsx | Button, Input (file), DropdownMenu |
| StatusBar.jsx | Badge, Tooltip |
| UserMessage.jsx | Card, Avatar |
| AssistantMessage.jsx | Card, Avatar |
| MediaMessage.jsx | Card, AspectRatio |
| ToolSelector.jsx | Checkbox, DropdownMenu |

## Implementation Strategy

For each component:

1. Create a new component using shadcn/ui primitives
2. Convert CSS classes to Tailwind utilities
3. Preserve component-specific theme variables
4. Test the component in isolation
5. Replace the old component with the new one
6. Test the component in context

Start with simpler components like Sidebar and gradually move to more complex ones.