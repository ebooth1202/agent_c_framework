# Chat Messages and Event Stream Design Document

## Executive Summary

This document outlines the comprehensive architecture for implementing chat message display and real-time event stream processing in the Agent C Realtime SDK. The implementation spans both core SDK components for event processing and UI components for rich message display, supporting streaming text, thoughts, tool calls, rich media, and message editing capabilities.

## Requirements Overview

### Core Requirements
1. **Initial message population** from ChatSessionChangedEvent
2. **Incremental message building** from event stream
3. **Support for multiple message types** (assistant, user, thought)
4. **Rich message display** with Markdown, footers, and interactive elements
5. **Message editing capability** with history truncation
6. **Real-time tool usage notifications**
7. **Rich media rendering** (HTML, SVG)
8. **System notifications and error display**

## Data Models

### Server Data Structures

The server sends data in vendor-specific formats that must be normalized for UI consumption.

#### ChatSession Structure

```typescript
// Actual server ChatSession structure
export interface ChatSession {
  session_id: string;
  created_at?: string;
  updated_at?: string;
  title?: string;
  deleted?: boolean;
  vendor?: 'anthropic' | 'openai';  // Vendor-specific message format
  display_name?: string;             // User display name
  messages: MessageParam[];          // Vendor-specific message array
}
```

#### MessageParam Structure (Vendor-Specific)

The `MessageParam` type varies based on the vendor field:

```typescript
// Anthropic format (when vendor === 'anthropic')
export interface AnthropicMessageParam {
  role: 'user' | 'assistant';
  content: string | ContentBlockParam[];  // Can be string or array
}

// ContentBlockParam for rich content
export type ContentBlockParam = 
  | TextBlockParam 
  | ImageBlockParam 
  | ToolUseBlockParam 
  | ToolResultBlockParam;

export interface TextBlockParam {
  type: 'text';
  text: string;
  cache_control?: CacheControlEphemeral;
}

export interface ImageBlockParam {
  type: 'image';
  source: {
    type: 'base64';
    media_type: string;
    data: string;
  };
}

export interface ToolUseBlockParam {
  type: 'tool_use';
  id: string;
  name: string;
  input: unknown;
  cache_control?: CacheControlEphemeral;
}

export interface ToolResultBlockParam {
  type: 'tool_result';
  tool_use_id: string;
  content?: string | ContentBlockParam[];
  is_error?: boolean;
  cache_control?: CacheControlEphemeral;
}

// OpenAI format (when vendor === 'openai') - for future support
export interface OpenAIMessageParam {
  role: 'user' | 'assistant' | 'system';
  content: string;
  // Additional OpenAI-specific fields
}
```

### Content Normalization Process

The EventStreamProcessor must normalize vendor-specific content into a consistent format for UI consumption:

```typescript
export class EventStreamProcessor {
  private normalizeMessageContent(message: MessageParam): string {
    // Handle string content directly
    if (typeof message.content === 'string') {
      return message.content;
    }
    
    // Handle ContentBlockParam array
    if (Array.isArray(message.content)) {
      return message.content
        .map(block => {
          switch (block.type) {
            case 'text':
              return block.text;
            case 'tool_use':
              return `[Tool: ${block.name}]`;
            case 'tool_result':
              // Recursively normalize tool result content
              if (typeof block.content === 'string') {
                return block.content;
              }
              if (Array.isArray(block.content)) {
                return this.normalizeContentBlocks(block.content);
              }
              return '[Tool Result]';
            case 'image':
              return '[Image]';
            default:
              return '';
          }
        })
        .join('\n');
    }
    
    return '';
  }
  
  private normalizeContentBlocks(blocks: ContentBlockParam[]): string {
    return blocks
      .filter(block => block.type === 'text')
      .map(block => (block as TextBlockParam).text)
      .join('\n');
  }
}
```

### UI Data Structures

After normalization, the UI works with consistent structures:

