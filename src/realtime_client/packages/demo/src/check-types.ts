// Type check file to verify components compile
import { ChatLayout } from './components/layout/ChatLayout'
import { ChatHeader } from './components/layout/ChatHeader'
import { MainContentArea } from './components/content/MainContentArea'
import { ChatMessagesView } from './components/content/ChatMessagesView'
import { AvatarDisplayView } from './components/content/AvatarDisplayView'
import { VoiceVisualizerView } from '@agentc/realtime-ui'

// These components are now imported from the UI package
import {
  ChatSidebar,
  SessionNameDropdown,
  SidebarTopMenu,
  ChatSessionList,
  UserDisplay
} from '@agentc/realtime-ui'

// This file helps verify all components can be imported and typed correctly
export {
  ChatLayout,
  ChatSidebar,
  ChatHeader,
  MainContentArea,
  ChatMessagesView,
  AvatarDisplayView,
  VoiceVisualizerView,
  SessionNameDropdown,
  SidebarTopMenu,
  ChatSessionList,
  UserDisplay
}