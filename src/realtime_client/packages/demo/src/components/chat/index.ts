/**
 * Chat Components for Agent C Realtime SDK
 * 
 * This module provides a complete chat interface with:
 * - Message rendering with markdown support
 * - Auto-scrolling behavior
 * - Typing indicators
 * - Code syntax highlighting
 * - Responsive design
 */

export { MessageList } from './message-list'
export type { MessageListProps } from './message-list'

export { Message } from './message'
export type { MessageProps, MessageData } from './message'

export { ScrollAnchor } from './scroll-anchor'
export type { ScrollAnchorProps } from './scroll-anchor'

export { TypingIndicator, typingIndicatorStyles } from './typing-indicator'
export type { TypingIndicatorProps } from './typing-indicator'

export { ChatInterface, CompactChatInterface } from './chat-interface'
export type { ChatInterfaceProps } from './chat-interface'

export { ViewManager } from './view-manager'
export type { ViewManagerProps } from './view-manager'

export { ChatLayout } from './chat-layout'
export type { ChatLayoutProps } from './chat-layout'

export { SidePanel } from './side-panel'
export type { SidePanelProps } from './side-panel'

export { ConnectionStatus } from './connection-status'
export type { ConnectionStatusProps } from './connection-status'