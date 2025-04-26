# ChatInterface Component

## Purpose

The `ChatInterface` component is the main container for the chat functionality in the Agent C React UI. It orchestrates all chat-related features, including message display, input handling, file uploads, and tool interactions.

## Import

```jsx
import { ChatInterface } from '../components/chat_interface/ChatInterface';
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| sessionId | string | null | Identifier for the current chat session |
| initialMessages | array | [] | Pre-loaded messages to display |
| onSendMessage | function | required | Handler for sending new messages |
| onSessionEnd | function | () => {} | Handler for ending the current session |
| showFilePanel | boolean | true | Whether to show the file upload panel |
| showToolSelector | boolean | true | Whether to show the tool selector |
| showPersonaSelector | boolean | true | Whether to show the persona selector |
| showStatusBar | boolean | true | Whether to show the status bar |

## Usage Example

```jsx
import { useState } from 'react';
import { ChatInterface } from '../components/chat_interface/ChatInterface';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  
  const handleSendMessage = async (message, files, selectedTools) => {
    // API call logic
    const response = await api.sendMessage(message, files, selectedTools);
    setMessages(prev => [...prev, response]);
  };
  
  return (
    <div className="chat-page">
      <ChatInterface 
        sessionId="session-123"
        initialMessages={messages}
        onSendMessage={handleSendMessage}
        onSessionEnd={() => console.log('Session ended')}
      />
    </div>
  );
};
```

## Component Structure

The ChatInterface is composed of several key sections:

```jsx
<div className="chat-interface">
  <div className="chat-interface-header">
    {/* Persona selector, configuration controls */}
  </div>
  
  <div className="chat-interface-body">
    <div className="chat-messages-container">
      <MessagesList />
    </div>
    
    {showFilePanel && (
      <FilesPanel />
    )}
  </div>
  
  <div className="chat-interface-footer">
    {showToolSelector && (
      <ToolSelector />
    )}
    
    <ChatInputArea />
    
    {showStatusBar && (
      <StatusBar />
    )}
  </div>
</div>
```

## Key Features

### Message Management

The component handles various message types:

- User messages
- Assistant responses
- System messages
- Tool call messages
- Streaming responses
- File attachments

### Streaming Support

The ChatInterface supports real-time message streaming:

- Handles partial message chunks
- Shows typing indicators during streaming
- Supports interruption of streaming responses

### File Management

Integrated file handling capabilities:

- File uploads through drag-and-drop or file picker
- Visual file previews
- File reference in messages
- Download support for files shared by the assistant

### Tool Integration

Support for AI tool usage:

- Tool selection interface
- Visualization of tool calls
- Tool call results display
- Error handling for failed tool calls

## State Management

The ChatInterface manages several key states:

- **Messages**: Array of all messages in the conversation
- **Streaming**: Boolean indicating if a response is currently streaming
- **Loading**: Boolean indicating background processing
- **Files**: Array of uploaded files
- **Selected Tools**: Array of enabled tools
- **Input Value**: Current text input value

## Key Methods

| Method | Purpose |
|--------|----------|
| `handleSendMessage` | Processes and sends user messages |
| `handleFileUpload` | Processes file uploads |
| `handleToolSelection` | Manages tool selection state |
| `handleStreamingResponse` | Processes streaming message chunks |
| `handleStopStreaming` | Cancels ongoing streaming responses |

## Styling

The ChatInterface component uses CSS from `src/styles/components/chat-interface.css` with several key CSS variables:

```css
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: var(--chat-max-width);
  margin: 0 auto;
  background-color: hsl(var(--background));
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
  overflow: hidden;
}

.chat-interface-body {
  display: flex;
  flex: 1;
  min-height: 0;
  position: relative;
}

.chat-messages-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Additional styles for header, footer, etc. */
```

## Responsive Behavior

The component adjusts its layout for different screen sizes:

- On larger screens, the file panel appears as a sidebar
- On smaller screens, the file panel collapses and becomes toggleable
- Input area and controls adapt to available width
- Tool selector becomes scrollable on narrow viewports

## Accessibility Considerations

- Proper focus management during interactions
- ARIA labels for interactive elements
- Keyboard navigation support
- Screen reader announcements for status changes

## Integration with Backend

The ChatInterface communicates with the backend through several methods:

- REST API calls for message sending/receiving
- WebSocket or SSE for streaming responses
- FormData for file uploads
- Error handling for API failures

## Implementation Details

```jsx
import React, { useState, useEffect, useRef } from 'react';
import MessagesList from './MessagesList';
import ChatInputArea from './ChatInputArea';
import FilesPanel from './FilesPanel';
import ToolSelector from './ToolSelector';
import StatusBar from './StatusBar';
import PersonaSelector from './PersonaSelector';

const ChatInterface = ({
  sessionId,
  initialMessages = [],
  onSendMessage,
  onSessionEnd = () => {},
  showFilePanel = true,
  showToolSelector = true,
  showPersonaSelector = true,
  showStatusBar = true
}) => {
  const [messages, setMessages] = useState(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedTools, setSelectedTools] = useState([]);
  const [inputValue, setInputValue] = useState('');
  
  // Message sending handler
  const handleSendMessage = async (text) => {
    if (!text.trim() && files.length === 0) return;
    
    // Add user message to the list
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      files: files.length > 0 ? [...files] : undefined
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setFiles([]);
    setIsLoading(true);
    
    try {
      // Call the provided message handler
      await onSendMessage(text, files, selectedTools);
    } catch (error) {
      // Handle error
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: `Error: ${error.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // File upload handler
  const handleFileUpload = (newFiles) => {
    setFiles(prev => [...prev, ...newFiles]);
  };
  
  // Tool selection handler
  const handleToolSelection = (tools) => {
    setSelectedTools(tools);
  };
  
  return (
    <div className="chat-interface">
      {showPersonaSelector && (
        <div className="chat-interface-header">
          <PersonaSelector />
        </div>
      )}
      
      <div className="chat-interface-body">
        <div className="chat-messages-container">
          <MessagesList 
            messages={messages} 
            isStreaming={isStreaming} 
          />
        </div>
        
        {showFilePanel && (
          <FilesPanel 
            files={files} 
            onFileUpload={handleFileUpload} 
            onFileRemove={(fileId) => {
              setFiles(prev => prev.filter(f => f.id !== fileId));
            }} 
          />
        )}
      </div>
      
      <div className="chat-interface-footer">
        {showToolSelector && (
          <ToolSelector 
            selectedTools={selectedTools}
            onToolSelection={handleToolSelection}
          />
        )}
        
        <ChatInputArea 
          value={inputValue}
          onChange={setInputValue}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          isStreaming={isStreaming}
          onStopStreaming={() => {
            // Handle stop streaming
          }}
        />
        
        {showStatusBar && (
          <StatusBar 
            isConnected={true}
            messageCount={messages.length}
            sessionId={sessionId}
          />
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
```

## Related Components

- [MessagesList](./messages-list.md)
- [ChatInputArea](./chat-input-area.md)
- [FilesPanel](./files-panel.md)
- [ToolSelector](./tool-selector.md)
- [PersonaSelector](./persona-selector.md)