```typescript
// Normalized message for UI consumption
export interface NormalizedMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;  // Always normalized to string
  timestamp: string;
  type: 'message' | 'thought' | 'media' | 'notification';
  status: 'streaming' | 'complete' | 'error';
  metadata?: {
    vendor?: 'anthropic' | 'openai';
    displayName?: string;
    originalContent?: MessageParam['content'];  // Preserve original for debugging
    inputTokens?: number;
    outputTokens?: number;
    stopReason?: string;
  };
  toolCalls?: ToolCall[];
}
```

### Vendor-Specific Handling

The system must handle vendor differences:

```typescript
export class VendorAdapter {
  static normalizeSession(session: ChatSession): NormalizedSession {
    return {
      sessionId: session.session_id,
      createdAt: session.created_at,
      updatedAt: session.updated_at,
      title: session.title,
      deleted: session.deleted,
      vendor: session.vendor || 'anthropic',  // Default to anthropic
      displayName: session.display_name,
      messages: session.messages.map(msg => 
        this.normalizeMessage(msg, session.vendor)
      )
    };
  }
  
  static normalizeMessage(
    message: MessageParam, 
    vendor?: string
  ): NormalizedMessage {
    const normalized: NormalizedMessage = {
      id: generateMessageId(),
      role: message.role,
      content: this.extractContent(message.content),
      timestamp: new Date().toISOString(),
      type: 'message',
      status: 'complete',
      metadata: {
        vendor: vendor as 'anthropic' | 'openai',
        originalContent: message.content
      }
    };
    
    // Extract tool calls if present in content blocks
    if (Array.isArray(message.content)) {
      normalized.toolCalls = this.extractToolCalls(message.content);
    }
    
    return normalized;
  }
  
  private static extractContent(
    content: string | ContentBlockParam[]
  ): string {
    if (typeof content === 'string') {
      return content;
    }
    
    return content
      .filter(block => block.type === 'text')
      .map(block => (block as TextBlockParam).text)
      .join('\n');
  }
  
  private static extractToolCalls(
    content: ContentBlockParam[]
  ): ToolCall[] | undefined {
    const toolCalls = content
      .filter(block => block.type === 'tool_use')
      .map(block => {
        const toolBlock = block as ToolUseBlockParam;
        return {
          id: toolBlock.id,
          function: {
            name: toolBlock.name,
            arguments: JSON.stringify(toolBlock.input)
          }
        };
      });
    
    return toolCalls.length > 0 ? toolCalls : undefined;
  }
}
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Event Stream                         │
│  (TextDelta, ThoughtDelta, ToolCall, RenderMedia, etc.) │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              EventStreamProcessor                       │
│  - Routes events to appropriate handlers                │
│  - Coordinates message building                         │
│  - Manages state transitions                           │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬─────────────┐
         ▼                       ▼             ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  MessageBuilder  │  │ ToolCallManager │  │ RichMediaHandler │
│  - Accumulates   │  │ - Tracks tools   │  │ - Processes      │
│    text/thoughts │  │ - Notifications  │  │   media events   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                       │             │
         └───────────┬───────────┴─────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Enhanced SessionManager                    │
│  - Maintains message history                           │
│  - Handles message mutations                           │
│  - Emits UI update events                             │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  UI Components                         │
│  - MessageList, Message, ThoughtMessage                │
│  - ToolCallDisplay, RichMediaDisplay                   │
│  - SystemNotification                                  │
└─────────────────────────────────────────────────────────┘
```

## Core SDK Components

### 1. EventStreamProcessor

**Purpose:** Central coordinator for processing incoming events and building messages with vendor normalization

