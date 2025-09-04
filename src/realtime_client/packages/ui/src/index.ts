// Utility exports
export { cn } from './lib/utils';

// Editor component exports (legacy - use input/MarkdownEditor instead)
export { MarkdownEditor as LegacyMarkdownEditor } from './components/editor';
export type { MarkdownEditorProps as LegacyMarkdownEditorProps } from './components/editor';

// Input component exports
export { 
  // Main integrated component
  InputArea,
  // Individual components
  InputContainer, 
  RichTextEditor,
  MarkdownEditor,
  InputToolbar,
  MicrophoneButton,
  // Temporarily rename the old ones to avoid conflicts
  AgentSelector as LegacyAgentSelector,
  OutputSelector as LegacyOutputSelector
} from './components/input';

export type { 
  InputAreaProps,
  InputContainerProps, 
  RichTextEditorProps,
  MarkdownEditorProps,
  InputToolbarProps,
  MicrophoneButtonProps,
  // Rename old types too
  AgentSelectorProps as LegacyAgentSelectorProps,
  OutputSelectorProps as LegacyOutputSelectorProps,
  Agent,
  OutputMode,
  OutputOption
} from './components/input';

// Control component exports - Include the new selectors here
export {
  ConnectionButton,
  AudioControls,
  AgentSelector,
  OutputSelector
} from './components/controls';

export type {
  ConnectionButtonProps,
  AudioControlsProps,
  AgentSelectorProps,
  OutputSelectorProps
} from './components/controls';