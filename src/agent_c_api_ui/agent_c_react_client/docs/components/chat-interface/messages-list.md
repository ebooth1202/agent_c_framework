# MessagesList Component

## Purpose

The `MessagesList` component displays a scrollable list of chat messages in the chat interface. It handles rendering different message types, automatic scrolling to new messages, and virtual rendering for performance optimization.

## Import

```jsx
import { MessagesList } from '../components/chat_interface/MessagesList';
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| messages | array | [] | Array of message objects to display |
| isStreaming | boolean | false | Whether a message is currently streaming in |
| showStatus | boolean | true | Whether to show the typing status indicator |
| showOptions | boolean | true | Whether to show message options (copy, etc.) |

## Usage Example

```jsx
<MessagesList 
  messages={sessionMessages} 
  isStreaming={isStreaming} 
  showStatus={true}
  showOptions={true}
/>
```

## Internal Components

The `MessagesList` component uses the following internal components:

- `MessageItem`: Renders individual messages based on their type
- `AnimatedStatusIndicator`: Shows typing/thinking status

## Message Types

The component handles the following message types:

1. `user`: Messages from the user
2. `assistant`: Responses from the AI assistant
3. `system`: System messages and notifications
4. `thought`: AI thinking/reasoning processes
5. `tool_call`: Tool usage by the AI

## Auto-Scrolling Behavior

The component automatically scrolls to new messages when:

- The user scrolls to the bottom before a new message arrives
- A new message is added by the user
- The first chunk of a streaming message arrives

Scrolling is managed using a combination of refs and the `useEffect` hook to provide a natural scrolling experience.

## Virtualization

For performance with large message histories, the component uses virtual rendering to only render messages that are visible or close to the viewport.

## CSS Variables

The component uses the following CSS variables for styling:

| Variable | Purpose |
|----------|----------|
| `--message-spacing` | Space between messages |
| `--message-border-radius` | Border radius for message bubbles |
| `--background` | Background color for the messages container |

## Example Implementation

```jsx
import React, { useRef, useEffect } from 'react';
import MessageItem from './MessageItem';
import AnimatedStatusIndicator from './AnimatedStatusIndicator';

const MessagesList = ({ messages, isStreaming, showStatus = true }) => {
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  
  // Auto-scroll logic
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  return (
    <div className="messages-list" ref={messagesContainerRef}>
      {messages.map((message, index) => (
        <MessageItem 
          key={message.id || index}
          message={message}
          isLastMessage={index === messages.length - 1}
        />
      ))}
      
      {showStatus && isStreaming && (
        <div className="status-indicator-container">
          <AnimatedStatusIndicator type="typing" />
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessagesList;
```

## Styling

The `MessagesList` component is styled using CSS in `src/styles/components/messages-list.css`. Key styling includes:

```css
.messages-list {
  display: flex;
  flex-direction: column;
  gap: var(--message-spacing);
  padding: var(--space-4);
  overflow-y: auto;
  height: 100%;
  background-color: hsl(var(--background));
}

.status-indicator-container {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-4);
  margin-top: var(--space-2);
}
```

## Accessibility Considerations

- Uses semantic HTML to ensure screen reader compatibility
- Maintains proper focus management during scrolling
- Includes aria labels for dynamic content

## Performance Optimization

- Uses `React.memo` to prevent unnecessary re-renders
- Implements virtualization for large message lists
- Uses refs instead of state for scroll position tracking

## Related Components

- [ChatInterface](./chat-interface.md)
- [MessageItem](./message-item.md)
- [ToolCallDisplay](./tool-call-display.md)