```typescript
export class EventStreamProcessor {
  private messageBuilder: MessageBuilder;
  private toolCallManager: ToolCallManager;
  private richMediaHandler: RichMediaHandler;
  private sessionManager: SessionManager;
  private currentVendor: 'anthropic' | 'openai' = 'anthropic';
  
  constructor(sessionManager: SessionManager) {
    this.sessionManager = sessionManager;
    this.messageBuilder = new MessageBuilder();
    this.toolCallManager = new ToolCallManager();
    this.richMediaHandler = new RichMediaHandler();
  }
  
  processEvent(event: ServerEvent): void {
    switch (event.type) {
      case 'chat_session_changed':
        this.handleSessionChanged(event);
        break;
      case 'text_delta':
        this.handleTextDelta(event);
        break;
      case 'thought_delta':
        this.handleThoughtDelta(event);
        break;
      case 'completion':
        this.handleCompletion(event);
        break;
      case 'tool_select_delta':
        this.handleToolSelect(event);
        break;
      case 'tool_call':
        this.handleToolCall(event);
        break;
      case 'render_media':
        this.handleRenderMedia(event);
        break;
      // ... other events
    }
  }
  
  private handleSessionChanged(event: ChatSessionChangedEvent): void {
    const session = event.chat_session;
    // Store vendor for content normalization
    this.currentVendor = session.vendor || 'anthropic';
    
    // Normalize all messages in the session
    const normalizedMessages = session.messages.map(msg => 
      this.normalizeMessage(msg)
    );
    
    // Update session with normalized messages
    this.sessionManager.setSession({
      ...session,
      messages: normalizedMessages,
      displayName: session.display_name
    });
  }
  
  private normalizeMessage(message: MessageParam): NormalizedMessage {
    return VendorAdapter.normalizeMessage(message, this.currentVendor);
  }
  
  private handleTextDelta(event: TextDeltaEvent): void {
    this.messageBuilder.appendText(event.content);
    this.sessionManager.updateStreamingMessage(
      this.messageBuilder.getCurrentMessage()
    );
  }
  
  private handleCompletion(event: CompletionEvent): void {
    if (!event.running) {
      const message = this.messageBuilder.finalize({
        inputTokens: event.input_tokens,
        outputTokens: event.output_tokens,
        stopReason: event.stop_reason,
        vendor: this.currentVendor
      });
      this.sessionManager.finalizeMessage(message);
      this.messageBuilder.reset();
    }
  }
}
```

### 2. MessageBuilder

**Purpose:** Accumulates streaming content and builds complete messages

```typescript
export interface MessageMetadata {
  inputTokens?: number;
  outputTokens?: number;
  stopReason?: string;
  toolCalls?: ToolCall[];
  vendor?: 'anthropic' | 'openai';
  displayName?: string;
  originalContent?: string | ContentBlockParam[];
}

export class MessageBuilder {
  private currentMessage: Partial<EnhancedMessage> | null = null;
  private messageType: 'assistant' | 'thought' | 'user' = 'assistant';
  private content: string = '';
  
  startMessage(type: 'assistant' | 'thought' | 'user'): void {
    this.currentMessage = {
      id: generateMessageId(),
      role: type === 'thought' ? 'assistant' : type,
      content: '',
      timestamp: new Date().toISOString(),
      type: type === 'thought' ? 'thought' : 'message',
      status: 'streaming'
    };
    this.messageType = type;
    this.content = '';
  }
  
  appendText(delta: string): void {
    this.content += delta;
    if (this.currentMessage) {
      this.currentMessage.content = this.content;
    }
  }
  
  finalize(metadata?: MessageMetadata): EnhancedMessage {
    if (!this.currentMessage) {
      throw new Error('No message to finalize');
    }
    
    return {
      ...this.currentMessage,
      content: this.content,
      status: 'complete',
      metadata: metadata || {},
      toolCalls: metadata?.toolCalls
    } as EnhancedMessage;
  }
  
  getCurrentMessage(): Partial<EnhancedMessage> | null {
    return this.currentMessage ? {
      ...this.currentMessage,
      content: this.content
    } : null;
  }
  
  reset(): void {
    this.currentMessage = null;
    this.content = '';
  }
}
```

### 3. ToolCallManager

