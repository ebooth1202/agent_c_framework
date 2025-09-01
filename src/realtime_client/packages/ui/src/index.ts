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
  AgentSelector,
  OutputSelector
} from './components/input';

export type { 
  InputAreaProps,
  InputContainerProps, 
  RichTextEditorProps,
  MarkdownEditorProps,
  InputToolbarProps,
  MicrophoneButtonProps,
  AgentSelectorProps,
  OutputSelectorProps,
  Agent,
  OutputMode,
  OutputOption
} from './components/input';