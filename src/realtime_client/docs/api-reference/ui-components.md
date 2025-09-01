# UI Components API Reference

This document provides comprehensive documentation for all components in the `@agentc/realtime-ui` package.

## Table of Contents

- [Input Components](#input-components)
  - [InputArea](#inputarea)
  - [InputContainer](#inputcontainer)
  - [InputToolbar](#inputtoolbar)
  - [MicrophoneButton](#microphonebutton)
  - [OutputSelector](#outputselector)
  - [AgentSelector](#agentselector)
  - [MarkdownEditor (Input)](#markdowneditor-input)
  - [RichTextEditor](#richtexteditor)
- [Editor Components](#editor-components)
  - [MarkdownEditor (Enhanced)](#markdowneditor-enhanced)
  - [CodeHighlightExample](#codehighlightexample)
  - [SmartPasteExample](#smartpasteexample)
- [UI Components (CenSuite)](#ui-components-censuite)
  - [Alert](#alert)
  - [Avatar](#avatar)
  - [Badge](#badge)
  - [Button](#button)
  - [DropdownMenu](#dropdownmenu)
  - [Separator](#separator)
  - [Tooltip](#tooltip)

---

## Input Components

### InputArea

A comprehensive input area component that integrates chat, voice recording, and avatar controls with the Realtime SDK.

#### Import
```tsx
import { InputArea } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| className | string | No | Additional CSS classes |
| maxHeight | string | No | Maximum height for the input area (default: "200px") |
| placeholder | string | No | Placeholder text for the input |
| agents | Agent[] | No | Available agent options |
| voiceOptions | OutputOption[] | No | Available voice options |
| avatarOptions | OutputOption[] | No | Available avatar options |
| onAgentChange | (agent: Agent) => void | No | Callback when agent changes |
| onOutputModeChange | (mode: OutputMode, option?: OutputOption) => void | No | Callback when output mode changes |

#### Usage
```tsx
<InputArea
  placeholder="Type a message or click the microphone to speak..."
  maxHeight="300px"
  onAgentChange={(agent) => console.log('Selected agent:', agent)}
/>
```

#### Features/Notes
- Integrates with SDK hooks for chat, audio, turn state, voice model, and avatar
- Handles text and voice input seamlessly
- Shows recording and typing indicators
- Manages error states and permissions
- Respects turn-based conversation flow

---

### InputContainer

A container component that provides consistent styling and layout for input areas.

#### Import
```tsx
import { InputContainer } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| children | React.ReactNode | Yes | Content to render inside the container |
| className | string | No | Additional CSS classes |
| maxHeight | string | No | Maximum height for scrollable content |

#### Usage
```tsx
<InputContainer maxHeight="400px">
  <RichTextEditor />
  <InputToolbar />
</InputContainer>
```

#### Features/Notes
- Provides consistent padding and border styling
- Supports scrollable content with max height
- Maintains focus states with ring highlights

---

### InputToolbar

A toolbar component with recording controls, send button, and mode selectors.

#### Import
```tsx
import { InputToolbar } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| onSend | () => void | No | Callback for send button click |
| canSend | boolean | No | Whether send button is enabled |
| isRecording | boolean | No | Current recording state |
| onStartRecording | () => void \| Promise<void> | No | Start recording callback |
| onStopRecording | () => void \| Promise<void> | No | Stop recording callback |
| audioLevel | number | No | Audio level (0-1) for visualization |
| selectedAgent | Agent | No | Currently selected agent |
| agents | Agent[] | No | Available agents |
| onAgentChange | (agent: Agent) => void | No | Agent selection callback |
| outputMode | OutputMode | No | Current output mode |
| outputOptions | OutputOption[] | No | Available output options |
| onOutputModeChange | (mode: OutputMode, option?: OutputOption) => void | No | Output mode change callback |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<InputToolbar
  onSend={handleSend}
  canSend={messageLength > 0}
  isRecording={isRecording}
  onStartRecording={startRecording}
  onStopRecording={stopRecording}
  audioLevel={currentAudioLevel}
/>
```

#### Features/Notes
- Combines multiple controls in a single toolbar
- Shows visual feedback for recording state
- Integrates agent and output mode selection
- Responsive layout that adapts to available space

---

### MicrophoneButton

A specialized button component for microphone recording with visual audio level feedback.

#### Import
```tsx
import { MicrophoneButton } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| isRecording | boolean | No | Current recording state |
| onStartRecording | () => void \| Promise<void> | No | Start recording callback |
| onStopRecording | () => void \| Promise<void> | No | Stop recording callback |
| audioLevel | number | No | Audio level (0-1) for visualization |
| showTooltip | boolean | No | Show tooltip on hover (default: true) |
| tooltipSide | 'top' \| 'right' \| 'bottom' \| 'left' | No | Tooltip position |
| disabled | boolean | No | Disable the button |
| loading | boolean | No | Show loading state |
| error | string \| null | No | Error message to display |
| variant | 'default' \| 'outline' \| 'secondary' \| 'ghost' \| 'destructive' | No | Button variant |
| size | 'default' \| 'sm' \| 'lg' \| 'xl' | No | Button size |

#### Usage
```tsx
<MicrophoneButton
  isRecording={isRecording}
  onStartRecording={async () => await startRecording()}
  onStopRecording={async () => await stopRecording()}
  audioLevel={audioLevel}
  showTooltip={true}
/>
```

#### Features/Notes
- Animated audio level visualization when recording
- Pulsing recording indicator
- Loading state with spinner
- Accessible with ARIA attributes
- Automatic icon switching based on state

---

### OutputSelector

A dropdown component for selecting output modes (text, voice, or avatar).

#### Import
```tsx
import { OutputSelector } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| value | OutputMode | No | Current output mode |
| onChange | (mode: OutputMode, option?: OutputOption) => void | No | Selection change callback |
| voiceOptions | OutputOption[] | No | Available voice options |
| avatarOptions | OutputOption[] | No | Available avatar options |
| disabled | boolean | No | Disable the selector |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<OutputSelector
  value={outputMode}
  onChange={(mode, option) => {
    setOutputMode(mode);
    if (option) setSelectedOption(option);
  }}
  voiceOptions={voices}
  avatarOptions={avatars}
/>
```

#### Features/Notes
- Three output modes: text-only, voice, and avatar
- Nested selection for voice and avatar options
- Visual indicators for each mode
- Keyboard navigation support

---

### AgentSelector

A dropdown component for selecting AI agents with avatars and descriptions.

#### Import
```tsx
import { AgentSelector } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| agents | Agent[] | Yes | Available agents |
| value | Agent | No | Currently selected agent |
| onChange | (agent: Agent) => void | No | Selection change callback |
| disabled | boolean | No | Disable the selector |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<AgentSelector
  agents={availableAgents}
  value={selectedAgent}
  onChange={(agent) => setSelectedAgent(agent)}
/>
```

#### Features/Notes
- Shows agent avatar, name, and description
- Supports emoji or React node avatars
- Indicates agent availability
- Accessible dropdown with keyboard navigation

---

### MarkdownEditor (Input)

A basic markdown editor component for the input area with automatic syntax conversion.

#### Import
```tsx
import { MarkdownEditor } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| value | string | No | Current editor content |
| onChange | (value: string) => void | No | Content change callback |
| placeholder | string | No | Placeholder text |
| onSubmit | (value: string) => void | No | Submit callback (Cmd/Ctrl+Enter) |
| disabled | boolean | No | Disable editing |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<MarkdownEditor
  value={content}
  onChange={setContent}
  placeholder="Type your message..."
  onSubmit={handleSubmit}
/>
```

#### Features/Notes
- Auto-converts markdown syntax as you type
- Keyboard shortcuts for formatting
- Plain text output despite rich display
- Supports Cmd/Ctrl+Enter to submit

---

### RichTextEditor

A rich text editor with formatting toolbar and markdown support.

#### Import
```tsx
import { RichTextEditor } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| value | string | No | Current editor content |
| onChange | (value: string) => void | No | Content change callback |
| onSubmit | () => void | No | Submit callback |
| placeholder | string | No | Placeholder text |
| disabled | boolean | No | Disable editing |
| showToolbar | boolean | No | Show formatting toolbar (default: true) |
| maxHeight | string | No | Maximum editor height |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<RichTextEditor
  value={content}
  onChange={setContent}
  onSubmit={handleSubmit}
  showToolbar={true}
  maxHeight="300px"
/>
```

#### Features/Notes
- Visual formatting toolbar with common actions
- Supports bold, italic, code, lists, and more
- Keyboard shortcuts for all formatting options
- Auto-resizing with max height constraint

---

## Editor Components

### MarkdownEditor (Enhanced)

An enhanced Tiptap-based markdown editor with live rendering, syntax highlighting, and image support.

#### Import
```tsx
import { MarkdownEditor } from '@agentc/realtime-ui/editor'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| value | string | No | Current editor content |
| onChange | (value: string) => void | No | Content change callback |
| placeholder | string | No | Placeholder text |
| onSubmit | (value: string) => void | No | Submit callback |
| disabled | boolean | No | Disable editing |
| enableSmartPaste | boolean | No | Enable smart paste processing (default: true) |
| maxImageSize | number | No | Maximum image size in bytes |
| onImageUpload | (file: File) => Promise<string> | No | Image upload handler |
| onImageUploadStart | () => void | No | Image upload start callback |
| onImageUploadComplete | (url: string) => void | No | Image upload complete callback |
| onImageUploadError | (error: Error) => void | No | Image upload error callback |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<MarkdownEditor
  value={content}
  onChange={setContent}
  enableSmartPaste={true}
  onImageUpload={async (file) => {
    const url = await uploadImage(file);
    return url;
  }}
/>
```

#### Features/Notes
- Live markdown syntax conversion
- Syntax highlighting for code blocks
- Image paste and drag-drop support
- Smart paste for formatted content
- Typography enhancements (smart quotes, dashes)
- Full keyboard shortcut support

#### Markdown Patterns
- `**text**` → **bold**
- `*text*` or `_text_` → *italic*
- `` `text` `` → `inline code`
- `~~text~~` → ~~strikethrough~~
- `# Heading` → Heading levels 1-3
- `- item` → Bullet lists
- `1. item` → Numbered lists
- `> quote` → Blockquotes
- `---` → Horizontal rules
- `` ```language `` → Code blocks with syntax highlighting

#### Keyboard Shortcuts
- `Cmd/Ctrl+B`: Bold
- `Cmd/Ctrl+I`: Italic
- `Cmd/Ctrl+E`: Inline code
- `Cmd/Ctrl+Alt+C`: Code block
- `Cmd/Ctrl+Shift+S`: Strikethrough
- `Cmd/Ctrl+K`: Add/edit link
- `Cmd/Ctrl+Z`: Undo
- `Cmd/Ctrl+Shift+Z`: Redo
- `Cmd/Ctrl+Enter`: Submit

---

### CodeHighlightExample

A demonstration component showing code syntax highlighting capabilities.

#### Import
```tsx
import { CodeHighlightExample } from '@agentc/realtime-ui/editor'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| language | string | No | Programming language for highlighting (default: 'typescript') |
| code | string | No | Code to display |
| editable | boolean | No | Allow editing the code (default: false) |

#### Usage
```tsx
<CodeHighlightExample
  language="javascript"
  code={sampleCode}
  editable={false}
/>
```

#### Features/Notes
- Supports multiple programming languages
- Syntax highlighting with customizable themes
- Optional editing capabilities
- Copy code button integration

---

### SmartPasteExample

A demonstration component showing smart paste processing capabilities.

#### Import
```tsx
import { SmartPasteExample } from '@agentc/realtime-ui/editor'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| onPaste | (processedContent: string) => void | No | Callback with processed paste content |
| showPreview | boolean | No | Show preview of processed content (default: true) |

#### Usage
```tsx
<SmartPasteExample
  onPaste={(content) => console.log('Processed:', content)}
  showPreview={true}
/>
```

#### Features/Notes
- Processes formatted content from various sources
- Converts to clean markdown
- Handles tables, lists, and code blocks
- Preserves formatting intent

---

## UI Components (CenSuite)

### Alert

A component for displaying important messages with different severity levels.

#### Import
```tsx
import { Alert, AlertDescription, AlertTitle } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| variant | 'default' \| 'destructive' | No | Alert style variant |
| className | string | No | Additional CSS classes |
| children | React.ReactNode | Yes | Alert content |

#### Usage
```tsx
<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Something went wrong. Please try again.
  </AlertDescription>
</Alert>
```

#### Features/Notes
- Semantic color coding for different alert types
- Optional title and description structure
- Icon integration support
- Accessible with proper ARIA roles

---

### Avatar

A component for displaying user or agent avatars with fallback support.

#### Import
```tsx
import { Avatar, AvatarImage, AvatarFallback } from '@agentc/realtime-ui'
```

#### Props

**Avatar**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| className | string | No | Additional CSS classes |

**AvatarImage**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| src | string | Yes | Image source URL |
| alt | string | Yes | Alternative text for accessibility |

**AvatarFallback**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| children | React.ReactNode | Yes | Fallback content (typically initials) |

#### Usage
```tsx
<Avatar>
  <AvatarImage src="/avatar.png" alt="User" />
  <AvatarFallback>UN</AvatarFallback>
</Avatar>
```

#### Features/Notes
- Automatic fallback when image fails to load
- Consistent sizing and border radius
- Supports custom fallback content
- Lazy loading support

---

### Badge

A component for displaying labels, counts, or status indicators.

#### Import
```tsx
import { Badge } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| variant | 'default' \| 'secondary' \| 'destructive' \| 'outline' | No | Badge style variant |
| className | string | No | Additional CSS classes |
| children | React.ReactNode | Yes | Badge content |

#### Usage
```tsx
<Badge variant="secondary">New</Badge>
<Badge variant="destructive">3</Badge>
```

#### Features/Notes
- Multiple visual variants for different contexts
- Inline display with proper spacing
- Supports icons and text
- Accessible color contrast

---

### Button

A versatile button component with multiple variants and sizes.

#### Import
```tsx
import { Button } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| variant | 'default' \| 'destructive' \| 'outline' \| 'secondary' \| 'ghost' \| 'link' | No | Button style variant |
| size | 'default' \| 'sm' \| 'lg' \| 'icon' | No | Button size |
| asChild | boolean | No | Render as child element |
| disabled | boolean | No | Disable the button |
| className | string | No | Additional CSS classes |
| onClick | (event: React.MouseEvent) => void | No | Click handler |
| children | React.ReactNode | Yes | Button content |

#### Usage
```tsx
<Button variant="primary" size="lg" onClick={handleClick}>
  Click Me
</Button>

<Button variant="outline" size="icon">
  <Settings className="h-4 w-4" />
</Button>
```

#### Features/Notes
- Six visual variants for different actions
- Four size options including icon-only
- Focus ring for keyboard navigation
- Loading and disabled states
- Icon support with automatic sizing

---

### DropdownMenu

A component for creating accessible dropdown menus with keyboard navigation.

#### Import
```tsx
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuGroup
} from '@agentc/realtime-ui'
```

#### Props

**DropdownMenuTrigger**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| asChild | boolean | No | Render as child element |
| children | React.ReactNode | Yes | Trigger element |

**DropdownMenuContent**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| align | 'start' \| 'center' \| 'end' | No | Content alignment |
| side | 'top' \| 'right' \| 'bottom' \| 'left' | No | Preferred side |
| sideOffset | number | No | Offset from trigger |

**DropdownMenuItem**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| onSelect | () => void | No | Selection callback |
| disabled | boolean | No | Disable the item |

#### Usage
```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Options</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>Actions</DropdownMenuLabel>
    <DropdownMenuItem onSelect={() => console.log('Edit')}>
      Edit
    </DropdownMenuItem>
    <DropdownMenuItem onSelect={() => console.log('Delete')}>
      Delete
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem disabled>
      Disabled Action
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### Features/Notes
- Full keyboard navigation (arrow keys, escape, enter)
- Accessible with ARIA attributes
- Portal rendering to avoid z-index issues
- Submenus and groups support
- Customizable positioning

---

### Separator

A component for visually separating content sections.

#### Import
```tsx
import { Separator } from '@agentc/realtime-ui'
```

#### Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| orientation | 'horizontal' \| 'vertical' | No | Separator direction (default: 'horizontal') |
| decorative | boolean | No | Whether separator is decorative (default: true) |
| className | string | No | Additional CSS classes |

#### Usage
```tsx
<div>
  <h2>Section 1</h2>
  <Separator />
  <h2>Section 2</h2>
</div>

<div className="flex items-center gap-4">
  <span>Item 1</span>
  <Separator orientation="vertical" className="h-4" />
  <span>Item 2</span>
</div>
```

#### Features/Notes
- Horizontal and vertical orientations
- Semantic HTML with proper ARIA roles
- Customizable color through CSS variables
- Responsive to parent container

---

### Tooltip

A component for displaying helpful information on hover or focus.

#### Import
```tsx
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider
} from '@agentc/realtime-ui'
```

#### Props

**TooltipProvider**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| delayDuration | number | No | Delay before showing tooltip (ms) |
| skipDelayDuration | number | No | Delay when moving between tooltips |

**TooltipContent**
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| side | 'top' \| 'right' \| 'bottom' \| 'left' | No | Preferred side |
| sideOffset | number | No | Offset from trigger |
| align | 'start' \| 'center' \| 'end' | No | Content alignment |

#### Usage
```tsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline" size="icon">
        <HelpCircle className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Click for more information</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

#### Features/Notes
- Keyboard accessible (shows on focus)
- Smart positioning to stay in viewport
- Customizable delay timing
- Supports rich content
- Portal rendering for proper z-indexing

---

## Type Definitions

### Core Types

```typescript
// Agent type for agent selection
interface Agent {
  id: string
  name: string
  description?: string
  avatar?: string | React.ReactNode
  available?: boolean
}

// Output mode types
type OutputMode = 'text' | 'voice' | 'avatar'

// Output option for voice/avatar selection
interface OutputOption {
  id: string
  name: string
  type: 'voice' | 'avatar'
  available?: boolean
  metadata?: {
    voiceId?: string
    avatarId?: string
    previewUrl?: string
  }
}
```

## Best Practices

### Accessibility
- All interactive components include proper ARIA attributes
- Keyboard navigation is fully supported
- Focus states are clearly visible
- Screen reader support is built-in

### Performance
- Components use React.memo where beneficial
- Event handlers are properly memoized
- Animations use CSS transforms for better performance
- Large lists should be virtualized when needed

### Styling
- All components follow the CenSuite design system
- Use semantic color tokens (never hardcode colors)
- Maintain consistent spacing with the 4px base unit
- Components are fully responsive

### Integration
- Components integrate seamlessly with `@agentc/realtime-react` hooks
- Error boundaries should be implemented at the app level
- Loading states are handled gracefully
- Components degrade gracefully when SDK context is missing

## Examples

### Complete Input Setup
```tsx
import { InputArea } from '@agentc/realtime-ui'
import { AgentCProvider } from '@agentc/realtime-react'

function ChatInterface() {
  return (
    <AgentCProvider config={realtimeConfig}>
      <InputArea
        placeholder="How can I help you today?"
        maxHeight="300px"
        agents={customAgents}
        onAgentChange={(agent) => {
          console.log('Switched to agent:', agent.name)
        }}
        onOutputModeChange={(mode, option) => {
          console.log('Output mode:', mode, option?.name)
        }}
      />
    </AgentCProvider>
  )
}
```

### Custom Toolbar
```tsx
import { InputToolbar, MicrophoneButton } from '@agentc/realtime-ui'

function CustomToolbar() {
  const [isRecording, setIsRecording] = useState(false)
  
  return (
    <InputToolbar
      onSend={() => sendMessage()}
      canSend={true}
      isRecording={isRecording}
      onStartRecording={() => setIsRecording(true)}
      onStopRecording={() => setIsRecording(false)}
      outputMode="voice"
    />
  )
}
```

## Version History

- **1.0.0** - Initial release with core input and UI components
- **1.1.0** - Added enhanced MarkdownEditor with image support
- **1.2.0** - Added SmartPaste functionality

## Support

For issues, questions, or contributions, please refer to the main project documentation or open an issue in the repository.