**Purpose:** Tracks tool usage state and manages notifications

```typescript
export interface ToolNotification {
  id: string;
  toolName: string;
  status: 'preparing' | 'executing' | 'complete';
  timestamp: Date;
}

export class ToolCallManager {
  private activeTools: Map<string, ToolNotification> = new Map();
  private completedToolCalls: ToolCall[] = [];
  
  onToolSelect(event: ToolSelectDeltaEvent): ToolNotification {
    const toolCall = event.tool_calls[0];
    const notification: ToolNotification = {
      id: toolCall.id,
      toolName: toolCall.function.name,
      status: 'preparing',
      timestamp: new Date()
    };
    
    this.activeTools.set(toolCall.id, notification);
    return notification;
  }
  
  onToolCallActive(event: ToolCallEvent): ToolNotification | null {
    const toolCall = event.tool_calls[0];
    const notification = this.activeTools.get(toolCall.id);
    
    if (notification && event.active) {
      notification.status = 'executing';
      return notification;
    }
    
    return null;
  }
  
  onToolCallComplete(event: ToolCallEvent): ToolCall[] {
    if (!event.active && event.tool_results) {
      event.tool_calls.forEach(tc => {
        this.activeTools.delete(tc.id);
        this.completedToolCalls.push({
          ...tc,
          result: event.tool_results?.find(r => r.tool_use_id === tc.id)
        });
      });
    }
    
    return this.completedToolCalls;
  }
  
  getActiveNotifications(): ToolNotification[] {
    return Array.from(this.activeTools.values())
      .filter(n => n.status !== 'complete');
  }
  
  reset(): void {
    this.activeTools.clear();
    this.completedToolCalls = [];
  }
}
```

### 4. RichMediaHandler

**Purpose:** Processes and validates rich media content

```typescript
export interface RichMediaContent {
  id: string;
  type: 'html' | 'svg' | 'image';
  content: string;
  metadata: {
    sentByClass: string;
    sentByFunction: string;
    timestamp: Date;
  };
}

export class RichMediaHandler {
  processRenderMediaEvent(event: RenderMediaEvent): RichMediaContent {
    const mediaType = this.determineMediaType(event.content_type);
    
    return {
      id: generateMediaId(),
      type: mediaType,
      content: this.sanitizeContent(event.content, mediaType),
      metadata: {
        sentByClass: event.sent_by_class,
        sentByFunction: event.sent_by_function,
        timestamp: new Date()
      }
    };
  }
  
  private determineMediaType(contentType: string): 'html' | 'svg' | 'image' {
    if (contentType.includes('html')) return 'html';
    if (contentType.includes('svg')) return 'svg';
    return 'image';
  }
  
  private sanitizeContent(content: string, type: string): string {
    // Implement content sanitization based on type
    // For HTML: use DOMPurify or similar
    // For SVG: validate SVG structure
    return content;
  }
}
```

### 5. MessageEditManager

**Purpose:** Handles message editing with history truncation

```typescript
export class MessageEditManager {
  constructor(
    private sessionManager: SessionManager,
    private client: RealtimeClient
  ) {}
  
  async editMessage(
    messageId: string, 
    newContent: string
  ): Promise<void> {
    // Get current message history
    const session = this.sessionManager.getCurrentSession();
    if (!session) throw new Error('No active session');
    
    // Find the message to edit
    const messageIndex = session.messages.findIndex(
      m => m.id === messageId
    );
    if (messageIndex === -1) throw new Error('Message not found');
    
    // Truncate history at edit point
    const truncatedMessages = session.messages.slice(0, messageIndex);
    
    // Send SetSessionMessagesEvent
    await this.client.setSessionMessages(truncatedMessages);
    
    // Wait for history event confirmation
    await this.waitForHistoryUpdate();
    
    // Send new user message with edited content
    await this.client.sendMessage(newContent);
  }
  
  private waitForHistoryUpdate(): Promise<void> {
    return new Promise((resolve) => {
      const handler = () => {
        this.client.off('history', handler);
        resolve();
      };
      this.client.once('history', handler);
    });
  }
}
```

