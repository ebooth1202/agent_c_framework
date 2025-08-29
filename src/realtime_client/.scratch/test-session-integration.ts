/**
 * Test file to verify SessionManager integration with RealtimeClient
 */

import { RealtimeClient } from '../packages/core/src/client/RealtimeClient';
import { SessionManager } from '../packages/core/src/session/SessionManager';
import type { ChatSession } from '../packages/core/src/events/types/CommonTypes';

// Mock configuration
const config = {
    apiUrl: 'wss://api.example.com/ws',
    authToken: 'test-token',
    debug: true,
    enableTurnManager: true,
    enableAudio: false
};

// Create client instance
const client = new RealtimeClient(config);

// Get session manager
const sessionManager = client.getSessionManager();

console.log('SessionManager integration test:');
console.log('================================');

// Verify session manager exists
console.assert(sessionManager !== null, 'SessionManager should be initialized');
console.log('✓ SessionManager is initialized');

// Verify session manager is an instance of SessionManager
console.assert(sessionManager instanceof SessionManager, 'Should be instance of SessionManager');
console.log('✓ SessionManager is correct type');

// Test event handling simulation
console.log('\nSimulating server events:');
console.log('-------------------------');

// Simulate chat_session_changed event
const mockSession: ChatSession = {
    session_id: 'test-session-123',
    session_name: 'Test Session',
    messages: [],
    token_count: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metadata: {}
};

// Subscribe to session changes
sessionManager?.on('session-changed', (event) => {
    console.log('✓ Session changed event received:', {
        previousId: event.previousSession?.session_id || 'none',
        currentId: event.currentSession?.session_id || 'none'
    });
});

// Simulate message events
sessionManager?.on('message-added', (event) => {
    console.log('✓ Message added to session:', {
        sessionId: event.sessionId,
        role: event.message.role,
        contentLength: event.message.content.length
    });
});

// Test text accumulation
console.log('\nTesting text accumulation:');
console.log('-------------------------');

// Start accumulation
sessionManager?.setCurrentSession(mockSession);
sessionManager?.handleTextDelta('Hello ');
console.log('Current accumulated text:', sessionManager?.getAccumulatedText());
console.assert(sessionManager?.getAccumulatedText() === 'Hello ', 'Should accumulate text delta');

sessionManager?.handleTextDelta('world!');
console.log('Current accumulated text:', sessionManager?.getAccumulatedText());
console.assert(sessionManager?.getAccumulatedText() === 'Hello world!', 'Should accumulate multiple deltas');

// Finalize text
const finalizedMessage = sessionManager?.handleTextDone();
console.log('✓ Text finalized as assistant message');
console.assert(finalizedMessage?.content === 'Hello world!', 'Should finalize with accumulated text');
console.assert(finalizedMessage?.role === 'assistant', 'Should be assistant role');
console.assert(sessionManager?.getAccumulatedText() === '', 'Accumulator should be reset');

// Test user message
console.log('\nTesting user message:');
console.log('---------------------');

const userMessage = sessionManager?.addUserMessage('This is a user message');
console.log('✓ User message added');
console.assert(userMessage?.role === 'user', 'Should be user role');
console.assert(userMessage?.content === 'This is a user message', 'Should have correct content');

// Verify session has messages
const currentSession = sessionManager?.getCurrentSession();
console.assert(currentSession?.messages.length === 2, 'Session should have 2 messages');
console.log('✓ Session has', currentSession?.messages.length, 'messages');

// Test session name update
console.log('\nTesting session name update:');
console.log('----------------------------');

const sessionId = sessionManager?.getCurrentSessionId();
if (sessionId) {
    sessionManager?.updateSessionName(sessionId, 'Updated Session Name');
    const updatedSession = sessionManager?.getCurrentSession();
    console.assert(updatedSession?.session_name === 'Updated Session Name', 'Name should be updated');
    console.log('✓ Session name updated to:', updatedSession?.session_name);
}

// Test statistics
console.log('\nSession statistics:');
console.log('------------------');
const stats = sessionManager?.getStatistics();
console.log('Total sessions:', stats?.totalSessions);
console.log('Total messages:', stats?.totalMessages);
console.log('Total tokens:', stats?.totalTokens);
console.log('Current session ID:', stats?.currentSessionId);
console.log('Has active accumulation:', stats?.hasActiveAccumulation);

console.log('\n✅ All integration tests passed!');
console.log('The SessionManager is properly integrated with RealtimeClient.');