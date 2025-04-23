# Phase 1: CSS Extraction and Cleanup - Tracking

## CSS Inventory Tracking

| CSS File | Purpose | Status | Notes |
|---------|---------|--------|-------|
| globals.css | Global styles and CSS variables | 📝 To Analyze | Contains shadcn/ui variables |
| main.css | Main application styles | 📝 To Analyze | |
| component-styles.css | Component-specific imports | 📝 To Analyze | |
| common/badges.css | Badge styling | 📝 To Analyze | |
| common/cards.css | Card styling | 📝 To Analyze | |
| common/interactive.css | Interactive element styling | 📝 To Analyze | |
| common/layout.css | Layout utilities | 📝 To Analyze | |
| common/reset.css | CSS resets | 📝 To Analyze | |
| common/tooltips.css | Tooltip styling | 📝 To Analyze | |
| common/typography.css | Typography styles | 📝 To Analyze | |
| common/utilities.css | Utility classes | 📝 To Analyze | |
| common/variables.css | CSS variables | 📝 To Analyze | |
| components/agent-config-display.css | AgentConfigDisplay component styling | 📝 To Analyze | |
| components/agent-config-hover-card.css | AgentConfigHoverCard component styling | 📝 To Analyze | |
| components/animated-status-indicator.css | AnimatedStatusIndicator component styling | 📝 To Analyze | |
| components/assistant-message.css | AssistantMessage component styling | 📝 To Analyze | |
| components/chat-input-area.css | ChatInputArea component styling | 📝 To Analyze | |
| components/drag-drop-overlay.css | DragDropOverlay component styling | 📝 To Analyze | |
| components/file-item.css | FileItem component styling | 📝 To Analyze | |
| components/layout.css | Layout component styling | 📝 To Analyze | |
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
| Sidebar.jsx | Traditional CSS | Button | High | 📝 To Analyze |
| PageHeader.jsx | Traditional CSS | - | High | 📝 To Analyze |
| MobileNav.jsx | Traditional CSS | Button | High | 📝 To Analyze |
| ChatInterface.jsx | Mixed | Card, Button | High | 📝 To Analyze |
| MessagesList.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| StatusBar.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| CollapsibleOptions.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| FileUploadManager.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| DragDropArea.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
| ToolCallDisplay.jsx | Traditional CSS | - | Medium | 📝 To Analyze |
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
| Textarea | Installed | ChatInputArea | - |
| Toast | Installed | - | - |
| Tooltip | Installed | - | - |
| Accordion | Need to install | - | - |
| Avatar | Need to install | - | - |
| DropdownMenu | Need to install | - | - |
| Form | Need to install | - | react-hook-form, zod |
| Separator | Need to install | - | - |
| Sheet | Need to install | MobileNav | - |
| ContextMenu | Need to install | - | - |

## CSS Variable Mapping

This section will be populated as we analyze the CSS files.