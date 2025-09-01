# Chat Interface Components - Phase 2

This directory contains the layout structure components for the Agent C Realtime chat interface.

## Components

### ChatLayout (`chat-layout.tsx`)
The main structural component that orchestrates the entire chat interface.

**Features:**
- Header with ConnectionStatus display
- Responsive layout with collapsible sidebar
- Main content area with ViewManager
- Footer with InputArea for user input
- Mobile-responsive design

**Usage:**
```tsx
import { ChatLayout } from '@/components/chat/chat-layout';

<ChatLayout defaultOutputMode="text" />
```

**Variants:**
- `ChatLayout` - Full-featured layout with sidebar
- `CompactChatLayout` - Minimal layout for embedding
- `DebugChatLayout` - Development layout with debug panel

### SidePanel (`side-panel.tsx`)
Collapsible sidebar for session management.

**Features:**
- Session list with search/filter
- New session button
- Mobile overlay mode (sheet) 
- Desktop sidebar mode
- Responsive toggle behavior

**Props:**
- `isOpen` - Control panel visibility
- `onToggle` - Toggle callback
- `isMobile` - Force mobile/desktop mode
- `sessions` - Array of session objects
- `activeSessionId` - Currently active session
- `onNewSession` - New session callback
- `onSelectSession` - Session selection callback
- `onDeleteSession` - Session deletion callback

### ViewManager (`view-manager.tsx`)
Manages different output modes and renders appropriate views.

**Features:**
- Three view modes: text (chat), voice, avatar
- Smooth transitions between views
- Placeholder content for future implementation

**Props:**
- `outputMode` - Current mode ('text' | 'voice' | 'avatar')
- `className` - Additional CSS classes

### InputArea (`input-area.tsx`)
User input component with text and voice controls.

**Features:**
- Text message input with auto-resize
- Voice recording controls
- Output mode selector
- Audio level visualization
- Keyboard shortcuts (Enter to send)

**Props:**
- `outputMode` - Current output mode
- `onOutputModeChange` - Mode change callback

## Integration Example

```tsx
'use client';

import { ChatLayout } from '@/components/chat/chat-layout';
import { AgentCProvider } from '@agentc/realtime-react';

export default function ChatPage() {
  return (
    <AgentCProvider 
      apiUrl="wss://api.agentc.ai/v1/realtime"
      authToken="your-token"
      autoConnect={false}
      debug={true}
    >
      <div className="h-screen w-full">
        <ChatLayout defaultOutputMode="text" />
      </div>
    </AgentCProvider>
  );
}
```

## Design System Compliance

All components follow the CenSuite design system:
- **Colors**: Semantic color tokens only (primary, secondary, muted, destructive)
- **Spacing**: 4px base unit scale (p-2, p-4, p-6, p-8)
- **Typography**: Consistent hierarchy with proper font weights
- **Accessibility**: ARIA labels, keyboard navigation, focus management

## Mobile Responsiveness

- **SidePanel**: Transforms to overlay sheet on mobile
- **ChatLayout**: Adapts layout for mobile screens
- **InputArea**: Responsive button layout
- **ViewManager**: Mobile-optimized views

## Phase 2 Status

✅ **Completed:**
- ChatLayout with responsive design
- SidePanel with session management UI
- ViewManager with view switching
- InputArea with text/voice controls
- Mobile responsiveness
- Accessibility features

🔄 **Placeholders for Future Phases:**
- Actual chat messages (Phase 3)
- Voice visualizer (Phase 5)
- Avatar video stream (Phase 6)
- Real session management (Phase 7)

## Next Steps

Phase 3 will implement:
- Real-time message display
- Message history
- Typing indicators
- Message status indicators