### 6. Enhanced SessionManager

**Additions to existing SessionManager:**

```typescript
export interface EnhancedMessage extends Message {
  id: string;
  type: 'message' | 'thought' | 'media' | 'notification';
  status: 'streaming' | 'complete' | 'error';
  metadata?: MessageMetadata;
  toolCalls?: ToolCall[];
  isCollapsed?: boolean; // For thoughts
}

// Additional methods for SessionManager
class SessionManager {
  // ... existing code ...
  
  private streamingMessage: Partial<EnhancedMessage> | null = null;
  private toolNotifications: Map<string, ToolNotification> = new Map();
  
  updateStreamingMessage(message: Partial<EnhancedMessage>): void {
    this.streamingMessage = message;
    this.emit('message-streaming', {
      sessionId: this.currentSessionId!,
      message
    });
  }
  
  finalizeMessage(message: EnhancedMessage): void {
    const session = this.getCurrentSession();
    if (!session) return;
    
    // Replace or add the finalized message
    const existingIndex = session.messages.findIndex(
      m => m.id === message.id
    );
    
    if (existingIndex >= 0) {
      session.messages[existingIndex] = message;
    } else {
      session.messages.push(message);
    }
    
    this.streamingMessage = null;
    this.emit('message-complete', {
      sessionId: session.session_id,
      message
    });
  }
  
  addToolNotification(notification: ToolNotification): void {
    this.toolNotifications.set(notification.id, notification);
    this.emit('tool-notification', notification);
  }
  
  removeToolNotification(id: string): void {
    this.toolNotifications.delete(id);
    this.emit('tool-notification-removed', id);
  }
  
  addRichMedia(media: RichMediaContent): void {
    const session = this.getCurrentSession();
    if (!session) return;
    
    const mediaMessage: EnhancedMessage = {
      id: media.id,
      role: 'assistant',
      type: 'media',
      content: media.content,
      contentType: media.type,
      timestamp: media.metadata.timestamp.toISOString(),
      status: 'complete',
      metadata: media.metadata
    };
    
    session.messages.push(mediaMessage);
    this.emit('media-added', {
      sessionId: session.session_id,
      media: mediaMessage
    });
  }
}
```

## UI Components Design

### 1. Enhanced Message Component

```tsx
export interface MessageProps {
  message: EnhancedMessage;
  onEdit?: (messageId: string, content: string) => void;
  onCopy?: (content: string) => void;
  showTokenCounts?: boolean;
}

export const Message: React.FC<MessageProps> = ({
  message,
  onEdit,
  onCopy,
  showTokenCounts = true
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [showToolCalls, setShowToolCalls] = useState(false);
  
  if (message.type === 'thought') {
    return <ThoughtMessage message={message} />;
  }
  
  if (message.type === 'media') {
    return <RichMediaDisplay message={message} />;
  }
  
  return (
    <div className="message-container">
      <div className="message-content">
        {isEditing ? (
          <MessageEditor
            content={editContent}
            onSave={(content) => {
              onEdit?.(message.id, content);
              setIsEditing(false);
            }}
            onCancel={() => setIsEditing(false)}
          />
        ) : (
          <MarkdownRenderer content={message.content} />
        )}
      </div>
      
      <MessageFooter
        message={message}
        onEdit={() => setIsEditing(true)}
        onCopy={() => onCopy?.(message.content)}
        onToggleToolCalls={() => setShowToolCalls(!showToolCalls)}
        showTokenCounts={showTokenCounts}
      />
      
      {showToolCalls && message.toolCalls && (
        <ToolCallDisplay toolCalls={message.toolCalls} />
      )}
    </div>
  );
};
```

### 2. ThoughtMessage Component

