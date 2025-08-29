# SessionManager Integration with RealtimeClient

## Summary
Successfully integrated the SessionManager class with RealtimeClient to handle session management and message history tracking.

## Changes Made

### 1. Imports and Properties
- Added `SessionManager` to the imports from '../session'
- Added private property `sessionManager: SessionManager | null`

### 2. Initialization
- SessionManager is initialized in the constructor with configuration:
  ```typescript
  this.sessionManager = new SessionManager({
      maxSessions: 50,
      persistSessions: false
  });
  ```

### 3. Event Handling Setup
- Created `setupSessionManagerHandlers()` method that subscribes to server events:
  - `chat_session_changed` → Updates current session via `setCurrentSession()`
  - `text_delta` → Accumulates text chunks via `handleTextDelta()`
  - `completion` (when running=false) → Finalizes text via `handleTextDone()`
  - `chat_session_name_changed` → Updates session name via `updateSessionName()`
- Called in the WebSocket `onOpen` callback after successful connection

### 4. User Message Tracking
- Updated `sendText()` method to add user messages to session history:
  ```typescript
  if (this.sessionManager) {
      this.sessionManager.addUserMessage(text);
  }
  ```

### 5. Session Management Methods
Enhanced existing session methods with SessionManager integration:
- `newChatSession()` - Resets text accumulator when creating new session
- `resumeChatSession()` - Resets text accumulator when switching sessions
- `setChatSessionName()` - Updates local session name immediately for better UX

### 6. Public Access
- Added `getSessionManager()` getter method for external access to SessionManager

### 7. Cleanup
- Reset accumulator in `disconnect()` method
- Properly destroy SessionManager in `destroy()` method

## Text Accumulation Flow

1. **Text Delta Events**: Server sends `text_delta` events with content chunks
2. **Accumulation**: SessionManager accumulates these chunks internally
3. **Completion**: When server sends `completion` event with `running: false`, the accumulated text is finalized as an assistant message
4. **History**: The finalized message is added to the current session's message history

## Benefits

- **Centralized session management**: All session data in one place
- **Automatic history tracking**: Messages are automatically added to session history
- **Text accumulation**: Properly handles streaming text responses
- **Event-driven updates**: Session changes are observable via events
- **Memory management**: Configurable max sessions with automatic pruning
- **Clean separation**: SessionManager handles all session logic independently

## Usage Example

```typescript
const client = new RealtimeClient(config);
const sessionManager = client.getSessionManager();

// Subscribe to session changes
sessionManager.on('session-changed', ({ currentSession }) => {
    console.log('Active session:', currentSession?.session_id);
});

// Subscribe to new messages
sessionManager.on('message-added', ({ message }) => {
    console.log('New message:', message.role, message.content);
});

// Send a message (automatically tracked)
client.sendText('Hello, assistant!');

// Get current session info
const session = sessionManager.getCurrentSession();
console.log('Messages:', session?.messages);
```

## Backward Compatibility

The integration maintains full backward compatibility:
- All existing methods work as before
- SessionManager is optional (can be null)
- No breaking changes to the public API
- Event subscriptions are set up only after connection