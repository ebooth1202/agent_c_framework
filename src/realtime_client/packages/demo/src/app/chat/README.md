# Chat Page - Production Implementation

## Overview

The chat page (`/chat`) is the main entry point for users to interact with the Agent C Realtime system. It provides a complete, production-ready implementation with proper authentication, SDK initialization, and a full-featured chat interface.

## Architecture

### Component Hierarchy

```
ChatPage (Main Export)
├── AuthProvider (Authentication Context)
│   └── AuthGuard (Authentication Check)
│       └── ClientProvider (SDK Initialization)
│           └── ChatContent (Main Interface)
│               ├── Header (Navigation & User Info)
│               └── ChatInterface (Chat Component)
```

### Authentication Flow

1. **Page Load**: User navigates to `/chat`
2. **Auth Check**: `AuthProvider` verifies JWT token validity
3. **Redirect Logic**:
   - If not authenticated → Redirect to `/login`
   - If authenticated → Continue to SDK initialization
4. **SDK Setup**: `ClientProvider` initializes RealtimeClient with auth tokens
5. **Connection**: WebSocket connection established with backend
6. **Ready State**: Chat interface becomes available

### Key Components

#### AuthProvider
- Manages authentication state
- Provides auth context to child components
- Handles token refresh and expiration
- Source: `/contexts/auth-context.tsx`

#### AuthGuard
- Enforces authentication requirement
- Shows loading state during auth check
- Redirects unauthenticated users to login
- Renders children only when authenticated

#### ClientProvider
- Initializes `RealtimeClient` with configuration
- Manages SDK lifecycle (connect/disconnect)
- Passes auth tokens and session ID to SDK
- Handles connection errors and retries
- Source: `/components/providers/client-provider.tsx`

#### ChatContent
- Main UI container with header and chat area
- Displays user information and logout button
- Shows available communication modes (text/voice/avatar)
- Provides navigation back to dashboard

#### ChatInterface
- Core chat functionality from Phase 4
- Manages messages, input, and output modes
- Handles voice streaming and turn management
- Provides view switching (text/voice/avatar)
- Source: `/components/chat/chat-interface.tsx`

## Features

### Security
- JWT-based authentication required
- Automatic redirect for unauthenticated users
- Token validation on every page load
- Secure WebSocket connection with auth headers

### User Experience
- Loading states during authentication
- Connection status indicators
- Error handling with user-friendly messages
- Smooth transitions between auth states
- Mode indicators (text/voice/avatar)

### Communication Modes
- **Text Mode**: Traditional text chat
- **Voice Mode**: Real-time voice streaming with turn management
- **Avatar Mode**: HeyGen avatar integration (when available)

### State Management
- Authentication state via React Context
- SDK state via AgentCProvider
- Local component state for UI
- Proper cleanup on unmount

## Configuration

### Environment Variables

```env
# Required
NEXT_PUBLIC_AGENTC_API_URL=wss://agent-c-prod.censius.ai

# Optional (defaults shown)
NEXT_PUBLIC_AUTH_API_URL=/api/auth
```

### ClientProvider Options

```typescript
<ClientProvider
  apiUrl={process.env.NEXT_PUBLIC_AGENTC_API_URL}
  enableAudio={true}              // Enable audio capture/playback
  enableTurnManagement={true}     // Server-controlled turn taking
  respectTurnState={true}         // Prevent talk-over
>
```

## Usage Patterns

### Direct Navigation
Users can navigate directly to `/chat` but will be redirected to login if not authenticated:

```
/chat → [Not Authenticated] → /login → [Login Success] → /chat
```

### Post-Login Flow
After successful login, users are typically redirected to the dashboard, then can access chat:

```
/login → [Login Success] → /dashboard → [Click Chat] → /chat
```

### Session Persistence
The authentication token is stored in localStorage, allowing sessions to persist across page refreshes:

```typescript
// Token stored on login
localStorage.setItem('auth_token', response.token);

// Token retrieved on page load
const token = localStorage.getItem('auth_token');
```

## Error Handling

### Authentication Errors
- Invalid/expired token → Redirect to login
- Network error during auth check → Show error message
- Missing credentials → Show authentication required card

### Connection Errors
- WebSocket connection failure → Display connection alert
- Reconnection attempts → Automatic with exponential backoff
- Max retries exceeded → Show error with retry option

### Runtime Errors
- Audio permission denied → Fallback to text mode
- Message send failure → Show error toast
- Stream interruption → Automatic recovery attempt

## Development Tips

### Testing Authentication Flow
1. Clear localStorage to test unauthenticated state
2. Use browser DevTools to monitor WebSocket connections
3. Check Network tab for auth token in WS headers
4. Verify JWT expiration handling

### Debugging Connection Issues
```typescript
// Enable debug mode in ClientProvider
<ClientProvider
  apiUrl={apiUrl}
  debug={true}  // Logs all SDK events
>
```

### Performance Monitoring
- Check for memory leaks in Chrome DevTools
- Monitor WebSocket frame size for audio data
- Verify proper cleanup on component unmount
- Track reconnection attempts in console

## Production Considerations

### Scalability
- WebSocket connections are persistent
- Consider connection limits per server
- Implement proper load balancing
- Monitor concurrent user limits

### Security
- Always use WSS (WebSocket Secure) in production
- Validate JWT tokens on backend
- Implement rate limiting for messages
- Sanitize user input before display

### Monitoring
- Track WebSocket connection metrics
- Monitor authentication failures
- Log chat session durations
- Measure audio quality metrics

### User Experience
- Provide clear connection status
- Show typing indicators for agent responses
- Handle network interruptions gracefully
- Offer fallback to text mode if audio fails

## Future Enhancements

### Planned Features
- [ ] Session history persistence
- [ ] File upload support
- [ ] Screen sharing capability
- [ ] Multi-agent conversations
- [ ] Custom avatar selection

### Technical Improvements
- [ ] Implement message encryption
- [ ] Add offline message queue
- [ ] Optimize audio compression
- [ ] Enhance reconnection logic
- [ ] Add analytics integration

## Troubleshooting

### Common Issues

**"Not connected to server" alert**
- Check WebSocket URL configuration
- Verify auth token is valid
- Check network connectivity
- Review browser console for errors

**Audio not working**
- Ensure microphone permissions granted
- Check audio device selection
- Verify browser supports Web Audio API
- Try fallback to text mode

**Page keeps redirecting to login**
- Clear browser localStorage
- Check token expiration time
- Verify auth endpoint is accessible
- Review auth context initialization

**Messages not sending**
- Confirm WebSocket connection active
- Check turn state (if voice mode)
- Verify message format/content
- Review console for SDK errors

## Related Documentation

- [Authentication System](../login/README.md)
- [Client Provider](../../components/providers/README.md)
- [Chat Interface](../../components/chat/README.md)
- [SDK Documentation](../../../../realtime-core/README.md)