```tsx
export const ThoughtMessage: React.FC<{ message: EnhancedMessage }> = ({
  message
}) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const firstLine = message.content.split('\n')[0];
  
  return (
    <div className="thought-message">
      <button
        className="thought-toggle"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <ChevronIcon className={isCollapsed ? 'rotate-0' : 'rotate-90'} />
        <span className="thought-preview">
          {isCollapsed ? firstLine : 'Hide thought process'}
        </span>
      </button>
      
      {!isCollapsed && (
        <div className="thought-content">
          <MarkdownRenderer content={message.content} />
          <MessageFooter
            message={message}
            onCopy={() => navigator.clipboard.writeText(message.content)}
            showTokenCounts={true}
          />
        </div>
      )}
    </div>
  );
};
```

### 3. MessageFooter Component

```tsx
export const MessageFooter: React.FC<{
  message: EnhancedMessage;
  onEdit?: () => void;
  onCopy?: () => void;
  onToggleToolCalls?: () => void;
  showTokenCounts?: boolean;
}> = ({
  message,
  onEdit,
  onCopy,
  onToggleToolCalls,
  showTokenCounts
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const hasToolCalls = message.toolCalls && message.toolCalls.length > 0;
  
  return (
    <div className="message-footer">
      <div className="footer-left">
        {showTokenCounts && message.metadata?.inputTokens && (
          <span className="token-count">
            {message.metadata.inputTokens} → {message.metadata.outputTokens}
          </span>
        )}
        
        {hasToolCalls && (
          <button
            className="tool-calls-toggle"
            onClick={onToggleToolCalls}
          >
            <ToolIcon className="icon" />
            {message.toolCalls!.length} tool{message.toolCalls!.length > 1 ? 's' : ''}
          </button>
        )}
      </div>
      
      <div className="footer-right">
        {isUser && (
          <button
            className="edit-button"
            onClick={onEdit}
            aria-label="Edit message"
          >
            <EditIcon className="icon" />
          </button>
        )}
        
        <button
          className="copy-button"
          onClick={onCopy}
          aria-label="Copy message"
        >
          <CopyIcon className="icon" />
        </button>
      </div>
    </div>
  );
};
```

### 4. ToolNotification Component

```tsx
export const ToolNotification: React.FC<{
  notification: ToolNotification;
}> = ({ notification }) => {
  const getMessage = () => {
    switch (notification.status) {
      case 'preparing':
        return `Agent is preparing to use ${notification.toolName}...`;
      case 'executing':
        return `Agent is using ${notification.toolName}...`;
      default:
        return '';
    }
  };
  
  return (
    <div className="tool-notification">
      <LoadingSpinner className="notification-spinner" />
      <span className="notification-text">{getMessage()}</span>
    </div>
  );
};
```

### 5. RichMediaDisplay Component

```tsx
export const RichMediaDisplay: React.FC<{
  message: EnhancedMessage;
}> = ({ message }) => {
  const renderContent = () => {
    switch (message.contentType) {
      case 'html':
        return (
          <div 
            className="rich-html"
            dangerouslySetInnerHTML={{ __html: message.content }}
          />
        );
      
      case 'svg':
        return (
          <div 
            className="rich-svg"
            dangerouslySetInnerHTML={{ __html: message.content }}
          />
        );
      
      default:
        return <div>Unsupported media type</div>;
    }
  };
  
  return (
    <div className="rich-media-container">
      {renderContent()}
      <div className="media-attribution">
        Sent by {message.metadata?.sentByClass}.{message.metadata?.sentByFunction}
      </div>
    </div>
  );
};
```

### 6. SystemNotification Component

```tsx
export const SystemNotification: React.FC<{
  event: SystemMessageEvent | ErrorEvent;
}> = ({ event }) => {
  const severity = 'severity' in event ? event.severity : 'error';
  const content = 'content' in event ? event.content : event.message;
  
  return (
    <div className={`system-notification severity-${severity}`}>
      <div className="notification-icon">
        {severity === 'error' ? <ErrorIcon /> : <InfoIcon />}
      </div>
      <div className="notification-content">
        {content}
      </div>
    </div>
  );
};
```

