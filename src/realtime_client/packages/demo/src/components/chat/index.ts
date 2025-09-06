/**
 * Chat Components for Agent C Realtime SDK Demo
 * 
 * This module provides demo-specific chat components.
 * Core chat components have been moved to @agentc/realtime-ui package.
 */

// Demo-specific components (not moved to UI package)
export { ChatInterface, CompactChatInterface } from './chat-interface'
export type { ChatInterfaceProps } from './chat-interface'

export { ViewManager } from './view-manager'
export type { ViewManagerProps } from './view-manager'

export { ChatLayout } from './chat-layout'
export type { ChatLayoutProps } from './chat-layout'

export { SidePanel } from './side-panel'
export type { SidePanelProps } from './side-panel'

// Re-export from UI package for backwards compatibility
export { 
  MessageList,
  Message,
  ScrollAnchor,
  TypingIndicator,
  ConnectionStatus,
  typingIndicatorStyles
} from '@agentc/realtime-ui'

export type {
  MessageListProps,
  MessageProps,
  MessageData,
  ScrollAnchorProps,
  TypingIndicatorProps,
  ConnectionStatusProps
} from '@agentc/realtime-ui'