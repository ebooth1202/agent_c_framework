/**
 * Chat Components for Agent C Realtime SDK Demo
 * 
 * This module exports demo-specific chat components.
 * Core reusable chat components are imported from @agentc/realtime-ui package.
 */

// Demo-specific components only
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