## Event Flow Sequences

### 1. Session Initialization Flow

```
1. ChatSessionChangedEvent received with vendor and display_name
   → EventStreamProcessor.handleSessionChanged()
   → Store vendor for normalization
   → Normalize all MessageParam objects
   → Convert content (string | ContentBlockParam[]) to string
   → SessionManager.setSession() with normalized data
   → UI receives consistent message format
```

### 2. Standard Text Response Flow

```
1. User sends message → TextInputEvent
2. Server responds with InteractionEvent (started: true)
3. CompletionEvent (running: true)
4. TextDeltaEvent stream begins
   → EventStreamProcessor.handleTextDelta()
   → MessageBuilder.appendText()
   → SessionManager.updateStreamingMessage()
   → UI updates with streaming text
5. CompletionEvent (running: false) with token counts
   → MessageBuilder.finalize() with vendor metadata
   → SessionManager.finalizeMessage()
   → UI shows complete message with footer
6. InteractionEvent (started: false)
```

### 3. Tool Usage Flow

```
1. ToolSelectDeltaEvent received
   → ToolCallManager.onToolSelect()
   → UI shows "Agent is preparing to use X..."
2. ToolCallEvent (active: true)
   → ToolCallManager.onToolCallActive()
   → UI updates to "Agent is using X..."
3. Tool execution occurs
4. ToolCallEvent (active: false) with results
   → ToolCallManager.onToolCallComplete()
   → UI removes notification
   → Tool calls added to message footer
```

### 4. Message Editing Flow

```
1. User clicks edit on their message
2. UI enters edit mode
3. User modifies content and saves
4. MessageEditManager.editMessage() called
   → Truncates message history
   → Sends SetSessionMessagesEvent
5. Server responds with HistoryEvent
6. New TextInputEvent sent with edited content
7. Normal response flow continues
```

## React Hook Integration

### useMessages Hook

```typescript
export const useMessages = () => {
  const client = useRealtimeClient();
  const [messages, setMessages] = useState<EnhancedMessage[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<Partial<EnhancedMessage> | null>(null);
  const [toolNotifications, setToolNotifications] = useState<ToolNotification[]>([]);
  
  useEffect(() => {
    const sessionManager = client.getSessionManager();
    
    const handleMessageStreaming = ({ message }: any) => {
      setStreamingMessage(message);
    };
    
    const handleMessageComplete = ({ message }: any) => {
      setMessages(prev => [...prev, message]);
      setStreamingMessage(null);
    };
    
    const handleToolNotification = (notification: ToolNotification) => {
      setToolNotifications(prev => [...prev, notification]);
    };
    
    sessionManager.on('message-streaming', handleMessageStreaming);
    sessionManager.on('message-complete', handleMessageComplete);
    sessionManager.on('tool-notification', handleToolNotification);
    
    return () => {
      sessionManager.off('message-streaming', handleMessageStreaming);
      sessionManager.off('message-complete', handleMessageComplete);
      sessionManager.off('tool-notification', handleToolNotification);
    };
  }, [client]);
  
  const editMessage = useCallback(async (messageId: string, content: string) => {
    const editManager = new MessageEditManager(
      client.getSessionManager(),
      client
    );
    await editManager.editMessage(messageId, content);
  }, [client]);
  
  return {
    messages,
    streamingMessage,
    toolNotifications,
    editMessage
  };
};
```

## Type Definitions

