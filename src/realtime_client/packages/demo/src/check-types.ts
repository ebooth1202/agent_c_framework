// Type check file to verify components compile
import { ChatLayout } from './components/layout/ChatLayout'
import { ChatSidebar } from './components/sidebar/ChatSidebar'
import { ChatHeader } from './components/layout/ChatHeader'
import { MainContentArea } from './components/content/MainContentArea'
import { ChatMessagesView } from './components/content/ChatMessagesView'
import { AvatarDisplayView } from './components/content/AvatarDisplayView'
import { VoiceVisualizerView } from './components/content/VoiceVisualizerView'
import { SessionNameDropdown } from './components/layout/SessionNameDropdown'
import { SidebarTopMenu } from './components/sidebar/SidebarTopMenu'
import { ChatSessionList } from './components/sidebar/ChatSessionList'
import { UserDisplay } from './components/sidebar/UserDisplay'

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