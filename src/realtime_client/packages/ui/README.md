# @agentc/realtime-ui

UI components for the Agent C Realtime SDK, built with shadcn/ui patterns and CenSuite compatibility.

## Installation

```bash
npm install @agentc/realtime-ui @agentc/realtime-react
```

## Setup

This package requires Tailwind CSS to be configured in your application with the appropriate CSS variables for theming.

### 1. Add CSS Variables

Add the following CSS variables to your global CSS file:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}
```

### 2. Configure Tailwind

Ensure your Tailwind config includes the UI package in its content paths:

```js
module.exports = {
  content: [
    // ... your other content paths
    "./node_modules/@agentc/realtime-ui/**/*.{js,ts,jsx,tsx}",
  ],
  // ... rest of your config
}
```

## Usage

```tsx
import { ConnectionButton, MicrophoneButton, OutputSelector } from '@agentc/realtime-ui';
import { AgentCProvider } from '@agentc/realtime-react';

function App() {
  return (
    <AgentCProvider>
      <ConnectionButton />
      <MicrophoneButton />
      <OutputSelector />
    </AgentCProvider>
  );
}
```

## Components

### Core Controls

#### OutputSelector

A hierarchical dropdown menu component that allows users to select the output mode for agent responses. Supports three modes: Text Only (no audio), Voice (synthesized speech), and Avatar (HeyGen streaming avatar - implementation pending).

```tsx
import { OutputSelector } from '@agentc/realtime-ui';

// Basic usage
<OutputSelector />

// With custom props
<OutputSelector
  className="w-[250px]"
  showIcon={true}
  showErrorAlerts={true}
  ariaLabel="Select output mode for agent responses"
  disabled={false}
/>

// Forward ref for imperative access
const outputRef = useRef<HTMLButtonElement>(null);
<OutputSelector ref={outputRef} />
```

**Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `undefined` | Additional CSS classes to apply to the root element |
| `disabled` | `boolean` | `false` | Whether the selector is disabled |
| `showIcon` | `boolean` | `true` | Whether to show the mode icon in the button |
| `ariaLabel` | `string` | Auto-generated | Custom ARIA label for the selector button |
| `showErrorAlerts` | `boolean` | `true` | Whether to show error alerts inline below the selector |

**Features:**

✅ **Hierarchical Menu Structure**
- Text Only option at root level for quick access
- Voice submenu with flat list of all available voices
- Avatar submenu for avatar selection (UI ready, integration pending)

✅ **Smart State Management**
- Automatically syncs with SDK voice model
- Shows current selection with check marks
- Loading states during voice changes
- Disabled state when disconnected

✅ **Full Accessibility Support**
- WCAG 2.1 AA compliant
- Complete keyboard navigation
- Screen reader announcements for all state changes
- Proper ARIA labels and live regions
- Focus management and visual indicators

✅ **Error Handling**
- User-friendly error messages
- Automatic error dismissal after 5 seconds
- Error recovery on successful operations
- Console logging for debugging

✅ **Responsive Design**
- Mobile-optimized menu widths
- Touch-friendly tap targets
- Scroll support for long voice lists
- Smooth animations and transitions

**Output Modes:**

1. **Text Only Mode**
   - Sets voice_id to "none" in SDK
   - Agent responds with text messages only
   - No audio output generated
   - Icon: Type (text icon)

2. **Voice Mode**
   - Select from available TTS voices
   - Display format: "vendor - voice_id"
   - Shows description as secondary text
   - Icon: Mic (microphone icon)
   - Supports OpenAI, ElevenLabs, and other vendors

3. **Avatar Mode** (Coming Soon)
   - HeyGen streaming avatar integration
   - Display format: "avatar_id - pose_name"
   - Filters to show only active, public avatars
   - Icon: User (avatar icon)
   - Currently logs selection to console

**Events and Integration:**

The component automatically integrates with the SDK through React hooks:

```tsx
// The component listens for these SDK events:
- 'agent_voice_changed': Updates selection when voice changes
- 'agent_data_updated': Refreshes available voices/avatars
- 'connection_error': Disables selector on connection loss
- 'connected': Re-enables selector on reconnection

// The component calls these SDK methods:
- client.setAgentVoice(voice_id): Changes the agent's voice
- client.getVoiceModel(): Gets current voice selection
- client.getAgentData(): Gets available voices and avatars
```

**Usage Examples:**

```tsx
// Basic implementation in a chat interface
function ChatInterface() {
  return (
    <div className="flex items-center gap-4">
      <OutputSelector />
      <ConnectionButton />
      <MicrophoneButton />
    </div>
  );
}

// With error handling and custom styling
function CustomOutputControl() {
  return (
    <OutputSelector
      className="min-w-[200px] max-w-[300px]"
      showErrorAlerts={true}
      showIcon={true}
      ariaLabel="Choose how the AI assistant responds"
    />
  );
}

// Programmatic control with ref
function ProgrammaticControl() {
  const selectorRef = useRef<HTMLButtonElement>(null);
  
  const focusSelector = () => {
    selectorRef.current?.focus();
  };
  
  return (
    <>
      <OutputSelector ref={selectorRef} />
      <button onClick={focusSelector}>Focus Output Selector</button>
    </>
  );
}
```

**Testing:**

The component includes comprehensive test coverage:

```bash
# Run unit tests
pnpm test packages/ui/test/controls/OutputSelector.test.tsx

# Run integration tests
pnpm test packages/demo/src/components/__tests__/OutputSelector.integration.test.tsx
```

Test coverage includes:
- Display of all menu options
- Event firing for each selection type
- State highlighting and synchronization
- Disabled states and loading states
- Error handling scenarios
- Accessibility compliance
- SDK integration and event propagation

**Known Limitations:**
- Avatar selection is currently deferred (UI complete, awaiting SDK integration)
- HeyGen avatar integration will be implemented in a future release
- Voice changes during active conversation apply after current turn ends
- Maximum of 50 voices can be displayed (scrollable list)

#### ConnectionButton

Connect/disconnect button with connection status indicator.

```tsx
<ConnectionButton showStatus={true} />
```

#### MicrophoneButton

Audio input toggle with visual feedback.

```tsx
<MicrophoneButton disabled={false} />
```

#### ChatMessage

Message display component with markdown support.

```tsx
<ChatMessage
  message={{
    role: 'assistant',
    content: 'Hello! How can I help you today?',
    timestamp: new Date().toISOString()
  }}
/>
```

### Additional Components

More components are being added incrementally:
- `AgentSelector` - Switch between available agents
- `SessionList` - Display and manage chat sessions
- `AudioVisualizer` - Real-time audio level display
- `TurnIndicator` - Show current conversation turn state

## Development

This package follows CenSuite and shadcn/ui patterns for consistency with Centric's design system.