```typescript
// Enhanced types for the implementation
export interface EnhancedMessage extends Message {
  id: string;
  type: 'message' | 'thought' | 'media' | 'notification';
  status: 'streaming' | 'complete' | 'error';
  contentType?: 'text' | 'html' | 'svg';
  metadata?: {
    inputTokens?: number;
    outputTokens?: number;
    stopReason?: string;
    sentByClass?: string;
    sentByFunction?: string;
  };
  toolCalls?: Array<{
    id: string;
    function: {
      name: string;
      arguments: string;
    };
    result?: any;
  }>;
  isCollapsed?: boolean;
}

export interface MessageStreamState {
  messages: EnhancedMessage[];
  streamingMessage: Partial<EnhancedMessage> | null;
  toolNotifications: ToolNotification[];
  activeInteraction: string | null;
}
```

## Implementation Phases

### Phase 1: Core SDK Components
1. Implement EventStreamProcessor with vendor normalization
2. Create VendorAdapter for content normalization
3. Create MessageBuilder class with vendor awareness
4. Implement ToolCallManager
5. Add RichMediaHandler
6. Enhance SessionManager with new methods

### Phase 2: Basic UI Components
1. Create enhanced Message component
2. Implement MessageFooter with actions
3. Add basic MarkdownRenderer
4. Create SystemNotification component

### Phase 3: Advanced Features
1. Implement ThoughtMessage with collapsing
2. Add ToolCallDisplay component
3. Create RichMediaDisplay component
4. Implement MessageEditManager
5. Add ToolNotification component

### Phase 4: Integration & Polish
1. Create useMessages hook
2. Integrate with existing ChatMessagesView
3. Add animations and transitions
4. Implement keyboard shortcuts
5. Add accessibility features

## Testing Strategy

### Unit Tests
- EventStreamProcessor event routing
- VendorAdapter content normalization (string and ContentBlockParam[])
- MessageBuilder accumulation and finalization
- ToolCallManager state transitions
- MessageEditManager truncation logic
- Vendor-specific message parsing

### Integration Tests
- Full event stream to UI flow
- Message editing with server round-trip
- Tool notification lifecycle
- Rich media rendering

### E2E Tests
- Complete conversation flow
- Message editing user journey
- Tool usage visualization
- Error handling and recovery

## Performance Considerations

1. **Message Virtualization**: For long conversations, implement virtual scrolling
2. **Debounced Updates**: Batch streaming updates to avoid excessive re-renders
3. **Lazy Loading**: Load message history on demand
4. **Memoization**: Use React.memo for message components
5. **Content Sanitization**: Cache sanitized HTML/SVG content

## Security Considerations

1. **HTML Sanitization**: Use DOMPurify for RenderMediaEvent HTML content
2. **SVG Validation**: Validate SVG structure before rendering
3. **XSS Prevention**: Never use dangerouslySetInnerHTML without sanitization
4. **Content Security Policy**: Implement CSP headers for the application

## Key Considerations

### Vendor Compatibility

The system is designed to handle multiple LLM vendors with different message formats:

1. **Anthropic Format**: Supports rich content blocks including text, images, tool use, and tool results
2. **OpenAI Format**: Currently supports basic text content (extensible for future requirements)
3. **Normalization Layer**: All vendor-specific formats are normalized to a consistent UI format
4. **Metadata Preservation**: Original content is preserved in metadata for debugging and future needs

### Content Type Handling

1. **String Content**: Passed through directly
2. **ContentBlockParam Arrays**: 
   - Text blocks are extracted and concatenated
   - Tool use blocks are converted to tool calls
   - Images are marked with placeholders
   - Tool results are recursively processed

### Display Name Integration

The `display_name` field from ChatSession is used to:
- Show user identification in the UI
- Personalize the chat experience
- Track message attribution in multi-user scenarios

## Conclusion

This design provides a comprehensive architecture for handling the complex requirements of chat message display and event stream processing, with special attention to vendor-specific data formats and content normalization. The modular approach allows for incremental implementation while maintaining clear separation of concerns between SDK event processing and UI rendering. The vendor adapter pattern ensures that the UI always receives consistent data regardless of the backend LLM provider. The system is designed to be extensible, performant, and secure while providing a rich user experience with real-time updates, interactive features, and support for diverse content types.