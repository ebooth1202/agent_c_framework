# Phase 1: CSS Extraction and Cleanup - Tracking

## CSS Inventory Tracking

| CSS File | Purpose | Status | Notes |
|---------|---------|--------|-------|
| globals.css | Global styles and CSS variables | ✅ Analyzed | Contains shadcn/ui variables and Tailwind directives |
| main.css | Main application styles | ✅ Analyzed | Import file for component and common styles |
| component-styles.css | Component-specific imports | ✅ Analyzed | Legacy import file for backwards compatibility |
| common/badges.css | Badge styling | 📝 To Analyze | |
| common/cards.css | Card styling | 📝 To Analyze | |
| common/interactive.css | Interactive element styling | 📝 To Analyze | |
| common/layout.css | Layout utilities | 📝 To Analyze | |
| common/reset.css | CSS resets | 📝 To Analyze | |
| common/tooltips.css | Tooltip styling | 📝 To Analyze | |
| common/typography.css | Typography styles | 📝 To Analyze | |
| common/utilities.css | Utility classes | 📝 To Analyze | |
| common/variables.css | CSS variables | ✅ Analyzed | Comprehensive set of theme variables, colors, spacing, typography |
| components/agent-config-display.css | AgentConfigDisplay component styling | 📝 To Analyze | |
| components/agent-config-hover-card.css | AgentConfigHoverCard component styling | 📝 To Analyze | |
| components/animated-status-indicator.css | AnimatedStatusIndicator component styling | 📝 To Analyze | |
| components/assistant-message.css | AssistantMessage component styling | ✅ Analyzed | Styling for assistant message bubbles, content, and tool calls |
| components/chat-input-area.css | ChatInputArea component styling | ✅ Analyzed | Styling for chat input textarea and action buttons |
| components/drag-drop-overlay.css | DragDropOverlay component styling | 📝 To Analyze | |
| components/file-item.css | FileItem component styling | 📝 To Analyze | |
| components/layout.css | Layout component styling | ✅ Analyzed | Main layout structure with header, navigation, and content area |
| components/markdown-message.css | MarkdownMessage component styling | 📝 To Analyze | |
| components/media-message.css | MediaMessage component styling | 📝 To Analyze | |
| components/mobile-nav.css | MobileNav component styling | 📝 To Analyze | |
| components/model-parameter-controls.css | ModelParameterControls component styling | 📝 To Analyze | |
| components/page-header.css | PageHeader component styling | 📝 To Analyze | |
| components/parameter-documentation.css | ParameterDocumentation component styling | 📝 To Analyze | |
| components/persona-selector.css | PersonaSelector component styling | 📝 To Analyze | |
| components/sidebar.css | Sidebar component styling | 📝 To Analyze | |
| components/status-bar.css | StatusBar component styling | 📝 To Analyze | |
| components/system-message.css | SystemMessage component styling | 📝 To Analyze | |
| components/thought-display.css | ThoughtDisplay component styling | 📝 To Analyze | |
| components/tool-call-display.css | ToolCallDisplay component styling | 📝 To Analyze | |
| components/tool-call-item-integrated.css | Integrated ToolCallItem styling | 📝 To Analyze | |
| components/tool-call-item.css | ToolCallItem component styling | 📝 To Analyze | |
| components/user-message.css | UserMessage component styling | 📝 To Analyze | |

## Component Inventory Tracking

| Component | Current Style Type | shadcn/ui Dependencies | Migration Priority | Status |
|-----------|-------------------|------------------------|-------------------|--------|
| Layout.jsx | Traditional CSS | Card | High | 📝 To Analyze |
| Sidebar.jsx | Traditional CSS | Button | High | ✅ Analyzed | Navigation sidebar with links, could be migrated to Sheet for mobile |
| PageHeader.jsx | Traditional CSS | - | High | 📝 To Analyze |
| MobileNav.jsx | Traditional CSS | Button | High | 📝 To Analyze |
| ChatInterface.jsx | Mixed | Card, Button, Dialog | High | ✅ Analyzed | Uses shadcn/ui Card and Button with custom CSS classes |
| ChatInputArea.jsx | Mixed | Textarea, Button | High | ✅ Migrated | Converted to use shadcn/ui Textarea component |
| MessagesList.jsx | CSS | ScrollArea | Medium | ✅ Analyzed | Uses shadcn/ui ScrollArea component with better semantic CSS classes |
| StatusBar.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| CollapsibleOptions.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| FileUploadManager.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| DragDropArea.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| ToolCallDisplay.jsx | Mixed | Badge | Medium | ✅ Analyzed | Uses Badge component with custom container styling |
| ThoughtDisplay.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| TokenUsageDisplay.jsx | Traditional CSS | - | Low | 📝 To Analyze |
| PersonaSelector.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| ModelParameterControls.jsx | Traditional CSS | - | Medium | 📝 To Analyze |

## shadcn/ui Component Needs Assessment

| shadcn/ui Component | Status | Required By | Dependencies |
|---------------------|--------|-------------|-------------|
| Alert | Installed | - | - |
| AlertDialog | Installed | - | - |
| Badge | Installed | - | - |
| Button | Installed | Multiple | - |
| Card | Installed | Multiple | - |
| Checkbox | Installed | - | - |
| Collapsible | Installed | CollapsibleOptions | - |
| Dialog | Installed | - | - |
| HoverCard | Installed | AgentConfigHoverCard | - |
| Input | Installed | Multiple | - |
| Label | Installed | Multiple | - |
| Progress | Installed | - | - |
| ScrollArea | Installed | - | - |
| Select | Installed | - | - |
| Slider | Installed | ModelParameterControls | - |
| Switch | Installed | - | - |
| Tabs | Installed | - | - |
| Textarea | Installed | ChatInputArea | - | ✅ Implemented in ChatInputArea |
| Toast | Installed | - | - |
| Tooltip | Installed | - | - |
| Accordion | Need to install | CollapsibleOptions | - |
| Avatar | Need to install | UserMessage, AssistantMessage | - |
| DropdownMenu | Need to install | FileUploadManager, ToolSelector | - |
| Form | Need to install | ChatInputArea, ModelParameterControls | react-hook-form, zod |
| Separator | Need to install | CollapsibleOptions, StatusBar | - |
| Sheet | Need to install | MobileNav, Sidebar (mobile view) | - |
| ContextMenu | Need to install | MessageItem (for actions) | - |

## CSS Variable Mapping

See the comprehensive CSS-to-Tailwind mapping document at `.scratch/css_to_tailwind_mapping.md`

## Component Dependency Map

See the detailed component dependency analysis at `.scratch/component_dependency_map.md`