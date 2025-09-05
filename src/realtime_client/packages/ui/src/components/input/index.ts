/**
 * Input Components for Agent C Realtime UI
 * 
 * The InputArea is the main component that integrates all input functionality.
 * Individual components are also exported for advanced customization.
 */

// Main integrated component
export { InputArea } from './InputArea'
export type { InputAreaProps } from './InputArea'

// Individual components for advanced usage
export { InputContainer } from './InputContainer'
export type { InputContainerProps } from './InputContainer'

export { RichTextEditor } from './RichTextEditor'
export type { RichTextEditorProps } from './RichTextEditor'

export { MarkdownEditor } from './MarkdownEditor'
export type { MarkdownEditorProps } from './MarkdownEditor'

export { InputToolbar } from './InputToolbar'
export type { InputToolbarProps } from './InputToolbar'

export { MicrophoneButton } from './MicrophoneButton'
export type { MicrophoneButtonProps } from './MicrophoneButton'

export { AgentSelector } from './AgentSelector'
export type { AgentSelectorProps } from './AgentSelector'

export { OutputSelector } from './OutputSelector'
export type { OutputSelectorProps } from './OutputSelector'

// Types
export type { 
  Agent,
  AgentTool, 
  OutputMode, 
  OutputOption 
} from './types'